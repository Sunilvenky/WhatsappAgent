"""Sentiment Analysis Service using BERT pre-trained models.

Uses cardiffnlp/twitter-roberta-base-sentiment-latest for sentiment classification
and j-hartmann/emotion-english-distilroberta-base for emotion detection.
"""

import logging
from typing import Dict, Any, Optional
from functools import lru_cache

from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    pipeline,
)
import torch

logger = logging.getLogger(__name__)


class SentimentAnalyzer:
    """Analyzes sentiment and emotions in text messages using BERT models."""

    def __init__(self):
        """Initialize sentiment analyzer with pre-trained models."""
        self.device = 0 if torch.cuda.is_available() else -1
        self.sentiment_model = None
        self.emotion_model = None
        self._load_models()

    def _load_models(self):
        """Load pre-trained BERT models for sentiment and emotion detection."""
        try:
            logger.info("Loading sentiment analysis models...")

            # Load sentiment model (positive/negative/neutral)
            self.sentiment_model = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                device=self.device,
                top_k=None,  # Return all scores
            )

            # Load emotion model (joy, sadness, anger, fear, surprise, disgust, neutral)
            self.emotion_model = pipeline(
                "text-classification",
                model="j-hartmann/emotion-english-distilroberta-base",
                device=self.device,
                top_k=None,
            )

            logger.info("✅ Sentiment analysis models loaded successfully")

        except Exception as e:
            logger.error(f"❌ Failed to load sentiment models: {e}")
            raise

    def analyze(
        self,
        text: str,
        include_emotions: bool = True,
        return_all_scores: bool = False,
    ) -> Dict[str, Any]:
        """Analyze sentiment and emotions in text.

        Args:
            text: Input text to analyze
            include_emotions: Whether to include emotion detection
            return_all_scores: Whether to return scores for all classes

        Returns:
            Dictionary with sentiment and emotion analysis:
            {
                "sentiment": "positive",  # positive, negative, neutral
                "sentiment_score": 0.95,
                "confidence": 0.95,
                "emotion": "joy",  # Primary emotion
                "emotion_score": 0.85,
                "all_sentiments": [...],  # If return_all_scores=True
                "all_emotions": [...]     # If return_all_scores=True
            }
        """
        if not text or not text.strip():
            return {
                "sentiment": "neutral",
                "sentiment_score": 0.0,
                "confidence": 0.0,
                "error": "Empty text provided",
            }

        try:
            # Truncate very long texts (BERT max is 512 tokens)
            text = text[:500]

            result = {}

            # Analyze sentiment
            sentiment_results = self.sentiment_model(text)[0]
            top_sentiment = max(sentiment_results, key=lambda x: x["score"])

            result["sentiment"] = self._normalize_sentiment_label(
                top_sentiment["label"]
            )
            result["sentiment_score"] = round(top_sentiment["score"], 4)
            result["confidence"] = round(top_sentiment["score"], 4)

            if return_all_scores:
                result["all_sentiments"] = [
                    {
                        "label": self._normalize_sentiment_label(s["label"]),
                        "score": round(s["score"], 4),
                    }
                    for s in sentiment_results
                ]

            # Analyze emotions
            if include_emotions and self.emotion_model:
                emotion_results = self.emotion_model(text)[0]
                top_emotion = max(emotion_results, key=lambda x: x["score"])

                result["emotion"] = top_emotion["label"]
                result["emotion_score"] = round(top_emotion["score"], 4)

                if return_all_scores:
                    result["all_emotions"] = [
                        {
                            "label": e["label"],
                            "score": round(e["score"], 4),
                        }
                        for e in emotion_results
                    ]

            # Add risk assessment for customer support
            result["risk_level"] = self._assess_risk(result)

            return result

        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            return {
                "sentiment": "neutral",
                "sentiment_score": 0.0,
                "confidence": 0.0,
                "error": str(e),
            }

    def analyze_batch(
        self,
        texts: list[str],
        include_emotions: bool = True,
    ) -> list[Dict[str, Any]]:
        """Analyze sentiment for multiple texts efficiently.

        Args:
            texts: List of texts to analyze
            include_emotions: Whether to include emotion detection

        Returns:
            List of analysis results
        """
        if not texts:
            return []

        try:
            # Filter empty texts
            valid_texts = [(i, t[:500]) for i, t in enumerate(texts) if t and t.strip()]
            if not valid_texts:
                return [{"sentiment": "neutral", "sentiment_score": 0.0}] * len(texts)

            indices, truncated_texts = zip(*valid_texts)

            # Batch sentiment analysis
            sentiment_results = self.sentiment_model(truncated_texts)

            # Batch emotion analysis
            emotion_results = []
            if include_emotions and self.emotion_model:
                emotion_results = self.emotion_model(truncated_texts)

            # Combine results
            results = [None] * len(texts)
            for i, idx in enumerate(indices):
                top_sentiment = max(sentiment_results[i], key=lambda x: x["score"])

                result = {
                    "sentiment": self._normalize_sentiment_label(top_sentiment["label"]),
                    "sentiment_score": round(top_sentiment["score"], 4),
                    "confidence": round(top_sentiment["score"], 4),
                }

                if emotion_results:
                    top_emotion = max(emotion_results[i], key=lambda x: x["score"])
                    result["emotion"] = top_emotion["label"]
                    result["emotion_score"] = round(top_emotion["score"], 4)

                result["risk_level"] = self._assess_risk(result)
                results[idx] = result

            # Fill in None values for empty texts
            for i, result in enumerate(results):
                if result is None:
                    results[i] = {
                        "sentiment": "neutral",
                        "sentiment_score": 0.0,
                        "confidence": 0.0,
                    }

            return results

        except Exception as e:
            logger.error(f"Batch sentiment analysis failed: {e}")
            return [{"sentiment": "neutral", "error": str(e)}] * len(texts)

    def get_conversation_sentiment(
        self, messages: list[str]
    ) -> Dict[str, Any]:
        """Analyze sentiment trend across a conversation.

        Args:
            messages: List of messages in chronological order

        Returns:
            Conversation-level sentiment analysis with trend
        """
        if not messages:
            return {"overall_sentiment": "neutral", "trend": "stable"}

        results = self.analyze_batch(messages, include_emotions=False)

        # Calculate overall metrics
        sentiments = [r.get("sentiment", "neutral") for r in results]
        scores = [r.get("sentiment_score", 0.0) for r in results]

        sentiment_counts = {
            "positive": sentiments.count("positive"),
            "negative": sentiments.count("negative"),
            "neutral": sentiments.count("neutral"),
        }

        overall = max(sentiment_counts, key=sentiment_counts.get)

        # Calculate trend
        if len(scores) >= 2:
            first_half_avg = sum(scores[: len(scores) // 2]) / (len(scores) // 2)
            second_half_avg = sum(scores[len(scores) // 2 :]) / (
                len(scores) - len(scores) // 2
            )
            diff = second_half_avg - first_half_avg

            if diff > 0.1:
                trend = "improving"
            elif diff < -0.1:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "stable"

        return {
            "overall_sentiment": overall,
            "sentiment_distribution": sentiment_counts,
            "average_score": round(sum(scores) / len(scores), 4),
            "trend": trend,
            "message_count": len(messages),
            "messages_analyzed": results,
        }

    def _normalize_sentiment_label(self, label: str) -> str:
        """Normalize different sentiment label formats."""
        label = label.lower()
        if "pos" in label:
            return "positive"
        elif "neg" in label:
            return "negative"
        else:
            return "neutral"

    def _assess_risk(self, analysis: Dict[str, Any]) -> str:
        """Assess customer support risk based on sentiment/emotion.

        Returns:
            Risk level: "high", "medium", "low"
        """
        sentiment = analysis.get("sentiment", "neutral")
        emotion = analysis.get("emotion", "")
        sentiment_score = analysis.get("sentiment_score", 0.0)

        # High risk: Strong negative sentiment or anger/disgust
        if sentiment == "negative" and sentiment_score > 0.7:
            return "high"
        if emotion in ["anger", "disgust"] and analysis.get("emotion_score", 0) > 0.6:
            return "high"

        # Medium risk: Moderate negative or fear/sadness
        if sentiment == "negative":
            return "medium"
        if emotion in ["fear", "sadness"] and analysis.get("emotion_score", 0) > 0.5:
            return "medium"

        # Low risk: Positive or neutral
        return "low"


# Global singleton instance
_sentiment_analyzer: Optional[SentimentAnalyzer] = None


@lru_cache(maxsize=1)
def get_sentiment_analyzer() -> SentimentAnalyzer:
    """Get or create global sentiment analyzer instance."""
    global _sentiment_analyzer
    if _sentiment_analyzer is None:
        _sentiment_analyzer = SentimentAnalyzer()
    return _sentiment_analyzer
