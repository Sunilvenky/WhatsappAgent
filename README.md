# 🚀 Smart WhatsApp Marketing Agent

**An AI-powered, production-ready WhatsApp marketing automation platform with intelligent campaign execution, reply classification, and ban risk detection.**

[![Status](https://img.shields.io/badge/status-97%25_complete-brightgreen)]()
[![Progress](https://img.shields.io/badge/ML_features-6%2F6_ready-blue)]()
[![Training](https://img.shields.io/badge/ML_training-automated-success)]()
[![License](https://img.shields.io/badge/license-MIT-orange)]()

---

## ✨ What's Built

### **Core Platform** (PR 1-3) ✅
- ✅ FastAPI REST API with JWT authentication & RBAC
- ✅ PostgreSQL database with 8 models (Users, Contacts, Campaigns, Messages, Conversations, Leads, Phone Numbers, Unsubscribers)
- ✅ 60+ API endpoints with OpenAPI documentation
- ✅ SQLAlchemy ORM with Alembic migrations
- ✅ Docker Compose infrastructure
- ✅ Comprehensive test suite

### **WhatsApp Integration** (PR 4) ✅
- ✅ Free WhatsApp integration using Baileys (no Meta API costs!)
- ✅ Node.js gateway service with QR code authentication
- ✅ Session persistence (login once, stay forever)
- ✅ Webhook system for incoming messages
- ✅ Anti-ban features (delays, typing indicators, read receipts)
- ✅ Message status tracking (sent, delivered, read)

### **AI Features** (PR 5) ✅
- ✅ **Multi-provider LLM support** (OpenAI, Anthropic, Ollama)
- ✅ **AI Message Rewriter**: Transform spammy text into natural, human-like messages
- ✅ **Reply Classifier**: Detect intent (interested, not interested, question, unsubscribe)
- ✅ **Ban Risk Detector**: Analyze sending patterns and prevent WhatsApp bans
- ✅ **Lead Scorer**: AI-powered lead quality scoring (0-100)
- ✅ **Auto-response System**: Intelligent automated replies

### **Campaign Engine** (PR 6) ✅
- ✅ **Celery Task Queue**: Async campaign execution with Redis
- ✅ **Campaign Worker**: Automated message sending with throttling
- ✅ **Drip Campaigns**: Multi-step sequences with custom delays
- ✅ **Number Warmup**: 14-day gradual volume increase (20 → 1000 msgs/day)
- ✅ **Message Throttling**: Hourly/daily limits to prevent bans
- ✅ **Retry Logic**: Exponential backoff for failed messages
- ✅ **Personalization Engine**: Template variables with contact data
- ✅ **Ban Risk Monitoring**: Auto-pause campaigns at critical risk

### **Analytics** (PR 7) ✅
- ✅ **Real-time Dashboard**: Message stats, campaign metrics
- ✅ **Campaign Analytics**: Delivery, read, response rates
- ✅ **Message Timeline**: Historical volume tracking
- ✅ **Engagement Metrics**: Response rates, read rates
- ✅ **Hot Lead Detection**: Automatically identify high-value leads
- ✅ **Daily Reports**: Automated stats generation

### **🤖 Machine Learning** (Phase 1 & 2) ✅ **NEW!**
#### **Phase 1: Pre-trained Models**
- ✅ **Sentiment Analysis**: BERT-based emotion detection (positive/negative/neutral + 7 emotions)
- ✅ **Voice Transcription**: Whisper 99-language support with automatic translation
- ✅ **Translation**: Google Translate API for multilingual campaigns (100+ languages)

#### **Phase 2: Custom ML Models**
- ✅ **Lead Scoring**: XGBoost model (24 features, 0-100 score, quality tiers)
- ✅ **Churn Prediction**: Random Forest (32 features, retention recommendations)
- ✅ **Engagement Prediction**: Logistic Regression (27 features, optimal send time)
- ✅ **Training Pipeline**: Automated ML training, validation, and versioning

#### **🎓 ML Training System** ✅ **LATEST!**
- ✅ **CLI Training**: Developer-friendly command-line training
- ✅ **Web UI**: Non-technical user training dashboard (6 endpoints)
- ✅ **Automated Testing**: Model validation and quality assurance
- ✅ **Data Generation**: Synthetic data for testing (200 contacts, 150 conversations, 120 leads)
- ✅ **GitHub Actions**: Automated weekly retraining
- ✅ **Progress Tracking**: Real-time training status and metrics
- ✅ **Comprehensive Docs**: 600+ line training guide

**Total ML Endpoints**: 34 (28 ML + 6 Training)  
**Training Files**: 6 (CLI, Web UI, Testing, Data Gen, Workflow, Docs)

---

## 🎯 Key Features

| Feature | Description | Status |
|---------|-------------|--------|
| **Free WhatsApp** | No Meta API costs, direct protocol | ✅ Ready |
| **AI Rewriting** | Make messages sound human | ✅ Ready |
| **Smart Classification** | Auto-detect reply intent | ✅ Ready |
| **Ban Prevention** | Real-time risk monitoring | ✅ Ready |
| **Lead Scoring (AI + ML)** | AI + XGBoost quality scores | ✅ Ready |
| **Drip Campaigns** | Multi-step automation | ✅ Ready |
| **Number Warmup** | Gradual volume ramp-up | ✅ Ready |
| **Auto-responses** | Intelligent reply bot | ✅ Ready |
| **Analytics** | Real-time dashboards | ✅ Ready |
| **🆕 Sentiment Analysis** | BERT emotion detection | ✅ Ready |
| **🆕 Voice Transcription** | Whisper 99 languages | ✅ Ready |
| **🆕 Translation** | 100+ language support | ✅ Ready |
| **🆕 Churn Prediction** | ML retention insights | ✅ Ready |
| **🆕 Optimal Timing** | ML send-time optimization | ✅ Ready |
| **🎓 ML Training System** | Automated model training | ✅ Ready |
| **📊 Training Dashboard** | Web UI for training | ✅ Ready |

---

## ⚡ Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- PostgreSQL 14+
- Redis 6+
- Docker & Docker Compose (recommended)

### 1. Environment Setup

```bash
# Clone repository
git clone <repo-url>
cd whatsapp-agent

# Copy environment file
cp apps/api/.env.example apps/api/.env

# Edit .env and add your API keys
nano apps/api/.env
```

**Required API Keys:**
- `OPENAI_API_KEY` - For AI features (or use Ollama for free local LLM)
- `WHATSAPP_WEBHOOK_SECRET` - Random secret for webhook security

### 2. Start Services (Docker - Recommended)

```bash
cd infra
docker-compose up -d
```

This starts:
- PostgreSQL database (port 5432)
- Redis (port 6379)
- WhatsApp Gateway (port 3001)
- FastAPI server (port 8000)
- Celery worker
- Celery beat scheduler

### 3. Initialize Database

```bash
# Run migrations
cd apps/api
alembic upgrade head

# Create default admin user
python -m app.scripts.init_db
```

**Default Admin Credentials:**
- Username: `admin`
- Password: `admin123`
- **⚠️ Change immediately in production!**

### 4. Connect WhatsApp

```bash
# Get QR code
curl http://localhost:8000/api/v1/whatsapp/qr \
  -H "Authorization: Bearer YOUR_TOKEN"

# Scan QR code with WhatsApp mobile app
# Session persists across restarts - only need to scan once!
```

### 5. Test Everything Works

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Create test contact
curl -X POST http://localhost:8000/api/v1/contacts \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Test User","phone":"+1234567890","email":"test@example.com"}'

# Test AI message rewriting
curl -X POST http://localhost:8000/api/v1/ai/rewrite \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message":"BUY NOW!!!","tone":"friendly"}'
```

---

## 🎓 ML Model Training

Train custom ML models with your data for accurate predictions!

### Quick Start (CLI)

```powershell
# 1. Generate synthetic training data (if needed)
python -m apps.api.app.ml.generate_training_data

# 2. Train all models
python -m apps.api.app.ml.train_models

# 3. Test models
python -m apps.api.app.ml.test_models
```

### Web UI Training

```bash
# Start training via API
curl -X POST http://localhost:8000/api/v1/training/start \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"model": "all", "test_size": 0.2, "cv_folds": 5}'

# Monitor progress
curl http://localhost:8000/api/v1/training/status \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Automated Weekly Retraining

Models automatically retrain every Sunday at 2 AM via GitHub Actions!

**Manual Trigger:**
1. Go to GitHub Actions tab
2. Select "Train ML Models" workflow
3. Click "Run workflow"

**Output:**
```
🤖 ML MODEL TRAINING PIPELINE

🎯 TRAINING LEAD SCORING MODEL
📊 Training samples: 96
✅ Training complete!
📈 Model Performance:
   Mean Absolute Error: 8.45
   R² Score: 0.87
```

**Training Guide**: See [docs/TRAINING_GUIDE.md](docs/TRAINING_GUIDE.md) for complete instructions.

---

## 📖 Documentation

### Core Documentation
- **[Complete AI & Campaign Guide](docs/PR5_6_7_AI_AND_CAMPAIGNS.md)** - AI features, campaign execution, analytics
- **[WhatsApp Integration](docs/PR4_WHATSAPP_INTEGRATION.md)** - Gateway setup, troubleshooting
- **[API Reference](docs/API_REFERENCE.md)** - Complete endpoint documentation
- **[Architecture](docs/ARCHITECTURE.md)** - System design and data models
- **[Operations](docs/OPERATIONS.md)** - Deployment and monitoring

### ML Documentation 🆕
- **[ML Training Guide](docs/TRAINING_GUIDE.md)** - Complete training instructions (600+ lines)
- **[ML Features](docs/ML_FEATURES.md)** - Detailed ML feature documentation (1500+ lines)
- **[Training System](docs/ML_TRAINING_SYSTEM.md)** - Training system architecture
- **[Phase 1 & 2 Complete](docs/PHASE_1_2_COMPLETE.md)** - ML implementation summary

---

## 🎮 Usage Examples

### Create AI-Powered Campaign

```bash
# 1. Create campaign with AI rewriting enabled
curl -X POST http://localhost:8000/api/v1/campaigns \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Product Launch",
    "message_template": "Hi {name}! Check out our new product!",
    "contact_ids": [1, 2, 3, 4, 5],
    "phone_number_id": 1,
    "metadata": {"tone": "friendly"}
  }'

# 2. Start campaign (AI will rewrite each message uniquely)
curl -X POST http://localhost:8000/api/v1/campaigns/1/start \
  -H "Authorization: Bearer YOUR_TOKEN"

# 3. Monitor analytics
curl http://localhost:8000/api/v1/analytics/campaigns/1 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Process Incoming Replies with AI

```bash
# Webhook automatically processes replies
# AI classifies intent: interested, not_interested, question, unsubscribe
# Auto-responds based on classification
# Updates lead score in real-time
```

### Get Hot Leads

```bash
curl "http://localhost:8000/api/v1/ai/hot-leads?threshold=80" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🧪 Testing

### Run Test Suite

```bash
# Install dependencies
pip install -r requirements.txt

# Run all tests
pytest apps/api/app/tests/ -v

# Run specific test
pytest apps/api/app/tests/test_campaign_models.py -v

# With coverage
pytest --cov=app apps/api/app/tests/
```

---

## 🏗️ Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   React UI      │────▶│  FastAPI API    │────▶│  PostgreSQL DB  │
│   (Future)      │     │  JWT Auth       │     │  8 Models       │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                              │    │
                    ┌─────────┘    └──────────┐
                    ▼                          ▼
         ┌─────────────────┐        ┌─────────────────┐
         │ WhatsApp Gateway│        │  Celery Workers │
         │  Node.js/Baileys│        │  Campaign Exec  │
         │  QR Auth        │        │  AI Processing  │
         └─────────────────┘        └─────────────────┘
                    │                          │
                    └──────────┬───────────────┘
                               ▼
                    ┌─────────────────┐
                    │  Redis Queue    │
                    │  Session Store  │
                    └─────────────────┘
```

### Tech Stack

**Backend:**
- FastAPI (Python 3.9+)
- SQLAlchemy + Alembic
- PostgreSQL 14
- Celery + Redis
- JWT Authentication

**WhatsApp:**
- Baileys v6.7 (Node.js)
- Express.js
- QR Code Auth

**AI:**
- OpenAI GPT-4 / Claude / Ollama
- LangChain
- Custom classifiers

**Infrastructure:**
- Docker Compose
- Redis
- Persistent volumes

---

## 🔐 Security

- JWT token-based authentication
- Role-based access control (Admin, Marketer, Sales)
- Webhook secret verification
- Password hashing with bcrypt
- Rate limiting on API endpoints
- SQL injection protection (SQLAlchemy)
- XSS protection
- Environment variable configuration

---

## � API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register user
- `POST /api/v1/auth/login` - Login (get JWT)
- `GET /api/v1/auth/me` - Get current user
- `PUT /api/v1/auth/password` - Change password

### Contacts
- `GET /api/v1/contacts` - List contacts
- `POST /api/v1/contacts` - Create contact
- `GET /api/v1/contacts/{id}` - Get contact
- `PUT /api/v1/contacts/{id}` - Update contact
- `DELETE /api/v1/contacts/{id}` - Delete contact

### Campaigns
- `GET /api/v1/campaigns` - List campaigns
- `POST /api/v1/campaigns` - Create campaign
- `POST /api/v1/campaigns/{id}/start` - Start campaign
- `POST /api/v1/campaigns/{id}/pause` - Pause campaign
- `GET /api/v1/campaigns/{id}/stats` - Get stats

### AI Features
- `POST /api/v1/ai/rewrite` - Rewrite message
- `POST /api/v1/ai/classify` - Classify reply
- `POST /api/v1/ai/ban-risk` - Check ban risk
- `POST /api/v1/ai/score-lead` - Score lead
- `GET /api/v1/ai/hot-leads` - Get hot leads

### ML Features (28 endpoints)
- **Sentiment**: Analyze messages, conversations, batch
- **Voice**: Transcribe, translate audio messages
- **Translation**: Translate text, detect language
- **Lead Scoring**: Score leads with ML, batch scoring
- **Churn**: Predict churn risk, batch predictions
- **Engagement**: Predict engagement, optimal send times
- **Training**: Model management, metrics history

### ML Training (6 endpoints)
- `GET /api/v1/training/status` - Get training status
- `POST /api/v1/training/start` - Start training
- `POST /api/v1/training/stop` - Cancel training
- `GET /api/v1/training/history` - View past runs
- `GET /api/v1/training/models` - List trained models
- `POST /api/v1/training/schedule` - Schedule retraining

### Analytics
- `GET /api/v1/analytics/dashboard` - Dashboard stats
- `GET /api/v1/analytics/campaigns/{id}` - Campaign analytics
- `GET /api/v1/analytics/messages/timeline` - Message timeline
- `GET /api/v1/analytics/engagement` - Engagement metrics

### WhatsApp
- `GET /api/v1/whatsapp/status` - Connection status
- `GET /api/v1/whatsapp/qr` - Get QR code
- `POST /api/v1/whatsapp/send` - Send message
- `POST /api/v1/whatsapp/logout` - Logout session

**Full API documentation**: http://localhost:8000/docs

---

## 💡 Best Practices

### Avoiding WhatsApp Bans

1. **Use AI Message Rewriting** - Avoid spam patterns
2. **Enable Number Warmup** - Start slow, ramp up gradually
3. **Monitor Ban Risk** - Check `/api/v1/ai/ban-risk` regularly
4. **Respect Throttle Limits** - Don't exceed daily/hourly limits
5. **Use Random Delays** - Appear more human-like
6. **Handle Unsubscribes** - Auto-detect and respect opt-outs

### Campaign Optimization

1. **Score Leads First** - Target high-quality leads
2. **Personalize Messages** - Use template variables
3. **Test Small Batches** - Validate before full send
4. **Monitor Analytics** - Track engagement metrics
5. **A/B Test Messages** - Use alternative generation
6. **Use Drip Campaigns** - Multi-touch sequences

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

## � License

This project is licensed under the MIT License.

---

## 🙋 Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/yourusername/whatsapp-agent/issues)
- **Email**: support@example.com

---

## 🎉 What's Next?

The platform is **90% complete** and ready for testing! Remaining items:

- [ ] End-to-end integration tests
- [ ] Production deployment guide
- [ ] React admin dashboard
- [ ] CRM integrations (Salesforce, HubSpot)
- [ ] Multi-tenant support
- [ ] Advanced reporting

**Start testing today and build your WhatsApp marketing automation! 🚀**