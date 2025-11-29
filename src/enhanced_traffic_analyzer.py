"""
Enhanced Traffic Analyzer Module for SMART FLOW v2

Extends TrafficAnalyzer with:
- Queue length integration in density calculation
- Weighted priority calculation based on vehicle types
- Congestion trend detection
- Throughput metrics calculation
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
import time
from collections import deque

from src.traffic_analyzer import TrafficAnalyzer
from src.queue_estimator import QueueMetrics
from src.enhanced_detector import VehicleType


class CongestionTrend(Enum):
    """Congestion trend classifications"""
    IMPROVING = "improving"
    STABLE = "stable"
    WORSENING = "worsening"


@dataclass
class DensitySnapshot:
    """Snapshot of density at a point in time"""
    timestamp: float
    lane: str
    density: float
    vehicle_count: int
    queue_length: float


@dataclass
class LaneData:
    """Comprehensive lane data for priority calculation"""
    vehicle_count: int
    queue_length: float  # in meters
    wait_time: float  # average wait time in seconds
    vehicle_types: Dict[VehicleType, int]
    has_emergency: bool
    pedestrian_count: int


class EnhancedTrafficAnalyzer(TrafficAnalyzer):
    """
    Enhanced traffic analyzer with queue-aware density calculation,
    weighted priorities, trend detection, and throughput tracking.
    
    Extends the base TrafficAnalyzer with advanced features for
    comprehensive traffic analysis.
    """
    
    # Vehicle type priority weights
    # Higher weight = higher priority in signal allocation
    VEHICLE_TYPE_WEIGHTS = {
        VehicleType.CAR: 1.0,
        VehicleType.MOTORCYCLE: 0.8,
        VehicleType.BICYCLE: 0.7,
        VehicleType.TRUCK: 1.5,
        VehicleType.BUS: 2.0,  # Public transit gets higher priority
        VehicleType.EMERGENCY_AMBULANCE: 10.0,
        VehicleType.EMERGENCY_FIRE: 10.0,
        VehicleType.EMERGENCY_POLICE: 10.0,
    }
    
    # Queue length weight factor
    # How much queue length contributes to density calculation
    QUEUE_WEIGHT_FACTOR = 0.5
    
    # Congestion trend thresholds
    TREND_WINDOW_SIZE = 10  # Number of snapshots to analyze
    TREND_IMPROVEMENT_THRESHOLD = -0.1  # Density decreasing by 10%
    TREND_WORSENING_THRESHOLD = 0.1  # Density increasing by 10%
    
    # Throughput tracking
    THROUGHPUT_WINDOW_SECONDS = 3600.0  # 1 hour window
    
    def __init__(self):
        """Initialize enhanced traffic analyzer."""
        super().__init__()
        
        # Historical data for trend detection
        self.density_history: Dict[str, deque] = {}
        
        # Throughput tracking
        self.throughput_data: Dict[str, List[float]] = {}  # lane -> list of timestamps
        
    def calculate_density(self, lane_counts: Dict[str, int], 
                         queue_metrics: Optional[Dict[str, QueueMetrics]] = None) -> Dict[str, float]:
        """
        Calculate traffic density integrating queue length.
        
        This enhanced version incorporates queue length into density calculation,
        providing a more accurate representation of congestion that accounts for
        both vehicle count and spatial extent.
        
        Args:
            lane_counts: Dictionary mapping lane names to vehicle counts
            queue_metrics: Optional dictionary mapping lane names to QueueMetrics
            
        Returns:
            Dict[str, float]: Dictionary mapping lane names to enhanced density values
        """
        # Start with base density (vehicle count)
        base_densities = super().calculate_density(lane_counts)
        
        # If no queue metrics provided, return base densities
        if queue_metrics is None:
            return base_densities
        
        # Enhance densities with queue length information
        enhanced_densities = {}
        
        for lane, base_density in base_densities.items():
            if lane in queue_metrics:
                queue_metric = queue_metrics[lane]
                
                # Normalize queue length to a comparable scale
                # Longer queues indicate higher congestion
                queue_contribution = queue_metric.length_meters * self.QUEUE_WEIGHT_FACTOR
                
                # Combined density = base density + weighted queue contribution
                enhanced_density = base_density + queue_contribution
                
                enhanced_densities[lane] = enhanced_density
            else:
                # No queue data for this lane, use base density
                enhanced_densities[lane] = base_density
        
        return enhanced_densities
    
    def calculate_weighted_priority(self, lane_data: LaneData) -> float:
        """
        Calculate weighted priority for a lane considering multiple factors.
        
        This method implements multi-factor allocation by considering:
        - Vehicle count
        - Queue length
        - Wait time
        - Vehicle type composition
        - Emergency vehicle presence
        
        Args:
            lane_data: Comprehensive lane data
            
        Returns:
            Weighted priority score (higher = more priority)
        """
        # Base priority from vehicle count
        count_priority = float(lane_data.vehicle_count)
        
        # Queue length contribution (longer queues need more time)
        # Normalize to similar scale as vehicle count
        queue_priority = lane_data.queue_length * 0.2  # Roughly 5 meters per vehicle
        
        # Wait time contribution (fairness factor)
        # Lanes that have waited longer get priority boost
        wait_priority = lane_data.wait_time * 0.1  # 10 seconds = 1 priority point
        
        # Vehicle type weighting
        type_priority = 0.0
        total_vehicles = sum(lane_data.vehicle_types.values())
        
        if total_vehicles > 0:
            for vehicle_type, count in lane_data.vehicle_types.items():
                weight = self.VEHICLE_TYPE_WEIGHTS.get(vehicle_type, 1.0)
                type_priority += count * weight
            
            # Normalize by total vehicles to get weighted average
            type_priority = type_priority / total_vehicles
        else:
            type_priority = 1.0  # Default weight
        
        # Emergency vehicle override
        emergency_multiplier = 10.0 if lane_data.has_emergency else 1.0
        
        # Pedestrian consideration (slight boost if pedestrians waiting)
        pedestrian_boost = 1.0 + (0.1 * min(lane_data.pedestrian_count, 10))
        
        # Calculate weighted priority
        # Formula: (count + queue + wait) * type_weight * emergency * pedestrian
        base_priority = count_priority + queue_priority + wait_priority
        weighted_priority = base_priority * type_priority * emergency_multiplier * pedestrian_boost
        
        return weighted_priority
    
    def detect_congestion_trend(self, lane: str, current_density: float, 
                               current_count: int, current_queue: float) -> CongestionTrend:
        """
        Detect congestion trend for a lane.
        
        Analyzes historical density data to determine if congestion is
        improving, stable, or worsening. This enables proactive signal timing
        adjustments.
        
        Args:
            lane: Lane identifier
            current_density: Current density value
            current_count: Current vehicle count
            current_queue: Current queue length in meters
            
        Returns:
            CongestionTrend indicating traffic pattern
        """
        # Initialize history for this lane if needed
        if lane not in self.density_history:
            self.density_history[lane] = deque(maxlen=self.TREND_WINDOW_SIZE)
        
        # Add current snapshot
        snapshot = DensitySnapshot(
            timestamp=time.time(),
            lane=lane,
            density=current_density,
            vehicle_count=current_count,
            queue_length=current_queue
        )
        self.density_history[lane].append(snapshot)
        
        # Need at least 3 snapshots to detect trend
        if len(self.density_history[lane]) < 3:
            return CongestionTrend.STABLE
        
        # Calculate trend using linear regression on density values
        snapshots = list(self.density_history[lane])
        n = len(snapshots)
        
        # Simple trend calculation: compare recent average to older average
        mid_point = n // 2
        older_avg = sum(s.density for s in snapshots[:mid_point]) / mid_point
        recent_avg = sum(s.density for s in snapshots[mid_point:]) / (n - mid_point)
        
        # Avoid division by zero
        if older_avg == 0:
            return CongestionTrend.STABLE
        
        # Calculate relative change
        relative_change = (recent_avg - older_avg) / older_avg
        
        # Classify trend
        if relative_change <= self.TREND_IMPROVEMENT_THRESHOLD:
            return CongestionTrend.IMPROVING
        elif relative_change >= self.TREND_WORSENING_THRESHOLD:
            return CongestionTrend.WORSENING
        else:
            return CongestionTrend.STABLE
    
    def calculate_throughput(self, lane: str, time_window: float = None) -> float:
        """
        Calculate throughput for a lane (vehicles per hour).
        
        Tracks vehicles that have cleared the intersection and calculates
        the rate over a specified time window.
        
        Args:
            lane: Lane identifier
            time_window: Time window in seconds (default: 1 hour)
            
        Returns:
            Throughput in vehicles per hour
        """
        if time_window is None:
            time_window = self.THROUGHPUT_WINDOW_SECONDS
        
        # Initialize throughput data for this lane if needed
        if lane not in self.throughput_data:
            self.throughput_data[lane] = []
        
        current_time = time.time()
        
        # Remove old timestamps outside the window
        cutoff_time = current_time - time_window
        self.throughput_data[lane] = [
            ts for ts in self.throughput_data[lane] if ts >= cutoff_time
        ]
        
        # Calculate throughput
        vehicle_count = len(self.throughput_data[lane])
        
        # Convert to vehicles per hour
        if time_window > 0:
            throughput = (vehicle_count / time_window) * 3600.0
        else:
            throughput = 0.0
        
        return throughput
    
    def record_vehicle_cleared(self, lane: str, timestamp: Optional[float] = None) -> None:
        """
        Record that a vehicle has cleared the intersection.
        
        This method should be called when a vehicle exits the intersection
        to track throughput metrics.
        
        Args:
            lane: Lane identifier
            timestamp: Timestamp of clearance (defaults to current time)
        """
        if timestamp is None:
            timestamp = time.time()
        
        # Initialize throughput data for this lane if needed
        if lane not in self.throughput_data:
            self.throughput_data[lane] = []
        
        # Record the clearance
        self.throughput_data[lane].append(timestamp)
    
    def get_throughput_summary(self, time_window: float = None) -> Dict[str, float]:
        """
        Get throughput summary for all lanes.
        
        Args:
            time_window: Time window in seconds (default: 1 hour)
            
        Returns:
            Dictionary mapping lane names to throughput values (vehicles/hour)
        """
        summary = {}
        
        for lane in self.throughput_data.keys():
            summary[lane] = self.calculate_throughput(lane, time_window)
        
        return summary
    
    def reset_history(self, lane: Optional[str] = None) -> None:
        """
        Reset historical data for trend detection and throughput.
        
        Args:
            lane: Specific lane to reset, or None to reset all lanes
        """
        if lane is None:
            # Reset all lanes
            self.density_history.clear()
            self.throughput_data.clear()
        else:
            # Reset specific lane
            if lane in self.density_history:
                self.density_history[lane].clear()
            if lane in self.throughput_data:
                self.throughput_data[lane].clear()
