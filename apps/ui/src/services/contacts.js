/**
 * Contacts Service
 * Handles contact management operations
 */
import { get, post, put, del } from './api';

/**
 * Get all contacts with pagination and filters
 * @param {Object} params - Query parameters
 * @returns {Promise<Object>} Contacts list with pagination info
 */
export const getContacts = async (params = {}) => {
  try {
    const queryParams = new URLSearchParams();
    
    // Add pagination
    if (params.skip !== undefined) queryParams.append('skip', params.skip);
    if (params.limit !== undefined) queryParams.append('limit', params.limit);
    
    // Add filters
    if (params.search) queryParams.append('search', params.search);
    if (params.tags) queryParams.append('tags', params.tags);
    if (params.status) queryParams.append('status', params.status);
    
    const url = `/contacts${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
    const response = await get(url);
    return response;
  } catch (error) {
    console.error('Get contacts error:', error);
    throw error;
  }
};

/**
 * Get contact by ID
 * @param {string} contactId - Contact ID
 * @returns {Promise<Object>} Contact data
 */
export const getContact = async (contactId) => {
  try {
    const response = await get(`/contacts/${contactId}`);
    return response;
  } catch (error) {
    console.error('Get contact error:', error);
    throw error;
  }
};

/**
 * Create new contact
 * @param {Object} contactData - Contact data
 * @returns {Promise<Object>} Created contact
 */
export const createContact = async (contactData) => {
  try {
    const response = await post('/contacts', contactData);
    return response;
  } catch (error) {
    console.error('Create contact error:', error);
    throw error;
  }
};

/**
 * Update contact
 * @param {string} contactId - Contact ID
 * @param {Object} contactData - Contact data to update
 * @returns {Promise<Object>} Updated contact
 */
export const updateContact = async (contactId, contactData) => {
  try {
    const response = await put(`/contacts/${contactId}`, contactData);
    return response;
  } catch (error) {
    console.error('Update contact error:', error);
    throw error;
  }
};

/**
 * Delete contact
 * @param {string} contactId - Contact ID
 * @returns {Promise<Object>} Response
 */
export const deleteContact = async (contactId) => {
  try {
    const response = await del(`/contacts/${contactId}`);
    return response;
  } catch (error) {
    console.error('Delete contact error:', error);
    throw error;
  }
};

/**
 * Bulk import contacts
 * @param {Array} contacts - Array of contact data
 * @returns {Promise<Object>} Import result
 */
export const importContacts = async (contacts) => {
  try {
    const response = await post('/contacts/bulk-import', { contacts });
    return response;
  } catch (error) {
    console.error('Import contacts error:', error);
    throw error;
  }
};

/**
 * Add tag to contact
 * @param {string} contactId - Contact ID
 * @param {string} tag - Tag to add
 * @returns {Promise<Object>} Updated contact
 */
export const addContactTag = async (contactId, tag) => {
  try {
    const response = await post(`/contacts/${contactId}/tags`, { tag });
    return response;
  } catch (error) {
    console.error('Add contact tag error:', error);
    throw error;
  }
};

/**
 * Remove tag from contact
 * @param {string} contactId - Contact ID
 * @param {string} tag - Tag to remove
 * @returns {Promise<Object>} Updated contact
 */
export const removeContactTag = async (contactId, tag) => {
  try {
    const response = await del(`/contacts/${contactId}/tags/${tag}`);
    return response;
  } catch (error) {
    console.error('Remove contact tag error:', error);
    throw error;
  }
};

/**
 * Get contact conversation history
 * @param {string} contactId - Contact ID
 * @returns {Promise<Array>} Conversation messages
 */
export const getContactConversations = async (contactId) => {
  try {
    const response = await get(`/contacts/${contactId}/conversations`);
    return response;
  } catch (error) {
    console.error('Get contact conversations error:', error);
    throw error;
  }
};

/**
 * Search contacts
 * @param {string} query - Search query
 * @returns {Promise<Array>} Matching contacts
 */
export const searchContacts = async (query) => {
  try {
    const response = await get(`/contacts/search?q=${encodeURIComponent(query)}`);
    return response;
  } catch (error) {
    console.error('Search contacts error:', error);
    throw error;
  }
};

export default {
  getContacts,
  getContact,
  createContact,
  updateContact,
  deleteContact,
  importContacts,
  addContactTag,
  removeContactTag,
  getContactConversations,
  searchContacts,
};
