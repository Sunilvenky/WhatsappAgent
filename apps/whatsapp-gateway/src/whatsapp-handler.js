/**
 * WhatsApp Connection Handler using Baileys
 */

import * as baileys from '@whiskeysockets/baileys';
import { Boom } from '@hapi/boom';
import qrcode from 'qrcode';
import fs from 'fs';
import path from 'path';
import axios from 'axios';
import config from './config.js';
import logger from './logger.js';
import { randomDelay, formatPhoneNumber, isValidPhoneNumber } from './utils.js';

// Baileys imports interop
const makeWASocket = baileys.default?.default || baileys.default || baileys.makeWASocket || baileys;
const useMultiFileAuthState = baileys.useMultiFileAuthState || baileys.default?.useMultiFileAuthState;
const fetchLatestBaileysVersion = baileys.fetchLatestBaileysVersion || baileys.default?.fetchLatestBaileysVersion;
const DisconnectReason = baileys.DisconnectReason || baileys.default?.DisconnectReason;
const makeCacheableSignalKeyStore = baileys.makeCacheableSignalKeyStore || baileys.default?.makeCacheableSignalKeyStore;
const makeInMemoryStore = baileys.makeInMemoryStore || baileys.default?.makeInMemoryStore;

class WhatsAppHandler {
  constructor(sessionId = 'default') {
    this.sessionId = sessionId;
    this.sessionDir = path.join(config.sessionsDir, sessionId);
    this.socket = null;
    this.qrCode = null;
    this.isConnected = false;
    this.connectionStatus = 'disconnected';
    this.messagesSentToday = 0;
    this.lastResetDate = new Date().toDateString();
    this.store = null;

    // Ensure session directory exists
    if (!fs.existsSync(this.sessionDir)) {
      fs.mkdirSync(this.sessionDir, { recursive: true });
    }
  }

  /**
   * Initialize WhatsApp connection
   */
  async connect() {
    try {
      logger.info(`Initializing WhatsApp connection for session: ${this.sessionId}`);

      // Get latest Baileys version
      let version = [2, 3000, 1015901307];
      try {
        if (typeof fetchLatestBaileysVersion === 'function') {
          const latest = await fetchLatestBaileysVersion();
          version = latest.version;
        }
      } catch (e) {
        logger.warn('Failed to fetch latest Baileys version, using fallback');
      }

      // Load auth state
      const { state, saveCreds } = await useMultiFileAuthState(this.sessionDir);

      // Create in-memory store for chats
      if (typeof makeInMemoryStore === 'function') {
        this.store = makeInMemoryStore({});
        const storePath = path.join(this.sessionDir, 'store.json');
        if (fs.existsSync(storePath)) {
          try {
            this.store.readFromFile(storePath);
          } catch (e) {
            logger.warn('Failed to read store file', e);
          }
        }

        // Save store every 10 seconds
        setInterval(() => {
          try {
            this.store.writeToFile(storePath);
          } catch (e) {
            // Silently ignore store save errors
          }
        }, 10000);
      }

      // Create socket connection
      this.socket = makeWASocket({
        version,
        auth: {
          creds: state.creds,
          keys: typeof makeCacheableSignalKeyStore === 'function' ? makeCacheableSignalKeyStore(state.keys, logger) : state.keys,
        },
        printQRInTerminal: false,
        browser: ['WhatsApp Agent', 'Chrome', '1.0.0'],
        generateHighQualityLinkPreview: true,
        syncFullHistory: false,
        markOnlineOnConnect: config.enablePresenceUpdates,
        logger,
      });

      // Bind store to socket
      if (this.store) {
        this.store.bind(this.socket.ev);
      }

      // Handle connection updates
      this.socket.ev.on('connection.update', async (update) => {
        await this.handleConnectionUpdate(update, saveCreds);
      });

      // Handle credentials update
      this.socket.ev.on('creds.update', saveCreds);

      // Handle incoming messages
      this.socket.ev.on('messages.upsert', async (m) => {
        await this.handleIncomingMessages(m);
      });

      // Handle message updates (delivery, read receipts)
      this.socket.ev.on('messages.update', async (updates) => {
        await this.handleMessageUpdates(updates);
      });

      logger.info('WhatsApp handler initialized successfully');
    } catch (error) {
      logger.error('Failed to initialize WhatsApp connection:', error);
      throw error;
    }
  }

  /**
   * Handle connection updates
   */
  async handleConnectionUpdate(update, saveCreds) {
    const { connection, lastDisconnect, qr } = update;

    // Handle QR code
    if (qr) {
      this.qrCode = await qrcode.toDataURL(qr);
      this.connectionStatus = 'qr_ready';
      logger.info('QR Code generated, scan to authenticate');
    }

    // Handle connection state
    if (connection === 'close') {
      const statusCode = lastDisconnect?.error?.output?.statusCode;
      const shouldReconnect = statusCode !== DisconnectReason.loggedOut;

      logger.info('Connection closed', {
        shouldReconnect,
        statusCode,
      });

      if (shouldReconnect) {
        logger.info('Reconnecting...');
        // Add a delay before reconnecting to avoid spam
        setTimeout(() => this.connect(), 5000);
      } else {
        this.isConnected = false;
        this.connectionStatus = 'logged_out';
        this.qrCode = null;
      }
    } else if (connection === 'open') {
      this.isConnected = true;
      this.connectionStatus = 'connected';
      this.qrCode = null;
      logger.info('WhatsApp connection established successfully');
    } else if (connection === 'connecting') {
      this.connectionStatus = 'connecting';
      logger.info('Connecting to WhatsApp...');
    }
  }

