# 🧪 Testing Guide - Smart WhatsApp Agent

Complete testing workflow for PR 5, 6, and 7 (AI Features, Campaign Execution, Analytics).

---

## ✅ Pre-Flight Checklist

Before testing, ensure you have:

- [ ] Python 3.9+ installed
- [ ] Node.js 18+ installed
- [ ] PostgreSQL 14+ running
- [ ] Redis 6+ running
- [ ] OpenAI API key (or Ollama installed for free local LLM)
- [ ] `.env` file configured in `apps/api/`
- [ ] All dependencies installed (`pip install -r requirements.txt`)

---

## 🚀 Test Suite 1: Service Startup

### 1.1 Start Infrastructure

```bash
# Start PostgreSQL & Redis (Docker)
cd infra
docker-compose up -d postgres redis

# Verify services
docker ps
# Should see: postgres, redis containers running
```

### 1.2 Start API Server

```bash
cd apps/api
uvicorn app.main:app --reload --port 8000
```

**Expected Output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
```

### 1.3 Start Celery Workers

**Terminal 1: Celery Worker**
```bash
cd apps/api
celery -A app.workers.celery_app worker --loglevel=info --queues=campaigns,messages,analytics
```

**Terminal 2: Celery Beat (Scheduler)**
```bash
cd apps/api
celery -A app.workers.celery_app beat --loglevel=info
```

**Expected Output:**
```
[tasks]
  . app.workers.campaign_worker.execute_campaign
  . app.workers.campaign_worker.process_scheduled_campaigns
  . app.workers.message_worker.send_message
  . app.workers.analytics_worker.update_campaign_analytics
```

### 1.4 Health Check

```bash
curl http://localhost:8000/api/v1/health
```

**Expected:**
```json
{
  "code": "ok",
  "message": "healthy",
  "data": {"status": "ok"}
}
```

✅ **PASS CRITERIA**: All services running, health check returns OK

---

## 🔐 Test Suite 2: Authentication

### 2.1 Initialize Database

```bash
cd apps/api
alembic upgrade head
python -m app.scripts.init_db
```

**Expected:** Default admin user created

### 2.2 Login

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

**Expected Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

**Save this token as `$TOKEN` for subsequent tests!**

### 2.3 Verify Authentication

```bash
export TOKEN="your-token-here"

curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

**Expected:** User details returned

✅ **PASS CRITERIA**: Login successful, token works

---

## 📞 Test Suite 3: WhatsApp Integration

### 3.1 Start WhatsApp Gateway

```bash
cd apps/whatsapp-gateway
npm install
npm start
```

**Expected:**
```
WhatsApp Gateway listening on port 3001
Waiting for QR code scan...
```

### 3.2 Get QR Code

```bash
curl http://localhost:8000/api/v1/whatsapp/qr \
  -H "Authorization: Bearer $TOKEN"
```

**Expected:**
```json
{
  "qr_code": "2@vWpKFY...",
  "status": "waiting_for_scan",
  "instructions": "Scan this QR code with WhatsApp"
}
```

### 3.3 Scan QR Code

1. Open WhatsApp on your phone
2. Go to **Settings > Linked Devices > Link a Device**
3. Scan the QR code
4. Wait for connection

### 3.4 Verify Connection

```bash
curl http://localhost:8000/api/v1/whatsapp/status \
  -H "Authorization: Bearer $TOKEN"
```

**Expected:**
```json
{
  "status": "connected",
  "phone_number": "+1234567890",
  "session_active": true
}
```

### 3.5 Test Message Sending

```bash
curl -X POST http://localhost:8000/api/v1/whatsapp/send \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "to": "+1234567890",
    "message": "Test message from Smart WhatsApp Agent!"
  }'
```

**Expected:**
```json
{
  "success": true,
  "message_id": "wamid.xxx",
  "status": "sent"
}
```

**Verify:** Check your WhatsApp - you should receive the message!

✅ **PASS CRITERIA**: QR scan successful, message delivered to WhatsApp

---

## 🤖 Test Suite 4: AI Features

### 4.1 Test Message Rewriting

```bash
curl -X POST http://localhost:8000/api/v1/ai/rewrite \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "BUY NOW!!! FREE SHIPPING!!! LIMITED TIME ONLY!!!",
    "contact_name": "John",
    "tone": "friendly"
  }'
```

**Expected:**
- Original spam-like message is transformed
- No excessive caps or punctuation
- Natural, conversational tone
- Message includes contact name

**Example Output:**
```json
{
  "original": "BUY NOW!!! FREE SHIPPING!!!...",
  "rewritten": "Hey John! 👋 I wanted to let you know about our special offer that's available for a limited time. Free shipping included! Let me know if you'd like more details.",
  "tone": "friendly"
}
```

### 4.2 Test Reply Classification

```bash
curl -X POST http://localhost:8000/api/v1/ai/classify \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "reply_text": "Thanks! Can you tell me more about pricing?",
    "original_message": "We just launched our new product!"
  }'
```

