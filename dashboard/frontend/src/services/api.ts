/**
 * API service for communicating with SMART FLOW v2 backend
 */

import axios from 'axios';
import { SystemStatus, Metrics, HistoricalData } from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8080';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const apiService = {
  /**
   * Get system status
   */
  async getStatus(): Promise<SystemStatus> {
    const response = await api.get<SystemStatus>('/api/status');
    return response.data;
  },

  /**
   * Get current metrics
   */
  async getMetrics(): Promise<Metrics> {
    const response = await api.get<Metrics>('/api/metrics');
    return response.data;
  },

  /**
   * Get historical data for a metric
   */
  async getHistory(metric: string): Promise<HistoricalData> {
    const response = await api.get<HistoricalData>(`/api/history/${metric}`);
    return response.data;
  },

  /**
   * Override signal for a lane
   */
  async overrideSignal(lane: string, state: string, duration: number): Promise<void> {
    await api.post('/api/override', {
      lane,
      state,
      duration,
    });
  },

  /**
   * Adjust system parameter
   */
  async adjustParameter(parameter: string, value: number): Promise<void> {
    await api.post('/api/adjust', {
      parameter,
      value,
    });
  },

  /**
   * Get list of intersections
   */
  async getIntersections(): Promise<any> {
    const response = await api.get('/api/intersections');
    return response.data;
  },
};

export default apiService;
