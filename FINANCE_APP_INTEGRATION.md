# WhatsApp Agent - Finance App Integration

## Integration Overview

Your WhatsApp Agent API can be integrated into any application to send WhatsApp messages. This guide shows how to integrate it with a Finance application.

---

## Architecture

```
Finance App (React/Vue/Angular)
        ↓
Finance Backend (Node/Python/Java)
        ↓
WhatsApp Agent API (FastAPI)
        ↓
WhatsApp Baileys Gateway
        ↓
WhatsApp Servers
        ↓
Customer WhatsApp
```

---

## Two Integration Models

### Model 1: Pull Model (Recommended for Billing)
Finance App → periodically calls → WhatsApp Agent API
- Best for: Scheduled messages (bill reminders, payment confirmations)
- Reliability: High (you control the flow)
- Example: Send message every time a payment is made

### Model 2: Push Model (Real-time)
WhatsApp Agent → sends webhook → Finance App
- Best for: Incoming customer messages
- Reliability: Medium (depends on webhook delivery)
- Example: Customer sends payment ID, Finance app receives it

**Most systems use BOTH models.**

---

## Step 1: Setup API Authentication

### Create API Key in WhatsApp Agent

```bash
# 1. Create a tenant
curl -X POST http://129.159.227.138/api/v1/tenants \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Finance App Prod",
    "description": "Integration with Finance system"
  }'

# Response will include tenant_id

# 2. Generate API key
curl -X POST http://129.159.227.138/api/v1/tenants/{tenant_id}/api-keys \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Finance App Key",
    "permissions": ["messages:send", "contacts:read", "contacts:create"]
  }'

# Response will include api_key - SAVE THIS!
# Example: sk_live_abc123xyz789
```

### Store in Finance App

```javascript
// finance-app/.env
WHATSAPP_API_URL=http://129.159.227.138
WHATSAPP_API_KEY=sk_live_abc123xyz789
```

---

## Step 2: Install WhatsApp Service

### For Node.js/JavaScript

```bash
npm install axios
```

### Create WhatsAppService.js

```javascript
// finance-app/services/WhatsAppService.js
import axios from 'axios';

class WhatsAppService {
  constructor(apiUrl, apiKey) {
    this.apiUrl = apiUrl;
    this.apiKey = apiKey;
    this.client = axios.create({
      baseURL: apiUrl,
      headers: {
        'X-API-Key': apiKey,
        'Content-Type': 'application/json'
      }
    });
  }

  // Send text message
  async sendMessage(contactId, message) {
    try {
      const response = await this.client.post('/api/v1/messages/send', {
        contact_id: contactId,
        message_body: message,
        message_type: 'text'
      });
      return response.data;
    } catch (error) {
      console.error('Failed to send message:', error);
      throw error;
    }
  }

  // Send with media
  async sendMediaMessage(contactId, mediaUrl, caption) {
    try {
      const response = await this.client.post('/api/v1/messages/send', {
        contact_id: contactId,
        message_type: 'image',
        media_url: mediaUrl,
        caption: caption
      });
      return response.data;
    } catch (error) {
      console.error('Failed to send media:', error);
      throw error;
    }
  }

  // Create or get contact
  async upsertContact(phoneNumber, firstName, lastName, email) {
    try {
      // First try to find existing contact
      const existing = await this.client.get('/api/v1/contacts', {
        params: { phone: phoneNumber }
      });

      if (existing.data.length > 0) {
        return existing.data[0];
      }

      // Create new contact
      const response = await this.client.post('/api/v1/contacts', {
        first_name: firstName,
        last_name: lastName,
        phone_numbers: [{ number: phoneNumber }],
        email: email
      });
      return response.data;
    } catch (error) {
      console.error('Failed to upsert contact:', error);
      throw error;
    }
  }

  // Get contact by ID
  async getContact(contactId) {
    try {
      const response = await this.client.get(`/api/v1/contacts/${contactId}`);
      return response.data;
    } catch (error) {
      console.error('Failed to get contact:', error);
      throw error;
    }
  }

  // Get conversation history
  async getConversation(contactId) {
    try {
      const response = await this.client.get(
        `/api/v1/conversations/${contactId}/messages`
      );
      return response.data;
    } catch (error) {
      console.error('Failed to get conversation:', error);
      throw error;
    }
  }
}

export default WhatsAppService;
```

### Initialize Service

```javascript
// finance-app/index.js
import WhatsAppService from './services/WhatsAppService.js';

const whatsapp = new WhatsAppService(
  process.env.WHATSAPP_API_URL,
  process.env.WHATSAPP_API_KEY
);

export default whatsapp;
```

---

## Step 3: Use in Finance Features

### Payment Confirmation

```javascript
// finance-app/payments/PaymentController.js
import whatsapp from '../index.js';

export const confirmPayment = async (req, res) => {
  const { customerId, amount, transactionId } = req.body;

  try {
    // Process payment
    const payment = await Payment.create({
      customerId,
      amount,
      transactionId,
      status: 'confirmed',
      timestamp: new Date()
    });

    // Send WhatsApp confirmation
    const message = `✅ Payment Confirmed

