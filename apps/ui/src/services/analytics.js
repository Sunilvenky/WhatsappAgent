/**
 * Analytics Service
 * Handles analytics data and reporting
 */
import { get } from './api';

/**
 * Get dashboard overview statistics
 * @returns {Promise<Object>} Dashboard stats
 */
export const getDashboardStats = async () => {
  try {
    const response = await get('/analytics/dashboard');
    return response;
  } catch (error) {
    console.error('Get dashboard stats error:', error);
    throw error;
  }
};

/**
 * Get message statistics
 * @param {Object} params - Query parameters (start_date, end_date, etc.)
 * @returns {Promise<Object>} Message stats
 */
export const getMessageStats = async (params = {}) => {
  try {
    const queryParams = new URLSearchParams();
    if (params.start_date) queryParams.append('start_date', params.start_date);
    if (params.end_date) queryParams.append('end_date', params.end_date);
    if (params.groupBy) queryParams.append('group_by', params.groupBy);
    
    const url = `/analytics/messages${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
    const response = await get(url);
    return response;
  } catch (error) {
    console.error('Get message stats error:', error);
    throw error;
  }
};

/**
 * Get campaign performance statistics
 * @param {Object} params - Query parameters
 * @returns {Promise<Object>} Campaign performance data
 */
export const getCampaignPerformance = async (params = {}) => {
  try {
    const queryParams = new URLSearchParams();
    if (params.campaign_id) queryParams.append('campaign_id', params.campaign_id);
    if (params.start_date) queryParams.append('start_date', params.start_date);
    if (params.end_date) queryParams.append('end_date', params.end_date);
    
    const url = `/analytics/campaigns${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
    const response = await get(url);
    return response;
  } catch (error) {
    console.error('Get campaign performance error:', error);
    throw error;
  }
};

/**
 * Get conversation statistics
 * @param {Object} params - Query parameters
 * @returns {Promise<Object>} Conversation stats
 */
export const getConversationStats = async (params = {}) => {
  try {
    const queryParams = new URLSearchParams();
    if (params.start_date) queryParams.append('start_date', params.start_date);
    if (params.end_date) queryParams.append('end_date', params.end_date);
    
    const url = `/analytics/conversations${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
    const response = await get(url);
    return response;
  } catch (error) {
    console.error('Get conversation stats error:', error);
    throw error;
  }
};

/**
 * Get lead statistics
 * @param {Object} params - Query parameters
 * @returns {Promise<Object>} Lead stats
 */
export const getLeadStats = async (params = {}) => {
  try {
    const queryParams = new URLSearchParams();
    if (params.start_date) queryParams.append('start_date', params.start_date);
    if (params.end_date) queryParams.append('end_date', params.end_date);
    if (params.stage) queryParams.append('stage', params.stage);
    
    const url = `/analytics/leads${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
    const response = await get(url);
    return response;
  } catch (error) {
    console.error('Get lead stats error:', error);
    throw error;
  }
};

/**
 * Get response time analytics
 * @param {Object} params - Query parameters
 * @returns {Promise<Object>} Response time data
 */
export const getResponseTimeStats = async (params = {}) => {
  try {
    const queryParams = new URLSearchParams();
    if (params.start_date) queryParams.append('start_date', params.start_date);
    if (params.end_date) queryParams.append('end_date', params.end_date);
    
    const url = `/analytics/response-times${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
    const response = await get(url);
    return response;
  } catch (error) {
    console.error('Get response time stats error:', error);
    throw error;
  }
};

/**
 * Get engagement metrics
 * @param {Object} params - Query parameters
 * @returns {Promise<Object>} Engagement metrics
 */
export const getEngagementMetrics = async (params = {}) => {
  try {
    const queryParams = new URLSearchParams();
    if (params.start_date) queryParams.append('start_date', params.start_date);
    if (params.end_date) queryParams.append('end_date', params.end_date);
    
    const url = `/analytics/engagement${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
    const response = await get(url);
    return response;
  } catch (error) {
    console.error('Get engagement metrics error:', error);
    throw error;
  }
};

/**
 * Get sentiment analysis data
 * @param {Object} params - Query parameters
 * @returns {Promise<Object>} Sentiment data
 */
export const getSentimentAnalysis = async (params = {}) => {
  try {
    const queryParams = new URLSearchParams();
    if (params.start_date) queryParams.append('start_date', params.start_date);
    if (params.end_date) queryParams.append('end_date', params.end_date);
    if (params.contact_id) queryParams.append('contact_id', params.contact_id);
    
    const url = `/analytics/sentiment${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
    const response = await get(url);
    return response;
  } catch (error) {
    console.error('Get sentiment analysis error:', error);
    throw error;
  }
};

/**
 * Get WhatsApp connection status
 * @returns {Promise<Object>} Connection status
 */
export const getWhatsAppStatus = async () => {
  try {
    const response = await get('/whatsapp/status');
    return response;
  } catch (error) {
    console.error('Get WhatsApp status error:', error);
    throw error;
  }
};

/**
 * Export analytics report
 * @param {Object} params - Export parameters
 * @returns {Promise<Blob>} Report file
 */
export const exportReport = async (params = {}) => {
  try {
    const queryParams = new URLSearchParams();
    if (params.report_type) queryParams.append('report_type', params.report_type);
    if (params.start_date) queryParams.append('start_date', params.start_date);
    if (params.end_date) queryParams.append('end_date', params.end_date);
    if (params.format) queryParams.append('format', params.format);
    
    const url = `/analytics/export${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
    const response = await get(url, { responseType: 'blob' });
    return response;
  } catch (error) {
    console.error('Export report error:', error);
    throw error;
  }
};

/**
 * Get user activity timeline
 * @param {Object} params - Query parameters
 * @returns {Promise<Array>} Activity timeline
 */
export const getActivityTimeline = async (params = {}) => {
  try {
    const queryParams = new URLSearchParams();
    if (params.start_date) queryParams.append('start_date', params.start_date);
    if (params.end_date) queryParams.append('end_date', params.end_date);
    if (params.limit) queryParams.append('limit', params.limit);
    
    const url = `/analytics/activity${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
    const response = await get(url);
    return response;
  } catch (error) {
    console.error('Get activity timeline error:', error);
    throw error;
  }
};

export default {
  getDashboardStats,
  getMessageStats,
  getCampaignPerformance,
  getConversationStats,
  getLeadStats,
  getResponseTimeStats,
  getEngagementMetrics,
  getSentimentAnalysis,
  getWhatsAppStatus,
  exportReport,
  getActivityTimeline,
};
