"""
Campaign execution and scheduling workers.
"""
import logging
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from .celery_app import celery_app
from ..core.database import get_db
from ..crud import campaign as campaign_crud
from ..crud import message as message_crud
from ..crud import contact as contact_crud
from ..models.campaign import CampaignStatus
from ..models.message import MessageStatus
from ..connectors.whatsapp_gateway import WhatsAppGatewayConnector
from ..ai import MessageRewriter, BanRiskDetector
from ..core.config import settings
from .utils import WarmupManager, MessageThrottler, MessagePersonalizer

logger = logging.getLogger(__name__)


@celery_app.task(name="app.workers.campaign_worker.execute_campaign")
def execute_campaign(campaign_id: int):
    """
    Execute a campaign by sending messages to all contacts.
    
    Args:
        campaign_id: Campaign ID to execute
    """
    logger.info(f"Starting campaign execution: {campaign_id}")
    
    # Run async function in event loop
    asyncio.run(_execute_campaign_async(campaign_id))


async def _execute_campaign_async(campaign_id: int):
    """Async implementation of campaign execution."""
    db = next(get_db())
    
    try:
        # Get campaign
        campaign = campaign_crud.get_campaign(db, campaign_id)
        if not campaign:
            logger.error(f"Campaign {campaign_id} not found")
            return
        
        # Update status to running
        campaign_crud.update_campaign(
            db,
            campaign_id,
            {"status": CampaignStatus.RUNNING, "started_at": datetime.utcnow()}
        )
        
        # Get contacts
        contacts = contact_crud.get_contacts_by_ids(db, campaign.contact_ids)
        if not contacts:
            logger.warning(f"No contacts found for campaign {campaign_id}")
            campaign_crud.update_campaign(db, campaign_id, {"status": CampaignStatus.COMPLETED})
            return
        
        logger.info(f"Campaign {campaign_id}: {len(contacts)} contacts to process")
        
        # Initialize services
        gateway = WhatsAppGatewayConnector()
        rewriter = MessageRewriter()
        throttler = MessageThrottler(campaign.phone_number_id)
        warmup = WarmupManager(campaign.phone_number_id)
        personalizer = MessagePersonalizer()
        
        # Check if warmup is needed
        if settings.WARMUP_ENABLED and not warmup.is_warmed_up():
            max_messages = warmup.get_daily_limit()
            logger.info(f"Number in warmup phase, limiting to {max_messages} messages")
            contacts = contacts[:max_messages]
        
        # Process contacts
        success_count = 0
        failed_count = 0
        
        for contact in contacts:
            try:
                # Check throttling
                if not throttler.can_send_message():
                    logger.warning(f"Throttle limit reached for campaign {campaign_id}")
                    break
                
                # Personalize message
                personalized_msg = personalizer.personalize(
                    campaign.message_template,
                    contact
                )
                
                # Optionally rewrite message with AI
                if settings.AI_MESSAGE_REWRITING_ENABLED:
                    final_message = await rewriter.rewrite_message(
                        personalized_msg,
                        contact_name=contact.name,
                        tone=campaign.metadata.get("tone", "friendly")
                    )
                else:
                    final_message = personalized_msg
                
                # Send message
                result = await gateway.send_message(
                    to=contact.phone,
                    message=final_message
                )
                
                # Create message record
                message_crud.create_message(
                    db,
                    {
                        "campaign_id": campaign_id,
                        "contact_id": contact.id,
                        "phone_number_id": campaign.phone_number_id,
                        "content": final_message,
                        "status": MessageStatus.SENT if result.get("success") else MessageStatus.FAILED,
                        "external_id": result.get("message_id"),
                        "sent_at": datetime.utcnow() if result.get("success") else None,
                        "metadata": {"gateway_response": result}
                    }
                )
                
                if result.get("success"):
                    success_count += 1
                    throttler.record_message_sent()
                    warmup.record_message_sent()
                else:
                    failed_count += 1
                    logger.error(f"Failed to send to {contact.phone}: {result.get('error')}")
                
                # Throttle delay
                await throttler.delay()
                
            except Exception as e:
                logger.error(f"Error processing contact {contact.id}: {e}")
                failed_count += 1
        
        # Update campaign stats
        campaign_crud.update_campaign(
            db,
            campaign_id,
            {
                "status": CampaignStatus.COMPLETED,
                "completed_at": datetime.utcnow(),
                "metadata": {
                    **campaign.metadata,
                    "messages_sent": success_count,
                    "messages_failed": failed_count,
                }
            }
        )
        
        logger.info(
            f"Campaign {campaign_id} completed: "
            f"{success_count} sent, {failed_count} failed"
        )
        
    except Exception as e:
        logger.error(f"Campaign {campaign_id} execution failed: {e}")
        campaign_crud.update_campaign(
            db,
            campaign_id,
            {"status": CampaignStatus.FAILED, "metadata": {"error": str(e)}}
        )
    finally:
        db.close()


