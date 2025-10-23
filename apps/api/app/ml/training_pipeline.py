"""ML Training Pipeline for automated model training and management.

Handles data preparation, training, validation, hyperparameter tuning,
and model versioning for all Phase 2 custom models.
"""

import logging
from typing import Dict, Any, Optional, List, Type
from pathlib import Path
from datetime import datetime
import json

import pandas as pd
from sqlalchemy.orm import Session

from apps.api.app.ml.models.lead_scoring import LeadScoringModel
from apps.api.app.ml.models.churn_prediction import ChurnPredictionModel
from apps.api.app.ml.models.engagement_prediction import EngagementPredictionModel
from apps.api.app.crud import lead as lead_crud
from apps.api.app.crud import contact as contact_crud
from apps.api.app.crud import message as message_crud
from apps.api.app.crud import campaign as campaign_crud

logger = logging.getLogger(__name__)


class MLTrainingPipeline:
    """Automated ML training pipeline for all custom models."""

    def __init__(
        self,
        models_dir: str = "models",
        min_training_samples: int = 100,
    ):
        """Initialize training pipeline.

        Args:
            models_dir: Directory to save trained models
            min_training_samples: Minimum samples required for training
        """
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.min_training_samples = min_training_samples
        
        self.supported_models = {
            "lead_scoring": LeadScoringModel,
            "churn_prediction": ChurnPredictionModel,
            "engagement_prediction": EngagementPredictionModel,
        }

    def prepare_lead_scoring_data(
        self, db: Session, user_id: int
    ) -> List[Dict[str, Any]]:
        """Prepare training data for lead scoring model.

        Args:
            db: Database session
            user_id: User ID to get data for

        Returns:
            List of lead dictionaries with features and scores
        """
        logger.info("Preparing lead scoring training data...")
        
        # Get all leads with their interactions
        leads = lead_crud.get_leads(db, user_id=user_id)
        
        training_data = []
        for lead in leads:
            # Skip if no score assigned (need labeled data)
            if lead.score is None:
                continue
            
            # Get messages for this lead
            messages = message_crud.get_messages_by_contact(
                db, contact_id=lead.contact_id
            )
            
            # Calculate features
            lead_data = {
                "lead_score": lead.score,  # Target variable
                
                # Response behavior
                "avg_response_time_minutes": self._calculate_avg_response_time(messages),
                "response_rate": len([m for m in messages if m.direction == "inbound"]) / max(len(messages), 1),
                "messages_received": len([m for m in messages if m.direction == "inbound"]),
                "messages_sent": len([m for m in messages if m.direction == "outbound"]),
                
                # Engagement metrics
                "conversation_count": len(set(m.conversation_id for m in messages if m.conversation_id)),
                "avg_conversation_length": len(messages) / max(1, len(set(m.conversation_id for m in messages if m.conversation_id))),
                "days_since_first_contact": (datetime.utcnow() - lead.created_at).days,
                "days_since_last_contact": (datetime.utcnow() - lead.updated_at).days,
                "contact_frequency_per_week": len(messages) / max(1, (datetime.utcnow() - lead.created_at).days / 7),
                
                # Sentiment (placeholder - integrate with sentiment analyzer)
                "avg_sentiment_score": 0.5,
                "positive_sentiment_ratio": 0.3,
                "negative_sentiment_ratio": 0.1,
                "avg_emotion_score": 0.5,
                
                # Campaign interaction (placeholder)
                "campaign_opens": 0,
                "campaign_clicks": 0,
                "campaign_responses": 0,
                "campaign_engagement_rate": 0.0,
                
                # Time patterns
                "preferred_contact_hour": 14,
                "weekend_activity_ratio": 0.2,
                "business_hours_ratio": 0.7,
                
                # Lead indicators
                "question_count": len([m for m in messages if "?" in (m.content or "")]),
                "price_inquiry_count": self._count_price_inquiries(messages),
                "meeting_request_count": 0,
                "positive_keywords_count": 0,
            }
            
            training_data.append(lead_data)
        
        logger.info(f"Prepared {len(training_data)} lead scoring samples")
        return training_data

    def prepare_churn_data(
        self, db: Session, user_id: int
    ) -> List[Dict[str, Any]]:
        """Prepare training data for churn prediction model.

        Args:
            db: Database session
            user_id: User ID to get data for

        Returns:
            List of customer dictionaries with features and churn labels
        """
        logger.info("Preparing churn prediction training data...")
        
        contacts = contact_crud.get_contacts(db, user_id=user_id)
        
        training_data = []
        for contact in contacts:
            # Determine if churned (no activity in 90+ days)
            messages = message_crud.get_messages_by_contact(db, contact_id=contact.id)
            if not messages:
                continue
            
            last_message_date = max(m.created_at for m in messages)
            days_inactive = (datetime.utcnow() - last_message_date).days
            churned = days_inactive > 90
            
            customer_data = {
                "churned": churned,  # Target variable
                
                # Recency metrics
                "days_since_last_purchase": days_inactive,  # Placeholder
                "days_since_last_message": days_inactive,
                "days_since_last_campaign_open": days_inactive,
                
                # Frequency decline
                "messages_this_month": len([m for m in messages if (datetime.utcnow() - m.created_at).days <= 30]),
                "messages_last_month": len([m for m in messages if 30 < (datetime.utcnow() - m.created_at).days <= 60]),
                "purchase_frequency_decline": 0.0,
                "engagement_frequency_decline": self._calculate_engagement_decline(messages),
                
                # Monetary value (placeholder)
                "total_lifetime_value": 0.0,
                "avg_order_value": 0.0,
                "months_since_first_purchase": (datetime.utcnow() - contact.created_at).days / 30,
                
                # Support interactions (placeholder)
                "support_tickets_count": 0,
                "unresolved_tickets_count": 0,
                "avg_ticket_resolution_days": 0.0,
                "complaint_count": 0,
                
                # Sentiment trends (placeholder)
                "current_sentiment_score": 0.5,
                "sentiment_score_30d_ago": 0.5,
                "sentiment_decline_rate": 0.0,
                "negative_sentiment_ratio": 0.0,
                
                # Engagement decline
                "response_rate_current": 0.0,
                "response_rate_30d_ago": 0.0,
                "campaign_engagement_decline": 0.0,
                "conversation_length_decline": 0.0,
                
                # Product interaction (placeholder)
                "product_views_decline": 0.0,
                "cart_abandonment_rate": 0.0,
                "refund_count": 0,
                "discount_usage_increase": 0.0,
                
                # Behavioral signals
                "unsubscribe_attempts": 1 if contact.is_unsubscribed else 0,
                "opted_out_campaigns": 0,
                "ignored_messages_ratio": 0.0,
                "contact_preference_changes": 0,
            }
            
            training_data.append(customer_data)
        
        logger.info(f"Prepared {len(training_data)} churn prediction samples")
        return training_data

    def prepare_engagement_data(
        self, db: Session, user_id: int
    ) -> List[Dict[str, Any]]:
        """Prepare training data for engagement prediction model.

        Args:
            db: Database session
            user_id: User ID to get data for

        Returns:
            List of engagement dictionaries with features and labels
        """
        logger.info("Preparing engagement prediction training data...")
        
        messages = message_crud.get_user_messages(db, user_id=user_id)
        
        training_data = []
        for message in messages:
            if message.direction != "outbound":
                continue
            
            # Check if message was engaged with (replied within 24 hours)
            contact_messages = message_crud.get_messages_by_contact(
                db, contact_id=message.contact_id
            )
            
            later_messages = [
                m for m in contact_messages
                if m.direction == "inbound" and m.created_at > message.created_at
                and (m.created_at - message.created_at).total_seconds() < 86400
            ]
            
            engaged = len(later_messages) > 0
            
            engagement_data = {
                "engaged": engaged,  # Target variable
                
                # Historical engagement (placeholder)
                "past_open_rate": 0.5,
                "past_click_rate": 0.3,
                "past_response_rate": 0.4,
                "avg_response_time_hours": 12.0,
                
                # Time patterns
                "hour_of_day": message.created_at.hour,
                "day_of_week": message.created_at.weekday(),
                "is_weekend": message.created_at.weekday() >= 5,
                "is_business_hours": 9 <= message.created_at.hour <= 17,
                
                # Recency
                "days_since_last_engagement": 7,
                "days_since_last_campaign": 7,
                "hours_since_last_message": 24,
                
                # Contact preferences (placeholder)
                "preferred_contact_hour": 14,
                "preferred_day_of_week": 2,
                "timezone_offset": 0,
                
                # Campaign characteristics
                "message_length": len(message.content or ""),
                "has_media": bool(message.media_url),
                "has_link": "http" in (message.content or ""),
                "has_call_to_action": any(
                    word in (message.content or "").lower()
                    for word in ["click", "buy", "visit", "shop", "order", "register"]
                ),
                "personalization_level": 0.5,
                
                # Historical performance (placeholder)
                "engagement_rate_this_hour": 0.5,
                "engagement_rate_this_day": 0.5,
                "engagement_rate_this_weekday": 0.5,
                
                # Contact activity
                "messages_received_last_7d": len(contact_messages),
                "campaigns_received_last_30d": 0,
                "conversation_count_last_30d": 0,
                
                # Sentiment & quality (placeholder)
                "avg_sentiment_score_last_30d": 0.5,
                "message_quality_score": 0.5,
            }
            
            training_data.append(engagement_data)
        
        logger.info(f"Prepared {len(training_data)} engagement prediction samples")
        return training_data

    def train_model(
        self,
        model_name: str,
        training_data: List[Dict[str, Any]],
        hyperparameters: Optional[Dict[str, Any]] = None,
        save_model: bool = True,
    ) -> Dict[str, Any]:
        """Train a specific model.

        Args:
            model_name: Name of model to train (lead_scoring, churn_prediction, engagement_prediction)
            training_data: Prepared training data
            hyperparameters: Optional hyperparameters for the model
            save_model: Whether to save trained model to disk

        Returns:
            Training result with metrics and metadata
        """
        if model_name not in self.supported_models:
            return {
                "success": False,
                "error": f"Unsupported model: {model_name}",
            }
        
        if len(training_data) < self.min_training_samples:
            return {
                "success": False,
                "error": f"Insufficient training data: {len(training_data)} < {self.min_training_samples}",
            }
        
        try:
            logger.info(f"Training {model_name} model...")
            
            # Initialize model
            model_class = self.supported_models[model_name]
            model = model_class()
            
            # Train
            result = model.train(
                training_data=training_data,
                hyperparameters=hyperparameters,
            )
            
            # Save if successful
            if result.get("success") and save_model:
                model_path = self.models_dir / f"{model_name}.joblib"
                model.save(str(model_path))
                result["model_path"] = str(model_path)
            
            return result
            
        except Exception as e:
            logger.error(f"Model training failed: {e}")
            return {
                "success": False,
                "error": str(e),
            }

    def train_all_models(
        self, db: Session, user_id: int
    ) -> Dict[str, Any]:
        """Train all custom ML models.

        Args:
            db: Database session
            user_id: User ID to train models for

        Returns:
            Training results for all models
        """
        logger.info("Starting full training pipeline...")
        
        results = {}
        
        # Train lead scoring
        try:
            lead_data = self.prepare_lead_scoring_data(db, user_id)
            results["lead_scoring"] = self.train_model("lead_scoring", lead_data)
        except Exception as e:
            logger.error(f"Lead scoring training failed: {e}")
            results["lead_scoring"] = {"success": False, "error": str(e)}
        
        # Train churn prediction
        try:
            churn_data = self.prepare_churn_data(db, user_id)
            results["churn_prediction"] = self.train_model("churn_prediction", churn_data)
        except Exception as e:
            logger.error(f"Churn prediction training failed: {e}")
            results["churn_prediction"] = {"success": False, "error": str(e)}
        
        # Train engagement prediction
        try:
            engagement_data = self.prepare_engagement_data(db, user_id)
            results["engagement_prediction"] = self.train_model(
                "engagement_prediction", engagement_data
            )
        except Exception as e:
            logger.error(f"Engagement prediction training failed: {e}")
            results["engagement_prediction"] = {"success": False, "error": str(e)}
        
        # Summary
        successful = sum(1 for r in results.values() if r.get("success"))
        
        summary = {
            "total_models": len(results),
            "successful": successful,
            "failed": len(results) - successful,
            "timestamp": datetime.utcnow().isoformat(),
            "models": results,
        }
        
        logger.info(
            f"✅ Training pipeline complete: "
            f"{successful}/{len(results)} models trained successfully"
        )
        
        return summary

    def _calculate_avg_response_time(self, messages: List) -> float:
        """Calculate average response time in minutes."""
        if len(messages) < 2:
            return 60.0
        
        response_times = []
        for i in range(1, len(messages)):
            if messages[i].direction == "inbound" and messages[i-1].direction == "outbound":
                time_diff = (messages[i].created_at - messages[i-1].created_at).total_seconds() / 60
                response_times.append(time_diff)
        
        return sum(response_times) / len(response_times) if response_times else 60.0

    def _count_price_inquiries(self, messages: List) -> int:
        """Count messages with price-related keywords."""
        price_keywords = ["price", "cost", "how much", "payment", "pay", "$"]
        count = 0
        
        for message in messages:
            if any(keyword in (message.content or "").lower() for keyword in price_keywords):
                count += 1
        
        return count

    def _calculate_engagement_decline(self, messages: List) -> float:
        """Calculate engagement frequency decline rate."""
        if len(messages) < 2:
            return 0.0
        
        # Split into two periods
        mid_point = len(messages) // 2
        first_half = messages[:mid_point]
        second_half = messages[mid_point:]
        
        if not first_half or not second_half:
            return 0.0
        
        # Calculate frequency (messages per day)
        first_days = (first_half[-1].created_at - first_half[0].created_at).days or 1
        second_days = (second_half[-1].created_at - second_half[0].created_at).days or 1
        
        first_freq = len(first_half) / first_days
        second_freq = len(second_half) / second_days
        
        # Calculate decline rate
        if first_freq == 0:
            return 0.0
        
        return (first_freq - second_freq) / first_freq


# Global singleton instance
_training_pipeline: Optional[MLTrainingPipeline] = None


def get_training_pipeline(models_dir: str = "models") -> MLTrainingPipeline:
    """Get or create global training pipeline instance."""
    global _training_pipeline
    if _training_pipeline is None:
        _training_pipeline = MLTrainingPipeline(models_dir=models_dir)
    return _training_pipeline
