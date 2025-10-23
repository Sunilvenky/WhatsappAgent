# 🤖 Machine Learning Features - Smart WhatsApp Agent

**Complete ML capabilities for intelligent WhatsApp marketing automation.**

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Phase 1: Pre-trained Models](#phase-1-pre-trained-models)
   - [Sentiment Analysis](#sentiment-analysis)
   - [Voice Transcription](#voice-transcription)
   - [Translation](#translation)
3. [Phase 2: Custom ML Models](#phase-2-custom-ml-models)
   - [Lead Scoring](#lead-scoring)
   - [Churn Prediction](#churn-prediction)
   - [Engagement Prediction](#engagement-prediction)
4. [Training Pipeline](#training-pipeline)
5. [API Reference](#api-reference)
6. [Integration Examples](#integration-examples)
7. [Performance & Optimization](#performance--optimization)

---

## 🎯 Overview

The Smart WhatsApp Agent includes **6 production-ready ML features** across 2 phases:

### **Phase 1: Pre-trained Models** (Ready to Use)
- ✅ **Sentiment Analysis** - BERT-based emotion detection
- ✅ **Voice Transcription** - Whisper 99-language support
- ✅ **Translation** - Google Translate API (100+ languages)

### **Phase 2: Custom Models** (Train on Your Data)
- 🎯 **Lead Scoring** - XGBoost quality prediction (0-100)
- 🚨 **Churn Prediction** - Random Forest retention insights
- ⏰ **Engagement Prediction** - Logistic Regression optimal timing

### **Key Benefits**
- 🚀 **Immediate Value** - Phase 1 works out-of-the-box
- 📊 **Data-Driven** - Phase 2 learns from your actual data
- 🔄 **Automated** - Training pipeline handles everything
- 🎯 **Actionable** - Every prediction includes recommendations

---

## 🔬 Phase 1: Pre-trained Models

### Sentiment Analysis

**Purpose**: Analyze customer emotions in real-time to prioritize responses and detect issues.

#### **Models Used**
- **Sentiment**: `cardiffnlp/twitter-roberta-base-sentiment-latest`
  - Classes: Positive, Negative, Neutral
  - Accuracy: ~94% on social media text
  
- **Emotion**: `j-hartmann/emotion-english-distilroberta-base`
  - Classes: Joy, Sadness, Anger, Fear, Surprise, Disgust, Neutral
  - Accuracy: ~88% on emotional text

#### **Features**
- ✅ Single text analysis
- ✅ Batch processing (efficient for 100+ messages)
- ✅ Conversation trend analysis
- ✅ Customer support risk assessment (high/medium/low)

#### **API Endpoints**

**1. Analyze Single Text**
```http
POST /api/v1/ml/sentiment/analyze
Content-Type: application/json

{
  "text": "Thank you so much! This product is amazing!",
  "include_emotions": true,
  "return_all_scores": false
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "sentiment": "positive",
    "sentiment_score": 0.9876,
    "confidence": 0.9876,
    "emotion": "joy",
    "emotion_score": 0.8521,
    "risk_level": "low"
  }
}
```

**2. Batch Analysis**
```http
POST /api/v1/ml/sentiment/batch
Content-Type: application/json

{
  "texts": [
    "I love this!",
    "This is terrible service",
    "When will my order arrive?"
  ],
  "include_emotions": true
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "results": [
      {
        "sentiment": "positive",
        "sentiment_score": 0.95,
        "emotion": "joy",
        "risk_level": "low"
      },
      {
        "sentiment": "negative",
        "sentiment_score": 0.92,
        "emotion": "anger",
        "risk_level": "high"
      },
      {
        "sentiment": "neutral",
        "sentiment_score": 0.78,
        "emotion": "neutral",
        "risk_level": "medium"
      }
    ],
    "count": 3
  }
}
```

**3. Conversation Trend**
```http
POST /api/v1/ml/sentiment/conversation
Content-Type: application/json

{
  "messages": [
    "Hi, I'm interested in your product",
    "Can you tell me more about pricing?",
    "Thanks, I'll think about it",
    "Actually, I'm not satisfied with the response"
  ]
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "overall_sentiment": "neutral",
    "sentiment_distribution": {
      "positive": 1,
      "negative": 1,
      "neutral": 2
    },
    "average_score": 0.62,
    "trend": "declining",
    "message_count": 4
  }
}
```

#### **Integration Example**

```python
from app.ml import get_sentiment_analyzer

async def analyze_incoming_message(message: str):
    """Analyze sentiment of incoming WhatsApp message."""
    analyzer = get_sentiment_analyzer()
    
    result = analyzer.analyze(
        text=message,
        include_emotions=True
    )
    
    # Prioritize high-risk messages
    if result["risk_level"] == "high":
        await notify_support_team(message, result)
    
    return result
```

---

### Voice Transcription

**Purpose**: Convert voice messages to text with automatic language detection.

#### **Model Used**
- **Whisper** by OpenAI (`base` model by default)
- **Sizes**: tiny, base, small, medium, large
- **Languages**: 99 languages supported
- **Accuracy**: 95%+ for English, 85%+ for most languages

#### **Features**
- ✅ Upload audio files (mp3, wav, m4a, ogg)
- ✅ Automatic language detection
- ✅ Translate to English
- ✅ Word-level timestamps
- ✅ Confidence scoring

#### **API Endpoints**

**1. Transcribe Audio**
```http
POST /api/v1/ml/voice/transcribe-upload
Content-Type: multipart/form-data

file: <audio_file>
language: "en" (optional)
```

**Response:**
```json
{
  "success": true,
  "data": {
    "text": "Hello, I would like to order your product",
    "language": "en",
    "confidence": 0.94,
    "duration": 5.2,
    "segments": [
      {"start": 0.0, "end": 1.5, "text": "Hello,"},
      {"start": 1.5, "end": 3.8, "text": "I would like to"},
      {"start": 3.8, "end": 5.2, "text": "order your product"}
    ]
  }
}
```

**2. Translate Audio to English**
```http
POST /api/v1/ml/voice/translate-upload
Content-Type: multipart/form-data

file: <audio_file>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "text": "I want to buy your product",
    "language": "es",
    "duration": 4.8
  }
}
```

**3. Detect Language**
```http
POST /api/v1/ml/voice/detect-language-upload
Content-Type: multipart/form-data

file: <audio_file>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "language": "es"
  }
}
```

**4. Get Supported Languages**
```http
GET /api/v1/ml/voice/supported-languages
```

**Response:**
```json
{
  "success": true,
  "data": {
    "languages": ["en", "es", "hi", "pt", "zh", ...],
    "count": 99
  }
}
```

#### **Integration Example**

```python
from app.ml import get_voice_transcriber

async def handle_voice_message(audio_bytes: bytes, filename: str):
    """Transcribe voice message from WhatsApp."""
    transcriber = get_voice_transcriber()
    
    result = transcriber.transcribe_bytes(
        audio_bytes=audio_bytes,
        filename=filename
    )
    
    # Save transcription
    transcribed_text = result["text"]
    detected_language = result["language"]
    
    return {
        "text": transcribed_text,
        "language": detected_language,
        "duration": result["duration"]
    }
```

---

### Translation

**Purpose**: Enable multilingual campaigns and auto-translate customer messages.

#### **Service Used**
- **Google Translate API** via `googletrans`
- **Language Detection**: `langdetect` library
- **Languages**: 100+ supported
- **Accuracy**: 95%+ for major languages

#### **Features**
- ✅ Auto language detection
- ✅ Batch translation (efficient for campaigns)
- ✅ Multilingual campaigns (1 message → N languages)
- ✅ Popular languages shortlist for WhatsApp

#### **API Endpoints**

**1. Translate Text**
```http
POST /api/v1/ml/translation/translate
Content-Type: application/json

{
  "text": "Hello, how are you?",
  "target_language": "es",
  "source_language": null
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "translated_text": "Hola, ¿cómo estás?",
    "source_language": "en",
    "target_language": "es",
    "confidence": 0.98,
    "original_text": "Hello, how are you?"
  }
}
```

**2. Batch Translation**
```http
POST /api/v1/ml/translation/batch
Content-Type: application/json

{
  "texts": ["Hello", "Thank you", "Goodbye"],
  "target_language": "hi",
  "source_language": "en"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "results": [
      {
        "translated_text": "नमस्ते",
        "source_language": "en",
        "target_language": "hi"
      },
      {
        "translated_text": "धन्यवाद",
        "source_language": "en",
        "target_language": "hi"
      },
      {
        "translated_text": "अलविदा",
        "source_language": "en",
        "target_language": "hi"
      }
    ],
    "count": 3
  }
}
```

**3. Detect Language**
```http
POST /api/v1/ml/translation/detect-language
Content-Type: application/json

{
  "text": "Bonjour, comment allez-vous?"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "language": "fr",
    "language_name": "french",
    "confidence": 0.99,
    "all_probabilities": [
      {"language": "fr", "probability": 0.99},
      {"language": "en", "probability": 0.01}
    ]
  }
}
```

**4. Multilingual Translation**
```http
POST /api/v1/ml/translation/multilingual
Content-Type: application/json

{
  "text": "New product launch tomorrow!",
  "target_languages": ["es", "hi", "pt", "ar"]
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "translations": {
      "es": "¡Lanzamiento de nuevo producto mañana!",
      "hi": "कल नया उत्पाद लॉन्च!",
      "pt": "Lançamento de novo produto amanhã!",
      "ar": "إطلاق منتج جديد غدًا!"
    },
    "count": 4
  }
}
```

**5. Get Popular Languages**
```http
GET /api/v1/ml/translation/popular-languages
```

**Response:**
```json
{
  "success": true,
  "data": {
    "languages": [
      {"code": "en", "name": "english"},
      {"code": "es", "name": "spanish"},
      {"code": "hi", "name": "hindi"},
      {"code": "pt", "name": "portuguese"},
      ...
    ],
    "count": 20
  }
}
```

#### **Integration Example**

```python
from app.ml import get_translator

async def send_multilingual_campaign(message: str, contacts: List[Contact]):
    """Send campaign in each contact's preferred language."""
    translator = get_translator()
    
    # Group contacts by language
    by_language = {}
    for contact in contacts:
        lang = contact.preferred_language or "en"
        if lang not in by_language:
            by_language[lang] = []
        by_language[lang].append(contact)
    
    # Translate message for each language
    results = {}
    for lang, contact_group in by_language.items():
        translation = translator.translate(
            text=message,
            target_language=lang
        )
        
        # Send to contacts in this language
        for contact in contact_group:
            await send_message(contact, translation["translated_text"])
        
        results[lang] = len(contact_group)
    
    return results
```

---

## 🎯 Phase 2: Custom ML Models

### Lead Scoring

**Purpose**: Predict lead quality (0-100) to prioritize sales efforts.

#### **Model Details**
- **Algorithm**: XGBoost Regressor
- **Features**: 24 behavioral + engagement metrics
- **Training**: Requires minimum 100 labeled leads
- **Output**: Score (0-100) + Quality Tier + Contributing Factors

#### **Feature Categories**

**1. Response Behavior** (4 features)
- `avg_response_time_minutes`
- `response_rate`
- `messages_received`
- `messages_sent`

**2. Engagement Metrics** (5 features)
- `conversation_count`
- `avg_conversation_length`
- `days_since_first_contact`
- `days_since_last_contact`
- `contact_frequency_per_week`

**3. Sentiment & Emotion** (4 features)
- `avg_sentiment_score`
- `positive_sentiment_ratio`
- `negative_sentiment_ratio`
- `avg_emotion_score`

**4. Campaign Interaction** (4 features)
- `campaign_opens`
- `campaign_clicks`
- `campaign_responses`
- `campaign_engagement_rate`

**5. Time Patterns** (3 features)
- `preferred_contact_hour`
- `weekend_activity_ratio`
- `business_hours_ratio`

**6. Lead Indicators** (4 features)
- `question_count`
- `price_inquiry_count`
- `meeting_request_count`
- `positive_keywords_count`

#### **Quality Tiers**
- **Hot** (80-100): Ready to buy, prioritize immediately
- **Warm** (60-79): Interested, needs nurturing
- **Cold** (40-59): Low engagement, re-engagement needed
- **Unqualified** (0-39): Poor fit, consider disqualifying

#### **API Endpoints**

**1. Predict Lead Score**
```http
POST /api/v1/ml/models/lead-scoring/predict
Content-Type: application/json

{
  "lead_data": {
    "avg_response_time_minutes": 15.5,
    "response_rate": 0.85,
    "messages_received": 12,
    "messages_sent": 15,
    "conversation_count": 3,
    "avg_sentiment_score": 0.75,
    "campaign_opens": 5,
    "question_count": 4,
    "price_inquiry_count": 2
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "lead_score": 78.5,
    "quality_tier": "warm",
    "top_contributing_factors": [
      {
        "factor": "Response Rate",
        "value": 0.85,
        "importance": 0.142
      },
      {
        "factor": "Avg Response Time Minutes",
        "value": 15.5,
        "importance": 0.128
      },
      {
        "factor": "Price Inquiry Count",
        "value": 2,
        "importance": 0.115
      }
    ],
    "model_version": "1.0.0"
  }
}
```

**2. Batch Scoring**
```http
POST /api/v1/ml/models/lead-scoring/batch
Content-Type: application/json

{
  "leads_data": [
    {...lead_1...},
    {...lead_2...},
    {...lead_3...}
  ]
}
```

**3. Feature Importance**
```http
GET /api/v1/ml/models/lead-scoring/feature-importance
```

**Response:**
```json
{
  "success": true,
  "data": {
    "feature_importance": {
      "response_rate": 0.142,
      "avg_response_time_minutes": 0.128,
      "price_inquiry_count": 0.115,
      "campaign_engagement_rate": 0.098,
      ...
    },
    "model_version": "1.0.0"
  }
}
```

---

### Churn Prediction

**Purpose**: Identify customers at risk of churning with actionable retention strategies.

#### **Model Details**
- **Algorithm**: Random Forest Classifier
- **Features**: 32 recency/frequency/monetary metrics
- **Training**: Requires minimum 100 customers with 90-day history
- **Output**: Churn Probability + Risk Level + Retention Recommendations

#### **Feature Categories**

**1. Recency Metrics** (3 features)
- `days_since_last_purchase`
- `days_since_last_message`
- `days_since_last_campaign_open`

**2. Frequency Decline** (4 features)
- `messages_this_month`
- `messages_last_month`
- `purchase_frequency_decline`
- `engagement_frequency_decline`

**3. Monetary Value** (3 features)
- `total_lifetime_value`
- `avg_order_value`
- `months_since_first_purchase`

**4. Support Interactions** (4 features)
- `support_tickets_count`
- `unresolved_tickets_count`
- `avg_ticket_resolution_days`
- `complaint_count`

**5. Sentiment Trends** (4 features)
- `current_sentiment_score`
- `sentiment_score_30d_ago`
- `sentiment_decline_rate`
- `negative_sentiment_ratio`

**6. Engagement Decline** (4 features)
- `response_rate_current`
- `response_rate_30d_ago`
- `campaign_engagement_decline`
- `conversation_length_decline`

**7. Product Interaction** (4 features)
- `product_views_decline`
- `cart_abandonment_rate`
- `refund_count`
- `discount_usage_increase`

**8. Behavioral Signals** (4 features)
- `unsubscribe_attempts`
- `opted_out_campaigns`
- `ignored_messages_ratio`
- `contact_preference_changes`

#### **Risk Levels**
- **Critical** (70-100%): Immediate action required within 24 hours
- **High** (50-69%): High priority, reach out within 3 days
- **Medium** (30-49%): Monitor closely, proactive engagement
- **Low** (0-29%): Stable, maintain regular touchpoints

#### **API Endpoints**

**1. Predict Churn**
```http
POST /api/v1/ml/models/churn-prediction/predict
Content-Type: application/json

{
  "customer_data": {
    "days_since_last_purchase": 45,
    "purchase_frequency_decline": 0.6,
    "sentiment_decline_rate": 0.3,
    "support_tickets_count": 3,
    "unresolved_tickets_count": 1,
    "response_rate_current": 0.2,
    "response_rate_30d_ago": 0.7
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "churn_probability": 0.7823,
    "will_churn": true,
    "risk_level": "critical",
    "top_risk_factors": [
      {
        "factor": "Purchase Frequency Decline",
        "value": 0.6,
        "importance": 0.156
      },
      {
        "factor": "Days Since Last Purchase",
        "value": 45,
        "importance": 0.142
      },
      {
        "factor": "Sentiment Decline Rate",
        "value": 0.3,
        "importance": 0.138
      }
    ],
    "retention_recommendations": [
      "🚨 URGENT: Reach out with personalized offer within 24 hours",
      "Send win-back campaign with exclusive discount",
      "Prioritize resolution of open support tickets",
      "Schedule customer satisfaction call to address concerns"
    ],
    "model_version": "1.0.0"
  }
}
```

**2. Batch Prediction**
```http
POST /api/v1/ml/models/churn-prediction/batch
Content-Type: application/json

{
  "customers_data": [
    {...customer_1...},
    {...customer_2...}
  ]
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "results": [...],
    "count": 2,
    "high_risk_count": 1
  }
}
```

---

### Engagement Prediction

**Purpose**: Predict optimal send times and engagement likelihood for maximum campaign performance.

#### **Model Details**
- **Algorithm**: Logistic Regression (with StandardScaler)
- **Features**: 27 time-based + behavioral metrics
- **Training**: Requires minimum 100 message interactions
- **Output**: Engagement Probability + Optimal Send Time + Recommendations

#### **Feature Categories**

**1. Historical Engagement** (4 features)
- `past_open_rate`
- `past_click_rate`
- `past_response_rate`
- `avg_response_time_hours`

**2. Time Patterns** (4 features)
- `hour_of_day` (0-23)
- `day_of_week` (0-6, Monday=0)
- `is_weekend`
- `is_business_hours`

**3. Recency** (3 features)
- `days_since_last_engagement`
- `days_since_last_campaign`
- `hours_since_last_message`

**4. Contact Preferences** (3 features)
- `preferred_contact_hour`
- `preferred_day_of_week`
- `timezone_offset`

**5. Campaign Characteristics** (5 features)
- `message_length`
- `has_media`
- `has_link`
- `has_call_to_action`
- `personalization_level` (0-1)

**6. Historical Performance by Time** (3 features)
- `engagement_rate_this_hour`
- `engagement_rate_this_day`
- `engagement_rate_this_weekday`

**7. Contact Activity** (3 features)
- `messages_received_last_7d`
- `campaigns_received_last_30d`
- `conversation_count_last_30d`

**8. Sentiment & Quality** (2 features)
- `avg_sentiment_score_last_30d`
- `message_quality_score`

#### **Engagement Levels**
- **Very High** (70-100%): Excellent timing, high likelihood
- **High** (50-69%): Good timing, send confidently
- **Medium** (30-49%): Fair timing, consider optimization
- **Low** (0-29%): Poor timing, reschedule recommended

#### **API Endpoints**

**1. Predict Engagement**
```http
POST /api/v1/ml/models/engagement-prediction/predict
Content-Type: application/json

{
  "engagement_data": {
    "past_open_rate": 0.65,
    "hour_of_day": 14,
    "day_of_week": 2,
    "is_business_hours": true,
    "preferred_contact_hour": 14,
    "has_call_to_action": true,
    "personalization_level": 0.8,
    "messages_received_last_7d": 3
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "engagement_probability": 0.7234,
    "will_engage": true,
    "engagement_level": "very_high",
    "recommendations": [
      "✨ Add personalization (name, past purchases) to increase engagement",
      "🎯 Include clear call-to-action to improve response rate"
    ],
    "model_version": "1.0.0"
  }
}
```

**2. Find Optimal Send Time**
```http
POST /api/v1/ml/models/engagement-prediction/optimal-time
Content-Type: application/json

{
  "contact_data": {
    "past_open_rate": 0.65,
    "preferred_contact_hour": 14,
    "timezone_offset": -5,
    "is_business_hours": true,
    "personalization_level": 0.8
  },
  "hours_to_test": [9, 10, 11, 12, 13, 14, 15, 16, 17]
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "optimal_hour": 14,
    "optimal_time": "14:00",
    "max_engagement_probability": 0.7856,
    "all_hours": [
      {"hour": 9, "engagement_probability": 0.5234},
      {"hour": 10, "engagement_probability": 0.6123},
      {"hour": 11, "engagement_probability": 0.6789},
      {"hour": 12, "engagement_probability": 0.7234},
      {"hour": 13, "engagement_probability": 0.7456},
      {"hour": 14, "engagement_probability": 0.7856},
      {"hour": 15, "engagement_probability": 0.7234},
      {"hour": 16, "engagement_probability": 0.6543},
      {"hour": 17, "engagement_probability": 0.5876}
    ]
  }
}
```

---

## 🏗️ Training Pipeline

### Overview

The ML Training Pipeline automates the entire model training workflow:
1. ✅ **Data Preparation** - Extracts features from database
2. ✅ **Training** - Trains models with cross-validation
3. ✅ **Validation** - Evaluates performance metrics
4. ✅ **Versioning** - Saves models with metadata
5. ✅ **Deployment** - Makes models available via API

### Requirements

**Minimum Training Data:**
- **Lead Scoring**: 100 leads with assigned scores
- **Churn Prediction**: 100 customers with 90-day history
- **Engagement Prediction**: 100 message interactions

**Data Quality:**
- Clean, labeled data (no null values in target variables)
- Balanced classes (for classification models)
- Representative samples across all feature ranges

### API Endpoints

**1. Train Single Model**
```http
POST /api/v1/ml/training/train-model
Content-Type: application/json

{
  "model_name": "lead_scoring",
  "hyperparameters": {
    "n_estimators": 100,
    "max_depth": 6,
    "learning_rate": 0.1
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "success": true,
    "metrics": {
      "train_rmse": 8.23,
      "train_mae": 6.45,
      "train_r2": 0.87,
      "val_rmse": 10.15,
      "val_mae": 8.12,
      "val_r2": 0.81
    },
    "feature_importance": {...},
    "metadata": {
      "version": "1.0.0",
      "created_at": "2025-10-23T12:00:00Z",
      "trained_samples": 250
    },
    "model_path": "models/lead_scoring.joblib"
  }
}
```

**2. Train All Models**
```http
POST /api/v1/ml/training/train-all
```

**Response:**
```json
{
  "success": true,
  "data": {
    "total_models": 3,
    "successful": 3,
    "failed": 0,
    "timestamp": "2025-10-23T12:00:00Z",
    "models": {
      "lead_scoring": {
        "success": true,
        "metrics": {...},
        "model_path": "models/lead_scoring.joblib"
      },
      "churn_prediction": {
        "success": true,
        "metrics": {...},
        "model_path": "models/churn_prediction.joblib"
      },
      "engagement_prediction": {
        "success": true,
        "metrics": {...},
        "model_path": "models/engagement_prediction.joblib"
      }
    }
  }
}
```

**3. Get Training Status**
```http
GET /api/v1/ml/training/status
```

**Response:**
```json
{
  "success": true,
  "data": {
    "lead_scoring": {
      "trained": true,
      "metadata": {
        "version": "1.0.0",
        "trained_samples": 250,
        "performance_metrics": {...}
      }
    },
    "churn_prediction": {
      "trained": true,
      "metadata": {...}
    },
    "engagement_prediction": {
      "trained": false,
      "metadata": {}
    }
  }
}
```

### Python Integration

```python
from app.ml.training_pipeline import get_training_pipeline
from app.core.database import get_db

async def train_all_models(user_id: int):
    """Train all ML models for a user."""
    db = next(get_db())
    pipeline = get_training_pipeline()
    
    result = pipeline.train_all_models(db, user_id)
    
    print(f"✅ Trained {result['successful']}/{result['total_models']} models")
    
    for model_name, model_result in result["models"].items():
        if model_result["success"]:
            metrics = model_result["metrics"]
            print(f"  {model_name}: R²={metrics.get('val_r2', 'N/A'):.3f}")
        else:
            print(f"  {model_name}: FAILED - {model_result['error']}")
    
    return result
```

---

## 📚 API Reference

### Base URL
```
http://localhost:8000/api/v1/ml
```

### Authentication
All endpoints require Bearer token authentication:
```http
Authorization: Bearer <access_token>
```

### Endpoint Summary

| Category | Endpoint | Method | Description |
|----------|----------|--------|-------------|
| **Health** | `/health` | GET | Check ML service status |
| **Sentiment** | `/sentiment/analyze` | POST | Analyze single text |
| **Sentiment** | `/sentiment/batch` | POST | Analyze multiple texts |
| **Sentiment** | `/sentiment/conversation` | POST | Analyze conversation trend |
| **Voice** | `/voice/transcribe-upload` | POST | Transcribe audio file |
| **Voice** | `/voice/translate-upload` | POST | Translate audio to English |
| **Voice** | `/voice/detect-language-upload` | POST | Detect audio language |
| **Voice** | `/voice/supported-languages` | GET | List supported languages |
| **Translation** | `/translation/translate` | POST | Translate text |
| **Translation** | `/translation/batch` | POST | Translate multiple texts |
| **Translation** | `/translation/detect-language` | POST | Detect text language |
| **Translation** | `/translation/multilingual` | POST | Translate to multiple languages |
| **Translation** | `/translation/supported-languages` | GET | List all languages |
| **Translation** | `/translation/popular-languages` | GET | List popular languages |
| **Lead Scoring** | `/models/lead-scoring/predict` | POST | Score single lead |
| **Lead Scoring** | `/models/lead-scoring/batch` | POST | Score multiple leads |
| **Lead Scoring** | `/models/lead-scoring/feature-importance` | GET | Get feature importance |
| **Churn** | `/models/churn-prediction/predict` | POST | Predict churn |
| **Churn** | `/models/churn-prediction/batch` | POST | Predict churn batch |
| **Churn** | `/models/churn-prediction/feature-importance` | GET | Get feature importance |
| **Engagement** | `/models/engagement-prediction/predict` | POST | Predict engagement |
| **Engagement** | `/models/engagement-prediction/optimal-time` | POST | Find optimal send time |
| **Engagement** | `/models/engagement-prediction/feature-importance` | GET | Get feature importance |
| **Training** | `/training/train-model` | POST | Train single model |
| **Training** | `/training/train-all` | POST | Train all models |
| **Training** | `/training/status` | GET | Get training status |

---

## 🔧 Integration Examples

### Example 1: Auto-Prioritize Support Tickets

```python
from app.ml import get_sentiment_analyzer

async def prioritize_support_ticket(message: str, contact_id: int):
    """Automatically prioritize support tickets by sentiment."""
    analyzer = get_sentiment_analyzer()
    
    result = analyzer.analyze(message, include_emotions=True)
    
    priority = {
        "high": result["risk_level"] == "high",
        "sentiment": result["sentiment"],
        "emotion": result["emotion"],
        "confidence": result["confidence"]
    }
    
    # Auto-escalate high-risk messages
    if priority["high"]:
        await escalate_to_supervisor(contact_id, message, result)
    
    return priority
```

### Example 2: Multilingual Campaign

```python
from app.ml import get_translator

async def send_multilingual_campaign(
    campaign_id: int,
    message_en: str,
    contacts: List[Contact]
):
    """Send campaign in each contact's language."""
    translator = get_translator()
    
    # Group by language
    by_language = {}
    for contact in contacts:
        lang = contact.preferred_language or "en"
        by_language.setdefault(lang, []).append(contact)
    
    # Translate and send
    results = {}
    for lang, group in by_language.items():
        if lang != "en":
            translation = translator.translate(
                text=message_en,
                target_language=lang
            )
            message = translation["translated_text"]
        else:
            message = message_en
        
        # Send to all contacts in this language
        for contact in group:
            await send_message(contact.phone_number, message)
        
        results[lang] = len(group)
    
    return results
```

### Example 3: Smart Lead Routing

```python
from app.ml.models.lead_scoring import get_lead_scoring_model

async def route_lead_to_sales_rep(lead_id: int):
    """Route leads based on predicted score."""
    model = get_lead_scoring_model()
    
    # Get lead data
    lead_data = await prepare_lead_data(lead_id)
    
    # Predict score
    result = model.predict(lead_data)
    score = result["lead_score"]
    tier = result["quality_tier"]
    
    # Route by quality
    if tier == "hot":
        await assign_to_senior_rep(lead_id, score)
    elif tier == "warm":
        await assign_to_mid_level_rep(lead_id, score)
    else:
        await assign_to_marketing_automation(lead_id, score)
    
    return {
        "lead_id": lead_id,
        "score": score,
        "tier": tier,
        "assigned": True
    }
```

### Example 4: Proactive Churn Prevention

```python
from app.ml.models.churn_prediction import get_churn_prediction_model

async def daily_churn_check():
    """Check all customers for churn risk daily."""
    model = get_churn_prediction_model()
    
    customers = await get_active_customers()
    
    high_risk = []
    for customer in customers:
        customer_data = await prepare_customer_data(customer.id)
        
        result = model.predict(customer_data)
        
        if result["risk_level"] in ["critical", "high"]:
            high_risk.append({
                "customer_id": customer.id,
                "churn_probability": result["churn_probability"],
                "risk_level": result["risk_level"],
                "recommendations": result["retention_recommendations"]
            })
    
    # Send alerts
    if high_risk:
        await send_retention_alerts(high_risk)
    
    return {
        "checked": len(customers),
        "high_risk": len(high_risk)
    }
```

### Example 5: Optimal Send Time Scheduler

```python
from app.ml.models.engagement_prediction import get_engagement_prediction_model

async def schedule_campaign_optimally(
    campaign_id: int,
    contacts: List[Contact]
):
    """Schedule campaign at optimal time for each contact."""
    model = get_engagement_prediction_model()
    
    schedule = {}
    
    for contact in contacts:
        contact_data = await prepare_contact_data(contact.id)
        
        # Find optimal hour
        result = model.predict_optimal_send_time(
            contact_data=contact_data,
            hours_to_test=[9, 10, 11, 12, 13, 14, 15, 16, 17, 18]
        )
        
        optimal_hour = result["optimal_hour"]
        
        # Add to schedule
        schedule.setdefault(optimal_hour, []).append(contact.id)
    
    # Create scheduled tasks
    for hour, contact_ids in schedule.items():
        await create_scheduled_send(
            campaign_id=campaign_id,
            contact_ids=contact_ids,
            send_hour=hour
        )
    
    return schedule
```

---

## ⚡ Performance & Optimization

### Phase 1 Models (Pre-trained)

**Sentiment Analysis**
- **Latency**: 50-100ms per text (CPU), 10-20ms (GPU)
- **Batch**: 500 texts in 2-3 seconds
- **Memory**: ~1.5GB (models loaded)
- **Optimization**: Use batch endpoints for >10 texts

**Voice Transcription**
- **Latency**: Real-time factor ~0.1-0.3x (10-30s audio → 3-9s transcription)
- **Model Sizes**:
  - tiny: Fast, 75MB, 90% accuracy
  - base: Balanced, 140MB, 95% accuracy ✅ **Recommended**
  - small: Better, 460MB, 96% accuracy
  - medium: Great, 1.5GB, 97% accuracy
  - large: Best, 2.9GB, 98% accuracy
- **Memory**: 1-3GB depending on model size
- **Optimization**: Use `base` for production, `large` for critical accuracy

**Translation**
- **Latency**: 100-300ms per text (API call)
- **Batch**: 100 texts in 5-10 seconds
- **Rate Limits**: Google Translate API limits apply
- **Optimization**: Cache common translations, batch when possible

### Phase 2 Models (Custom)

**Lead Scoring (XGBoost)**
- **Training**: 1-5 minutes for 1000 samples
- **Prediction**: <10ms per lead
- **Batch**: 10,000 leads in 5 seconds
- **Memory**: ~50MB per model
- **Optimization**: Pre-load model at startup

**Churn Prediction (Random Forest)**
- **Training**: 2-10 minutes for 1000 samples
- **Prediction**: <20ms per customer
- **Batch**: 5,000 customers in 5 seconds
- **Memory**: ~100MB per model
- **Optimization**: Use batch endpoints for reports

**Engagement Prediction (Logistic Regression)**
- **Training**: 30 seconds - 2 minutes for 1000 samples
- **Prediction**: <5ms per engagement
- **Optimal Time**: 24 hours tested in <200ms
- **Memory**: ~10MB per model
- **Optimization**: Fastest model, scale freely

### Production Deployment Tips

1. **GPU Acceleration** (Phase 1)
   - Install CUDA for PyTorch/Transformers
   - 5-10x faster sentiment + voice processing
   - Required for high-volume operations

2. **Model Caching**
   - Pre-load all models at startup
   - Use singleton pattern (already implemented)
   - Warm up with test predictions

3. **Async Processing**
   - Use Celery for batch operations
   - Process voice transcription in background
   - Queue model training jobs

4. **Monitoring**
   - Track prediction latency
   - Monitor model drift (accuracy decline)
   - Log feature importance changes

5. **Retraining Schedule**
   - **Lead Scoring**: Weekly (fresh engagement data)
   - **Churn Prediction**: Monthly (long-term trends)
   - **Engagement Prediction**: Daily (time patterns shift)

---

## 🎓 Best Practices

### Data Quality
- ✅ Clean, labeled training data
- ✅ Balanced classes (churn/no-churn ~50/50 ideal)
- ✅ Representative samples across all features
- ✅ Remove outliers and null values

### Feature Engineering
- ✅ Normalize time-based features
- ✅ Create interaction terms (e.g., sentiment × recency)
- ✅ Use domain knowledge to create custom features
- ✅ Track feature importance over time

### Model Maintenance
- ✅ Retrain regularly (see schedule above)
- ✅ A/B test new model versions
- ✅ Monitor prediction distribution shift
- ✅ Version control all model artifacts

### API Usage
- ✅ Use batch endpoints for bulk operations
- ✅ Cache predictions when appropriate
- ✅ Handle errors gracefully (model not trained, insufficient data)
- ✅ Log predictions for model monitoring

---

## 📞 Support

For questions or issues:
1. Check `/api/v1/ml/health` endpoint
2. Review logs in `apps/api/app/ml/`
3. Verify training data quality
4. Ensure minimum sample requirements met

**Common Issues:**
- **"Model not trained"**: Run `/training/train-model` first
- **"Insufficient training data"**: Need minimum 100 samples
- **GPU not detected**: Install CUDA toolkit
- **Slow predictions**: Use batch endpoints or GPU acceleration

---

**Built with ❤️ for Smart WhatsApp Agent**
