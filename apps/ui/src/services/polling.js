/**
 * Polling Service for Periodic Data Updates
 */

import { get } from './api';

class PollingService {
  constructor() {
    this.polls = {};
  }

  /**
   * Start polling an endpoint
   */
  start(key, endpoint, interval = 10000, callback) {
    if (this.polls[key]) {
      clearInterval(this.polls[key]);
    }

    // Initial fetch
    this.fetch(endpoint, callback);

    // Setup interval
    this.polls[key] = setInterval(() => {
      this.fetch(endpoint, callback);
    }, interval);

    console.log(`📊 Polling started: ${key} (${interval}ms)`);
  }

  /**
   * Stop polling
   */
  stop(key) {
    if (this.polls[key]) {
      clearInterval(this.polls[key]);
      delete this.polls[key];
      console.log(`⏹️  Polling stopped: ${key}`);
    }
  }

  /**
   * Stop all polls
   */
  stopAll() {
    Object.keys(this.polls).forEach(key => this.stop(key));
  }

  /**
   * Internal fetch function
   */
  async fetch(endpoint, callback) {
    try {
      const data = await get(endpoint);
      callback(null, data);
    } catch (error) {
      console.error(`Polling error for ${endpoint}:`, error);
      callback(error, null);
    }
  }

  // Convenience methods
  pollDashboardStats(callback, interval = 10000) {
    this.start('dashboard_stats', '/analytics/dashboard', interval, callback);
  }

  pollMessageStats(callback, interval = 15000) {
    this.start('message_stats', '/messages/stats', interval, callback);
  }

  pollContacts(callback, interval = 20000) {
    this.start('contacts', '/contacts', interval, callback);
  }

  pollCampaigns(callback, interval = 15000) {
    this.start('campaigns', '/campaigns', interval, callback);
  }

  pollLeads(callback, interval = 20000) {
    this.start('leads', '/leads', interval, callback);
  }
}

export const pollingService = new PollingService();
export default pollingService;
