/**
 * WhatsApp Gateway API Routes
 */

import express from 'express';
import WhatsAppHandler from './whatsapp-handler.js';
import logger from './logger.js';
import { formatError, formatSuccess, sanitizeMessage } from './utils.js';

const router = express.Router();

// Map to store multiple WhatsApp handler instances (one per tenant/user)
const handlers = new Map();

/**
 * Get or initialize a WhatsApp handler for a specific session
 * @param {string} sessionId - Unique ID for the session/tenant
 */
async function getHandler(sessionId) {
  if (!sessionId) return null;

  let handler = handlers.get(sessionId);
  if (!handler) {
    logger.info(`Initializing new WhatsApp session for tenant: ${sessionId}`);
    handler = new WhatsAppHandler(sessionId);
    handlers.set(sessionId, handler);
    await handler.connect();
  }
  return handler;
}

/**
 * Middleware to extract and validate session ID
 */
const sessionMiddleware = async (req, res, next) => {
  const sessionId = req.headers['x-session-id'] || req.query.session_id || 'default';

  try {
    const handler = await getHandler(sessionId);
    if (!handler) {
      return res.status(400).json(formatError({ message: 'Missing or invalid session ID' }));
    }
    req.whatsapp = handler;
    req.sessionId = sessionId;
    next();
  } catch (error) {
    logger.error(`Failed to initialize session ${sessionId}:`, error);
    res.status(500).json(formatError(error));
  }
};

// Apply session middleware to all authenticated routes
router.use(['/auth', '/messages', '/contacts', '/health'], (req, res, next) => {
  // Only apply to specific sub-routes if needed, or all for simplicity
  sessionMiddleware(req, res, next);
});

/**
 * GET /auth/qr - Get QR code for authentication
 */
router.get('/auth/qr', async (req, res) => {
  try {
    const handler = req.whatsapp;
    const qrCode = handler.getQRCode();

    if (!qrCode) {
      return res.json(formatSuccess({
        qrCode: null,
        message: 'Already authenticated or waiting for QR code',
      }));
    }

    res.json(formatSuccess({
      qrCode,
      message: 'Scan this QR code with WhatsApp',
    }));
  } catch (error) {
    logger.error('Failed to get QR code:', error);
    res.status(500).json(formatError(error));
  }
});

/**
 * GET /auth/status - Get connection status
 */
router.get('/auth/status', async (req, res) => {
  try {
    const handler = req.whatsapp;
    const status = handler.getConnectionStatus();

    res.json(formatSuccess(status));
  } catch (error) {
    logger.error('Failed to get status:', error);
    res.status(500).json(formatError(error));
  }
});

/**
 * POST /auth/logout - Logout from WhatsApp
 */
router.post('/auth/logout', async (req, res) => {
  try {
    const handler = req.whatsapp;
    await handler.logout();
    handlers.delete(req.sessionId);

    res.json(formatSuccess(null, 'Logged out successfully'));
  } catch (error) {
    logger.error('Failed to logout:', error);
    res.status(500).json(formatError(error));
  }
});

/**
 * POST /messages/send - Send a single message
 */
router.post('/messages/send', async (req, res) => {
  try {
    const { to, message, options } = req.body;

    // Validation
    if (!to || !message) {
      return res.status(400).json(formatError({
        message: 'Missing required fields: to, message',
      }));
    }

    const handler = req.whatsapp;

    if (!handler.isWhatsAppConnected()) {
      return res.status(503).json(formatError({
        message: 'WhatsApp not connected. Please scan QR code first.',
      }));
    }

    // Sanitize message
    const sanitized = sanitizeMessage(message);

    // Send message
    const result = await handler.sendMessage(to, sanitized, options || {});

    res.json(formatSuccess(result, 'Message sent successfully'));
  } catch (error) {
    logger.error('Failed to send message:', error);
    res.status(500).json(formatError(error));
  }
});

/**
 * POST /messages/bulk - Send multiple messages
 */
router.post('/messages/bulk', async (req, res) => {
  try {
    const { messages } = req.body;

    // Validation
    if (!messages || !Array.isArray(messages) || messages.length === 0) {
      return res.status(400).json(formatError({
        message: 'messages must be a non-empty array',
      }));
    }

    const handler = req.whatsapp;

    if (!handler.isWhatsAppConnected()) {
      return res.status(503).json(formatError({
        message: 'WhatsApp not connected. Please scan QR code first.',
      }));
    }

    // Sanitize all messages
    const sanitized = messages.map(msg => ({
      ...msg,
      message: sanitizeMessage(msg.message),
    }));

    // Send messages
    const results = await handler.sendBulkMessages(sanitized);

    const successCount = results.filter(r => r.success).length;
    const failedCount = results.length - successCount;

    res.json(formatSuccess({
      results,
      summary: {
        total: results.length,
        success: successCount,
        failed: failedCount,
      },
    }, `Sent ${successCount}/${results.length} messages successfully`));
  } catch (error) {
    logger.error('Failed to send bulk messages:', error);
    res.status(500).json(formatError(error));
  }
});

/**
 * GET /contacts/check/:phoneNumber - Check if contact exists on WhatsApp
 */
router.get('/contacts/check/:phoneNumber', async (req, res) => {
  try {
    const { phoneNumber } = req.params;

    const handler = req.whatsapp;

    if (!handler.isWhatsAppConnected()) {
      return res.status(503).json(formatError({
        message: 'WhatsApp not connected',
      }));
    }

    const contact = await handler.getContact(phoneNumber);

    if (!contact) {
      return res.json(formatSuccess({
        exists: false,
        number: phoneNumber,
      }));
    }

    res.json(formatSuccess(contact));
  } catch (error) {
    logger.error('Failed to check contact:', error);
    res.status(500).json(formatError(error));
  }
});

/**
 * GET /health - Health check
 */
router.get('/health', (req, res) => {
  const health = {
    status: 'ok',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    whatsappConnected: req.whatsapp ? req.whatsapp.isWhatsAppConnected() : false,
    sessionId: req.sessionId,
  };

  res.json(formatSuccess(health));
});

/**
 * GET / - API info
 */
router.get('/', (req, res) => {
  res.json({
    name: 'WhatsApp Gateway API',
    version: '1.0.0',
    description: 'Free WhatsApp messaging API using Baileys',
    endpoints: {
      auth: {
        'GET /auth/qr': 'Get QR code for authentication',
        'GET /auth/status': 'Get connection status',
        'POST /auth/logout': 'Logout from WhatsApp',
      },
      messages: {
        'POST /messages/send': 'Send a single message',
        'POST /messages/bulk': 'Send multiple messages',
      },
      contacts: {
        'GET /contacts/check/:phoneNumber': 'Check if contact exists',
      },
      system: {
        'GET /health': 'Health check',
        'GET /': 'API information',
      },
    },
  });
});

export default router;