**Expected:**
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
    "requires_human_review": true
  }
}
```

### 4.3 Test Ban Risk Detection

```bash
curl -X POST http://localhost:8000/api/v1/ai/ban-risk \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "FREE!!! CLICK NOW!!! LIMITED TIME OFFER!!!"
  }'
```

**Expected:**
```json
{
  "risk_score": 85,
  "risk_level": "high",
  "spam_indicators": [
    "Excessive caps and punctuation",
    "Spam keywords: FREE, LIMITED TIME",
    "Multiple exclamation marks"
  ],
  "suggestions": [
    "Remove excessive punctuation",
    "Use natural language",
    "Avoid spam trigger words"
  ]
}
```

### 4.4 Test Lead Scoring

**First, create a test contact:**

```bash
curl -X POST http://localhost:8000/api/v1/contacts \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Jane Doe",
    "phone": "+1234567890",
    "email": "jane@example.com"
  }'
```

**Then score the lead:**

```bash
curl -X POST http://localhost:8000/api/v1/ai/score-lead \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "contact_id": 1
  }'
```

**Expected:**
```json
{
  "total_score": 45,
  "quality_tier": "cold",
  "priority": "low",
  "breakdown": {
    "engagement": 0,
    "profile": 12,
    "behavior": 0,
    "timing": 0
  },
  "insights": [
    "❄️ Cold lead - needs more engagement",
    "Complete profile with email",
    "No conversation history yet"
  ],
  "next_actions": [
    "📚 Share educational content",
    "❓ Ask qualifying questions"
  ]
}
```

✅ **PASS CRITERIA**: All AI endpoints return valid responses

---

## 🎯 Test Suite 5: Campaign Execution

### 5.1 Create Contacts

```bash
# Create 5 test contacts
for i in {1..5}; do
  curl -X POST http://localhost:8000/api/v1/contacts \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "{
      \"name\": \"Test Contact $i\",
      \"phone\": \"+12345678$(printf '%02d' $i)\",
      \"email\": \"test$i@example.com\"
    }"
done
```

### 5.2 Create Campaign with AI Rewriting

```bash
curl -X POST http://localhost:8000/api/v1/campaigns \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Campaign with AI",
    "message_template": "Hi {name}! We have a special offer for you!",
    "contact_ids": [1, 2, 3, 4, 5],
    "phone_number_id": 1,
    "metadata": {
      "tone": "friendly",
      "ai_rewriting_enabled": true
    }
  }'
```

**Expected:** Campaign created with ID

### 5.3 Execute Campaign

```bash
curl -X POST http://localhost:8000/api/v1/campaigns/1/start \
  -H "Authorization: Bearer $TOKEN"
```

**Expected:**
```json
{
  "status": "started",
  "campaign_id": 1,
  "message": "Campaign queued for execution"
}
```

### 5.4 Monitor Celery Logs

**Watch the Celery worker terminal:**

```
[2025-10-23 10:00:00] INFO: Starting campaign execution: 1
[2025-10-23 10:00:01] INFO: Campaign 1: 5 contacts to process
[2025-10-23 10:00:02] INFO: Message rewritten: 45 -> 98 chars
[2025-10-23 10:00:04] INFO: Message 1 sent successfully
[2025-10-23 10:00:07] INFO: Throttle delay: 2.5s
[2025-10-23 10:00:09] INFO: Message 2 sent successfully
...
```

### 5.5 Verify Messages Sent

**Check WhatsApp:** All 5 contacts should receive uniquely rewritten messages!

### 5.6 Check Campaign Analytics

```bash
curl http://localhost:8000/api/v1/analytics/campaigns/1 \
  -H "Authorization: Bearer $TOKEN"
```

**Expected:**
```json
{
  "campaign_id": 1,
  "status": "completed",
  "analytics": {
    "total_messages": 5,
    "delivered_count": 5,
    "failed_count": 0,
    "response_rate": 0,
    "delivery_rate": 100
  }
}
```

✅ **PASS CRITERIA**: Campaign executes, messages sent with AI rewriting

---

## 💧 Test Suite 6: Drip Campaigns

### 6.1 Create Drip Campaign

```bash
curl -X POST http://localhost:8000/api/v1/campaigns \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Onboarding Drip",
    "type": "drip",
    "contact_ids": [1],
    "phone_number_id": 1,
    "metadata": {
      "sequence": [
        {
          "delay_hours": 0,
          "message": "Welcome {name}! Thanks for joining us."
        },
        {
          "delay_hours": 0.02,
          "message": "Quick tip: You can reply to this message anytime!"
        },
        {
          "delay_hours": 0.04,
          "message": "Need help? Just ask!"
        }
      ]
    }
  }'
```

### 6.2 Start Drip Campaign

```bash
curl -X POST http://localhost:8000/api/v1/campaigns/2/start \
  -H "Authorization: Bearer $TOKEN"
