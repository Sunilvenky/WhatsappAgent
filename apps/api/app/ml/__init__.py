"""Machine Learning module for Smart WhatsApp Agent.

Phase 1: Pre-trained models (sentiment, voice, translation)
Phase 2: Custom models (lead scoring, churn, engagement)
"""

from .sentiment_analyzer import SentimentAnalyzer, get_sentiment_analyzer

# Optional imports (may not have all dependencies)
try:
    from .voice_transcriber import VoiceTranscriber, get_voice_transcriber
except ImportError:
    VoiceTranscriber = None
    get_voice_transcriber = None

try:
    from .translator import Translator, get_translator
except ImportError:
    Translator = None
    get_translator = None

from .models.lead_scoring import LeadScoringModel, get_lead_scoring_model
from .models.churn_prediction import ChurnPredictionModel, get_churn_prediction_model
from .models.engagement_prediction import EngagementPredictionModel, get_engagement_prediction_model
from .training_pipeline import MLTrainingPipeline, get_training_pipeline

__all__ = [
    # Phase 1: Pre-trained models
    "SentimentAnalyzer",
    "get_sentiment_analyzer",
    "VoiceTranscriber",
    "get_voice_transcriber",
    "Translator",
    "get_translator",
    # Phase 2: Custom ML models
    "LeadScoringModel",
    "get_lead_scoring_model",
    "ChurnPredictionModel",
    "get_churn_prediction_model",
    "EngagementPredictionModel",
    "get_engagement_prediction_model",
    "MLTrainingPipeline",
    "get_training_pipeline",
]
