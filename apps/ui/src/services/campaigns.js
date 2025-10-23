/**
 * Campaigns Service
 * Handles campaign management and scheduling
 */
import { get, post, put, del, patch } from './api';

/**
 * Get all campaigns with pagination and filters
 * @param {Object} params - Query parameters
 * @returns {Promise<Object>} Campaigns list with pagination
 */
export const getCampaigns = async (params = {}) => {
  try {
    const queryParams = new URLSearchParams();
    
    // Add pagination
    if (params.skip !== undefined) queryParams.append('skip', params.skip);
    if (params.limit !== undefined) queryParams.append('limit', params.limit);
    
    // Add filters
    if (params.status) queryParams.append('status', params.status);
    if (params.search) queryParams.append('search', params.search);
    
    const url = `/campaigns${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
    const response = await get(url);
    return response;
  } catch (error) {
    console.error('Get campaigns error:', error);
    throw error;
  }
};

/**
 * Get campaign by ID
 * @param {string} campaignId - Campaign ID
 * @returns {Promise<Object>} Campaign data
 */
export const getCampaign = async (campaignId) => {
  try {
    const response = await get(`/campaigns/${campaignId}`);
    return response;
  } catch (error) {
    console.error('Get campaign error:', error);
    throw error;
  }
};

/**
 * Create new campaign
 * @param {Object} campaignData - Campaign data
 * @returns {Promise<Object>} Created campaign
 */
export const createCampaign = async (campaignData) => {
  try {
    const response = await post('/campaigns', campaignData);
    return response;
  } catch (error) {
    console.error('Create campaign error:', error);
    throw error;
  }
};

/**
 * Update campaign
 * @param {string} campaignId - Campaign ID
 * @param {Object} campaignData - Campaign data to update
 * @returns {Promise<Object>} Updated campaign
 */
export const updateCampaign = async (campaignId, campaignData) => {
  try {
    const response = await put(`/campaigns/${campaignId}`, campaignData);
    return response;
  } catch (error) {
    console.error('Update campaign error:', error);
    throw error;
  }
};

/**
 * Delete campaign
 * @param {string} campaignId - Campaign ID
 * @returns {Promise<Object>} Response
 */
export const deleteCampaign = async (campaignId) => {
  try {
    const response = await del(`/campaigns/${campaignId}`);
    return response;
  } catch (error) {
    console.error('Delete campaign error:', error);
    throw error;
  }
};

/**
 * Start campaign
 * @param {string} campaignId - Campaign ID
 * @returns {Promise<Object>} Response
 */
export const startCampaign = async (campaignId) => {
  try {
    const response = await post(`/campaigns/${campaignId}/start`);
    return response;
  } catch (error) {
    console.error('Start campaign error:', error);
    throw error;
  }
};

/**
 * Pause campaign
 * @param {string} campaignId - Campaign ID
 * @returns {Promise<Object>} Response
 */
export const pauseCampaign = async (campaignId) => {
  try {
    const response = await post(`/campaigns/${campaignId}/pause`);
    return response;
  } catch (error) {
    console.error('Pause campaign error:', error);
    throw error;
  }
};

/**
 * Resume campaign
 * @param {string} campaignId - Campaign ID
 * @returns {Promise<Object>} Response
 */
export const resumeCampaign = async (campaignId) => {
  try {
    const response = await post(`/campaigns/${campaignId}/resume`);
    return response;
  } catch (error) {
    console.error('Resume campaign error:', error);
    throw error;
  }
};

/**
 * Stop campaign
 * @param {string} campaignId - Campaign ID
 * @returns {Promise<Object>} Response
 */
export const stopCampaign = async (campaignId) => {
  try {
    const response = await post(`/campaigns/${campaignId}/stop`);
    return response;
  } catch (error) {
    console.error('Stop campaign error:', error);
    throw error;
  }
};

/**
 * Get campaign statistics
 * @param {string} campaignId - Campaign ID
 * @returns {Promise<Object>} Campaign stats
 */
export const getCampaignStats = async (campaignId) => {
  try {
    const response = await get(`/campaigns/${campaignId}/stats`);
    return response;
  } catch (error) {
    console.error('Get campaign stats error:', error);
    throw error;
  }
};

/**
 * Get campaign messages
 * @param {string} campaignId - Campaign ID
 * @returns {Promise<Array>} Campaign messages
 */
export const getCampaignMessages = async (campaignId) => {
  try {
    const response = await get(`/campaigns/${campaignId}/messages`);
    return response;
  } catch (error) {
    console.error('Get campaign messages error:', error);
    throw error;
  }
};

/**
 * Test campaign (send to test contacts)
 * @param {string} campaignId - Campaign ID
 * @param {Array} testContacts - Test contact IDs
 * @returns {Promise<Object>} Test result
 */
export const testCampaign = async (campaignId, testContacts) => {
  try {
    const response = await post(`/campaigns/${campaignId}/test`, {
      contact_ids: testContacts,
    });
    return response;
  } catch (error) {
    console.error('Test campaign error:', error);
    throw error;
  }
};

/**
 * Duplicate campaign
 * @param {string} campaignId - Campaign ID
 * @returns {Promise<Object>} Duplicated campaign
 */
export const duplicateCampaign = async (campaignId) => {
  try {
    const response = await post(`/campaigns/${campaignId}/duplicate`);
    return response;
  } catch (error) {
    console.error('Duplicate campaign error:', error);
    throw error;
  }
};

export default {
  getCampaigns,
  getCampaign,
  createCampaign,
  updateCampaign,
  deleteCampaign,
  startCampaign,
  pauseCampaign,
  resumeCampaign,
  stopCampaign,
  getCampaignStats,
  getCampaignMessages,
  testCampaign,
  duplicateCampaign,
};
