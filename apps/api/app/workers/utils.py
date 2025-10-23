"""
Utility classes for campaign workers.
"""
import asyncio
import random
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from redis import Redis
import re

from ..core.config import settings

logger = logging.getLogger(__name__)


class MessageThrottler:
    """
    Throttles message sending to avoid rate limits and bans.
    """
    
    def __init__(self, phone_number_id: int):
        self.phone_number_id = phone_number_id
        self.redis = Redis.from_url(settings.REDIS_URL, decode_responses=True)
        
        self.max_per_hour = settings.MAX_MESSAGES_PER_HOUR
        self.max_per_day = settings.MAX_MESSAGES_PER_DAY
        self.min_delay = settings.MESSAGE_DELAY_MIN
        self.max_delay = settings.MESSAGE_DELAY_MAX
    
    def can_send_message(self) -> bool:
        """Check if we can send another message without exceeding limits."""
        now = datetime.utcnow()
        hour_key = f"throttle:hour:{self.phone_number_id}:{now.strftime('%Y%m%d%H')}"
        day_key = f"throttle:day:{self.phone_number_id}:{now.strftime('%Y%m%d')}"
        
        hour_count = int(self.redis.get(hour_key) or 0)
        day_count = int(self.redis.get(day_key) or 0)
        
        if hour_count >= self.max_per_hour:
            logger.warning(f"Hourly limit reached: {hour_count}/{self.max_per_hour}")
            return False
        
        if day_count >= self.max_per_day:
            logger.warning(f"Daily limit reached: {day_count}/{self.max_per_day}")
            return False
        
        return True
    
    def record_message_sent(self):
        """Record that a message was sent."""
        now = datetime.utcnow()
        hour_key = f"throttle:hour:{self.phone_number_id}:{now.strftime('%Y%m%d%H')}"
        day_key = f"throttle:day:{self.phone_number_id}:{now.strftime('%Y%m%d')}"
        
        # Increment counters
        self.redis.incr(hour_key)
        self.redis.incr(day_key)
        
        # Set expiry
        self.redis.expire(hour_key, 3600)  # 1 hour
        self.redis.expire(day_key, 86400)  # 1 day
    
    async def delay(self):
        """Apply random delay between messages to appear human."""
        delay_seconds = random.uniform(self.min_delay, self.max_delay)
        logger.debug(f"Throttle delay: {delay_seconds:.2f}s")
        await asyncio.sleep(delay_seconds)


class WarmupManager:
    """
    Manages phone number warmup to gradually increase sending volume.
    """
    
    def __init__(self, phone_number_id: int):
        self.phone_number_id = phone_number_id
        self.redis = Redis.from_url(settings.REDIS_URL, decode_responses=True)
        self.warmup_days = settings.WARMUP_DAYS
        
        # Warmup schedule (day: max messages)
        self.schedule = {
            1: 20,
            2: 30,
            3: 50,
            4: 75,
            5: 100,
            6: 150,
            7: 200,
            8: 300,
            9: 400,
            10: 500,
            11: 700,
            12: 900,
            13: 1000,
            14: 1000,  # Fully warmed up
        }
    
    def get_warmup_day(self) -> Optional[int]:
        """Get current warmup day (1-14) or None if not in warmup."""
        start_date_str = self.redis.get(f"warmup:start:{self.phone_number_id}")
        
        if not start_date_str:
            # Start warmup
            now = datetime.utcnow()
            self.redis.set(
                f"warmup:start:{self.phone_number_id}",
                now.isoformat(),
                ex=self.warmup_days * 86400  # Expire after warmup period
            )
            return 1
        
        start_date = datetime.fromisoformat(start_date_str)
        days_elapsed = (datetime.utcnow() - start_date).days + 1
        
        if days_elapsed > self.warmup_days:
            return None  # Warmup complete
        
        return days_elapsed
    
    def is_warmed_up(self) -> bool:
        """Check if number is fully warmed up."""
        warmup_day = self.get_warmup_day()
        return warmup_day is None or warmup_day >= self.warmup_days
    
    def get_daily_limit(self) -> int:
        """Get daily message limit based on warmup status."""
        if self.is_warmed_up():
            return settings.MAX_MESSAGES_PER_DAY
        
        warmup_day = self.get_warmup_day()
        return self.schedule.get(warmup_day, 20)
    
    def record_message_sent(self):
        """Record message sent during warmup."""
        warmup_day = self.get_warmup_day()
        if warmup_day:
            day_key = f"warmup:sent:{self.phone_number_id}:{datetime.utcnow().strftime('%Y%m%d')}"
            self.redis.incr(day_key)
            self.redis.expire(day_key, 86400)
    
    def get_messages_sent_today(self) -> int:
        """Get count of messages sent today during warmup."""
        day_key = f"warmup:sent:{self.phone_number_id}:{datetime.utcnow().strftime('%Y%m%d')}"
        return int(self.redis.get(day_key) or 0)