Amount: $${amount}
Transaction ID: ${transactionId}
Date: ${new Date().toLocaleDateString()}

Thank you!`;

    await whatsapp.sendMessage(customerId, message);

    res.json({
      success: true,
      payment,
      message: 'Payment confirmed and notification sent'
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};
```

### Bill Reminder

```javascript
// finance-app/bills/BillReminder.js
import whatsapp from '../index.js';
import cron from 'node-cron';

// Run every day at 9 AM
cron.schedule('0 9 * * *', async () => {
  try {
    // Get all bills due in next 3 days
    const bills = await Bill.find({
      dueDate: {
        $gte: new Date(),
        $lte: new Date(Date.now() + 3 * 24 * 60 * 60 * 1000)
      },
      status: 'pending'
    });

    for (const bill of bills) {
      const message = `📋 Bill Reminder

Bill Amount: $${bill.amount}
Due Date: ${bill.dueDate.toLocaleDateString()}
Reference: ${bill.billId}

⚠️ Please pay before the due date to avoid penalties.`;

      await whatsapp.sendMessage(bill.customerId, message);
    }

    console.log(`Sent ${bills.length} bill reminders`);
  } catch (error) {
    console.error('Failed to send bill reminders:', error);
  }
});
```

### Late Payment Notice

```javascript
// finance-app/bills/LatePaymentNotice.js
import whatsapp from '../index.js';

export const sendLatePaymentNotice = async (billId) => {
  try {
    const bill = await Bill.findById(billId);

    const message = `⚠️ URGENT: Payment Overdue

Bill Amount: $${bill.amount}
Days Overdue: ${Math.floor(
  (Date.now() - bill.dueDate) / (1000 * 60 * 60 * 24)
)}

Please make payment immediately to:
🏦 Account: ${bill.accountNumber}
📧 Support: support@finance.com

Thank you`;

    await whatsapp.sendMessage(bill.customerId, message);
  } catch (error) {
    console.error('Failed to send late payment notice:', error);
  }
};
```

### Invoice Link

```javascript
// finance-app/invoices/SendInvoice.js
import whatsapp from '../index.js';

export const sendInvoice = async (customerId, invoiceId) => {
  try {
    const invoice = await Invoice.findById(invoiceId);
    const downloadUrl = `https://finance.app/invoices/${invoiceId}/download`;

    const message = `📄 Your Invoice is Ready

Invoice #: ${invoice.invoiceNumber}
Amount Due: $${invoice.total}
Due Date: ${invoice.dueDate.toLocaleDateString()}

📥 Download: ${downloadUrl}

Questions? Contact us at support@finance.com`;

    await whatsapp.sendMessage(customerId, message);
  } catch (error) {
    console.error('Failed to send invoice:', error);
  }
};
```

---

## Step 4: Receive Incoming Messages (Webhooks)

### Register Webhook

```bash
curl -X POST http://129.159.227.138/api/v1/webhooks/register \
  -H "X-API-Key: sk_live_abc123xyz789" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://your-finance-app.com/webhooks/whatsapp",
    "events": ["message_received", "message_delivered", "message_failed"],
    "active": true
  }'
```

### Handle Webhook in Finance App

```javascript
// finance-app/webhooks/whatsappWebhook.js
import express from 'express';
import whatsapp from '../index.js';

const router = express.Router();

// Middleware to verify webhook signature
const verifyWebhookSignature = (req, res, next) => {
  // Optional: Verify X-Webhook-Signature header
  next();
};

// Handle incoming webhook
router.post('/whatsapp', verifyWebhookSignature, async (req, res) => {
  const { event, data } = req.body;

  try {
    switch (event) {
      case 'message_received':
        await handleIncomingMessage(data);
        break;

      case 'message_delivered':
        await handleDelivery(data);
        break;

      case 'message_failed':
        await handleFailure(data);
        break;

      default:
        console.log('Unknown event:', event);
    }

    res.json({ success: true });
  } catch (error) {
    console.error('Webhook error:', error);
    res.status(500).json({ error: error.message });
  }
});

// Handle incoming message from customer
async function handleIncomingMessage(data) {
  const { contact_id, message_body, message_id } = data;

  console.log(`Received message from contact ${contact_id}: ${message_body}`);

  // Example: Customer sends payment reference
  if (message_body.match(/^PAY\d+$/)) {
    const paymentRef = message_body;
    const payment = await Payment.findOne({ reference: paymentRef });

    if (payment) {
      const reply = `✅ We found your payment!\n\nAmount: $${payment.amount}\nStatus: ${payment.status}`;
      await whatsapp.sendMessage(contact_id, reply);
    } else {
      const reply = `❌ Payment not found. Please check your reference and try again.`;
      await whatsapp.sendMessage(contact_id, reply);
    }
  }

  // Store message in database
  await Message.create({
    contact_id,
    message_body,
    message_id,
    direction: 'incoming',
    timestamp: new Date()
  });
}

