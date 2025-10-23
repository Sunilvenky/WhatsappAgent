"""Lead Scoring Model using XGBoost.

Predicts lead quality score (0-100) based on engagement patterns,
sentiment analysis, and interaction history.
"""

import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime, timedelta
import json

import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import joblib

logger = logging.getLogger(__name__)


class LeadScoringModel:
    """XGBoost model for predicting lead quality scores."""

    def __init__(self, model_path: Optional[str] = None):
        """Initialize lead scoring model.

        Args:
            model_path: Path to saved model file (loads if exists)
        """
        self.model = None
        self.feature_names = [
            # Response behavior
            "avg_response_time_minutes",
            "response_rate",
            "messages_received",
            "messages_sent",
            
            # Engagement metrics
            "conversation_count",
            "avg_conversation_length",
            "days_since_first_contact",
            "days_since_last_contact",
            "contact_frequency_per_week",
            
            # Sentiment & emotion
            "avg_sentiment_score",
            "positive_sentiment_ratio",
            "negative_sentiment_ratio",
            "avg_emotion_score",
            
            # Campaign interaction
            "campaign_opens",
            "campaign_clicks",
            "campaign_responses",
            "campaign_engagement_rate",
            
            # Time patterns
            "preferred_contact_hour",
            "weekend_activity_ratio",
            "business_hours_ratio",
            
            # Lead indicators
            "question_count",
            "price_inquiry_count",
            "meeting_request_count",
            "positive_keywords_count",
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
        self, lead_data: Dict[str, Any]
    ) -> pd.DataFrame:
        """Prepare features from lead data.

        Args:
            lead_data: Dictionary with lead information and interaction history

        Returns:
            DataFrame with prepared features
        """
        features = {}
        
        # Response behavior
        features["avg_response_time_minutes"] = lead_data.get(
            "avg_response_time_minutes", 60.0
        )
        features["response_rate"] = lead_data.get("response_rate", 0.0)
        features["messages_received"] = lead_data.get("messages_received", 0)
        features["messages_sent"] = lead_data.get("messages_sent", 0)
        
        # Engagement metrics
        features["conversation_count"] = lead_data.get("conversation_count", 0)
        features["avg_conversation_length"] = lead_data.get(
            "avg_conversation_length", 1.0
        )
        features["days_since_first_contact"] = lead_data.get(
            "days_since_first_contact", 0
        )
        features["days_since_last_contact"] = lead_data.get(
            "days_since_last_contact", 0
        )
        features["contact_frequency_per_week"] = lead_data.get(
            "contact_frequency_per_week", 0.0
        )
        
        # Sentiment & emotion
        features["avg_sentiment_score"] = lead_data.get("avg_sentiment_score", 0.5)
        features["positive_sentiment_ratio"] = lead_data.get(
            "positive_sentiment_ratio", 0.0
        )
        features["negative_sentiment_ratio"] = lead_data.get(
            "negative_sentiment_ratio", 0.0
        )
        features["avg_emotion_score"] = lead_data.get("avg_emotion_score", 0.5)
        
        # Campaign interaction
        features["campaign_opens"] = lead_data.get("campaign_opens", 0)
        features["campaign_clicks"] = lead_data.get("campaign_clicks", 0)
        features["campaign_responses"] = lead_data.get("campaign_responses", 0)
        features["campaign_engagement_rate"] = lead_data.get(
            "campaign_engagement_rate", 0.0
        )
        
        # Time patterns
        features["preferred_contact_hour"] = lead_data.get(
            "preferred_contact_hour", 12
        )
        features["weekend_activity_ratio"] = lead_data.get(
            "weekend_activity_ratio", 0.0
        )
        features["business_hours_ratio"] = lead_data.get("business_hours_ratio", 0.5)
        
        # Lead indicators
        features["question_count"] = lead_data.get("question_count", 0)
        features["price_inquiry_count"] = lead_data.get("price_inquiry_count", 0)
        features["meeting_request_count"] = lead_data.get("meeting_request_count", 0)
        features["positive_keywords_count"] = lead_data.get(
            "positive_keywords_count", 0
        )
        
        return pd.DataFrame([features])

    def train(
        self,
        training_data: List[Dict[str, Any]],
        validation_split: float = 0.2,
        hyperparameters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Train lead scoring model.

        Args:
            training_data: List of lead dictionaries with features and scores
            validation_split: Fraction of data to use for validation
            hyperparameters: XGBoost hyperparameters (uses defaults if None)

        Returns:
            Training metrics and validation results
        """
        try:
            logger.info(f"Training lead scoring model on {len(training_data)} samples")
            
            # Prepare features and labels
            X_list = []
            y_list = []
            
            for lead in training_data:
                features_df = self.prepare_features(lead)
                X_list.append(features_df)
                y_list.append(lead.get("lead_score", 50))  # Target score 0-100
            
            X = pd.concat(X_list, ignore_index=True)
            y = np.array(y_list)
            
            # Split data
            X_train, X_val, y_train, y_val = train_test_split(
                X, y, test_size=validation_split, random_state=42
            )
            
            # Default hyperparameters
            if hyperparameters is None:
                hyperparameters = {
                    "n_estimators": 100,
                    "max_depth": 6,
                    "learning_rate": 0.1,
                    "subsample": 0.8,
                    "colsample_bytree": 0.8,
                    "min_child_weight": 1,
                    "gamma": 0,
                    "objective": "reg:squarederror",
                    "random_state": 42,
                }
            
            # Train model
            self.model = xgb.XGBRegressor(**hyperparameters)
            self.model.fit(
                X_train,
                y_train,
                eval_set=[(X_val, y_val)],
                verbose=False,
            )
            
            # Evaluate
            y_train_pred = self.model.predict(X_train)
            y_val_pred = self.model.predict(X_val)
            
            metrics = {
                "train_rmse": float(np.sqrt(mean_squared_error(y_train, y_train_pred))),
                "train_mae": float(mean_absolute_error(y_train, y_train_pred)),
                "train_r2": float(r2_score(y_train, y_train_pred)),
                "val_rmse": float(np.sqrt(mean_squared_error(y_val, y_val_pred))),
                "val_mae": float(mean_absolute_error(y_val, y_val_pred)),
                "val_r2": float(r2_score(y_val, y_val_pred)),
            }
            
            # Feature importance
            feature_importance = dict(
                zip(
                    self.feature_names,
                    self.model.feature_importances_.tolist(),
                )
            )
            
            # Update metadata
            self.model_metadata = {
                "version": "1.0.0",
                "created_at": datetime.utcnow().isoformat(),
                "trained_samples": len(training_data),
                "feature_importance": feature_importance,
                "performance_metrics": metrics,
                "hyperparameters": hyperparameters,
            }
            
            logger.info(
                f"✅ Training complete: "
                f"Val RMSE={metrics['val_rmse']:.2f}, "
                f"Val R²={metrics['val_r2']:.3f}"
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

    def predict(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predict lead score for a single lead.

        Args:
            lead_data: Lead information and interaction history

        Returns:
            Prediction result with score, confidence, and insights
        """
        if self.model is None:
            return {
                "lead_score": 50,
                "error": "Model not trained or loaded",
            }
        
        try:
            # Prepare features
            X = self.prepare_features(lead_data)
            
            # Predict
            score = float(self.model.predict(X)[0])
            
            # Clip to 0-100 range
            score = max(0, min(100, score))
            
            # Get feature contributions (SHAP-like explanation)
            feature_values = X.iloc[0].to_dict()
            feature_importance = self.model_metadata.get("feature_importance", {})
            
            # Top contributing features
            contributions = []
            for feature, value in feature_values.items():
                importance = feature_importance.get(feature, 0)
                contributions.append({
                    "feature": feature,
                    "value": value,
                    "importance": importance,
                    "contribution": value * importance,
                })
            
            contributions.sort(key=lambda x: abs(x["contribution"]), reverse=True)
            top_factors = contributions[:5]
            
            # Quality tier
            if score >= 80:
                quality = "hot"
            elif score >= 60:
                quality = "warm"
            elif score >= 40:
                quality = "cold"
            else:
                quality = "unqualified"
            
            return {
                "lead_score": round(score, 2),
                "quality_tier": quality,
                "top_contributing_factors": [
                    {
                        "factor": f["feature"].replace("_", " ").title(),
                        "value": f["value"],
                        "importance": round(f["importance"], 3),
                    }
                    for f in top_factors
                ],
                "model_version": self.model_metadata.get("version"),
            }
            
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            return {
                "lead_score": 50,
                "error": str(e),
            }

    def predict_batch(
        self, leads_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Predict lead scores for multiple leads.

        Args:
            leads_data: List of lead dictionaries

        Returns:
            List of prediction results
        """
        results = []
        for lead in leads_data:
            result = self.predict(lead)
            results.append(result)
        
        return results

    def save(self, path: str):
        """Save model to disk.

        Args:
            path: Path to save model (will create .joblib and .json files)
        """
        try:
            model_path = Path(path)
            model_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save model
            joblib.dump(self.model, str(model_path))
            
            # Save metadata
            metadata_path = model_path.with_suffix(".json")
            with open(metadata_path, "w") as f:
                json.dump(self.model_metadata, f, indent=2)
            
            logger.info(f"✅ Model saved to {path}")
            
        except Exception as e:
            logger.error(f"Failed to save model: {e}")
            raise

    def load(self, path: str):
        """Load model from disk.

        Args:
            path: Path to saved model file
        """
        try:
            model_path = Path(path)
            
            # Load model
            self.model = joblib.load(str(model_path))
            
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
        """Get feature importance scores.

        Returns:
            Dictionary mapping feature names to importance scores
        """
        if not self.model_metadata.get("feature_importance"):
            return {}
        
        # Sort by importance
        importance = self.model_metadata["feature_importance"]
        sorted_importance = dict(
            sorted(importance.items(), key=lambda x: x[1], reverse=True)
        )
        
        return sorted_importance


# Global singleton instance
_lead_scoring_model: Optional[LeadScoringModel] = None


def get_lead_scoring_model(model_path: Optional[str] = None) -> LeadScoringModel:
    """Get or create global lead scoring model instance."""
    global _lead_scoring_model
    if _lead_scoring_model is None:
        _lead_scoring_model = LeadScoringModel(model_path=model_path)
    return _lead_scoring_model
