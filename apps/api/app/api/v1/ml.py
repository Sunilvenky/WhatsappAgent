"""Machine Learning API endpoints.

Phase 1: Sentiment analysis, voice transcription, translation
Phase 2: Custom ML models (lead scoring, churn, engagement)
"""

import logging
from typing import List, Optional
from pathlib import Path
import tempfile

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from apps.api.app.core.database import get_db
from apps.api.app.auth.dependencies import get_current_user
from apps.api.app.models.user import User
from apps.api.app.ml.sentiment_analyzer import get_sentiment_analyzer
from apps.api.app.ml.voice_transcriber import get_voice_transcriber
from apps.api.app.ml.translator import get_translator
from apps.api.app.ml.models.lead_scoring import get_lead_scoring_model
from apps.api.app.ml.models.churn_prediction import get_churn_prediction_model
from apps.api.app.ml.models.engagement_prediction import get_engagement_prediction_model
from apps.api.app.ml.training_pipeline import get_training_pipeline

router = APIRouter(prefix="/ml", tags=["Machine Learning"])
logger = logging.getLogger(__name__)


# ===== PHASE 1: PRE-TRAINED MODELS =====


# --- Sentiment Analysis Schemas ---


class SentimentAnalysisRequest(BaseModel):
    """Request to analyze sentiment of text."""

    text: str = Field(..., description="Text to analyze")
    include_emotions: bool = Field(
        True, description="Include emotion detection"
    )
    return_all_scores: bool = Field(
        False, description="Return scores for all classes"
    )


class SentimentBatchRequest(BaseModel):
    """Request to analyze sentiment of multiple texts."""

    texts: List[str] = Field(..., description="List of texts to analyze")
    include_emotions: bool = Field(True, description="Include emotion detection")


class ConversationSentimentRequest(BaseModel):
    """Request to analyze sentiment trend across a conversation."""

    messages: List[str] = Field(
        ..., description="Messages in chronological order"
    )


# --- Voice Transcription Schemas ---


class TranscriptionRequest(BaseModel):
    """Request to transcribe audio from URL."""

    audio_url: str = Field(..., description="URL to audio file")
    language: Optional[str] = Field(
        None, description="ISO 639-1 language code (auto-detect if None)"
    )


class LanguageDetectionRequest(BaseModel):
    """Request to detect language of audio."""

    audio_url: str = Field(..., description="URL to audio file")


# --- Translation Schemas ---


class TranslationRequest(BaseModel):
    """Request to translate text."""

    text: str = Field(..., description="Text to translate")
    target_language: str = Field(
        "en", description="Target language code (ISO 639-1)"
    )
    source_language: Optional[str] = Field(
        None, description="Source language (auto-detect if None)"
    )


class TranslationBatchRequest(BaseModel):
    """Request to translate multiple texts."""

    texts: List[str] = Field(..., description="Texts to translate")
    target_language: str = Field(
        "en", description="Target language code"
    )
    source_language: Optional[str] = Field(
        None, description="Source language (auto-detect if None)"
    )


class LanguageDetectionTextRequest(BaseModel):
    """Request to detect language of text."""

    text: str = Field(..., description="Text to analyze")


class MultilingualTranslationRequest(BaseModel):
    """Request to translate text to multiple languages."""

    text: str = Field(..., description="Text to translate")
    target_languages: List[str] = Field(
        ..., description="List of target language codes"
    )


# ===== SENTIMENT ANALYSIS ENDPOINTS =====


@router.post("/sentiment/analyze")
async def analyze_sentiment(
    request: SentimentAnalysisRequest,
    current_user: User = Depends(get_current_user),
):
    """Analyze sentiment and emotions in text.

    Returns sentiment (positive/negative/neutral), emotion,
    confidence scores, and risk level for customer support.
    """
    try:
        analyzer = get_sentiment_analyzer()
        result = analyzer.analyze(
            text=request.text,
            include_emotions=request.include_emotions,
            return_all_scores=request.return_all_scores,
        )

        return {
            "success": True,
            "data": result,
        }

    except Exception as e:
        logger.error(f"Sentiment analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sentiment/batch")
