/**
 * Utility functions
 */

/**
 * Random delay between min and max milliseconds
 */
export function randomDelay(min, max) {
  const delay = Math.floor(Math.random() * (max - min + 1)) + min;
  return new Promise(resolve => setTimeout(resolve, delay));
}

/**
 * Format phone number to WhatsApp format
 */
export function formatPhoneNumber(phoneNumber) {
  // Remove all non-numeric characters
  let cleaned = phoneNumber.replace(/\D/g, '');
  
  // Add country code if missing
  if (!cleaned.startsWith('1') && cleaned.length === 10) {
    cleaned = '1' + cleaned;
  }
  
  // Add @s.whatsapp.net suffix
  return cleaned + '@s.whatsapp.net';
}

/**
 * Validate phone number
 */
export function isValidPhoneNumber(phoneNumber) {
  // Basic validation - should have at least 10 digits
  const cleaned = phoneNumber.replace(/\D/g, '');
  return cleaned.length >= 10 && cleaned.length <= 15;
}

/**
 * Sleep for specified milliseconds
 */
export function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Extract phone number from WhatsApp JID
 */
export function extractPhoneNumber(jid) {
  return jid.split('@')[0];
}

/**
 * Generate unique ID
 */
export function generateId() {
  return Date.now().toString(36) + Math.random().toString(36).substr(2);
}

/**
 * Check if message is spam-like
 */
export function isSpamLike(message) {
  const spamIndicators = [
    /\b(free|win|winner|prize|claim|urgent|act now)\b/i,
    /(.)\1{4,}/, // Repeated characters
    /(https?:\/\/[^\s]+){3,}/, // Multiple URLs
    /[A-Z]{5,}/, // Excessive caps
  ];
  
  return spamIndicators.some(pattern => pattern.test(message));
}

/**
 * Sanitize message content
 */
export function sanitizeMessage(message) {
  // Remove excessive whitespace
  message = message.replace(/\s+/g, ' ').trim();
  
  // Limit length
  if (message.length > 4096) {
    message = message.substring(0, 4093) + '...';
  }
  
  return message;
}

/**
 * Calculate message sending rate
 */
export function calculateSendingRate(messagesSent, timeWindowMs) {
  const messagesPerMinute = (messagesSent / timeWindowMs) * 60000;
  return Math.round(messagesPerMinute * 100) / 100;
}

/**
 * Format error for API response
 */
export function formatError(error) {
  return {
    success: false,
    error: {
      message: error.message || 'Unknown error',
      code: error.code || 'INTERNAL_ERROR',
      details: error.details || null,
    },
  };
}

/**
 * Format success response
 */
export function formatSuccess(data, message = 'Success') {
  return {
    success: true,
    message,
    data,
  };
}