  /**
   * Handle incoming messages
   */
  async handleIncomingMessages(m) {
    const messages = m.messages;

    for (const message of messages) {
      // Skip if message is from me
      if (message.key.fromMe) continue;

      const messageContent = message.message?.conversation ||
        message.message?.extendedTextMessage?.text ||
        '';

      const messageData = {
        id: message.key.id,
        from: message.key.remoteJid,
        timestamp: message.messageTimestamp,
        message: messageContent,
        type: Object.keys(message.message || {})[0],
        sessionId: this.sessionId,
      };

      logger.info('Incoming message received:', messageData);

      // Send to webhook
      await this.sendToWebhook(messageData);
    }
  }

  /**
   * Handle message status updates
   */
  async handleMessageUpdates(updates) {
    for (const update of updates) {
      const status = update.update?.status;
      if (status) {
        logger.info('Message status update:', {
          id: update.key.id,
          status,
        });

        // Send status update to webhook
        await this.sendToWebhook({
          event: 'message_status',
          messageId: update.key.id,
          status,
          sessionId: this.sessionId,
        });
      }
    }
  }

  /**
   * Send message
   */
  async sendMessage(to, message, options = {}) {
    try {
      if (!this.isConnected) {
        throw new Error('WhatsApp not connected');
      }

      // Validate phone number
      const formattedNumber = formatPhoneNumber(to);
      if (!isValidPhoneNumber(formattedNumber)) {
        throw new Error(`Invalid phone number: ${to}`);
      }

      // Check daily limit
      this.checkDailyLimit();

      // Apply random delay for anti-ban
      if (config.randomDelayEnabled) {
        await randomDelay(config.messageDelayMin, config.messageDelayMax);
      }

      // Send typing indicator
      if (config.enableTypingIndicator) {
        await this.socket.sendPresenceUpdate('composing', formattedNumber);
        await randomDelay(1000, 2000);
      }

      // Send message
      const result = await this.socket.sendMessage(formattedNumber, {
        text: message,
        ...options,
      });

      // Send read receipt
      if (config.enableReadReceipts) {
        await this.socket.sendPresenceUpdate('available', formattedNumber);
      }

      // Increment counter
      this.messagesSentToday++;

      logger.info('Message sent successfully:', {
        to: formattedNumber,
        messageId: result.key.id,
      });

      return {
        success: true,
        messageId: result.key.id,
        timestamp: result.messageTimestamp,
      };
    } catch (error) {
      logger.error('Failed to send message:', error);
      throw error;
    }
  }

  /**
   * Send bulk messages
   */
  async sendBulkMessages(messages) {
    const results = [];

    for (const msg of messages) {
      try {
        const result = await this.sendMessage(msg.to, msg.message, msg.options || {});
        results.push({
          to: msg.to,
          ...result,
        });
      } catch (error) {
        results.push({
          to: msg.to,
          success: false,
          error: error.message,
        });
      }

      // Additional delay between messages
      if (config.randomDelayEnabled) {
        await randomDelay(2000, 5000);
      }
    }

    return results;
  }

  /**
   * Check if connected
   */
  isWhatsAppConnected() {
    return this.isConnected;
  }

  /**
   * Get QR code
   */
  getQRCode() {
    return this.qrCode;
  }

  /**
   * Get connection status
   */
  getConnectionStatus() {
    return {
      status: this.connectionStatus,
      isConnected: this.isConnected,
      sessionId: this.sessionId,
      messagesSentToday: this.messagesSentToday,
      dailyLimit: config.dailyMessageLimit,
    };
  }

  /**
   * Logout
   */
  async logout() {
    try {
      if (this.socket) {
        await this.socket.logout();
        this.isConnected = false;
        this.connectionStatus = 'logged_out';
        logger.info('Logged out successfully');
      }
    } catch (error) {
      logger.error('Failed to logout:', error);
      throw error;
    }
  }

  /**
   * Check daily message limit
   */
  checkDailyLimit() {
    const today = new Date().toDateString();

    // Reset counter if it's a new day
    if (this.lastResetDate !== today) {
      this.messagesSentToday = 0;
      this.lastResetDate = today;
    }

    // Check limit
    if (this.messagesSentToday >= config.dailyMessageLimit) {
      throw new Error(`Daily message limit reached: ${config.dailyMessageLimit}`);
    }
  }

  /**
   * Send data to webhook
   */
  async sendToWebhook(data) {
    try {
      if (!config.webhookUrl) {
        return;
      }

      await axios.post(config.webhookUrl, data, {
        headers: {
          'Content-Type': 'application/json',
          'X-Webhook-Secret': config.webhookSecret,
        },
        timeout: 5000,
      });

      logger.debug('Webhook notification sent successfully');
    } catch (error) {
      logger.error('Failed to send webhook:', error.message);
      // Don't throw - webhook failures shouldn't stop message processing
    }
  }

  /**
   * Get contact info
   */
  async getContact(phoneNumber) {
    try {
      const formattedNumber = formatPhoneNumber(phoneNumber);
      const [contact] = await this.socket.onWhatsApp(formattedNumber);

      if (!contact) {
        return null;
      }

      return {
        exists: contact.exists,
        jid: contact.jid,
        number: phoneNumber,
      };
    } catch (error) {
      logger.error('Failed to get contact:', error);
      return null;
    }
  }
}

export default WhatsAppHandler;
