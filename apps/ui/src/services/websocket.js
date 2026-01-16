/**
 * WebSocket Service for Real-time Updates
 */

class WebSocketService {
  constructor() {
    this.ws = null;
    this.url = import.meta.env.VITE_API_URL || 'http://localhost:8000';
    this.listeners = {};
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.isClosed = false;
  }

  connect(token) {
    return new Promise((resolve, reject) => {
      try {
        const wsUrl = this.url.replace('http', 'ws') + `/ws?token=${token}`;
        console.log('🔌 Connecting to WebSocket:', wsUrl);
        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => {
          console.log('✅ WebSocket connected');
          this.reconnectAttempts = 0;
          this.emit('connected', {});
          resolve();
        };

        this.ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            this.emit(data.type, data.payload || data);
          } catch (e) {
            console.error('Parse error:', e);
          }
        };

        this.ws.onerror = (error) => {
          console.error('❌ WebSocket error:', error);
          this.emit('error', { error });
        };

        this.ws.onclose = () => {
          console.log('⚠️  WebSocket disconnected');
          this.emit('disconnected', {});
          
          if (!this.isClosed && this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`🔄 Reconnecting... (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
            setTimeout(() => this.connect(token), 3000);
          }
        };
      } catch (error) {
        reject(error);
      }
    });
  }

  disconnect() {
    this.isClosed = true;
    if (this.ws) {
      this.ws.close();
    }
  }

  send(type, payload = {}) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ type, payload }));
    } else {
      console.warn('⚠️  WebSocket not connected');
    }
  }

  on(eventType, callback) {
    if (!this.listeners[eventType]) {
      this.listeners[eventType] = [];
    }
    this.listeners[eventType].push(callback);
    
    // Return unsubscribe function
    return () => {
      this.listeners[eventType] = this.listeners[eventType].filter(cb => cb !== callback);
    };
  }

  emit(eventType, data) {
    if (this.listeners[eventType]) {
      this.listeners[eventType].forEach(callback => {
        try {
          callback(data);
        } catch (error) {
          console.error(`Error in ${eventType}:`, error);
        }
      });
    }
  }

  isConnected() {
    return this.ws && this.ws.readyState === WebSocket.OPEN;
  }
}

export const websocketService = new WebSocketService();
export default websocketService;
