# Smart WhatsApp Agent - AI Features, Campaign Execution & Analytics

## Complete Feature Documentation (PR 5, 6, 7)

**Status**: ✅ **READY FOR TESTING**

This document covers the AI-powered features, automated campaign execution engine, and analytics system for the Smart WhatsApp Agent.

---

## 🎯 Features Implemented

### **PR 5: AI Features** ✅
- ✅ Multi-provider LLM client (OpenAI, Anthropic, Ollama)
- ✅ AI message rewriter (natural, human-like text)
- ✅ Reply classifier (intent detection, sentiment analysis)
- ✅ Ban risk detector (pattern analysis, spam detection)
- ✅ AI lead scorer (engagement-based scoring)
- ✅ REST API endpoints for all AI features

### **PR 6: Campaign Execution Engine** ✅
- ✅ Celery task queue with Redis
- ✅ Campaign execution worker
- ✅ Drip campaign sequencer
- ✅ Number warmup manager (14-day gradual ramp)
- ✅ Message throttling (hourly/daily limits)
- ✅ Retry logic with exponential backoff
- ✅ Message personalization engine
- ✅ Auto-response system
- ✅ Ban risk monitoring

### **PR 7: Analytics & Advanced Features** ✅
- ✅ Real-time campaign analytics
- ✅ Dashboard statistics
- ✅ Message timeline tracking
- ✅ Engagement metrics
- ✅ Top performer identification
- ✅ Daily report generation
- ✅ Automated lead score updates

---

## 📦 Dependencies Added

```plaintext
# AI/LLM
openai>=1.0.0
anthropic>=0.7.0
langchain>=0.1.0
tiktoken>=0.5.0

# Task Queue
celery>=5.3.0
redis>=5.0.0
apscheduler>=3.10.0

# Data Processing
pandas>=2.0.0
phonenumbers>=8.13.0
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   FastAPI REST API                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │   AI     │  │Analytics │  │Campaigns │              │
│  │Endpoints │  │Endpoints │  │Endpoints │              │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘              │
└───────┼────────────┼─────────────┼─────────────────────┘
        │            │             │
        ▼            ▼             ▼
┌──────────────────────────────────────────────────────────┐
│                   Service Layer                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │  Message │  │  Reply   │  │   Ban    │              │
│  │ Rewriter │  │Classifier│  │ Detector │              │
│  └──────────┘  └──────────┘  └──────────┘              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │   Lead   │  │Personaliz│  │ Throttle │              │
│  │  Scorer  │  │   er     │  │  Manager │              │
│  └──────────┘  └──────────┘  └──────────┘              │
└──────────────────────┬───────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────┐
│              Celery Worker Layer                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │Campaign  │  │ Message  │  │Analytics │              │
│  │ Worker   │  │  Worker  │  │ Worker   │              │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘              │
└───────┼────────────┼─────────────┼─────────────────────┘
        │            │             │
        ▼            ▼             ▼
┌──────────────────────────────────────────────────────────┐
│                 Redis (Message Queue)                     │
└──────────────────────────────────────────────────────────┘
        │            │             │
        ▼            ▼             ▼
┌──────────────────────────────────────────────────────────┐
│              PostgreSQL Database                          │
└──────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### 1. Environment Configuration

Create `.env` file in `apps/api/`:

```env
# AI/LLM Settings
OPENAI_API_KEY=sk-your-openai-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here
LLM_PROVIDER=openai  # openai, anthropic, ollama
LLM_MODEL=gpt-4-turbo-preview
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=1000

# Ollama (if using local LLM)
OLLAMA_BASE_URL=http://localhost:11434

# Campaign Settings
MAX_MESSAGES_PER_HOUR=100
MAX_MESSAGES_PER_DAY=1000
MESSAGE_DELAY_MIN=2
MESSAGE_DELAY_MAX=5
WARMUP_ENABLED=true
WARMUP_DAYS=14

# AI Feature Toggles
AI_MESSAGE_REWRITING_ENABLED=true
AI_REPLY_CLASSIFICATION_ENABLED=true
AI_BAN_RISK_DETECTION_ENABLED=true
AI_LEAD_SCORING_ENABLED=true

