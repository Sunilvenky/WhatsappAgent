# 🎓 ML Model Training Guide

Complete guide to training and managing ML models in the WhatsApp Agent platform.

## 📋 Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Quick Start](#quick-start)
4. [Training Methods](#training-methods)
5. [Model Details](#model-details)
6. [Troubleshooting](#troubleshooting)
7. [Best Practices](#best-practices)
8. [Automated Training](#automated-training)

---

## 🎯 Overview

The platform includes 3 ML models that learn from your data:

| Model | Purpose | Input | Output |
|-------|---------|-------|--------|
| **Lead Scoring** | Predict lead quality | Lead data (24 features) | Score 0-100 + quality tier |
| **Churn Prediction** | Predict customer churn | Contact data (32 features) | Churn probability + risk level |
| **Engagement Prediction** | Predict message engagement | Message context (27 features) | Engagement probability + best send time |

### Why Train Models?

- **Personalization**: Models learn YOUR customers' patterns
- **Accuracy**: Improves over time with more data
- **Automation**: Automatically prioritize leads, prevent churn, optimize send times

---

## ✅ Prerequisites

### 1. Data Requirements

**Minimum Data Needed:**
- **100+ Contacts** (for churn & engagement models)
- **100+ Leads** (for lead scoring model)
- **50+ Conversations** with message history

**Data Quality:**
- ✅ Real customer interactions (not test data)
- ✅ Diverse outcomes (conversions + non-conversions)
- ✅ Recent data (within last 3-6 months)

### 2. System Requirements

```bash
# Python 3.10+
python --version

# Required packages
pip install xgboost scikit-learn joblib pandas numpy
```

### 3. Database Setup

```bash
# Ensure database is running
cd infra
docker-compose up postgres -d

# Run migrations
cd ../apps/api
alembic upgrade head
```

---

## 🚀 Quick Start

### Option 1: Generate Synthetic Data (Testing)

If you don't have enough real data yet:

```powershell
# Generate 200 contacts, 150 conversations, 120 leads
python -m apps.api.app.ml.generate_training_data
```

**Output:**
```
🎲 SYNTHETIC DATA GENERATOR
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📇 Generating 200 contacts...
   [████████████████████████████████████] 100% - Contact: John Smith
✅ Created 200 contacts

💬 Generating 150 conversations...
   [████████████████████████████████████] 100% - Conversation #150
✅ Created 150 conversations

✉️ Generating messages for conversations...
   [████████████████████████████████████] 100% - Conv #150: 5 msgs
✅ Created 612 messages

🎯 Generating 120 leads...
   [████████████████████████████████████] 100% - Lead #120 (score: 87)
✅ Created 120 leads (36 converted, 84 not converted)

✅ DATA GENERATION COMPLETE
```

### Option 2: Use Real Data

Skip data generation if you have:
- ✅ 100+ real contacts
- ✅ 100+ real leads
- ✅ Message history

---

## 🎓 Training Methods

### Method 1: CLI (Command Line)

**Train All Models:**
```powershell
python -m apps.api.app.ml.train_models
```

**Train Single Model:**
```powershell
# Lead scoring only
python -m apps.api.app.ml.train_models lead_scoring

# Churn prediction only
python -m apps.api.app.ml.train_models churn

# Engagement prediction only
python -m apps.api.app.ml.train_models engagement
```

**Output Example:**
```
🤖 ML MODEL TRAINING PIPELINE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Training all 3 ML models...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 TRAINING LEAD SCORING MODEL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Preparing training data...
   Training samples: 96
   Testing samples: 24
   Features: 24

🔧 Training XGBoost model with cross-validation...
   CV Folds: 5
   Hyperparameter tuning enabled

✅ Training complete!

📈 Model Performance:
   Mean Absolute Error: 8.45
   R² Score: 0.87
   Model saved: apps/api/app/ml/trained_models/lead_scoring_model.pkl

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ TRAINING CHURN PREDICTION MODEL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
...
```

### Method 2: Web UI (Non-Technical Users)

**Access Training Dashboard:**
```
http://localhost:8000/docs#/ML%20Training
```

**Available Endpoints:**

1. **GET `/api/v1/training/status`**
   - Check current training status
   - See progress in real-time

2. **POST `/api/v1/training/start`**
   - Start training (all models or specific)
   - Body:
     ```json
     {
       "model": "all",
       "test_size": 0.2,
       "cv_folds": 5
     }
     ```

3. **POST `/api/v1/training/stop`**
   - Cancel in-progress training

4. **GET `/api/v1/training/history`**
   - View past training runs
   - See metrics and duration

5. **GET `/api/v1/training/models`**
   - List trained models
   - See file sizes and dates

**Example Training Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/training/start" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "all",
    "test_size": 0.2,
    "cv_folds": 5
  }'
```

**Monitor Progress:**
```bash
curl -X GET "http://localhost:8000/api/v1/training/status" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
  "status": "training",
  "current_model": "churn",
  "progress": 66,
  "message": "Training churn prediction model...",
  "started_at": "2024-01-15T10:30:00Z",
  "metrics": {
    "lead_scoring": {
      "mae": 8.45,
      "r2": 0.87
    }
  }
}
```

### Method 3: Testing Models

After training, test predictions:

```powershell
python -m apps.api.app.ml.test_models
```

**Output:**
```
🧪 ML MODEL TESTING SUITE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 TESTING LEAD SCORING MODEL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📥 Loading model...
✅ Model loaded successfully

📊 Fetching sample leads...
✅ Found 5 leads to test

🔮 Making predictions...

   Lead #1 (ID: 1):
      Score: 87.3/100
      Quality: hot
      Recommendation: High priority - contact immediately

   Lead #2 (ID: 2):
      Score: 45.2/100
      Quality: cold
      Recommendation: Nurture with automated campaigns

📈 Results:
   Average Score: 65.8/100
   Predictions: 5/5
   ✅ Lead scoring model working correctly

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 TESTING SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Passed: 3/3 models
   ✅ PASS - lead_scoring
   ✅ PASS - churn_prediction
   ✅ PASS - engagement_prediction

🎉 All models working correctly!
```

---

## 🔍 Model Details

### 1. Lead Scoring Model

**Algorithm:** XGBoost Regressor

**Features (24):**
- Response behavior (reply rate, time to respond)
- Engagement metrics (message count, conversation length)
- Sentiment analysis (positive/negative sentiment)
- Campaign performance (click rate, conversion events)
- Contact quality (profile completeness, opt-in status)

**Output:**
```json
{
  "success": true,
  "score": 87.3,
  "quality_tier": "hot",
  "confidence": 0.92,
  "recommendation": "High priority - contact immediately",
  "factors": {
    "positive": ["High engagement", "Quick responses"],
    "negative": ["No conversions yet"]
  }
}
```

**Performance Targets:**
- Mean Absolute Error: < 10 points
- R² Score: > 0.80

### 2. Churn Prediction Model

**Algorithm:** Random Forest Classifier

**Features (32):**
- RFM analysis (recency, frequency, monetary)
- Sentiment trends (sentiment decline over time)
- Engagement decline (reduced message frequency)
- Support tickets (complaint frequency)
- Purchase history (order value, frequency)

**Output:**
```json
{
  "success": true,
  "churn_probability": 0.73,
  "risk_level": "high",
  "confidence": 0.89,
  "recommendations": [
    "Send personalized retention offer",
    "Assign to customer success team",
    "Schedule check-in call"
  ],
  "risk_factors": [
    "No messages in 30 days",
    "Negative sentiment trend",
    "Unsubscribed from campaigns"
  ]
}
```

**Performance Targets:**
- Accuracy: > 75%
- Precision: > 70%
- Recall: > 75%
- F1 Score: > 0.72

### 3. Engagement Prediction Model

**Algorithm:** Logistic Regression

**Features (27):**
- Time patterns (hour of day, day of week)
- Content type (promotional, support, informational)
- Recipient preferences (past engagement by time/content)
- Message characteristics (length, sentiment, urgency)
- Context (campaign type, previous interactions)

**Output:**
```json
{
  "success": true,
  "engagement_probability": 0.81,
  "optimal_send_time": "14:00",
  "best_day": "Tuesday",
  "confidence": 0.87,
  "recommendations": [
    "Send on Tuesday at 2:00 PM",
    "Use casual tone",
    "Include personalized greeting"
  ],
  "engagement_factors": {
    "positive": ["Preferred time window", "High past engagement"],
    "negative": ["Message length > 200 chars"]
  }
}
```

**Performance Targets:**
- Accuracy: > 75%
- Precision: > 70%
- Recall: > 75%
- F1 Score: > 0.72

---

## 🐛 Troubleshooting

### Error: "Not enough training data"

**Cause:** Less than 100 samples for training

**Solutions:**
1. Generate synthetic data:
   ```powershell
   python -m apps.api.app.ml.generate_training_data
   ```

2. Wait for more real data to accumulate

3. Import historical data from CSV

### Error: "Model not found"

**Cause:** Models haven't been trained yet

**Solution:**
```powershell
# Train models first
python -m apps.api.app.ml.train_models

# Then test
python -m apps.api.app.ml.test_models
```

### Error: "Low model accuracy (<50%)"

**Causes:**
- Poor data quality
- Insufficient training data
- Data not representative

**Solutions:**
1. **Check Data Quality:**
   ```sql
   -- Check for NULL values
   SELECT COUNT(*) FROM leads WHERE score IS NULL;
   
   -- Check data distribution
   SELECT converted, COUNT(*) FROM leads GROUP BY converted;
   ```

2. **Add More Data:**
   - Need 200+ samples for reliable models
   - Ensure diverse outcomes (both positive and negative)

3. **Clean Data:**
   ```powershell
   # Remove duplicates
   # Fill missing values
   # Normalize outliers
   ```

### Error: "Training taking too long"

**Causes:**
- Large dataset (10,000+ samples)
- Too many CV folds (>10)

**Solutions:**
1. **Reduce CV Folds:**
   ```json
   {
     "model": "all",
     "cv_folds": 3
   }
   ```

2. **Use Smaller Test Size:**
   ```json
   {
     "model": "all",
     "test_size": 0.1
   }
   ```

3. **Train Models Separately:**
   ```powershell
   # Train one at a time
   python -m apps.api.app.ml.train_models lead_scoring
   ```

### Error: "Database connection failed"

**Solution:**
```powershell
# Start database
cd infra
docker-compose up postgres -d

# Verify connection
docker-compose ps postgres
```

---

## 🎯 Best Practices

### 1. Training Frequency

**Recommended Schedule:**
- **Weekly:** For active businesses (100+ new leads/week)
- **Bi-weekly:** For moderate activity (50-100 new leads/week)
- **Monthly:** For low activity (<50 new leads/week)

### 2. Data Management

**Do:**
- ✅ Keep data clean (remove duplicates, handle missing values)
- ✅ Maintain data quality (validate inputs, sanitize data)
- ✅ Balance datasets (equal positive/negative examples)
- ✅ Use recent data (last 3-6 months)

**Don't:**
- ❌ Train on test data
- ❌ Use synthetic data in production
- ❌ Ignore data quality issues
- ❌ Over-train (daily training with same data)

### 3. Model Versioning

**Save Models with Dates:**
```powershell
# Models auto-saved to:
apps/api/app/ml/trained_models/
├── lead_scoring_model.pkl
├── churn_model.pkl
└── engagement_model.pkl
```

**Backup Before Retraining:**
```powershell
# Copy old models
cp apps/api/app/ml/trained_models/*.pkl backups/2024-01-15/
```

### 4. Performance Monitoring

**Track Metrics Over Time:**
```python
# After each training, record:
{
  "date": "2024-01-15",
  "model": "lead_scoring",
  "mae": 8.45,
  "r2": 0.87,
  "training_samples": 96
}
```

**Alert on Degradation:**
- If MAE increases by >20%
- If R² drops below 0.75
- If accuracy drops below 70%

### 5. A/B Testing

**Compare Model Versions:**
```python
# Deploy new model to 10% of traffic
# Compare conversion rates vs old model
# Full rollout if improvement > 5%
```

---

## ⚙️ Automated Training

### GitHub Actions (Weekly Retraining)

**Create `.github/workflows/train_models.yaml`:**

```yaml
name: Train ML Models

on:
  schedule:
    # Every Sunday at 2 AM UTC
    - cron: '0 2 * * 0'
  workflow_dispatch:  # Manual trigger

jobs:
  train:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install -r apps/api/requirements.txt
      
      - name: Train models
        run: |
          python -m apps.api.app.ml.train_models
        env:
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
      
      - name: Test models
        run: |
          python -m apps.api.app.ml.test_models
      
      - name: Upload models
        uses: actions/upload-artifact@v3
        with:
          name: trained-models
          path: apps/api/app/ml/trained_models/*.pkl
      
      - name: Notify on failure
        if: failure()
        run: |
          echo "Training failed! Check logs."
```

**Trigger Manually:**
```bash
# Go to GitHub Actions tab
# Select "Train ML Models" workflow
# Click "Run workflow"
```

### Celery Beat (Scheduled Tasks)

**Add to `celerybeat-schedule.py`:**

```python
from celery import Celery
from celery.schedules import crontab

app = Celery('tasks')

app.conf.beat_schedule = {
    'train-models-weekly': {
        'task': 'train_ml_models',
        'schedule': crontab(hour=2, minute=0, day_of_week=0),  # Sunday 2 AM
    },
}
```

**Create Celery Task:**

```python
# apps/api/app/workers/ml_worker.py

from celery import shared_task
from app.core.database import SessionLocal
from app.ml.train_models import train_all_models

@shared_task
def train_ml_models():
    """Train all ML models (Celery task)."""
    db = SessionLocal()
    try:
        result = await train_all_models(db)
        return result
    finally:
        db.close()
```

---

## 📊 Monitoring Dashboard

### Real-Time Training Status

**Web UI (React/Vue):**

```javascript
// Fetch training status every 2 seconds
setInterval(async () => {
  const response = await fetch('/api/v1/training/status', {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  const status = await response.json();
  
  // Update UI
  updateProgressBar(status.progress);
  updateMessage(status.message);
  updateMetrics(status.metrics);
}, 2000);
```

### Performance Alerts

**Email Alerts:**

```python
# If model performance drops
if mae > 15 or r2 < 0.70:
    send_email(
        to="admin@example.com",
        subject="ML Model Performance Alert",
        body=f"Lead scoring model performance degraded: MAE={mae}, R²={r2}"
    )
```

---

## 🎉 Summary

**Complete Training Workflow:**

1. **Prepare Data** → Generate or use real data
2. **Train Models** → CLI or Web UI
3. **Test Models** → Validate predictions
4. **Deploy** → Use in production
5. **Monitor** → Track performance
6. **Retrain** → Weekly/monthly updates

**Key Commands:**

```powershell
# 1. Generate data (if needed)
python -m apps.api.app.ml.generate_training_data

# 2. Train models
python -m apps.api.app.ml.train_models

# 3. Test models
python -m apps.api.app.ml.test_models
```

**Next Steps:**
- Set up automated weekly retraining
- Monitor model performance
- Integrate predictions into workflows
- Collect feedback to improve models

---

## 📚 Additional Resources

- [ML_FEATURES.md](./ML_FEATURES.md) - Detailed ML feature documentation
- [PHASE_1_2_COMPLETE.md](./PHASE_1_2_COMPLETE.md) - ML implementation guide
- [API_REFERENCE.md](./API_REFERENCE.md) - API endpoints reference

**Need Help?**
- Check [Troubleshooting](#troubleshooting) section
- Review training logs
- Contact support team
