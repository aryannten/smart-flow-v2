"""
Multi-Intersection Coordinator Module for SMART FLOW v2

Synchronizes signals across multiple intersections for green wave coordination.
"""

from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
import time


@dataclass
class NetworkConfig:
    """Network configuration for multiple intersections"""
    intersections: Dict[str, object]  # IntersectionConfig
    connections: List[Tuple[str, str]]  # (from_intersection, to_intersection)
    travel_times: Dict[Tuple[str, str], float]  # seconds
    coordination_enabled: bool


@dataclass
class NetworkMetrics:
    """Network-wide metrics"""
    average_travel_time: float
    stops_per_vehicle: float
    coordination_quality: float  # 0-1 score
    total_throughput: int
    network_delay: float


@dataclass
class CoordinationPlan:
    """Green wave coordination plan"""
    corridor: List[str]
    direction: str
    offsets: Dict[str, float]
    target_speed: float  # meters per second
    cycle_time: float


class MultiIntersectionCoordinator:
    """
    Coordinates signals across multiple intersections.
    
    Implements green wave coordination by calculating optimal signal offsets
    based on travel times between intersections.
    """
    
    def __init__(self, network_config: NetworkConfig):
        """
        Initialize multi-intersection coordinator.
        
        Args:
            network_config: Network configuration
        """
        self.network_config = network_config
        
        # Registry of intersection controllers
        self._controllers: Dict[str, Any] = {}
        
        # Calculated offsets for each intersection
        self._offsets: Dict[str, float] = {}
        
        # Active coordination plans
        self._coordination_plans: List[CoordinationPlan] = []
        
        # Metrics tracking
        self._total_vehicles_processed: int = 0
        self._total_stops: int = 0
        self._total_travel_time: float = 0.0
        self._vehicle_count: int = 0
        self._network_delay: float = 0.0
        
        # Synchronization state
        self._last_sync_time: float = 0.0
        self._sync_interval: float = 1.0  # seconds
    
    def register_intersection(self, intersection_id: str, controller: Any) -> None:
        """
        Register an intersection controller.
        
        Args:
            intersection_id: Intersection identifier
            controller: Signal controller for intersection
        """
        if intersection_id not in self.network_config.intersections:
            raise ValueError(f"Intersection {intersection_id} not in network configuration")
        
        self._controllers[intersection_id] = controller
        
        # Initialize offset to 0 if not already set
        if intersection_id not in self._offsets:
            self._offsets[intersection_id] = 0.0
    
    def calculate_offsets(self, travel_times: Dict[Tuple[str, str], float]) -> Dict[str, float]:
        """
        Calculate signal offsets for coordination.
        
        Uses the formula: Offset = (distance / target_speed) % cycle_time
        to create green waves where vehicles arriving from upstream intersections
        encounter green signals.
        
        Args:
            travel_times: Travel times between intersections in seconds
            
        Returns:
            Dictionary mapping intersection ID to offset time in seconds
        """
        if not travel_times:
            # No travel times provided, return zero offsets
            return {iid: 0.0 for iid in self.network_config.intersections.keys()}
        
        offsets: Dict[str, float] = {}
        
        # Get list of intersections in network order
        # Start with intersections that have no incoming connections
        intersection_ids = list(self.network_config.intersections.keys())
        
        if not intersection_ids:
            return offsets
        
        # Use first intersection as reference (offset = 0)
        reference_intersection = intersection_ids[0]
        offsets[reference_intersection] = 0.0
        
        # Calculate offsets for connected intersections
        # Use BFS-like approach to propagate offsets through network
        processed = {reference_intersection}
        queue = [reference_intersection]
        
        # Default cycle time (will be overridden if controllers are registered)
        default_cycle_time = 60.0
        
        while queue:
            current = queue.pop(0)
            current_offset = offsets[current]
            
            # Get cycle time for current intersection
            if current in self._controllers:
                controller = self._controllers[current]
                # Try to get cycle time from controller
                if hasattr(controller, 'config'):
                    cycle_time = getattr(controller.config, 'max_cycle_time', default_cycle_time)
                else:
                    cycle_time = default_cycle_time
            else:
                cycle_time = default_cycle_time
            
            # Find all connections from current intersection
            for from_id, to_id in self.network_config.connections:
                if from_id == current and to_id not in processed:
                    # Calculate offset for downstream intersection
                    travel_time = travel_times.get((from_id, to_id), 0.0)
                    
                    # Offset ensures vehicle arrives at green signal
                    # Formula: (previous_offset + travel_time) % cycle_time
                    new_offset = (current_offset + travel_time) % cycle_time
                    offsets[to_id] = new_offset
                    
                    processed.add(to_id)
                    queue.append(to_id)
        
        # Set offsets for any unprocessed intersections to 0
        for iid in intersection_ids:
            if iid not in offsets:
                offsets[iid] = 0.0
        
        # Store calculated offsets
        self._offsets = offsets
        
        return offsets
    
    def synchronize_signals(self) -> None:
        """
        Synchronize signals across network.
        
        Applies calculated offsets to registered intersection controllers
        to maintain coordination.
        """
        if not self.network_config.coordination_enabled:
            return
        
        current_time = time.time()
        
        # Only synchronize at specified intervals
        if current_time - self._last_sync_time < self._sync_interval:
            return
        
        self._last_sync_time = current_time
        
        # Apply offsets to each registered controller
        for intersection_id, controller in self._controllers.items():
            offset = self._offsets.get(intersection_id, 0.0)
            
            # Apply offset to controller if it supports it
            if hasattr(controller, 'set_offset'):
                controller.set_offset(offset)
            elif hasattr(controller, '_phase_start_time'):
                # Adjust phase start time to account for offset
                controller._phase_start_time = current_time - offset
    
    def create_green_wave(self, corridor: List[str], direction: str) -> CoordinationPlan:
        """
        Create green wave coordination plan.
        
        Args:
            corridor: List of intersection IDs in order along corridor
            direction: Direction of travel (e.g., 'northbound', 'eastbound')
            
        Returns:
            CoordinationPlan with offsets and timing
        """
        if not corridor:
            raise ValueError("Corridor must contain at least one intersection")
        
        # Validate all intersections are in network
        for iid in corridor:
            if iid not in self.network_config.intersections:
                raise ValueError(f"Intersection {iid} not in network configuration")
        
        # Calculate travel times along corridor
        corridor_travel_times: Dict[Tuple[str, str], float] = {}
        for i in range(len(corridor) - 1):
            from_id = corridor[i]
            to_id = corridor[i + 1]
            
            # Get travel time from network config
            travel_time = self.network_config.travel_times.get((from_id, to_id), 30.0)
            corridor_travel_times[(from_id, to_id)] = travel_time
        
        # Calculate offsets for corridor
        offsets = self.calculate_offsets(corridor_travel_times)
        
        # Estimate target speed (assuming average distance between intersections)
        # This is a simplified calculation
        if corridor_travel_times:
            avg_travel_time = sum(corridor_travel_times.values()) / len(corridor_travel_times)
            # Assume average distance of 400 meters between intersections
            target_speed = 400.0 / avg_travel_time if avg_travel_time > 0 else 13.9  # ~50 km/h
        else:
            target_speed = 13.9  # Default ~50 km/h
        
        # Get cycle time from first intersection controller
        cycle_time = 60.0  # Default
        if corridor[0] in self._controllers:
            controller = self._controllers[corridor[0]]
            if hasattr(controller, 'config'):
                cycle_time = getattr(controller.config, 'max_cycle_time', 60.0)
        
        # Create coordination plan
        plan = CoordinationPlan(
            corridor=corridor,
            direction=direction,
            offsets=offsets,
            target_speed=target_speed,
            cycle_time=cycle_time
        )
        
        # Store plan
        self._coordination_plans.append(plan)
        
        return plan
    
    def get_network_metrics(self) -> NetworkMetrics:
        """
        Get network-wide metrics.
        
        Returns:
            NetworkMetrics object with aggregated statistics
        """
        # Calculate average travel time
        avg_travel_time = 0.0
        if self._vehicle_count > 0:
            avg_travel_time = self._total_travel_time / self._vehicle_count
        
        # Calculate stops per vehicle
        stops_per_vehicle = 0.0
        if self._vehicle_count > 0:
            stops_per_vehicle = self._total_stops / self._vehicle_count
        
        # Calculate coordination quality (0-1 score)
        # Based on how well actual performance matches ideal green wave
        # Higher score = fewer stops and lower travel time
        coordination_quality = 0.0
        if self._vehicle_count > 0:
            # Ideal: 0 stops per vehicle
            # Good: < 1 stop per vehicle
            # Poor: > 2 stops per vehicle
            if stops_per_vehicle <= 1.0:
                coordination_quality = 1.0 - (stops_per_vehicle / 2.0)
            else:
                coordination_quality = max(0.0, 1.0 - (stops_per_vehicle / 4.0))
        
        return NetworkMetrics(
            average_travel_time=avg_travel_time,
            stops_per_vehicle=stops_per_vehicle,
            coordination_quality=coordination_quality,
            total_throughput=self._total_vehicles_processed,
            network_delay=self._network_delay
        )
    
    def update_metrics(self, vehicle_travel_time: float, vehicle_stops: int) -> None:
        """
        Update network metrics with data from a vehicle.
        
        Args:
            vehicle_travel_time: Time taken for vehicle to traverse network (seconds)
            vehicle_stops: Number of stops the vehicle made
        """
        self._total_travel_time += vehicle_travel_time
        self._total_stops += vehicle_stops
        self._vehicle_count += 1
        self._total_vehicles_processed += 1
    
    def reset_metrics(self) -> None:
        """Reset all metrics counters."""
        self._total_vehicles_processed = 0
        self._total_stops = 0
        self._total_travel_time = 0.0
        self._vehicle_count = 0
        self._network_delay = 0.0