# Redis & Celery
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Start Services

**Option A: Docker Compose** (Recommended)

```bash
cd infra
docker-compose up -d
```

**Option B: Manual**

```bash
# Terminal 1: Redis
redis-server

# Terminal 2: API Server
cd apps/api
uvicorn app.main:app --reload --port 8000

# Terminal 3: Celery Worker
cd apps/api
celery -A app.workers.celery_app worker --loglevel=info --queues=campaigns,messages,analytics

# Terminal 4: Celery Beat (Scheduler)
cd apps/api
celery -A app.workers.celery_app beat --loglevel=info
```

---

## 🤖 AI Features API

### 1. **Message Rewriting**

Transform marketing messages into natural, human-like text:

```bash
curl -X POST http://localhost:8000/api/v1/ai/rewrite \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "BUY NOW!!! LIMITED TIME OFFER!! Click here for FREE product!!!",
    "contact_name": "John",
    "tone": "friendly"
  }'
```

**Response:**
```json
{
  "original": "BUY NOW!!! LIMITED TIME OFFER!!...",
  "rewritten": "Hey John! 👋 I thought you might be interested in checking out our special offer that's running for a limited time. Let me know if you'd like more details!",
  "tone": "friendly"
}
```

### 2. **Reply Classification**

Classify incoming replies to determine intent and sentiment:

```bash
curl -X POST http://localhost:8000/api/v1/ai/classify \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "reply_text": "Thanks! Can you tell me more about pricing?",
    "original_message": "We have a new product launch"
  }'
```

**Response:**
```json
{
  "intent": "question",
  "sentiment": "positive",
  "confidence": 85,
  "key_phrases": ["pricing", "more info"],
  "suggested_action": "Send pricing details",
  "urgency": "medium",
  "auto_response": {
    "should_respond": false,
    "suggested_response": "Flag for human review",
    "requires_human_review": true
  }
}
```

### 3. **Ban Risk Detection**

Analyze ban risk for messages or sending patterns:

```bash
# Check message content
curl -X POST http://localhost:8000/api/v1/ai/ban-risk \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "FREE!!! CLICK NOW!!! LIMITED TIME!!!!"
  }'

# Check sending pattern
curl -X POST http://localhost:8000/api/v1/ai/ban-risk \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number_id": 1,
    "hours": 24
  }'
```

**Response:**
```json
{
  "risk_score": 75,
  "risk_level": "high",
  "factors": [
    "Very high message volume (>100/hour)",
    "Very similar messages detected (90% similarity)",
    "Low response rate (3%)"
  ],
  "recommendations": [
    "🚨 URGENT: Stop sending messages immediately for 24-48 hours",
    "Use AI message rewriting for more variation",
    "Reduce message sending rate to <50/hour"
  ],
  "metrics": {
    "total_messages": 500,
    "messages_per_hour": 125,
    "response_rate": 0.03,
    "blocked_count": 2
  }
}
```

### 4. **Lead Scoring**

Score leads based on engagement and behavior:

```bash
curl -X POST http://localhost:8000/api/v1/ai/score-lead \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "contact_id": 123
  }'
```

**Response:**
```json
{
  "total_score": 82,
  "quality_tier": "hot",
  "priority": "high",
  "breakdown": {
    "engagement": 32,
    "profile": 12,
    "behavior": 24,
    "timing": 8
  },
  "insights": [
    "🔥 Highly engaged lead - prioritize immediate follow-up",
    "Asked specific questions about implementation",
    "Responds quickly (avg 10 minutes)"
  ],
  "next_actions": [
    "📞 Call or schedule meeting within 24 hours",
    "💰 Send pricing and proposal",
    "🎯 Assign to senior sales rep"
  ]
}
```

---

## 📊 Campaign Execution

### 1. **Create & Execute Campaign**

