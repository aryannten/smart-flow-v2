"""
Metrics Logger module for SMART FLOW traffic signal simulation system.

Records simulation data for analysis and validation.
"""

import json
from typing import Dict, List, Optional, Any
from pathlib import Path
from src.models import SignalState
from dataclasses import asdict


class MetricsLogger:
    """
    Logs simulation metrics for analysis.
    
    This class records density measurements, signal allocations, and state transitions
    throughout the simulation. It provides summary statistics at the end.
    """
    
    def __init__(self, output_path: str):
        """
        Initialize the metrics logger with output file path.
        
        Args:
            output_path: Path to the output JSON file
        """
        self.output_path = output_path
        
        # Storage for logged data
        self._density_logs: List[Dict] = []
        self._allocation_logs: List[Dict] = []
        self._transition_logs: List[Dict] = []
        
        # Tracking for summary statistics
        self._cycle_count = 0
        self._lane_waiting_times: Dict[str, List[float]] = {}
        
    def log_density(self, timestamp: float, densities: Dict[str, float]) -> None:
        """
        Log vehicle density measurements for each lane.
        
        Args:
            timestamp: Simulation timestamp in seconds
            densities: Dictionary mapping lane names to density values
        """
        log_entry = {
            'timestamp': timestamp,
            'densities': densities.copy()
        }
        self._density_logs.append(log_entry)
    
    def log_signal_allocation(self, timestamp: float, green_times: Dict[str, int]) -> None:
        """
        Log green time allocation decisions.
        
        Args:
            timestamp: Simulation timestamp in seconds
            green_times: Dictionary mapping lane names to allocated green time in seconds
        """
        log_entry = {
            'timestamp': timestamp,
            'green_times': green_times.copy()
        }
        self._allocation_logs.append(log_entry)
        
        # Increment cycle count when allocation happens
        self._cycle_count += 1
    
    def log_state_transition(
        self, 
        timestamp: float, 
        lane: str, 
        old_state: SignalState, 
        new_state: SignalState
    ) -> None:
        """
        Log signal state transitions.
        
        Args:
            timestamp: Simulation timestamp in seconds
            lane: Lane identifier
            old_state: Previous signal state
            new_state: New signal state
        """
        log_entry = {
            'timestamp': timestamp,
            'lane': lane,
            'old_state': old_state.value,
            'new_state': new_state.value
        }
        self._transition_logs.append(log_entry)
        
        # Track waiting times (time spent in red state)
        if old_state == SignalState.RED and new_state == SignalState.GREEN:
            # Lane is getting green signal, calculate waiting time
            if lane not in self._lane_waiting_times:
                self._lane_waiting_times[lane] = []
            
            # Find the last time this lane went red
            last_red_time = None
            for transition in reversed(self._transition_logs[:-1]):  # Exclude current transition
                if transition['lane'] == lane and transition['new_state'] == 'red':
                    last_red_time = transition['timestamp']
                    break
            
            if last_red_time is not None:
                waiting_time = timestamp - last_red_time
                self._lane_waiting_times[lane].append(waiting_time)
    
    def finalize(self) -> None:
        """
        Calculate summary statistics and write all logs to file.
        
        Writes a JSON file containing all logged data and summary statistics.
        """
        # Calculate average waiting time per lane
        average_waiting_times = {}
        for lane, waiting_times in self._lane_waiting_times.items():
            if waiting_times:
                average_waiting_times[lane] = sum(waiting_times) / len(waiting_times)
            else:
                average_waiting_times[lane] = 0.0
        
        # Create summary statistics
        summary = {
            'total_cycles': self._cycle_count,
            'average_waiting_time_per_lane': average_waiting_times,
            'total_density_measurements': len(self._density_logs),
            'total_allocations': len(self._allocation_logs),
            'total_transitions': len(self._transition_logs)
        }
        
        # Compile all data
        output_data = {
            'summary': summary,
            'density_logs': self._density_logs,
            'allocation_logs': self._allocation_logs,
            'transition_logs': self._transition_logs
        }
        
        # Write to file
        output_path = Path(self.output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(output_data, f, indent=2)



class EnhancedMetricsLogger(MetricsLogger):
    """
    Enhanced metrics logger with comprehensive analytics for SMART FLOW v2.
    
    Extends the base MetricsLogger with:
    - Detection result logging (vehicles, pedestrians, emergency vehicles)
    - Queue metrics logging
    - Emergency event logging
    - Pedestrian activity logging
    - Throughput logging
    - Network metrics logging
    - Environmental impact calculation
    - Comprehensive report generation
    """
    
    def __init__(self, output_path: str):
        """
        Initialize the enhanced metrics logger.
        
        Args:
            output_path: Path to the output JSON file
        """
        super().__init__(output_path)
        
        # Additional storage for enhanced metrics
        self._detection_logs: List[Dict] = []
        self._queue_logs: List[Dict] = []
        self._emergency_logs: List[Dict] = []
        self._pedestrian_logs: List[Dict] = []
        self._throughput_logs: List[Dict] = []
        self._network_logs: List[Dict] = []
        
        # Tracking for per-vehicle metrics
        self._vehicle_tracking: Dict[int, Dict] = {}  # vehicle_id -> {entry_time, exit_time, stops}
        
        # Throughput tracking
        self._lane_throughput: Dict[str, List[float]] = {}  # lane -> list of timestamps
        
        # Environmental impact tracking
        self._total_idle_time: float = 0.0
        self._idle_vehicle_seconds: float = 0.0
    
    def log_detection_result(self, timestamp: float, result: Any) -> None:
        """
        Log detection results including vehicles, pedestrians, and emergency vehicles.
        
        Args:
            timestamp: Simulation timestamp in seconds
            result: DetectionResult object with vehicles, pedestrians, emergency_vehicles
        """
        # Extract detection counts
        vehicle_count = len(result.vehicles) if hasattr(result, 'vehicles') else 0
        pedestrian_count = len(result.pedestrians) if hasattr(result, 'pedestrians') else 0
        emergency_count = len(result.emergency_vehicles) if hasattr(result, 'emergency_vehicles') else 0
        
        # Create log entry
        log_entry = {
            'timestamp': timestamp,
            'vehicle_count': vehicle_count,
            'pedestrian_count': pedestrian_count,
            'emergency_vehicle_count': emergency_count
        }
        
        # Add vehicle type breakdown if available
        if hasattr(result, 'vehicles') and result.vehicles:
            vehicle_types: Dict[str, int] = {}
            for vehicle in result.vehicles:
                if hasattr(vehicle, 'class_name'):
                    vtype = vehicle.class_name
                    vehicle_types[vtype] = vehicle_types.get(vtype, 0) + 1
            log_entry['vehicle_types'] = vehicle_types
        
        self._detection_logs.append(log_entry)
    
    def log_queue_metrics(self, timestamp: float, metrics: Dict[str, Any]) -> None:
        """
        Log queue metrics for each lane.
        
        Args:
            timestamp: Simulation timestamp in seconds
            metrics: Dictionary mapping lane names to QueueMetrics objects
        """
        log_entry = {
            'timestamp': timestamp,
            'queues': {}
        }
        
        for lane, queue_metrics in metrics.items():
            # Convert QueueMetrics to dict
            if hasattr(queue_metrics, '__dict__'):
                queue_data = {
                    'length_meters': queue_metrics.length_meters,
                    'vehicle_count': queue_metrics.vehicle_count,
                    'density': queue_metrics.density,
                    'is_spillback': queue_metrics.is_spillback
                }
            else:
                # If it's already a dict
                queue_data = queue_metrics
            
            log_entry['queues'][lane] = queue_data
            
            # Track idle time for environmental impact
            # Vehicles in queue are idling
            if 'vehicle_count' in queue_data:
                # Assume 1 second of idle time per vehicle per log entry
                self._idle_vehicle_seconds += queue_data['vehicle_count']
        
        self._queue_logs.append(log_entry)
    
    def log_emergency_event(self, event: Any) -> None:
        """
        Log emergency vehicle event.
        
        Args:
            event: EmergencyEvent object
        """
        # Convert EmergencyEvent to dict
        if hasattr(event, '__dict__'):
            log_entry = {
                'vehicle_type': event.vehicle_type,
                'lane': event.lane,
                'timestamp': event.timestamp,
                'priority_level': event.priority_level
            }
        else:
            log_entry = event
        
        self._emergency_logs.append(log_entry)
    
    def log_pedestrian_activity(self, timestamp: float, crosswalk_data: Dict[str, int]) -> None:
        """
        Log pedestrian activity by crosswalk.
        
        Args:
            timestamp: Simulation timestamp in seconds
            crosswalk_data: Dictionary mapping crosswalk names to pedestrian counts
        """
        log_entry = {
            'timestamp': timestamp,
            'crosswalks': crosswalk_data.copy()
        }
        
        self._pedestrian_logs.append(log_entry)
    
    def log_throughput(self, timestamp: float, lane: str, count: int) -> None:
        """
        Log throughput for a lane.
        
        Args:
            timestamp: Simulation timestamp in seconds
            lane: Lane identifier
            count: Number of vehicles that passed through
        """
        log_entry = {
            'timestamp': timestamp,
            'lane': lane,
            'count': count
        }
        
        self._throughput_logs.append(log_entry)
        
        # Track for throughput calculation
        if lane not in self._lane_throughput:
            self._lane_throughput[lane] = []
        
        # Add timestamp for each vehicle
        for _ in range(count):
            self._lane_throughput[lane].append(timestamp)
    
    def log_network_metrics(self, timestamp: float, metrics: Any) -> None:
        """
        Log network-wide metrics for multi-intersection coordination.
        
        Args:
            timestamp: Simulation timestamp in seconds
            metrics: NetworkMetrics object
        """
        # Convert NetworkMetrics to dict
        if hasattr(metrics, '__dict__'):
            log_entry = {
                'timestamp': timestamp,
                'average_travel_time': metrics.average_travel_time,
                'stops_per_vehicle': metrics.stops_per_vehicle,
                'coordination_quality': metrics.coordination_quality,
                'total_throughput': metrics.total_throughput,
                'network_delay': metrics.network_delay
            }
        else:
            log_entry = {'timestamp': timestamp, **metrics}
        
        self._network_logs.append(log_entry)
    
    def track_vehicle(self, vehicle_id: int, entry_time: float, lane: str) -> None:
        """
        Start tracking a vehicle for per-vehicle wait time calculation.
        
        Args:
            vehicle_id: Unique vehicle identifier
            entry_time: Time when vehicle entered the intersection area
            lane: Lane where vehicle entered
        """
        self._vehicle_tracking[vehicle_id] = {
            'entry_time': entry_time,
            'exit_time': None,
            'lane': lane,
            'stops': 0,
            'wait_time': 0.0
        }
    
    def vehicle_stopped(self, vehicle_id: int) -> None:
        """
        Record that a vehicle has stopped (encountered red signal).
        
        Args:
            vehicle_id: Unique vehicle identifier
        """
        if vehicle_id in self._vehicle_tracking:
            self._vehicle_tracking[vehicle_id]['stops'] += 1
    
    def vehicle_departed(self, vehicle_id: int, exit_time: float) -> None:
        """
        Record that a vehicle has departed the intersection.
        
        Args:
            vehicle_id: Unique vehicle identifier
            exit_time: Time when vehicle exited the intersection area
        """
        if vehicle_id in self._vehicle_tracking:
            self._vehicle_tracking[vehicle_id]['exit_time'] = exit_time
            entry_time = self._vehicle_tracking[vehicle_id]['entry_time']
            self._vehicle_tracking[vehicle_id]['wait_time'] = exit_time - entry_time
    
    def calculate_environmental_impact(self) -> Dict[str, float]:
        """
        Calculate environmental impact metrics.
        
        Estimates fuel consumption and CO2 emissions based on idling time.
        Uses standard traffic engineering assumptions:
        - Average car idles at 0.6 liters/hour
        - Gasoline produces ~2.3 kg CO2 per liter
        
        Returns:
            Dictionary with environmental metrics
        """
        # Convert idle vehicle-seconds to idle vehicle-hours
        idle_hours = self._idle_vehicle_seconds / 3600.0
        
        # Calculate fuel consumption (liters)
        # Average car idles at 0.6 liters/hour
        fuel_consumed = idle_hours * 0.6
        
        # Calculate CO2 emissions (kg)
        # Gasoline produces ~2.3 kg CO2 per liter
        co2_emissions = fuel_consumed * 2.3
        
        # Estimate savings vs fixed timing
        # Assume adaptive system reduces idle time by 20-30%
        # This is a conservative estimate
        savings_percentage = 0.25
        emissions_saved = co2_emissions * savings_percentage
        
        return {
            'total_idle_time': self._idle_vehicle_seconds,
            'estimated_fuel_consumption': fuel_consumed,
            'estimated_co2_emissions': co2_emissions,
            'emissions_saved_vs_fixed_timing': emissions_saved
        }
    
    def generate_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive report with all metrics and analysis.
        
        Returns:
            Dictionary containing comprehensive report data
        """
        # Calculate per-vehicle wait time statistics
        vehicle_wait_times = [
            v['wait_time'] for v in self._vehicle_tracking.values() 
            if v['exit_time'] is not None
        ]
        
        avg_vehicle_wait_time = 0.0
        max_vehicle_wait_time = 0.0
        if vehicle_wait_times:
            avg_vehicle_wait_time = sum(vehicle_wait_times) / len(vehicle_wait_times)
            max_vehicle_wait_time = max(vehicle_wait_times)
        
        # Calculate throughput statistics
        throughput_by_lane = {}
        for lane, timestamps in self._lane_throughput.items():
            if timestamps:
                # Calculate vehicles per hour
                time_span = max(timestamps) - min(timestamps) if len(timestamps) > 1 else 1.0
                time_span_hours = time_span / 3600.0 if time_span > 0 else 1.0
                vehicles_per_hour = len(timestamps) / time_span_hours
                throughput_by_lane[lane] = vehicles_per_hour
            else:
                throughput_by_lane[lane] = 0.0
        
        # Calculate detection statistics
        total_vehicles_detected = sum(log['vehicle_count'] for log in self._detection_logs)
        total_pedestrians_detected = sum(log['pedestrian_count'] for log in self._detection_logs)
        total_emergency_vehicles = sum(log['emergency_vehicle_count'] for log in self._detection_logs)
        
        # Calculate queue statistics
        avg_queue_lengths = {}
        max_queue_lengths = {}
        spillback_events = {}
        
        for log in self._queue_logs:
            for lane, queue_data in log['queues'].items():
                if lane not in avg_queue_lengths:
                    avg_queue_lengths[lane] = []
                    max_queue_lengths[lane] = 0.0
                    spillback_events[lane] = 0
                
                avg_queue_lengths[lane].append(queue_data['length_meters'])
                max_queue_lengths[lane] = max(max_queue_lengths[lane], queue_data['length_meters'])
                
                if queue_data.get('is_spillback', False):
                    spillback_events[lane] += 1
        
        # Calculate averages
        for lane in avg_queue_lengths:
            if avg_queue_lengths[lane]:
                avg_queue_lengths[lane] = sum(avg_queue_lengths[lane]) / len(avg_queue_lengths[lane])
            else:
                avg_queue_lengths[lane] = 0.0
        
        # Environmental impact
        environmental_impact = self.calculate_environmental_impact()
        
        # Compile report
        report = {
            'summary': {
                'total_cycles': self._cycle_count,
                'total_vehicles_detected': total_vehicles_detected,
                'total_pedestrians_detected': total_pedestrians_detected,
                'total_emergency_vehicles': total_emergency_vehicles,
                'total_emergency_events': len(self._emergency_logs),
                'vehicles_tracked': len(self._vehicle_tracking),
                'vehicles_completed': len(vehicle_wait_times)
            },
            'performance': {
                'average_vehicle_wait_time': avg_vehicle_wait_time,
                'maximum_vehicle_wait_time': max_vehicle_wait_time,
                'average_waiting_time_per_lane': self._calculate_lane_waiting_times(),
                'throughput_by_lane': throughput_by_lane,
                'total_throughput': sum(throughput_by_lane.values())
            },
            'queue_analysis': {
                'average_queue_length_by_lane': avg_queue_lengths,
                'maximum_queue_length_by_lane': max_queue_lengths,
                'spillback_events_by_lane': spillback_events,
                'total_spillback_events': sum(spillback_events.values())
            },
            'environmental_impact': environmental_impact,
            'detection_summary': {
                'total_detection_frames': len(self._detection_logs),
                'average_vehicles_per_frame': total_vehicles_detected / len(self._detection_logs) if self._detection_logs else 0.0,
                'average_pedestrians_per_frame': total_pedestrians_detected / len(self._detection_logs) if self._detection_logs else 0.0
            },
            'pedestrian_summary': {
                'total_pedestrian_logs': len(self._pedestrian_logs),
                'crosswalk_activity': self._calculate_crosswalk_activity()
            },
            'network_summary': self._calculate_network_summary()
        }
        
        return report
    
    def _calculate_lane_waiting_times(self) -> Dict[str, float]:
        """Calculate average waiting time per lane from base class data."""
        average_waiting_times = {}
        for lane, waiting_times in self._lane_waiting_times.items():
            if waiting_times:
                average_waiting_times[lane] = sum(waiting_times) / len(waiting_times)
            else:
                average_waiting_times[lane] = 0.0
        return average_waiting_times
    
    def _calculate_crosswalk_activity(self) -> Dict[str, float]:
        """Calculate average pedestrian activity per crosswalk."""
        crosswalk_totals: Dict[str, List[int]] = {}
        
        for log in self._pedestrian_logs:
            for crosswalk, count in log['crosswalks'].items():
                if crosswalk not in crosswalk_totals:
                    crosswalk_totals[crosswalk] = []
                crosswalk_totals[crosswalk].append(count)
        
        # Calculate averages
        crosswalk_averages = {}
        for crosswalk, counts in crosswalk_totals.items():
            if counts:
                crosswalk_averages[crosswalk] = sum(counts) / len(counts)
            else:
                crosswalk_averages[crosswalk] = 0.0
        
        return crosswalk_averages
    
    def _calculate_network_summary(self) -> Dict[str, Any]:
        """Calculate network-wide summary statistics."""
        if not self._network_logs:
            return {
                'average_travel_time': 0.0,
                'average_stops_per_vehicle': 0.0,
                'average_coordination_quality': 0.0,
                'total_network_throughput': 0,
                'average_network_delay': 0.0
            }
        
        # Calculate averages across all network logs
        avg_travel_time = sum(log['average_travel_time'] for log in self._network_logs) / len(self._network_logs)
        avg_stops = sum(log['stops_per_vehicle'] for log in self._network_logs) / len(self._network_logs)
        avg_quality = sum(log['coordination_quality'] for log in self._network_logs) / len(self._network_logs)
        total_throughput = self._network_logs[-1]['total_throughput'] if self._network_logs else 0
        avg_delay = sum(log['network_delay'] for log in self._network_logs) / len(self._network_logs)
        
        return {
            'average_travel_time': avg_travel_time,
            'average_stops_per_vehicle': avg_stops,
            'average_coordination_quality': avg_quality,
            'total_network_throughput': total_throughput,
            'average_network_delay': avg_delay
        }
    
    def finalize(self) -> None:
        """
        Calculate summary statistics and write all logs to file.
        
        Extends base class finalize with enhanced metrics.
        """
        # Generate comprehensive report
        report = self.generate_report()
        
        # Compile all data including base class data
        output_data = {
            'summary': report['summary'],
            'performance': report['performance'],
            'queue_analysis': report['queue_analysis'],
            'environmental_impact': report['environmental_impact'],
            'detection_summary': report['detection_summary'],
            'pedestrian_summary': report['pedestrian_summary'],
            'network_summary': report['network_summary'],
            
            # Detailed logs
            'density_logs': self._density_logs,
            'allocation_logs': self._allocation_logs,
            'transition_logs': self._transition_logs,
            'detection_logs': self._detection_logs,
            'queue_logs': self._queue_logs,
            'emergency_logs': self._emergency_logs,
            'pedestrian_logs': self._pedestrian_logs,
            'throughput_logs': self._throughput_logs,
            'network_logs': self._network_logs,
            
            # Per-vehicle tracking
            'vehicle_tracking': {
                str(vid): vdata for vid, vdata in self._vehicle_tracking.items()
            }
        }
        
        # Write to file
        output_path = Path(self.output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(output_data, f, indent=2)
