/**
 * Type definitions for SMART FLOW v2 Dashboard
 */

export interface Metrics {
  timestamp: number;
  lanes: Record<string, LaneMetrics>;
  intersection?: IntersectionMetrics;
  emergency?: EmergencyEvent;
  pedestrian?: PedestrianMetrics;
}

export interface LaneMetrics {
  vehicle_count: number;
  density: number;
  queue_length: number;
  wait_time: number;
  signal_state: SignalState;
  throughput: number;
  vehicle_types?: Record<string, number>;
}

export interface IntersectionMetrics {
  total_vehicles: number;
  average_wait_time: number;
  throughput: number;
  cycle_time: number;
  efficiency: number;
}

export interface EmergencyEvent {
  vehicle_type: string;
  lane: string;
  timestamp: number;
  active: boolean;
}

export interface PedestrianMetrics {
  crosswalks: Record<string, CrosswalkData>;
}

export interface CrosswalkData {
  pedestrian_count: number;
  walk_signal: WalkSignalState;
}

export type SignalState = 'red' | 'yellow' | 'green';
export type WalkSignalState = 'dont_walk' | 'walk' | 'flashing_dont_walk';

export interface Alert {
  message: string;
  level: 'info' | 'warning' | 'error';
  timestamp: number;
}

export interface Command {
  command_type: string;
  target: string;
  value: any;
  timestamp: number;
}

export interface SystemStatus {
  status: string;
  connected_clients: number;
  pending_commands: number;
}

export interface HistoricalData {
  metric: string;
  data: Array<{
    timestamp: number;
    value: number;
  }>;
}

export interface WebSocketMessage {
  type: 'metrics_update' | 'alert' | 'status_update';
  data: any;
}
