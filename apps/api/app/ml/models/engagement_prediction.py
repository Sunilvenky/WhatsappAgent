"""Engagement Prediction Model using Logistic Regression.

Predicts optimal send times and engagement likelihood for campaigns
based on historical interaction patterns.
"""

import logging
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
from datetime import datetime, time
import json

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
)
import joblib

logger = logging.getLogger(__name__)


class EngagementPredictionModel:
    """Logistic Regression model for predicting message engagement."""

    def __init__(self, model_path: Optional[str] = None):
        """Initialize engagement prediction model.

        Args:
            model_path: Path to saved model file (loads if exists)
        """
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = [
            # Historical engagement
            "past_open_rate",
            "past_click_rate",
            "past_response_rate",
            "avg_response_time_hours",
            
            # Time patterns
            "hour_of_day",
            "day_of_week",  # 0=Monday, 6=Sunday
            "is_weekend",
            "is_business_hours",
            
            # Recency
            "days_since_last_engagement",
            "days_since_last_campaign",
            "hours_since_last_message",
            
            # Contact preferences
            "preferred_contact_hour",
            "preferred_day_of_week",
            "timezone_offset",
            
            # Campaign characteristics
            "message_length",
            "has_media",
            "has_link",
            "has_call_to_action",
            "personalization_level",  # 0-1
            
            # Historical performance by time
            "engagement_rate_this_hour",
            "engagement_rate_this_day",
            "engagement_rate_this_weekday",
            
            # Contact activity
            "messages_received_last_7d",
            "campaigns_received_last_30d",
            "conversation_count_last_30d",
            
            # Sentiment & quality
            "avg_sentiment_score_last_30d",
            "message_quality_score",  # Based on past campaigns
        ]
        
        self.model_metadata = {
            "version": "1.0.0",
            "created_at": None,
            "trained_samples": 0,
            "feature_importance": {},
            "performance_metrics": {},
        }
        
        if model_path and Path(model_path).exists():
            self.load(model_path)

    def prepare_features(
        self, engagement_data: Dict[str, Any]
    ) -> pd.DataFrame:
        """Prepare features from engagement data.

        Args:
            engagement_data: Dictionary with contact and campaign information

        Returns:
            DataFrame with prepared features
        """
        features = {}
        
        # Historical engagement
        features["past_open_rate"] = engagement_data.get("past_open_rate", 0.0)
        features["past_click_rate"] = engagement_data.get("past_click_rate", 0.0)
        features["past_response_rate"] = engagement_data.get("past_response_rate", 0.0)
        features["avg_response_time_hours"] = engagement_data.get(
            "avg_response_time_hours", 24.0
        )
        
        # Time patterns
        features["hour_of_day"] = engagement_data.get("hour_of_day", 12)
        features["day_of_week"] = engagement_data.get("day_of_week", 2)
        features["is_weekend"] = float(engagement_data.get("is_weekend", False))
        features["is_business_hours"] = float(
            engagement_data.get("is_business_hours", True)
        )
        
        # Recency
        features["days_since_last_engagement"] = engagement_data.get(
            "days_since_last_engagement", 30
        )
        features["days_since_last_campaign"] = engagement_data.get(
            "days_since_last_campaign", 30
        )
        features["hours_since_last_message"] = engagement_data.get(
            "hours_since_last_message", 168
        )
        
        # Contact preferences
        features["preferred_contact_hour"] = engagement_data.get(
            "preferred_contact_hour", 14
        )
        features["preferred_day_of_week"] = engagement_data.get(
            "preferred_day_of_week", 2
        )
        features["timezone_offset"] = engagement_data.get("timezone_offset", 0)
        
        # Campaign characteristics
        features["message_length"] = engagement_data.get("message_length", 100)
        features["has_media"] = float(engagement_data.get("has_media", False))
        features["has_link"] = float(engagement_data.get("has_link", False))
        features["has_call_to_action"] = float(
            engagement_data.get("has_call_to_action", False)
        )
        features["personalization_level"] = engagement_data.get(
            "personalization_level", 0.5
        )
        
        # Historical performance by time
        features["engagement_rate_this_hour"] = engagement_data.get(
            "engagement_rate_this_hour", 0.0
        )
        features["engagement_rate_this_day"] = engagement_data.get(
            "engagement_rate_this_day", 0.0
        )
        features["engagement_rate_this_weekday"] = engagement_data.get(
            "engagement_rate_this_weekday", 0.0
        )
        
        # Contact activity
        features["messages_received_last_7d"] = engagement_data.get(
            "messages_received_last_7d", 0
        )
        features["campaigns_received_last_30d"] = engagement_data.get(
            "campaigns_received_last_30d", 0
        )
        features["conversation_count_last_30d"] = engagement_data.get(
            "conversation_count_last_30d", 0
        )
        
        # Sentiment & quality
        features["avg_sentiment_score_last_30d"] = engagement_data.get(
            "avg_sentiment_score_last_30d", 0.5
        )
        features["message_quality_score"] = engagement_data.get(
            "message_quality_score", 0.5
        )
        
        return pd.DataFrame([features])

    def train(
        self,
        training_data: List[Dict[str, Any]],
        validation_split: float = 0.2,
        hyperparameters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Train engagement prediction model.

        Args:
            training_data: List of engagement dictionaries with features and labels
            validation_split: Fraction of data to use for validation
            hyperparameters: Logistic Regression hyperparameters

        Returns:
            Training metrics and validation results
        """
        try:
            logger.info(f"Training engagement model on {len(training_data)} samples")
            
            # Prepare features and labels
            X_list = []
            y_list = []
            
            for engagement in training_data:
                features_df = self.prepare_features(engagement)
                X_list.append(features_df)
                y_list.append(
                    1 if engagement.get("engaged", False) else 0
                )  # Binary: 1=engaged, 0=not engaged
            
            X = pd.concat(X_list, ignore_index=True)
            y = np.array(y_list)
            
            # Check class balance
            engagement_rate = y.mean()
            logger.info(f"Dataset engagement rate: {engagement_rate:.2%}")
            
            # Split data
            X_train, X_val, y_train, y_val = train_test_split(
                X, y, test_size=validation_split, random_state=42, stratify=y
            )
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_val_scaled = self.scaler.transform(X_val)
            
            # Default hyperparameters
            if hyperparameters is None:
                hyperparameters = {
                    "penalty": "l2",
                    "C": 1.0,
                    "solver": "lbfgs",
                    "max_iter": 1000,
                    "class_weight": "balanced",
                    "random_state": 42,
                }
            
            # Train model
            self.model = LogisticRegression(**hyperparameters)
            self.model.fit(X_train_scaled, y_train)
            
            # Evaluate
            y_train_pred = self.model.predict(X_train_scaled)
            y_val_pred = self.model.predict(X_val_scaled)
            y_val_proba = self.model.predict_proba(X_val_scaled)[:, 1]
            
            metrics = {
                "train_accuracy": float(accuracy_score(y_train, y_train_pred)),
                "train_precision": float(precision_score(y_train, y_train_pred)),
                "train_recall": float(recall_score(y_train, y_train_pred)),
                "train_f1": float(f1_score(y_train, y_train_pred)),
                "val_accuracy": float(accuracy_score(y_val, y_val_pred)),
                "val_precision": float(precision_score(y_val, y_val_pred)),
                "val_recall": float(recall_score(y_val, y_val_pred)),
                "val_f1": float(f1_score(y_val, y_val_pred)),
                "val_roc_auc": float(roc_auc_score(y_val, y_val_proba)),
            }
            
            # Feature importance (coefficients)
            feature_importance = dict(
                zip(
                    self.feature_names,
                    np.abs(self.model.coef_[0]).tolist(),
                )
            )
            
            # Update metadata
            self.model_metadata = {
                "version": "1.0.0",
                "created_at": datetime.utcnow().isoformat(),
                "trained_samples": len(training_data),
                "engagement_rate": float(engagement_rate),
                "feature_importance": feature_importance,
                "performance_metrics": metrics,
                "hyperparameters": hyperparameters,
            }
            
            logger.info(
                f"✅ Training complete: "
                f"Val F1={metrics['val_f1']:.3f}, "
                f"Val AUC={metrics['val_roc_auc']:.3f}"
            )
            
            return {
                "success": True,
                "metrics": metrics,
                "feature_importance": feature_importance,
                "metadata": self.model_metadata,
            }
            
        except Exception as e:
            logger.error(f"Training failed: {e}")
            return {
                "success": False,
                "error": str(e),
            }

    def predict(self, engagement_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predict engagement probability.

        Args:
            engagement_data: Contact and campaign information

        Returns:
            Prediction result with engagement probability and recommendations
        """
        if self.model is None:
            return {
                "engagement_probability": 0.5,
                "error": "Model not trained or loaded",
            }
        
        try:
            # Prepare features
            X = self.prepare_features(engagement_data)
            X_scaled = self.scaler.transform(X)
            
            # Predict
            engagement_proba = float(self.model.predict_proba(X_scaled)[0][1])
            will_engage = bool(self.model.predict(X_scaled)[0])
            
            # Engagement level
            if engagement_proba >= 0.7:
                level = "very_high"
            elif engagement_proba >= 0.5:
                level = "high"
            elif engagement_proba >= 0.3:
                level = "medium"
            else:
                level = "low"
            
            # Recommendations
            recommendations = self._generate_recommendations(
                engagement_data, engagement_proba
            )
            
            return {
                "engagement_probability": round(engagement_proba, 4),
                "will_engage": will_engage,
                "engagement_level": level,
                "recommendations": recommendations,
                "model_version": self.model_metadata.get("version"),
            }
            
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            return {
                "engagement_probability": 0.5,
                "error": str(e),
            }

    def predict_optimal_send_time(
        self, contact_data: Dict[str, Any], hours_to_test: List[int] = None
    ) -> Dict[str, Any]:
        """Predict optimal time to send message for maximum engagement.

        Args:
            contact_data: Contact information and preferences
            hours_to_test: List of hours to test (0-23). If None, tests all 24 hours.

        Returns:
            Optimal send time and engagement predictions for all hours
        """
        if hours_to_test is None:
            hours_to_test = list(range(24))
        
        predictions = []
        
        for hour in hours_to_test:
            # Create test data for this hour
            test_data = contact_data.copy()
            test_data["hour_of_day"] = hour
            test_data["is_business_hours"] = 9 <= hour <= 17
            
            # Predict
            result = self.predict(test_data)
            predictions.append({
                "hour": hour,
                "engagement_probability": result["engagement_probability"],
            })
        
        # Find optimal hour
        optimal = max(predictions, key=lambda x: x["engagement_probability"])
        
        return {
            "optimal_hour": optimal["hour"],
            "optimal_time": f"{optimal['hour']:02d}:00",
            "max_engagement_probability": optimal["engagement_probability"],
            "all_hours": predictions,
        }

    def predict_batch(
        self, engagements_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Predict engagement for multiple messages.

        Args:
            engagements_data: List of engagement dictionaries

        Returns:
            List of prediction results
        """
        results = []
        for engagement in engagements_data:
            result = self.predict(engagement)
            results.append(result)
        
        return results

    def _generate_recommendations(
        self, engagement_data: Dict[str, Any], engagement_proba: float
    ) -> List[str]:
        """Generate personalized engagement recommendations.

        Args:
            engagement_data: Engagement data
            engagement_proba: Predicted engagement probability

        Returns:
            List of actionable recommendations
        """
        recommendations = []
        
        hour = engagement_data.get("hour_of_day", 12)
        preferred_hour = engagement_data.get("preferred_contact_hour", 14)
        
        # Time optimization
        if abs(hour - preferred_hour) > 3:
            recommendations.append(
                f"⏰ Consider sending at {preferred_hour:02d}:00 "
                f"(contact's preferred time) for better engagement"
            )
        
        # Recency
        days_since_last = engagement_data.get("days_since_last_engagement", 0)
        if days_since_last > 14:
            recommendations.append(
                "📅 Contact has been inactive - consider re-engagement campaign"
            )
        
        # Message characteristics
        if not engagement_data.get("personalization_level", 0.5) > 0.3:
            recommendations.append(
                "✨ Add personalization (name, past purchases) to increase engagement"
            )
        
        if not engagement_data.get("has_call_to_action"):
            recommendations.append(
                "🎯 Include clear call-to-action to improve response rate"
            )
        
        # Campaign fatigue
        campaigns_30d = engagement_data.get("campaigns_received_last_30d", 0)
        if campaigns_30d > 10:
            recommendations.append(
                "⚠️ Contact may have campaign fatigue - space out messages"
            )
        
        if engagement_proba < 0.3:
            recommendations.append(
                "💡 Low engagement predicted - consider A/B testing message content"
            )
        
        return recommendations[:4]

    def save(self, path: str):
        """Save model and scaler to disk."""
        try:
            model_path = Path(path)
            model_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save model
            joblib.dump(self.model, str(model_path))
            
            # Save scaler
            scaler_path = model_path.parent / f"{model_path.stem}_scaler.joblib"
            joblib.dump(self.scaler, str(scaler_path))
            
            # Save metadata
            metadata_path = model_path.with_suffix(".json")
            with open(metadata_path, "w") as f:
                json.dump(self.model_metadata, f, indent=2)
            
            logger.info(f"✅ Model saved to {path}")
            
        except Exception as e:
            logger.error(f"Failed to save model: {e}")
            raise

    def load(self, path: str):
        """Load model and scaler from disk."""
        try:
            model_path = Path(path)
            
            # Load model
            self.model = joblib.load(str(model_path))
            
            # Load scaler
            scaler_path = model_path.parent / f"{model_path.stem}_scaler.joblib"
            if scaler_path.exists():
                self.scaler = joblib.load(str(scaler_path))
            
            # Load metadata
            metadata_path = model_path.with_suffix(".json")
            if metadata_path.exists():
                with open(metadata_path, "r") as f:
                    self.model_metadata = json.load(f)
            
            logger.info(
                f"✅ Model loaded from {path} "
                f"(version {self.model_metadata.get('version', 'unknown')})"
            )
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise

    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance scores (absolute coefficients)."""
        if not self.model_metadata.get("feature_importance"):
            return {}
        
        importance = self.model_metadata["feature_importance"]
        sorted_importance = dict(
            sorted(importance.items(), key=lambda x: x[1], reverse=True)
        )
        
        return sorted_importance


# Global singleton instance
_engagement_prediction_model: Optional[EngagementPredictionModel] = None


def get_engagement_prediction_model(
    model_path: Optional[str] = None
) -> EngagementPredictionModel:
    """Get or create global engagement prediction model instance."""
    global _engagement_prediction_model
    if _engagement_prediction_model is None:
        _engagement_prediction_model = EngagementPredictionModel(model_path=model_path)
    return _engagement_prediction_model
