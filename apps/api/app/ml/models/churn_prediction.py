"""Churn Prediction Model using Random Forest.

Predicts likelihood of customer churn based on engagement decline,
sentiment changes, and support interactions.
"""

import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime
import json

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    classification_report,
)
import joblib

logger = logging.getLogger(__name__)


class ChurnPredictionModel:
    """Random Forest model for predicting customer churn."""

    def __init__(self, model_path: Optional[str] = None):
        """Initialize churn prediction model.

        Args:
            model_path: Path to saved model file (loads if exists)
        """
        self.model = None
        self.feature_names = [
            # Recency metrics
            "days_since_last_purchase",
            "days_since_last_message",
            "days_since_last_campaign_open",
            
            # Frequency decline
            "messages_this_month",
            "messages_last_month",
            "purchase_frequency_decline",
            "engagement_frequency_decline",
            
            # Monetary value
            "total_lifetime_value",
            "avg_order_value",
            "months_since_first_purchase",
            
            # Support interactions
            "support_tickets_count",
            "unresolved_tickets_count",
            "avg_ticket_resolution_days",
            "complaint_count",
            
            # Sentiment trends
            "current_sentiment_score",
            "sentiment_score_30d_ago",
            "sentiment_decline_rate",
            "negative_sentiment_ratio",
            
            # Engagement decline
            "response_rate_current",
            "response_rate_30d_ago",
            "campaign_engagement_decline",
            "conversation_length_decline",
            
            # Product interaction
            "product_views_decline",
            "cart_abandonment_rate",
            "refund_count",
            "discount_usage_increase",
            
            # Behavioral signals
            "unsubscribe_attempts",
            "opted_out_campaigns",
            "ignored_messages_ratio",
            "contact_preference_changes",
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
        self, customer_data: Dict[str, Any]
    ) -> pd.DataFrame:
        """Prepare features from customer data.

        Args:
            customer_data: Dictionary with customer information and history

        Returns:
            DataFrame with prepared features
        """
        features = {}
        
        # Recency metrics
        features["days_since_last_purchase"] = customer_data.get(
            "days_since_last_purchase", 999
        )
        features["days_since_last_message"] = customer_data.get(
            "days_since_last_message", 999
        )
        features["days_since_last_campaign_open"] = customer_data.get(
            "days_since_last_campaign_open", 999
        )
        
        # Frequency decline
        features["messages_this_month"] = customer_data.get("messages_this_month", 0)
        features["messages_last_month"] = customer_data.get("messages_last_month", 0)
        features["purchase_frequency_decline"] = customer_data.get(
            "purchase_frequency_decline", 0.0
        )
        features["engagement_frequency_decline"] = customer_data.get(
            "engagement_frequency_decline", 0.0
        )
        
        # Monetary value
        features["total_lifetime_value"] = customer_data.get(
            "total_lifetime_value", 0.0
        )
        features["avg_order_value"] = customer_data.get("avg_order_value", 0.0)
        features["months_since_first_purchase"] = customer_data.get(
            "months_since_first_purchase", 0
        )
        
        # Support interactions
        features["support_tickets_count"] = customer_data.get(
            "support_tickets_count", 0
        )
        features["unresolved_tickets_count"] = customer_data.get(
            "unresolved_tickets_count", 0
        )
        features["avg_ticket_resolution_days"] = customer_data.get(
            "avg_ticket_resolution_days", 0.0
        )
        features["complaint_count"] = customer_data.get("complaint_count", 0)
        
        # Sentiment trends
        features["current_sentiment_score"] = customer_data.get(
            "current_sentiment_score", 0.5
        )
        features["sentiment_score_30d_ago"] = customer_data.get(
            "sentiment_score_30d_ago", 0.5
        )
        features["sentiment_decline_rate"] = customer_data.get(
            "sentiment_decline_rate", 0.0
        )
        features["negative_sentiment_ratio"] = customer_data.get(
            "negative_sentiment_ratio", 0.0
        )
        
        # Engagement decline
        features["response_rate_current"] = customer_data.get(
            "response_rate_current", 0.0
        )
        features["response_rate_30d_ago"] = customer_data.get(
            "response_rate_30d_ago", 0.0
        )
        features["campaign_engagement_decline"] = customer_data.get(
            "campaign_engagement_decline", 0.0
        )
        features["conversation_length_decline"] = customer_data.get(
            "conversation_length_decline", 0.0
        )
        
        # Product interaction
        features["product_views_decline"] = customer_data.get(
            "product_views_decline", 0.0
        )
        features["cart_abandonment_rate"] = customer_data.get(
            "cart_abandonment_rate", 0.0
        )
        features["refund_count"] = customer_data.get("refund_count", 0)
        features["discount_usage_increase"] = customer_data.get(
            "discount_usage_increase", 0.0
        )
        
        # Behavioral signals
        features["unsubscribe_attempts"] = customer_data.get(
            "unsubscribe_attempts", 0
        )
        features["opted_out_campaigns"] = customer_data.get("opted_out_campaigns", 0)
        features["ignored_messages_ratio"] = customer_data.get(
            "ignored_messages_ratio", 0.0
        )
        features["contact_preference_changes"] = customer_data.get(
            "contact_preference_changes", 0
        )
        
        return pd.DataFrame([features])

    def train(
        self,
        training_data: List[Dict[str, Any]],
        validation_split: float = 0.2,
        hyperparameters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Train churn prediction model.

        Args:
            training_data: List of customer dictionaries with features and churn labels
            validation_split: Fraction of data to use for validation
            hyperparameters: Random Forest hyperparameters

        Returns:
            Training metrics and validation results
        """
        try:
            logger.info(f"Training churn model on {len(training_data)} samples")
            
            # Prepare features and labels
            X_list = []
            y_list = []
            
            for customer in training_data:
                features_df = self.prepare_features(customer)
                X_list.append(features_df)
                y_list.append(
                    1 if customer.get("churned", False) else 0
                )  # Binary: 1=churned, 0=active
            
            X = pd.concat(X_list, ignore_index=True)
            y = np.array(y_list)
            
            # Check class balance
            churn_rate = y.mean()
            logger.info(f"Dataset churn rate: {churn_rate:.2%}")
            
            # Split data
            X_train, X_val, y_train, y_val = train_test_split(
                X, y, test_size=validation_split, random_state=42, stratify=y
            )
            
            # Default hyperparameters
            if hyperparameters is None:
                hyperparameters = {
                    "n_estimators": 100,
                    "max_depth": 10,
                    "min_samples_split": 10,
                    "min_samples_leaf": 4,
                    "max_features": "sqrt",
                    "class_weight": "balanced",  # Handle imbalanced classes
                    "random_state": 42,
                    "n_jobs": -1,
                }
            
            # Train model
            self.model = RandomForestClassifier(**hyperparameters)
            self.model.fit(X_train, y_train)
            
            # Evaluate
            y_train_pred = self.model.predict(X_train)
            y_val_pred = self.model.predict(X_val)
            y_val_proba = self.model.predict_proba(X_val)[:, 1]
            
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
                "churn_rate": float(churn_rate),
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

    def predict(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predict churn probability for a customer.

        Args:
            customer_data: Customer information and interaction history

        Returns:
            Prediction result with churn probability, risk level, and factors
        """
        if self.model is None:
            return {
                "churn_probability": 0.5,
                "error": "Model not trained or loaded",
            }
        
        try:
            # Prepare features
            X = self.prepare_features(customer_data)
            
            # Predict
            churn_proba = float(self.model.predict_proba(X)[0][1])
            churn_prediction = bool(self.model.predict(X)[0])
            
            # Risk level
            if churn_proba >= 0.7:
                risk_level = "critical"
            elif churn_proba >= 0.5:
                risk_level = "high"
            elif churn_proba >= 0.3:
                risk_level = "medium"
            else:
                risk_level = "low"
            
            # Top risk factors
            feature_values = X.iloc[0].to_dict()
            feature_importance = self.model_metadata.get("feature_importance", {})
            
            risk_factors = []
            for feature, value in feature_values.items():
                importance = feature_importance.get(feature, 0)
                
                # Identify high-risk values
                is_risk = False
                if "decline" in feature and value > 0.2:
                    is_risk = True
                elif "days_since" in feature and value > 30:
                    is_risk = True
                elif feature in ["support_tickets_count", "complaint_count"] and value > 2:
                    is_risk = True
                elif feature == "negative_sentiment_ratio" and value > 0.3:
                    is_risk = True
                
                if is_risk:
                    risk_factors.append({
                        "factor": feature,
                        "value": value,
                        "importance": importance,
                        "risk_score": value * importance,
                    })
            
            risk_factors.sort(key=lambda x: x["risk_score"], reverse=True)
            top_risk_factors = risk_factors[:5]
            
            # Retention recommendations
            recommendations = self._generate_recommendations(
                churn_proba, top_risk_factors
            )
            
            return {
                "churn_probability": round(churn_proba, 4),
                "will_churn": churn_prediction,
                "risk_level": risk_level,
                "top_risk_factors": [
                    {
                        "factor": f["factor"].replace("_", " ").title(),
                        "value": f["value"],
                        "importance": round(f["importance"], 3),
                    }
                    for f in top_risk_factors
                ],
                "retention_recommendations": recommendations,
                "model_version": self.model_metadata.get("version"),
            }
            
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            return {
                "churn_probability": 0.5,
                "error": str(e),
            }

    def predict_batch(
        self, customers_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Predict churn for multiple customers.

        Args:
            customers_data: List of customer dictionaries

        Returns:
            List of prediction results
        """
        results = []
        for customer in customers_data:
            result = self.predict(customer)
            results.append(result)
        
        return results

    def _generate_recommendations(
        self, churn_proba: float, risk_factors: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate personalized retention recommendations.

        Args:
            churn_proba: Churn probability
            risk_factors: Top risk factors

        Returns:
            List of actionable recommendations
        """
        recommendations = []
        
        if churn_proba >= 0.7:
            recommendations.append("🚨 URGENT: Reach out with personalized offer within 24 hours")
        
        for factor in risk_factors[:3]:
            factor_name = factor["factor"]
            
            if "days_since" in factor_name:
                recommendations.append(
                    f"Re-engage customer with targeted campaign about recent products"
                )
            elif "sentiment" in factor_name:
                recommendations.append(
                    "Schedule customer satisfaction call to address concerns"
                )
            elif "support" in factor_name or "complaint" in factor_name:
                recommendations.append(
                    "Prioritize resolution of open support tickets"
                )
            elif "decline" in factor_name:
                recommendations.append(
                    "Send win-back campaign with exclusive discount"
                )
            elif "engagement" in factor_name:
                recommendations.append(
                    "Create personalized content based on past interests"
                )
        
        if not recommendations:
            recommendations.append("Monitor customer engagement and maintain regular touchpoints")
        
        return recommendations[:4]  # Top 4 recommendations

    def save(self, path: str):
        """Save model to disk."""
        try:
            model_path = Path(path)
            model_path.parent.mkdir(parents=True, exist_ok=True)
            
            joblib.dump(self.model, str(model_path))
            
            metadata_path = model_path.with_suffix(".json")
            with open(metadata_path, "w") as f:
                json.dump(self.model_metadata, f, indent=2)
            
            logger.info(f"✅ Model saved to {path}")
            
        except Exception as e:
            logger.error(f"Failed to save model: {e}")
            raise

    def load(self, path: str):
        """Load model from disk."""
        try:
            model_path = Path(path)
            
            self.model = joblib.load(str(model_path))
            
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
        """Get feature importance scores."""
        if not self.model_metadata.get("feature_importance"):
            return {}
        
        importance = self.model_metadata["feature_importance"]
        sorted_importance = dict(
            sorted(importance.items(), key=lambda x: x[1], reverse=True)
        )
        
        return sorted_importance


# Global singleton instance
_churn_prediction_model: Optional[ChurnPredictionModel] = None


def get_churn_prediction_model(
    model_path: Optional[str] = None
) -> ChurnPredictionModel:
    """Get or create global churn prediction model instance."""
    global _churn_prediction_model
    if _churn_prediction_model is None:
        _churn_prediction_model = ChurnPredictionModel(model_path=model_path)
    return _churn_prediction_model
