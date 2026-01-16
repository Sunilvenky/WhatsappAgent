import React, { createContext, useContext, useEffect, useState } from 'react';
import websocketService from '../services/websocket';
import pollingService from '../services/polling';
import { useAuth } from './AuthContext';

const RealtimeContext = createContext();

export const useRealtime = () => {
  const context = useContext(RealtimeContext);
  if (!context) {
    throw new Error('useRealtime must be used within RealtimeProvider');
  }
  return context;
};

export const RealtimeProvider = ({ children }) => {
  const { user } = useAuth();
  const [wsConnected, setWsConnected] = useState(false);
  const [lastUpdate, setLastUpdate] = useState(null);

  useEffect(() => {
    if (!user?.token) return;

    // Connect WebSocket
    websocketService.connect(user.token).catch(err => {
      console.error('WebSocket connection failed:', err);
    });

    // Listen for connection status changes
    const unsubscribeConnected = websocketService.on('connected', () => {
      setWsConnected(true);
      console.log('🟢 WebSocket connected');
    });

    const unsubscribeDisconnected = websocketService.on('disconnected', () => {
      setWsConnected(false);
      console.log('🔴 WebSocket disconnected');
    });

    return () => {
      unsubscribeConnected();
      unsubscribeDisconnected();
      pollingService.stopAll();
      websocketService.disconnect();
    };
  }, [user?.token]);

  const value = {
    wsConnected,
    websocketService,
    pollingService,
    lastUpdate,
    setLastUpdate,
  };

  return (
    <RealtimeContext.Provider value={value}>
      {children}
    </RealtimeContext.Provider>
  );
};