```

### 6.3 Monitor Sequence Execution

**Watch Celery logs:**

```
[10:00:00] Drip campaign 2: sent step 0 to contact 1
[10:01:15] Drip campaign 2: sent step 1 to contact 1 (after 0.02h delay)
[10:02:30] Drip campaign 2: sent step 2 to contact 1 (after 0.04h delay)
```

**Verify WhatsApp:** Contact receives 3 messages with delays!

✅ **PASS CRITERIA**: Drip sequence executes with correct delays

---

## 📥 Test Suite 7: Incoming Message Handling

### 7.1 Send Reply from WhatsApp

1. Open WhatsApp on your phone
2. Reply to one of the test messages
3. Send: "Thanks! Can I get more info?"

### 7.2 Verify Webhook Processing

**Watch Celery logs:**

```
[10:05:00] Received incoming message from +1234567890
[10:05:01] Processed incoming message: wamid.xxx
[10:05:02] Classified reply: intent=question, confidence=85
```

### 7.3 Check Reply Classification

```bash
# Get conversation
curl http://localhost:8000/api/v1/conversations?contact_id=1 \
  -H "Authorization: Bearer $TOKEN"
```

**Expected:** Conversation shows classification metadata

### 7.4 Verify Auto-Response

If reply was "STOP" or "unsubscribe":

```bash
# Check contact status
curl http://localhost:8000/api/v1/contacts/1 \
  -H "Authorization: Bearer $TOKEN"
```

**Expected:** `is_subscribed: false`

✅ **PASS CRITERIA**: Incoming messages processed, classified, auto-responded

---

## 📊 Test Suite 8: Analytics

### 8.1 Dashboard Statistics

```bash
curl http://localhost:8000/api/v1/analytics/dashboard \
  -H "Authorization: Bearer $TOKEN"
```

**Expected:**
```json
{
  "total_messages_sent": 10,
  "total_messages_received": 1,
  "total_contacts": 5,
  "total_campaigns": 2,
  "active_campaigns": 0,
  "avg_response_rate": 10.0,
  "today_messages": 10
}
```

### 8.2 Message Timeline

```bash
curl "http://localhost:8000/api/v1/analytics/messages/timeline?days=7" \
  -H "Authorization: Bearer $TOKEN"
```

**Expected:** Array of daily message counts

### 8.3 Hot Leads

```bash
curl "http://localhost:8000/api/v1/ai/hot-leads?threshold=60" \
  -H "Authorization: Bearer $TOKEN"
```

**Expected:** List of high-scoring leads

✅ **PASS CRITERIA**: Analytics endpoints return accurate data

---

## 🛡️ Test Suite 9: Safety Features

### 9.1 Test Number Warmup

```bash
# Check warmup status
curl http://localhost:8000/api/v1/whatsapp/warmup-status \
  -H "Authorization: Bearer $TOKEN"
```

**Expected:**
```json
{
  "warmup_active": true,
  "current_day": 1,
  "daily_limit": 20,
  "messages_sent_today": 10,
  "remaining_today": 10
}
```

### 9.2 Test Throttling

Create campaign with 150 contacts (exceeds hourly limit):

**Expected:** Only 100 messages sent per hour

### 9.3 Test Ban Risk Monitoring

**Monitor Celery Beat logs:**

```
[10:30:00] Checking ban risks for active campaigns...
[10:30:01] Campaign 1: Risk score 25/100 (LOW)
[10:30:02] All campaigns within safe limits
```

✅ **PASS CRITERIA**: Warmup enforced, throttling works, monitoring active

---

## ✅ Final Checklist

After completing all test suites, verify:

- [ ] All services start without errors
- [ ] WhatsApp connection established
- [ ] Messages sent and received
- [ ] AI features working (rewriting, classification, scoring)
- [ ] Campaigns execute successfully
- [ ] Drip sequences work with delays
- [ ] Incoming messages processed and classified
- [ ] Analytics showing correct data
- [ ] Warmup and throttling enforced
- [ ] Ban risk monitoring active
- [ ] No errors in logs
- [ ] Database updated correctly

---

## 🐛 Troubleshooting

### Issue: Celery workers not starting

**Solution:**
```bash
# Check Redis connection
redis-cli ping
# Should return: PONG

# Verify Celery can connect
celery -A app.workers.celery_app inspect ping
```

### Issue: AI features failing

**Solution:**
```bash
# Check API key
echo $OPENAI_API_KEY

# Test LLM connection
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

### Issue: WhatsApp not connecting

**Solution:**
1. Restart WhatsApp Gateway
2. Delete `apps/whatsapp-gateway/sessions/*`
3. Get new QR code and scan again

### Issue: Messages not sending

**Solution:**
```bash
# Check WhatsApp Gateway logs
cd apps/whatsapp-gateway
npm run dev

# Check Celery worker logs
celery -A app.workers.celery_app worker --loglevel=debug
```

---

## 🎉 Success!

If all tests pass, your Smart WhatsApp Agent is **fully operational**! 🚀

**Next Steps:**
1. Create real campaigns with your contact list
2. Monitor analytics and optimize
3. Deploy to production
4. Integrate with your CRM

**Questions? Check the docs:**
- [Complete Feature Guide](PR5_6_7_AI_AND_CAMPAIGNS.md)
- [API Reference](API_REFERENCE.md)
- [Troubleshooting](PR4_WHATSAPP_INTEGRATION.md#troubleshooting)
