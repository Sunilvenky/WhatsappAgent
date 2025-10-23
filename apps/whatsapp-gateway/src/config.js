/**
 * WhatsApp Gateway Configuration
 */

import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

dotenv.config();

export const config = {
  // Server
  port: parseInt(process.env.PORT || '3001', 10),
  host: process.env.HOST || '0.0.0.0',
  nodeEnv: process.env.NODE_ENV || 'development',

  // WhatsApp
  sessionsDir: path.resolve(__dirname, '..', process.env.SESSIONS_DIR || './sessions'),
  maxRetryAttempts: parseInt(process.env.MAX_RETRY_ATTEMPTS || '3', 10),
  messageDelayMin: parseInt(process.env.MESSAGE_DELAY_MIN || '1000', 10),
  messageDelayMax: parseInt(process.env.MESSAGE_DELAY_MAX || '3000', 10),

  // Webhooks
  webhookUrl: process.env.WEBHOOK_URL || 'http://localhost:8000/api/v1/webhooks/whatsapp/incoming',
  webhookSecret: process.env.WEBHOOK_SECRET || 'default_secret_change_me',

  // Rate Limiting
  rateLimitWindowMs: parseInt(process.env.RATE_LIMIT_WINDOW_MS || '60000', 10),
  rateLimitMaxRequests: parseInt(process.env.RATE_LIMIT_MAX_REQUESTS || '100', 10),
  dailyMessageLimit: parseInt(process.env.DAILY_MESSAGE_LIMIT || '1000', 10),

  // Anti-Ban Features
  enableTypingIndicator: process.env.ENABLE_TYPING_INDICATOR === 'true',
  enableReadReceipts: process.env.ENABLE_READ_RECEIPTS === 'true',
  enablePresenceUpdates: process.env.ENABLE_PRESENCE_UPDATES === 'true',
  randomDelayEnabled: process.env.RANDOM_DELAY_ENABLED === 'true',

  // Logging
  logLevel: process.env.LOG_LEVEL || 'info',
  logPretty: process.env.LOG_PRETTY === 'true',

  // Security
  apiKey: process.env.API_KEY || 'default_api_key_change_me',
  corsOrigin: (process.env.CORS_ORIGIN || 'http://localhost:3000').split(','),
};

export default config;
