# WhatsApp Gateway Service

Free WhatsApp messaging API using Baileys - No Meta Cloud API required!

## Features

- ✅ **100% Free** - No Meta Cloud API costs
- ✅ **Direct Protocol** - Connects directly to WhatsApp servers
- ✅ **No Browser** - Runs as lightweight Node.js service
- ✅ **Session Persistence** - Login once, stay connected
- ✅ **Anti-Ban Features** - Rate limiting, random delays, human-like behavior
- ✅ **REST API** - Easy integration with any application
- ✅ **Webhook Support** - Real-time incoming message notifications
- ✅ **Bulk Messaging** - Send multiple messages with throttling

## Quick Start

### Prerequisites

- Node.js 18+ 
- npm or yarn

### Installation

```bash
# Install dependencies
npm install

# Copy environment file
cp .env.example .env

# Edit .env with your configuration

# Start server
npm start
```

The server will start on `http://localhost:3001`

### Docker

```bash
# Build image
docker build -t whatsapp-gateway .

# Run container
docker run -d -p 3001:3001 \
  -v $(pwd)/sessions:/app/sessions \
  --env-file .env \
  whatsapp-gateway
```

## API Endpoints

### Authentication

#### Get QR Code
```bash
GET /auth/qr
```

Returns QR code (base64 data URL) to scan with WhatsApp mobile app.

**Response:**
```json
{
  "success": true,
  "data": {
    "qrCode": "data:image/png;base64,..."
  }
}
```

#### Check Connection Status
```bash
GET /auth/status
```

**Response:**
```json
{
  "success": true,
  "data": {
    "status": "connected",
    "isConnected": true,
    "sessionId": "default",
    "messagesSentToday": 45,
    "dailyLimit": 1000
  }
}
```

#### Logout
```bash
POST /auth/logout
```

### Messages

#### Send Single Message
```bash
POST /messages/send
Content-Type: application/json

{
  "to": "+919900990099",
  "message": "Hello from WhatsApp Gateway!"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "messageId": "3EB0C8D5E9F...",
    "timestamp": 1698076800
  }
}
```

#### Send Bulk Messages
```bash
POST /messages/bulk
Content-Type: application/json

{
  "messages": [
    {
      "to": "+919900990099",
      "message": "Hello User 1!"
    },
    {
      "to": "+14155552671",
      "message": "Hello User 2!"
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "results": [
      {
        "to": "+919900990099",
        "success": true,
        "messageId": "3EB0..."
      },
      {
        "to": "+14155552671",
        "success": true,
        "messageId": "7AC1..."
      }
    ],
    "summary": {
      "total": 2,
      "success": 2,
      "failed": 0
    }
  }
}
```

### Contacts

#### Check if Contact Exists
```bash
GET /contacts/check/+919900990099
```

**Response:**
```json
{
  "success": true,
  "data": {
    "exists": true,
    "jid": "919900990099@s.whatsapp.net",
    "number": "+919900990099"
  }
}
```

### Health Check

```bash
GET /health
```

**Response:**
```json
{
  "success": true,
  "data": {
    "status": "ok",
    "timestamp": "2025-10-23T10:30:00.000Z",
    "uptime": 3600,
    "whatsappConnected": true
  }
}
```

## Configuration

All configuration is done via environment variables (`.env` file):

```env
# Server
PORT=3001
HOST=0.0.0.0
NODE_ENV=production

# WhatsApp
SESSIONS_DIR=./sessions
MAX_RETRY_ATTEMPTS=3
MESSAGE_DELAY_MIN=1000
MESSAGE_DELAY_MAX=3000

# Webhooks
WEBHOOK_URL=http://your-api:8000/api/v1/webhooks/whatsapp/incoming
WEBHOOK_SECRET=your_webhook_secret

# Rate Limiting
DAILY_MESSAGE_LIMIT=1000

# Anti-Ban Features
ENABLE_TYPING_INDICATOR=true
ENABLE_READ_RECEIPTS=true
RANDOM_DELAY_ENABLED=true

# Security
API_KEY=your_api_key_here
CORS_ORIGIN=http://localhost:3000,http://localhost:8000
```

## Webhooks

The gateway sends incoming messages to your webhook URL:

```json
{
  "id": "3EB0C8D5E9F...",
  "from": "919900990099@s.whatsapp.net",
  "timestamp": 1698076800,
  "message": "This is a reply from customer",
  "type": "conversation",
  "sessionId": "default"
}
```

Configure your webhook endpoint to receive:
- Incoming messages
- Message status updates (sent, delivered, read)

## Anti-Ban Features

The gateway includes several features to prevent WhatsApp bans:

- **Random Delays**: 1-3 seconds between messages
- **Daily Limits**: Configurable message limit per day
- **Typing Indicators**: Simulates human typing
- **Read Receipts**: Natural message flow
- **Rate Limiting**: Prevents spam detection
- **Message Variation**: Use AI to rewrite messages (in parent app)

## Security

### API Key Authentication

All requests (except `/health` and `/`) require API key:

```bash
curl -H "X-API-Key: your_api_key_here" \
  http://localhost:3001/auth/status
```

### Webhook Secret

Webhook calls include secret for verification:

```python
# Verify webhook authenticity
secret = request.headers.get('X-Webhook-Secret')
if secret != os.getenv('WEBHOOK_SECRET'):
    return Response(status=401)
```

## Scaling

### Multiple Phone Numbers

Run multiple gateway instances with different sessions:

```bash
# Instance 1
docker run -d -p 3001:3001 \
  -e SESSION_ID=phone1 \
  -v ./sessions/phone1:/app/sessions \
  whatsapp-gateway

# Instance 2
docker run -d -p 3002:3001 \
  -e SESSION_ID=phone2 \
  -v ./sessions/phone2:/app/sessions \
  whatsapp-gateway
```

### Load Balancing

Use nginx or HAProxy to distribute load across multiple instances.

## Troubleshooting

### QR Code Not Appearing

1. Check if already logged in: `GET /auth/status`
2. Logout and try again: `POST /auth/logout`
3. Check logs for connection errors

### Messages Not Sending

1. Verify connection: `GET /auth/status`
2. Check daily limit not exceeded
3. Verify phone number format (+countrycode + number)
4. Check logs for detailed error messages

### Connection Keeps Dropping

1. Ensure stable internet connection
2. Check if WhatsApp Web is logged in elsewhere
3. Verify session files are persisted correctly
4. Check for WhatsApp server issues

## Development

```bash
# Install dependencies
npm install

# Run in development mode with auto-reload
npm run dev

# Run tests
npm test
```

## License

MIT

## Support

For issues and questions, please check the main project documentation.