async def analyze_sentiment_batch(
    request: SentimentBatchRequest,
    current_user: User = Depends(get_current_user),
):
    """Analyze sentiment for multiple texts efficiently.

    Useful for analyzing all messages in a conversation or campaign responses.
    """
    try:
        analyzer = get_sentiment_analyzer()
        results = analyzer.analyze_batch(
            texts=request.texts,
            include_emotions=request.include_emotions,
        )

        return {
            "success": True,
            "data": {
                "results": results,
                "count": len(results),
            },
        }

    except Exception as e:
        logger.error(f"Batch sentiment analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sentiment/conversation")
async def analyze_conversation_sentiment(
    request: ConversationSentimentRequest,
    current_user: User = Depends(get_current_user),
):
    """Analyze sentiment trend across a conversation.

    Returns overall sentiment, distribution, and trend (improving/declining/stable).
    """
    try:
        analyzer = get_sentiment_analyzer()
        result = analyzer.get_conversation_sentiment(request.messages)

        return {
            "success": True,
            "data": result,
        }

    except Exception as e:
        logger.error(f"Conversation sentiment analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== VOICE TRANSCRIPTION ENDPOINTS =====


@router.post("/voice/transcribe-upload")
async def transcribe_upload(
    file: UploadFile = File(..., description="Audio file (mp3, wav, m4a, ogg)"),
    language: Optional[str] = None,
    current_user: User = Depends(get_current_user),
):
    """Transcribe uploaded audio file to text.

    Supports common audio formats: mp3, wav, m4a, ogg, etc.
    """
    try:
        # Read file bytes
        audio_bytes = await file.read()

        # Transcribe
        transcriber = get_voice_transcriber()
        result = transcriber.transcribe_bytes(
            audio_bytes=audio_bytes,
            filename=file.filename,
            language=language,
        )

        return {
            "success": True,
            "data": result,
        }

    except Exception as e:
        logger.error(f"Voice transcription failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/voice/translate-upload")
async def translate_voice_upload(
    file: UploadFile = File(..., description="Audio file to translate to English"),
    current_user: User = Depends(get_current_user),
):
    """Transcribe and translate audio to English.

    Automatically detects source language and translates to English.
    """
    try:
        # Save to temp file
        audio_bytes = await file.read()
        suffix = Path(file.filename).suffix or ".ogg"

        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as temp_file:
            temp_file.write(audio_bytes)
            temp_path = temp_file.name

        # Translate
        transcriber = get_voice_transcriber()
        result = transcriber.translate_to_english(temp_path)

        # Clean up
        try:
            Path(temp_path).unlink()
        except Exception:
            pass

        return {
            "success": True,
            "data": result,
        }

    except Exception as e:
        logger.error(f"Voice translation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/voice/detect-language-upload")
async def detect_voice_language_upload(
    file: UploadFile = File(..., description="Audio file for language detection"),
    current_user: User = Depends(get_current_user),
):
    """Detect language of uploaded audio file."""
    try:
        # Save to temp file
        audio_bytes = await file.read()
        suffix = Path(file.filename).suffix or ".ogg"

        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as temp_file:
            temp_file.write(audio_bytes)
            temp_path = temp_file.name

        # Detect language
        transcriber = get_voice_transcriber()
        language = transcriber.detect_language(temp_path)

        # Clean up
        try:
            Path(temp_path).unlink()
        except Exception:
            pass

        return {
            "success": True,
            "data": {
                "language": language,
            },
        }

    except Exception as e:
        logger.error(f"Language detection failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/voice/supported-languages")
async def get_supported_voice_languages(
    current_user: User = Depends(get_current_user),
):
    """Get list of languages supported by voice transcription."""
    transcriber = get_voice_transcriber()
    languages = transcriber.get_supported_languages()

    return {
        "success": True,
        "data": {
            "languages": languages,
            "count": len(languages),
        },
    }


# ===== TRANSLATION ENDPOINTS =====


@router.post("/translation/translate")
async def translate_text(
    request: TranslationRequest,
    current_user: User = Depends(get_current_user),
):
    """Translate text to target language.

    Automatically detects source language if not provided.
    """
    try:
        translator = get_translator()
        result = translator.translate(
            text=request.text,
            target_language=request.target_language,
            source_language=request.source_language,
        )

        return {
            "success": True,
            "data": result,
        }

    except Exception as e:
        logger.error(f"Translation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/translation/batch")
async def translate_batch(
    request: TranslationBatchRequest,
    current_user: User = Depends(get_current_user),
):
    """Translate multiple texts to target language."""
    try:
        translator = get_translator()
        results = translator.translate_batch(
            texts=request.texts,
            target_language=request.target_language,
            source_language=request.source_language,
        )

        return {
            "success": True,
            "data": {
                "results": results,
                "count": len(results),
            },
        }

    except Exception as e:
        logger.error(f"Batch translation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/translation/detect-language")
async def detect_text_language(
    request: LanguageDetectionTextRequest,
    current_user: User = Depends(get_current_user),
):
    """Detect language of text."""
    try:
        translator = get_translator()
        result = translator.detect_language(request.text)

        return {
            "success": True,
            "data": result,
        }

    except Exception as e:
        logger.error(f"Language detection failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/translation/multilingual")
async def translate_multilingual(
    request: MultilingualTranslationRequest,
    current_user: User = Depends(get_current_user),
):
    """Translate text to multiple languages.

    Useful for creating multilingual campaigns.
    """
    try:
        translator = get_translator()
        translations = translator.translate_with_fallback(
            text=request.text,
            target_languages=request.target_languages,
        )

        return {
            "success": True,
            "data": {
                "translations": translations,
                "count": len(translations),
            },
        }

    except Exception as e:
        logger.error(f"Multilingual translation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/translation/supported-languages")
async def get_supported_languages(
    current_user: User = Depends(get_current_user),
):
    """Get all supported languages for translation."""
    translator = get_translator()
    languages = translator.get_supported_languages()

    return {
        "success": True,
        "data": {
            "languages": languages,
            "count": len(languages),
        },
    }


@router.get("/translation/popular-languages")
async def get_popular_languages(
    current_user: User = Depends(get_current_user),
):
    """Get popular languages for WhatsApp marketing."""
    translator = get_translator()
    languages = translator.get_popular_languages()

    return {
        "success": True,
        "data": {
            "languages": languages,
            "count": len(languages),
        },
    }


# ===== UTILITY ENDPOINTS =====


@router.get("/health")
async def ml_health_check():
    """Check ML service health and loaded models."""
    try:
        # Check sentiment analyzer
        analyzer = get_sentiment_analyzer()
        sentiment_loaded = analyzer.sentiment_model is not None

        # Check voice transcriber
        transcriber = get_voice_transcriber()
        voice_loaded = transcriber.model is not None

        # Check translator
        translator = get_translator()
        translation_loaded = translator.translator is not None

        # Check Phase 2 models
        lead_model = get_lead_scoring_model()
        churn_model = get_churn_prediction_model()
        engagement_model = get_engagement_prediction_model()

        return {
            "success": True,
            "data": {
                "phase_1": {
                    "sentiment_analysis": {
                        "loaded": sentiment_loaded,
                        "device": getattr(analyzer, "device", "unknown"),
                    },
                    "voice_transcription": {
                        "loaded": voice_loaded,
                        "model_size": getattr(transcriber, "model_size", "unknown"),
                        "device": getattr(transcriber, "device", "unknown"),
                    },
                    "translation": {
                        "loaded": translation_loaded,
                    },
                },
                "phase_2": {
                    "lead_scoring": {
                        "loaded": lead_model.model is not None,
                        "version": lead_model.model_metadata.get("version", "untrained"),
                        "samples": lead_model.model_metadata.get("trained_samples", 0),
                    },
                    "churn_prediction": {
                        "loaded": churn_model.model is not None,
                        "version": churn_model.model_metadata.get("version", "untrained"),
                        "samples": churn_model.model_metadata.get("trained_samples", 0),
                    },
                    "engagement_prediction": {
                        "loaded": engagement_model.model is not None,
                        "version": engagement_model.model_metadata.get("version", "untrained"),
                        "samples": engagement_model.model_metadata.get("trained_samples", 0),
                    },
                },
            },
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


# ===== PHASE 2: CUSTOM ML MODELS =====


# --- Lead Scoring Schemas ---


class LeadScoringRequest(BaseModel):
    """Request to score a lead."""

    lead_data: dict = Field(..., description="Lead information and interaction history")


class LeadScoringBatchRequest(BaseModel):
    """Request to score multiple leads."""

    leads_data: List[dict] = Field(..., description="List of lead dictionaries")


# --- Churn Prediction Schemas ---


class ChurnPredictionRequest(BaseModel):
    """Request to predict customer churn."""

    customer_data: dict = Field(..., description="Customer information and history")


class ChurnPredictionBatchRequest(BaseModel):
    """Request to predict churn for multiple customers."""

    customers_data: List[dict] = Field(..., description="List of customer dictionaries")


# --- Engagement Prediction Schemas ---


class EngagementPredictionRequest(BaseModel):
    """Request to predict message engagement."""

    engagement_data: dict = Field(..., description="Contact and campaign information")


class OptimalTimeRequest(BaseModel):
    """Request to find optimal send time."""

    contact_data: dict = Field(..., description="Contact information and preferences")
    hours_to_test: Optional[List[int]] = Field(
        None, description="Hours to test (0-23). If None, tests all 24 hours."
    )


# --- Training Schemas ---


class TrainModelRequest(BaseModel):
    """Request to train a specific model."""

    model_name: str = Field(
        ..., description="Model name: lead_scoring, churn_prediction, engagement_prediction"
    )
    hyperparameters: Optional[dict] = Field(
        None, description="Optional hyperparameters"
    )


# ===== LEAD SCORING ENDPOINTS =====


@router.post("/models/lead-scoring/predict")
async def predict_lead_score(
    request: LeadScoringRequest,
    current_user: User = Depends(get_current_user),
):
    """Predict lead quality score (0-100).

    Returns score, quality tier, and top contributing factors.
    """
    try:
        model = get_lead_scoring_model()
        result = model.predict(request.lead_data)

        return {
            "success": True,
            "data": result,
        }

    except Exception as e:
        logger.error(f"Lead scoring failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/models/lead-scoring/batch")
async def predict_lead_scores_batch(
    request: LeadScoringBatchRequest,
    current_user: User = Depends(get_current_user),
):
    """Predict lead scores for multiple leads."""
    try:
        model = get_lead_scoring_model()
        results = model.predict_batch(request.leads_data)

        return {
            "success": True,
            "data": {
                "results": results,
                "count": len(results),
            },
        }

    except Exception as e:
        logger.error(f"Batch lead scoring failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models/lead-scoring/feature-importance")
async def get_lead_scoring_feature_importance(
    current_user: User = Depends(get_current_user),
):
    """Get feature importance for lead scoring model."""
    try:
        model = get_lead_scoring_model()
        importance = model.get_feature_importance()

        return {
            "success": True,
            "data": {
                "feature_importance": importance,
                "model_version": model.model_metadata.get("version"),
            },
        }

    except Exception as e:
        logger.error(f"Failed to get feature importance: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== CHURN PREDICTION ENDPOINTS =====


@router.post("/models/churn-prediction/predict")
async def predict_churn(
    request: ChurnPredictionRequest,
    current_user: User = Depends(get_current_user),
):
    """Predict customer churn probability.

    Returns churn probability, risk level, risk factors, and retention recommendations.
    """
    try:
        model = get_churn_prediction_model()
        result = model.predict(request.customer_data)

        return {
            "success": True,
            "data": result,
        }

    except Exception as e:
        logger.error(f"Churn prediction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/models/churn-prediction/batch")
async def predict_churn_batch(
    request: ChurnPredictionBatchRequest,
    current_user: User = Depends(get_current_user),
):
    """Predict churn for multiple customers."""
    try:
        model = get_churn_prediction_model()
        results = model.predict_batch(request.customers_data)

        return {
            "success": True,
            "data": {
                "results": results,
                "count": len(results),
                "high_risk_count": sum(1 for r in results if r.get("risk_level") in ["critical", "high"]),
            },
        }

    except Exception as e:
        logger.error(f"Batch churn prediction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models/churn-prediction/feature-importance")
async def get_churn_feature_importance(
    current_user: User = Depends(get_current_user),
):
    """Get feature importance for churn prediction model."""
    try:
        model = get_churn_prediction_model()
        importance = model.get_feature_importance()

        return {
            "success": True,
            "data": {
                "feature_importance": importance,
                "model_version": model.model_metadata.get("version"),
            },
        }

    except Exception as e:
        logger.error(f"Failed to get feature importance: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== ENGAGEMENT PREDICTION ENDPOINTS =====


@router.post("/models/engagement-prediction/predict")
async def predict_engagement(
    request: EngagementPredictionRequest,
    current_user: User = Depends(get_current_user),
):
    """Predict message engagement probability.

    Returns engagement probability, level, and optimization recommendations.
    """
    try:
        model = get_engagement_prediction_model()
        result = model.predict(request.engagement_data)

        return {
            "success": True,
            "data": result,
        }

    except Exception as e:
        logger.error(f"Engagement prediction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/models/engagement-prediction/optimal-time")
async def predict_optimal_send_time(
    request: OptimalTimeRequest,
    current_user: User = Depends(get_current_user),
):
    """Find optimal time to send message for maximum engagement.

    Tests all hours (or specified hours) and returns best time.
    """
    try:
        model = get_engagement_prediction_model()
        result = model.predict_optimal_send_time(
            contact_data=request.contact_data,
            hours_to_test=request.hours_to_test,
        )

        return {
            "success": True,
            "data": result,
        }

    except Exception as e:
        logger.error(f"Optimal time prediction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models/engagement-prediction/feature-importance")
async def get_engagement_feature_importance(
    current_user: User = Depends(get_current_user),
):
    """Get feature importance for engagement prediction model."""
    try:
        model = get_engagement_prediction_model()
        importance = model.get_feature_importance()

        return {
            "success": True,
            "data": {
                "feature_importance": importance,
                "model_version": model.model_metadata.get("version"),
            },
        }

    except Exception as e:
        logger.error(f"Failed to get feature importance: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== TRAINING ENDPOINTS =====


@router.post("/training/train-model")
async def train_model(
    request: TrainModelRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Train a specific ML model on user's data.

    Requires sufficient training data (minimum 100 samples).
    """
    try:
        pipeline = get_training_pipeline()
        
        # Prepare training data based on model type
        if request.model_name == "lead_scoring":
            training_data = pipeline.prepare_lead_scoring_data(db, current_user.id)
        elif request.model_name == "churn_prediction":
            training_data = pipeline.prepare_churn_data(db, current_user.id)
        elif request.model_name == "engagement_prediction":
            training_data = pipeline.prepare_engagement_data(db, current_user.id)
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid model name: {request.model_name}",
            )
        
        # Train model
        result = pipeline.train_model(
            model_name=request.model_name,
            training_data=training_data,
            hyperparameters=request.hyperparameters,
        )
        
        return {
            "success": result.get("success", False),
            "data": result,
        }

    except Exception as e:
        logger.error(f"Model training failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/training/train-all")
async def train_all_models(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Train all ML models on user's data.

    Trains lead scoring, churn prediction, and engagement prediction models.
    """
    try:
        pipeline = get_training_pipeline()
        result = pipeline.train_all_models(db, current_user.id)

        return {
            "success": True,
            "data": result,
        }

    except Exception as e:
        logger.error(f"Training pipeline failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/training/status")
async def get_training_status(
    current_user: User = Depends(get_current_user),
):
    """Get training status for all models.

    Shows which models are trained and their performance metrics.
    """
    try:
        lead_model = get_lead_scoring_model()
        churn_model = get_churn_prediction_model()
        engagement_model = get_engagement_prediction_model()

        return {
            "success": True,
            "data": {
                "lead_scoring": {
                    "trained": lead_model.model is not None,
                    "metadata": lead_model.model_metadata,
                },
                "churn_prediction": {
                    "trained": churn_model.model is not None,
                    "metadata": churn_model.model_metadata,
                },
                "engagement_prediction": {
                    "trained": engagement_model.model is not None,
                    "metadata": engagement_model.model_metadata,
                },
            },
        }

    except Exception as e:
        logger.error(f"Failed to get training status: {e}")
        raise HTTPException(status_code=500, detail=str(e))
