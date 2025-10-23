/**
 * Conversations Service
 * Handles conversation and message operations
 */
import { get, post, put, del } from './api';

/**
 * Get all conversations with pagination
 * @param {Object} params - Query parameters
 * @returns {Promise<Object>} Conversations list
 */
export const getConversations = async (params = {}) => {
  try {
    const queryParams = new URLSearchParams();
    if (params.skip !== undefined) queryParams.append('skip', params.skip);
    if (params.limit !== undefined) queryParams.append('limit', params.limit);
    if (params.status) queryParams.append('status', params.status);
    if (params.contact_id) queryParams.append('contact_id', params.contact_id);
    
    const url = `/conversations${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
    const response = await get(url);
    return response;
  } catch (error) {
    console.error('Get conversations error:', error);
    throw error;
  }
};

/**
 * Get conversation by ID
 * @param {string} conversationId - Conversation ID
 * @returns {Promise<Object>} Conversation data
 */
export const getConversation = async (conversationId) => {
  try {
    const response = await get(`/conversations/${conversationId}`);
    return response;
  } catch (error) {
    console.error('Get conversation error:', error);
    throw error;
  }
};

/**
 * Get conversation messages
 * @param {string} conversationId - Conversation ID
 * @param {Object} params - Query parameters
 * @returns {Promise<Array>} Messages list
 */
export const getConversationMessages = async (conversationId, params = {}) => {
  try {
    const queryParams = new URLSearchParams();
    if (params.skip !== undefined) queryParams.append('skip', params.skip);
    if (params.limit !== undefined) queryParams.append('limit', params.limit);
    
    const url = `/conversations/${conversationId}/messages${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
    const response = await get(url);
    return response;
  } catch (error) {
    console.error('Get conversation messages error:', error);
    throw error;
  }
};

/**
 * Send message in conversation
 * @param {string} conversationId - Conversation ID
 * @param {Object} messageData - Message data
 * @returns {Promise<Object>} Sent message
 */
export const sendMessage = async (conversationId, messageData) => {
  try {
    const response = await post(`/conversations/${conversationId}/messages`, messageData);
    return response;
  } catch (error) {
    console.error('Send message error:', error);
    throw error;
  }
};

/**
 * Update conversation status
 * @param {string} conversationId - Conversation ID
 * @param {string} status - New status
 * @returns {Promise<Object>} Updated conversation
 */
export const updateConversationStatus = async (conversationId, status) => {
  try {
    const response = await put(`/conversations/${conversationId}/status`, { status });
    return response;
  } catch (error) {
    console.error('Update conversation status error:', error);
    throw error;
  }
};

/**
 * Assign conversation to user
 * @param {string} conversationId - Conversation ID
 * @param {string} userId - User ID to assign to
 * @returns {Promise<Object>} Updated conversation
 */
export const assignConversation = async (conversationId, userId) => {
  try {
    const response = await put(`/conversations/${conversationId}/assign`, { user_id: userId });
    return response;
  } catch (error) {
    console.error('Assign conversation error:', error);
    throw error;
  }
};

/**
 * Mark conversation as read
 * @param {string} conversationId - Conversation ID
 * @returns {Promise<Object>} Response
 */
export const markAsRead = async (conversationId) => {
  try {
    const response = await post(`/conversations/${conversationId}/read`);
    return response;
  } catch (error) {
    console.error('Mark as read error:', error);
    throw error;
  }
};

/**
 * Search messages
 * @param {string} query - Search query
 * @returns {Promise<Array>} Matching messages
 */
export const searchMessages = async (query) => {
  try {
    const response = await get(`/conversations/search?q=${encodeURIComponent(query)}`);
    return response;
  } catch (error) {
    console.error('Search messages error:', error);
    throw error;
  }
};

/**
 * Delete message
 * @param {string} conversationId - Conversation ID
 * @param {string} messageId - Message ID
 * @returns {Promise<Object>} Response
 */
export const deleteMessage = async (conversationId, messageId) => {
  try {
    const response = await del(`/conversations/${conversationId}/messages/${messageId}`);
    return response;
  } catch (error) {
    console.error('Delete message error:', error);
    throw error;
  }
};

/**
 * Get conversation analytics
 * @param {string} conversationId - Conversation ID
 * @returns {Promise<Object>} Conversation analytics
 */
export const getConversationAnalytics = async (conversationId) => {
  try {
    const response = await get(`/conversations/${conversationId}/analytics`);
    return response;
  } catch (error) {
    console.error('Get conversation analytics error:', error);
    throw error;
  }
};

export default {
  getConversations,
  getConversation,
  getConversationMessages,
  sendMessage,
  updateConversationStatus,
  assignConversation,
  markAsRead,
  searchMessages,
  deleteMessage,
  getConversationAnalytics,
};
