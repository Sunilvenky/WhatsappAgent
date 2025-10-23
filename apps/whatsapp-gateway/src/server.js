/**
 * WhatsApp Gateway Express Server
 */

import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import rateLimit from 'express-rate-limit';
import config from './config.js';
import logger from './logger.js';
import routes from './routes.js';

const app = express();

// Security middleware
app.use(helmet());

// CORS configuration
app.use(cors({
  origin: config.corsOrigin,
  credentials: true,
}));

// Rate limiting
const limiter = rateLimit({
  windowMs: config.rateLimitWindowMs,
  max: config.rateLimitMaxRequests,
  message: { error: 'Too many requests, please try again later' },
});
app.use(limiter);

// Body parsing middleware
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// Request logging middleware
app.use((req, res, next) => {
  logger.info({
    method: req.method,
    path: req.path,
    ip: req.ip,
  });
  next();
});

// API key authentication middleware (optional)
const authMiddleware = (req, res, next) => {
  // Skip auth for health and root endpoints
  if (req.path === '/health' || req.path === '/') {
    return next();
  }
  
  const apiKey = req.headers['x-api-key'] || req.query.api_key;
  
  if (config.apiKey && apiKey !== config.apiKey) {
    return res.status(401).json({
      success: false,
      error: 'Invalid API key',
    });
  }
  
  next();
};

app.use(authMiddleware);

// API routes
app.use('/', routes);

// 404 handler
app.use((req, res) => {
  res.status(404).json({
    success: false,
    error: 'Endpoint not found',
  });
});

// Error handler
app.use((err, req, res, next) => {
  logger.error('Express error:', err);
  
  res.status(err.status || 500).json({
    success: false,
    error: err.message || 'Internal server error',
  });
});

// Start server
const startServer = () => {
  app.listen(config.port, config.host, () => {
    logger.info(`🚀 WhatsApp Gateway server started on http://${config.host}:${config.port}`);
    logger.info(`Environment: ${config.nodeEnv}`);
    logger.info(`Sessions directory: ${config.sessionsDir}`);
    logger.info(`Webhook URL: ${config.webhookUrl}`);
  });
};

// Handle graceful shutdown
process.on('SIGTERM', () => {
  logger.info('SIGTERM signal received: closing HTTP server');
  process.exit(0);
});

process.on('SIGINT', () => {
  logger.info('SIGINT signal received: closing HTTP server');
  process.exit(0);
});

// Start the server
startServer();

export default app;