@celery_app.task(name="app.workers.campaign_worker.process_scheduled_campaigns")
def process_scheduled_campaigns():
    """Process campaigns that are scheduled to start now."""
    db = next(get_db())
    
    try:
        # Find campaigns scheduled to run
        now = datetime.utcnow()
        campaigns = campaign_crud.get_campaigns_by_status(db, CampaignStatus.SCHEDULED)
        
        for campaign in campaigns:
            scheduled_time = campaign.scheduled_for
            if scheduled_time and scheduled_time <= now:
                logger.info(f"Starting scheduled campaign {campaign.id}")
                execute_campaign.delay(campaign.id)
                
    except Exception as e:
        logger.error(f"Error processing scheduled campaigns: {e}")
    finally:
        db.close()


@celery_app.task(name="app.workers.campaign_worker.process_drip_sequences")
def process_drip_sequences():
    """Process drip campaign sequences."""
    db = next(get_db())
    
    try:
        # Get active drip campaigns
        campaigns = campaign_crud.get_campaigns_by_type(db, "drip")
        
        for campaign in campaigns:
            if campaign.status != CampaignStatus.RUNNING:
                continue
            
            # Process drip sequence
            asyncio.run(_process_drip_sequence(db, campaign))
            
    except Exception as e:
        logger.error(f"Error processing drip sequences: {e}")
    finally:
        db.close()


async def _process_drip_sequence(db: Session, campaign):
    """Process a single drip campaign sequence."""
    # Get campaign sequence configuration
    sequence = campaign.metadata.get("sequence", [])
    if not sequence:
        return
    
    gateway = WhatsAppGatewayConnector()
    personalizer = MessagePersonalizer()
    
    # Get all contacts and their message history
    for contact_id in campaign.contact_ids:
        contact = contact_crud.get_contact(db, contact_id)
        if not contact:
            continue
        
        # Get messages already sent to this contact
        messages = message_crud.get_messages_by_contact(db, contact_id, campaign.id)
        current_step = len(messages)
        
        # Check if there's a next step
        if current_step >= len(sequence):
            continue  # Sequence completed
        
        # Get next step
        step = sequence[current_step]
        delay_hours = step.get("delay_hours", 24)
        
        # Check if enough time has passed since last message
        if messages:
            last_message = max(messages, key=lambda m: m.sent_at or datetime.min)
            if last_message.sent_at:
                hours_since = (datetime.utcnow() - last_message.sent_at).total_seconds() / 3600
                if hours_since < delay_hours:
                    continue  # Not time yet
        elif current_step > 0:
            continue  # No messages sent yet but not first step
        
        # Send next message in sequence
        try:
            message_template = step.get("message", "")
            personalized_msg = personalizer.personalize(message_template, contact)
            
            result = await gateway.send_message(
                to=contact.phone,
                message=personalized_msg
            )
            
            # Record message
            message_crud.create_message(
                db,
                {
                    "campaign_id": campaign.id,
                    "contact_id": contact.id,
                    "phone_number_id": campaign.phone_number_id,
                    "content": personalized_msg,
                    "status": MessageStatus.SENT if result.get("success") else MessageStatus.FAILED,
                    "external_id": result.get("message_id"),
                    "sent_at": datetime.utcnow() if result.get("success") else None,
                    "metadata": {
                        "drip_step": current_step,
                        "gateway_response": result
                    }
                }
            )
            
            logger.info(f"Drip campaign {campaign.id}: sent step {current_step} to contact {contact_id}")
            
        except Exception as e:
            logger.error(f"Error sending drip message to {contact_id}: {e}")


@celery_app.task(name="app.workers.campaign_worker.monitor_ban_risks")
def monitor_ban_risks():
    """Monitor and alert on ban risks."""
    db = next(get_db())
    
    try:
        asyncio.run(_monitor_ban_risks_async(db))
    except Exception as e:
        logger.error(f"Error monitoring ban risks: {e}")
    finally:
        db.close()


async def _monitor_ban_risks_async(db: Session):
    """Async ban risk monitoring."""
    detector = BanRiskDetector()
    
    # Get active campaigns
    active_campaigns = campaign_crud.get_campaigns_by_status(db, CampaignStatus.RUNNING)
    
    for campaign in active_campaigns:
        # Get recent messages
        messages = message_crud.get_recent_messages(
            db,
            phone_number_id=campaign.phone_number_id,
            hours=24
        )
        
        if not messages:
            continue
        
        # Analyze pattern
        message_data = [
            {
                "text": msg.content,
                "sent_at": msg.sent_at,
                "replied": bool(msg.reply),
                "blocked": msg.status == MessageStatus.BLOCKED,
            }
            for msg in messages
        ]
        
        risk_analysis = await detector.analyze_message_pattern(message_data)
        
        # Alert if high risk
        if risk_analysis["risk_level"] in ["high", "critical"]:
            logger.warning(
                f"⚠️ HIGH BAN RISK for campaign {campaign.id}: "
                f"Score {risk_analysis['risk_score']}/100"
            )
            logger.warning(f"Factors: {risk_analysis['factors']}")
            logger.warning(f"Recommendations: {risk_analysis['recommendations']}")
            
            # Pause campaign if critical
            if risk_analysis["risk_level"] == "critical":
                campaign_crud.update_campaign(
                    db,
                    campaign.id,
                    {
                        "status": CampaignStatus.PAUSED,
                        "metadata": {
                            **campaign.metadata,
                            "paused_reason": "Critical ban risk detected",
                            "ban_risk_analysis": risk_analysis,
                        }
                    }
                )
                logger.error(f"🚨 Campaign {campaign.id} PAUSED due to critical ban risk")