// Track delivery status
async function handleDelivery(data) {
  const { message_id, delivered_at } = data;
  await Message.updateOne(
    { message_id },
    { status: 'delivered', delivered_at }
  );
}

// Handle failed messages
async function handleFailure(data) {
  const { message_id, error } = data;
  await Message.updateOne(
    { message_id },
    { status: 'failed', error }
  );
}

export default router;
```

---

## Step 5: Test Integration

### Test 1: Create Contact

```bash
curl -X POST http://YOUR_FINANCE_APP/api/contacts \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "phone": "+1234567890",
    "email": "john@example.com"
  }'
```

### Test 2: Send Payment Confirmation

```bash
curl -X POST http://YOUR_FINANCE_APP/api/payments/confirm \
  -H "Content-Type: application/json" \
  -d '{
    "customerId": 1,
    "amount": 500,
    "transactionId": "TXN123456"
  }'
```

### Test 3: Verify WhatsApp Delivery

- Check your WhatsApp for the message
- Confirm it arrived successfully
- Reply to the message
- Verify webhook received your reply in Finance App logs

---

## Step 6: Error Handling

```javascript
// Robust error handling
async function sendMessageWithRetry(contactId, message, maxRetries = 3) {
  let lastError;

  for (let i = 0; i < maxRetries; i++) {
    try {
      return await whatsapp.sendMessage(contactId, message);
    } catch (error) {
      lastError = error;
      console.warn(`Attempt ${i + 1} failed, retrying...`);
      
      // Wait before retry (exponential backoff)
      await new Promise(resolve => 
        setTimeout(resolve, Math.pow(2, i) * 1000)
      );
    }
  }

  throw new Error(`Failed after ${maxRetries} attempts: ${lastError.message}`);
}
```

---

## Step 7: Database Schema

Add to Finance App database:

```sql
-- Store WhatsApp contacts
CREATE TABLE whatsapp_contacts (
  id INTEGER PRIMARY KEY,
  customer_id INTEGER,
  whatsapp_contact_id INTEGER,
  phone_number TEXT,
  verified BOOLEAN DEFAULT false,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(customer_id, phone_number)
);

-- Track WhatsApp messages
CREATE TABLE whatsapp_messages (
  id INTEGER PRIMARY KEY,
  customer_id INTEGER,
  message_body TEXT,
  direction ENUM('incoming', 'outgoing'),
  status ENUM('pending', 'sent', 'delivered', 'read', 'failed'),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  delivered_at TIMESTAMP,
  error_message TEXT
);

-- Store webhooks for logging/debugging
CREATE TABLE webhook_logs (
  id INTEGER PRIMARY KEY,
  event_type TEXT,
  payload JSON,
  processed BOOLEAN DEFAULT false,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## Step 8: Monitor & Debug

### Enable Logging

```javascript
import winston from 'winston';

const logger = winston.createLogger({
  level: 'info',
  format: winston.format.json(),
  transports: [
    new winston.transports.File({ filename: 'error.log', level: 'error' }),
    new winston.transports.File({ filename: 'combined.log' }),
    new winston.transports.Console()
  ]
});

// Log all WhatsApp operations
const loggedWhatsApp = {
  sendMessage: async (...args) => {
    logger.info('Sending message', { args });
    return whatsapp.sendMessage(...args);
  }
};
```

### Monitor WhatsApp Agent

```bash
# Check API health
curl http://129.159.227.138/api/v1/health

# View API docs
open http://129.159.227.138/docs

# Check database
curl http://129.159.227.138:8080

# View logs
ssh ubuntu@129.159.227.138
docker-compose logs -f api
```

---

## Production Checklist

- [ ] API key stored securely in .env
- [ ] Error handling implemented
- [ ] Retry logic for failed messages
- [ ] Webhook endpoint secured
- [ ] Logging enabled
- [ ] Database schema created
- [ ] Testing completed
- [ ] Rate limiting considered
- [ ] Monitoring setup
- [ ] Backup/fallback plan (email, SMS)

---

## Troubleshooting

### "API key not found"
- Verify API key in .env
- Check key hasn't expired
- Generate new key if needed

### "Contact not found"
- Verify contact_id exists
- Check contact is in same tenant
- Create contact first if new

### "Message not delivering"
- Verify Baileys is connected
- Check phone number format (+1234567890)
- View logs: docker-compose logs api

### "Webhook not receiving"
- Verify webhook URL is public
- Check firewall allows HTTPS
- Add logging to webhook handler
- Test manually: curl -X POST https://your-url/webhook

---

## Next Steps

1. ✅ Setup integration
2. ✅ Test with test contact
3. → Deploy to production
4. → Monitor messages
5. → Add more features (AI responses, scheduling, etc.)

**Questions?** Check the main README.md or API docs at http://129.159.227.138/docs
