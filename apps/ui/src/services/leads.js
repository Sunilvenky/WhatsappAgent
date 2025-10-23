/**
 * Leads Service
 * Handles lead management and scoring
 */
import { get, post, put, del } from './api';

/**
 * Get all leads with pagination and filters
 * @param {Object} params - Query parameters
 * @returns {Promise<Object>} Leads list
 */
export const getLeads = async (params = {}) => {
  try {
    const queryParams = new URLSearchParams();
    if (params.skip !== undefined) queryParams.append('skip', params.skip);
    if (params.limit !== undefined) queryParams.append('limit', params.limit);
    if (params.stage) queryParams.append('stage', params.stage);
    if (params.min_score !== undefined) queryParams.append('min_score', params.min_score);
    if (params.max_score !== undefined) queryParams.append('max_score', params.max_score);
    if (params.search) queryParams.append('search', params.search);
    
    const url = `/leads${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
    const response = await get(url);
    return response;
  } catch (error) {
    console.error('Get leads error:', error);
    throw error;
  }
};

/**
 * Get lead by ID
 * @param {string} leadId - Lead ID
 * @returns {Promise<Object>} Lead data
 */
export const getLead = async (leadId) => {
  try {
    const response = await get(`/leads/${leadId}`);
    return response;
  } catch (error) {
    console.error('Get lead error:', error);
    throw error;
  }
};

/**
 * Create new lead
 * @param {Object} leadData - Lead data
 * @returns {Promise<Object>} Created lead
 */
export const createLead = async (leadData) => {
  try {
    const response = await post('/leads', leadData);
    return response;
  } catch (error) {
    console.error('Create lead error:', error);
    throw error;
  }
};

/**
 * Update lead
 * @param {string} leadId - Lead ID
 * @param {Object} leadData - Lead data to update
 * @returns {Promise<Object>} Updated lead
 */
export const updateLead = async (leadId, leadData) => {
  try {
    const response = await put(`/leads/${leadId}`, leadData);
    return response;
  } catch (error) {
    console.error('Update lead error:', error);
    throw error;
  }
};

/**
 * Delete lead
 * @param {string} leadId - Lead ID
 * @returns {Promise<Object>} Response
 */
export const deleteLead = async (leadId) => {
  try {
    const response = await del(`/leads/${leadId}`);
    return response;
  } catch (error) {
    console.error('Delete lead error:', error);
    throw error;
  }
};

/**
 * Update lead stage
 * @param {string} leadId - Lead ID
 * @param {string} stage - New stage
 * @returns {Promise<Object>} Updated lead
 */
export const updateLeadStage = async (leadId, stage) => {
  try {
    const response = await put(`/leads/${leadId}/stage`, { stage });
    return response;
  } catch (error) {
    console.error('Update lead stage error:', error);
    throw error;
  }
};

/**
 * Score lead using ML model
 * @param {string} leadId - Lead ID
 * @returns {Promise<Object>} Lead with updated score
 */
export const scoreLead = async (leadId) => {
  try {
    const response = await post(`/leads/${leadId}/score`);
    return response;
  } catch (error) {
    console.error('Score lead error:', error);
    throw error;
  }
};

/**
 * Bulk score leads
 * @param {Array} leadIds - Array of lead IDs
 * @returns {Promise<Object>} Scoring results
 */
export const bulkScoreLeads = async (leadIds) => {
  try {
    const response = await post('/leads/bulk-score', { lead_ids: leadIds });
    return response;
  } catch (error) {
    console.error('Bulk score leads error:', error);
    throw error;
  }
};

/**
 * Add note to lead
 * @param {string} leadId - Lead ID
 * @param {string} note - Note text
 * @returns {Promise<Object>} Updated lead
 */
export const addLeadNote = async (leadId, note) => {
  try {
    const response = await post(`/leads/${leadId}/notes`, { note });
    return response;
  } catch (error) {
    console.error('Add lead note error:', error);
    throw error;
  }
};

/**
 * Get lead activity history
 * @param {string} leadId - Lead ID
 * @returns {Promise<Array>} Activity history
 */
export const getLeadActivity = async (leadId) => {
  try {
    const response = await get(`/leads/${leadId}/activity`);
    return response;
  } catch (error) {
    console.error('Get lead activity error:', error);
    throw error;
  }
};

/**
 * Convert lead to customer
 * @param {string} leadId - Lead ID
 * @returns {Promise<Object>} Response
 */
export const convertLead = async (leadId) => {
  try {
    const response = await post(`/leads/${leadId}/convert`);
    return response;
  } catch (error) {
    console.error('Convert lead error:', error);
    throw error;
  }
};

/**
 * Get lead funnel analytics
 * @returns {Promise<Object>} Funnel data
 */
export const getLeadFunnel = async () => {
  try {
    const response = await get('/leads/funnel');
    return response;
  } catch (error) {
    console.error('Get lead funnel error:', error);
    throw error;
  }
};

export default {
  getLeads,
  getLead,
  createLead,
  updateLead,
  deleteLead,
  updateLeadStage,
  scoreLead,
  bulkScoreLeads,
  addLeadNote,
  getLeadActivity,
  convertLead,
  getLeadFunnel,
};