```bash
# Create campaign
curl -X POST http://localhost:8000/api/v1/campaigns \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Product Launch Campaign",
    "message_template": "Hi {name}! We just launched {product_name}. Check it out!",
    "contact_ids": [1, 2, 3, 4, 5],
    "phone_number_id": 1,
    "metadata": {
      "tone": "friendly",
      "product_name": "SuperApp 2.0"
    }
  }'

# Execute campaign (triggers Celery worker)
curl -X POST http://localhost:8000/api/v1/campaigns/1/start \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 2. **Drip Campaign**

Create multi-step drip sequences:

```bash
curl -X POST http://localhost:8000/api/v1/campaigns \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Onboarding Drip",
    "type": "drip",
    "contact_ids": [1, 2, 3],
    "phone_number_id": 1,
    "metadata": {
      "sequence": [
        {
          "delay_hours": 0,
          "message": "Welcome {name}! Thanks for signing up."
        },
        {
          "delay_hours": 24,
          "message": "Hi {name}, here are some tips to get started..."
        },
        {
          "delay_hours": 72,
          "message": "How's it going {name}? Any questions?"
        }
      ]
    }
  }'
```

### 3. **Number Warmup**

The system automatically enforces a 14-day warmup period:

| Day | Max Messages |
|-----|-------------|
| 1   | 20          |
| 2   | 30          |
| 3   | 50          |
| 4   | 75          |
| 5   | 100         |
| 6   | 150         |
| 7   | 200         |
| 8   | 300         |
| 9   | 400         |
| 10  | 500         |
| 11  | 700         |
| 12  | 900         |
| 13-14 | 1000     |

---

## 📈 Analytics API

### 1. **Dashboard Statistics**

```bash
curl -X GET http://localhost:8000/api/v1/analytics/dashboard \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
  "total_messages_sent": 5420,
  "total_messages_received": 1234,
  "total_contacts": 1500,
  "total_campaigns": 25,
  "active_campaigns": 3,
  "avg_response_rate": 22.75,
  "today_messages": 150,
  "this_week_messages": 980
}
```

### 2. **Campaign Analytics**

```bash
curl -X GET http://localhost:8000/api/v1/analytics/campaigns/1 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
  "campaign_id": 1,
  "campaign_name": "Product Launch",
  "status": "completed",
  "analytics": {
    "total_messages": 500,
    "delivered_count": 485,
    "read_count": 420,
    "replied_count": 115,
    "failed_count": 15,
    "response_rate": 23.0,
    "delivery_rate": 97.0,
    "read_rate": 84.0,
    "engagement_score": 77.5
  }
}
```

### 3. **Message Timeline**

```bash
curl -X GET "http://localhost:8000/api/v1/analytics/messages/timeline?days=7" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 4. **Hot Leads**

```bash
curl -X GET "http://localhost:8000/api/v1/ai/hot-leads?threshold=80&limit=20" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🔄 Automated Workers

### Campaign Worker

**Tasks:**
- `execute_campaign` - Send messages to all contacts
- `process_scheduled_campaigns` - Start scheduled campaigns (runs every minute)
- `process_drip_sequences` - Process drip campaign steps (every 5 minutes)
- `monitor_ban_risks` - Check and alert on ban risks (every 30 minutes)

### Message Worker

**Tasks:**
- `send_message` - Send single message with retry
- `process_incoming_message` - Process replies with AI classification
- `cleanup_old_messages` - Delete messages older than 90 days (daily at 2 AM)
- `update_message_status` - Update message status from webhooks

### Analytics Worker

**Tasks:**
- `update_campaign_analytics` - Calculate campaign metrics (every 10 minutes)
- `generate_daily_report` - Generate daily stats report (daily at 2 AM)
- `update_lead_scores` - Recalculate all lead scores (configurable)

---

## 🛡️ Safety Features

### 1. **Automatic Ban Risk Monitoring**

The system continuously monitors for ban risk patterns:

- **Pattern Analysis**: Checks message volume, timing, similarity
- **Auto-Pause**: Pauses campaigns at critical risk level
- **Alerts**: Logs warnings when risk exceeds thresholds

### 2. **Message Throttling**

Prevents rate limit violations:

- Hourly limit: 100 messages (configurable)
- Daily limit: 1000 messages (configurable)
- Random delays: 2-5 seconds between messages
- Respects warmup schedule

### 3. **Retry Logic**

Handles failures gracefully:

- Max 3 retries per message
- Exponential backoff: 2^n minutes
- Tracks retry count in Redis
- Marks as failed after max retries

---

## 🧪 Testing

### Unit Tests

```bash
cd apps/api
pytest app/tests/
```

### Integration Test Example

```python
# Test AI message rewriting
async def test_message_rewriting():
    from app.ai import MessageRewriter
    
    rewriter = MessageRewriter()
    result = await rewriter.rewrite_message(
        "BUY NOW!!!",
        contact_name="John",
        tone="professional"
    )
    
    assert len(result) > 0
    assert "!!!" not in result  # Should remove spam indicators