class MessagePersonalizer:
    """
    Personalizes message templates with contact data.
    """
    
    def personalize(
        self,
        template: str,
        contact: Any,
        additional_vars: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Replace template variables with contact data.
        
        Template syntax: {variable_name}
        
        Available variables:
        - {name} or {first_name}: Contact's first name
        - {last_name}: Contact's last name
        - {full_name}: Full name
        - {phone}: Phone number
        - {email}: Email address
        - {company}: Company name
        - Any custom field from contact.metadata
        
        Args:
            template: Message template with variables
            contact: Contact object
            additional_vars: Additional variables to replace
            
        Returns:
            Personalized message
        """
        # Build variables dict
        variables = {
            "name": self._get_first_name(contact.name or ""),
            "first_name": self._get_first_name(contact.name or ""),
            "last_name": self._get_last_name(contact.name or ""),
            "full_name": contact.name or "there",
            "phone": contact.phone or "",
            "email": contact.email or "",
            "company": contact.metadata.get("company", "") if contact.metadata else "",
        }
        
        # Add metadata fields
        if contact.metadata:
            variables.update(contact.metadata)
        
        # Add additional variables
        if additional_vars:
            variables.update(additional_vars)
        
        # Replace variables in template
        result = template
        for key, value in variables.items():
            pattern = r'\{' + re.escape(key) + r'\}'
            result = re.sub(pattern, str(value), result, flags=re.IGNORECASE)
        
        # Clean up any remaining unreplaced variables
        result = re.sub(r'\{[^}]+\}', '', result)
        
        return result.strip()
    
    def _get_first_name(self, full_name: str) -> str:
        """Extract first name from full name."""
        if not full_name:
            return "there"
        return full_name.split()[0]
    
    def _get_last_name(self, full_name: str) -> str:
        """Extract last name from full name."""
        if not full_name:
            return ""
        parts = full_name.split()
        return parts[-1] if len(parts) > 1 else ""


class RetryManager:
    """
    Manages message retry with exponential backoff.
    """
    
    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries
        self.redis = Redis.from_url(settings.REDIS_URL, decode_responses=True)
    
    def should_retry(self, message_id: int) -> bool:
        """Check if message should be retried."""
        retry_count = self.get_retry_count(message_id)
        return retry_count < self.max_retries
    
    def get_retry_count(self, message_id: int) -> int:
        """Get current retry count for message."""
        key = f"retry:count:{message_id}"
        return int(self.redis.get(key) or 0)
    
    def increment_retry(self, message_id: int) -> int:
        """Increment retry count and return new count."""
        key = f"retry:count:{message_id}"
        count = self.redis.incr(key)
        self.redis.expire(key, 86400)  # Expire after 1 day
        return count
    
    def get_retry_delay(self, retry_count: int) -> int:
        """Calculate exponential backoff delay in seconds."""
        # Exponential backoff: 2^retry_count minutes
        delay_minutes = 2 ** retry_count
        return delay_minutes * 60
    
    def schedule_retry(self, message_id: int, task_name: str, **kwargs):
        """Schedule message retry with exponential backoff."""
        from .celery_app import celery_app
        
        retry_count = self.increment_retry(message_id)
        
        if retry_count > self.max_retries:
            logger.warning(f"Message {message_id} exceeded max retries ({self.max_retries})")
            return
        
        delay = self.get_retry_delay(retry_count)
        logger.info(f"Scheduling retry {retry_count} for message {message_id} in {delay}s")
        
        # Schedule task
        celery_app.send_task(
            task_name,
            kwargs=kwargs,
            countdown=delay
        )


def format_phone_number(phone: str) -> str:
    """Format phone number to E.164 format."""
    import phonenumbers
    
    try:
        parsed = phonenumbers.parse(phone, None)
        return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
    except Exception:
        # Remove non-digit characters
        digits = re.sub(r'\D', '', phone)
        if not digits.startswith('+'):
            digits = '+' + digits
        return digits


def extract_variables_from_template(template: str) -> list[str]:
    """Extract variable names from template."""
    return re.findall(r'\{([^}]+)\}', template)


def validate_template(template: str, required_vars: Optional[list[str]] = None) -> Dict[str, Any]:
    """
    Validate message template.
    
    Returns:
        Dict with is_valid (bool), errors (list), and variables (list)
    """
    errors = []
    variables = extract_variables_from_template(template)
    
    # Check length
    if len(template) > 4096:
        errors.append("Template exceeds maximum length (4096 characters)")
    
    # Check for required variables
    if required_vars:
        missing = set(required_vars) - set(variables)
        if missing:
            errors.append(f"Missing required variables: {', '.join(missing)}")
    
    # Check for balanced braces
    if template.count('{') != template.count('}'):
        errors.append("Unbalanced braces in template")
    
    return {
        "is_valid": len(errors) == 0,
        "errors": errors,
        "variables": variables,
    }
