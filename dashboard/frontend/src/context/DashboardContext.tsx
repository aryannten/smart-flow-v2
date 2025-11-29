/**
 * Dashboard context for global state management
 */

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { Metrics, Alert, SystemStatus } from '../types';
import { websocketService } from '../services/websocket';
import { apiService } from '../services/api';

interface DashboardContextType {
  metrics: Metrics | null;
  alerts: Alert[];
  status: SystemStatus | null;
  isConnected: boolean;
  addAlert: (alert: Alert) => void;
  clearAlerts: () => void;
}

const DashboardContext = createContext<DashboardContextType | undefined>(undefined);

export const useDashboard = () => {
  const context = useContext(DashboardContext);
  if (!context) {
    throw new Error('useDashboard must be used within DashboardProvider');
  }
  return context;
};

interface DashboardProviderProps {
  children: ReactNode;
}

export const DashboardProvider: React.FC<DashboardProviderProps> = ({ children }) => {
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [status, setStatus] = useState<SystemStatus | null>(null);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    // Connect to WebSocket
    websocketService.connect();

    // Subscribe to WebSocket messages
    const unsubscribe = websocketService.subscribe((message) => {
      switch (message.type) {
        case 'metrics_update':
          setMetrics(message.data);
          break;
        case 'alert':
          addAlert(message.data);
          break;
        case 'status_update':
          setStatus(message.data);
          break;
      }
    });

    // Check connection status periodically
    const connectionCheckInterval = setInterval(() => {
      setIsConnected(websocketService.isConnected());
    }, 1000);

    // Fetch initial status
    apiService.getStatus()
      .then(setStatus)
      .catch(console.error);

    // Fetch initial metrics
    apiService.getMetrics()
      .then(setMetrics)
      .catch(console.error);

    // Cleanup
    return () => {
      unsubscribe();
      clearInterval(connectionCheckInterval);
      websocketService.disconnect();
    };
  }, []);

  const addAlert = (alert: Alert) => {
    setAlerts(prev => [...prev, alert].slice(-100)); // Keep last 100 alerts
  };

  const clearAlerts = () => {
    setAlerts([]);
  };

  const value: DashboardContextType = {
    metrics,
    alerts,
    status,
    isConnected,
    addAlert,
    clearAlerts,
  };

  return (
    <DashboardContext.Provider value={value}>
      {children}
    </DashboardContext.Provider>
  );
};