```

### Manual Testing Workflow

1. **Start all services** (Redis, API, Celery workers)
2. **Create test campaign** with 5 contacts
3. **Execute campaign** and monitor Celery logs
4. **Simulate incoming reply** via webhook
5. **Check analytics** dashboard
6. **Verify lead scores** updated

---

## 📝 Configuration Reference

### AI Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | - | OpenAI API key |
| `ANTHROPIC_API_KEY` | - | Anthropic API key |
| `LLM_PROVIDER` | `openai` | LLM provider (openai/anthropic/ollama) |
| `LLM_MODEL` | `gpt-4-turbo-preview` | Model name |
| `LLM_TEMPERATURE` | `0.7` | Creativity (0-1) |

### Campaign Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `MAX_MESSAGES_PER_HOUR` | `100` | Hourly message limit |
| `MAX_MESSAGES_PER_DAY` | `1000` | Daily message limit |
| `MESSAGE_DELAY_MIN` | `2` | Min delay (seconds) |
| `MESSAGE_DELAY_MAX` | `5` | Max delay (seconds) |
| `WARMUP_ENABLED` | `true` | Enable warmup |
| `WARMUP_DAYS` | `14` | Warmup duration |

---

## 🚨 Troubleshooting

### Celery Workers Not Starting

```bash
# Check Redis connection
redis-cli ping

# Check Celery broker
celery -A app.workers.celery_app inspect ping

# View worker logs
celery -A app.workers.celery_app worker --loglevel=debug
```

### AI Features Not Working

1. **Check API keys** in `.env`
2. **Verify LLM provider** setting
3. **Test connection**:
```python
from app.ai import get_llm_client
client = get_llm_client()
result = await client.complete("Test prompt")
```

### Messages Not Sending

1. **Check WhatsApp Gateway** status
2. **Verify campaign status** (must be RUNNING)
3. **Check throttle limits** in Redis:
```bash
redis-cli KEYS "throttle:*"
```

---

## 🎉 Success! What's Next?

You now have a **fully functional Smart WhatsApp Agent** with:

✅ AI-powered message rewriting  
✅ Automated reply classification  
✅ Ban risk detection & prevention  
✅ Intelligent lead scoring  
✅ Campaign execution engine  
✅ Drip campaign sequencer  
✅ Number warmup automation  
✅ Real-time analytics  
✅ Automated workers  

### Testing Checklist

- [ ] Start all services (Redis, API, Celery)
- [ ] Create test campaign with AI rewriting enabled
- [ ] Execute campaign and verify messages sent
- [ ] Send test reply and verify classification
- [ ] Check analytics dashboard
- [ ] Verify ban risk monitoring
- [ ] Test drip campaign sequence
- [ ] Confirm lead scores updating

---

## 📚 Additional Resources

- [API Reference](API_REFERENCE.md) - Complete API documentation
- [Architecture Guide](ARCHITECTURE.md) - System design details
- [WhatsApp Integration](PR4_WHATSAPP_INTEGRATION.md) - Gateway setup
- [Operations Guide](OPERATIONS.md) - Production deployment

**Ready to test? Start the services and let's go! 🚀**
