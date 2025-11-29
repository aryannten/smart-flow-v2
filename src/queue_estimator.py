"""
Queue Estimator Module for SMART FLOW v2

Estimates spatial queue length from vehicle positions.
"""

from typing import List, Tuple, Optional
from dataclasses import dataclass
import math


@dataclass
class QueueMetrics:
    """Queue metrics for a lane"""
    length_meters: float
    vehicle_count: int
    density: float  # vehicles per meter
    head_position: Tuple[int, int]
    tail_position: Tuple[int, int]
    is_spillback: bool


class QueueEstimator:
    """
    Estimates spatial queue length from vehicle positions.
    
    This class analyzes vehicle positions to estimate queue length, density,
    and spillback conditions. It uses spatial analysis to determine the extent
    of queued vehicles waiting at a signal.
    """
    
    # Constants for queue estimation
    QUEUE_SPACING_THRESHOLD = 150  # pixels - max spacing between vehicles in a queue
    PIXELS_TO_METERS = 0.1  # conversion factor (configurable based on camera setup)
    SPILLBACK_THRESHOLD = 0.85  # queue is 85% of lane length
    AVERAGE_VEHICLE_LENGTH = 5.0  # meters
    SATURATION_FLOW_RATE = 1800  # vehicles per hour per lane (standard traffic engineering)
    
    def __init__(self, pixels_to_meters: float = 0.1, spillback_threshold: float = 0.85):
        """
        Initialize queue estimator.
        
        Args:
            pixels_to_meters: Conversion factor from pixels to meters
            spillback_threshold: Ratio of queue length to lane length for spillback detection
        """
        self.pixels_to_meters = pixels_to_meters
        self.spillback_threshold = spillback_threshold
    
    def estimate_queue(self, detections: List, lane: str) -> QueueMetrics:
        """
        Estimate queue metrics for a lane.
        
        Args:
            detections: List of vehicle detections with bbox and center attributes
            lane: Lane identifier (not used in current implementation but kept for interface)
            
        Returns:
            QueueMetrics object with comprehensive queue information
        """
        if not detections:
            # No vehicles - empty queue
            return QueueMetrics(
                length_meters=0.0,
                vehicle_count=0,
                density=0.0,
                head_position=(0, 0),
                tail_position=(0, 0),
                is_spillback=False
            )
        
        # Extract vehicle positions (centers)
        vehicle_positions = [det.center for det in detections]
        
        # Calculate queue length
        queue_length_pixels = self._calculate_queue_length_pixels(vehicle_positions)
        queue_length_meters = queue_length_pixels * self.pixels_to_meters
        
        # Find head and tail positions
        head_pos, tail_pos = self._find_queue_endpoints(vehicle_positions)
        
        # Calculate density
        vehicle_count = len(detections)
        density = vehicle_count / queue_length_meters if queue_length_meters > 0 else 0.0
        
        # Spillback detection (requires lane length - for now use heuristic)
        # A very long queue relative to vehicle count suggests spillback
        is_spillback = self._detect_spillback_heuristic(queue_length_meters, vehicle_count)
        
        return QueueMetrics(
            length_meters=queue_length_meters,
            vehicle_count=vehicle_count,
            density=density,
            head_position=head_pos,
            tail_position=tail_pos,
            is_spillback=is_spillback
        )
    
    def calculate_queue_length(self, vehicle_positions: List[Tuple[int, int]]) -> float:
        """
        Calculate queue length from vehicle positions.
        
        This method implements the algorithm described in the design document:
        1. Sort vehicles by position
        2. Find queue head (closest to intersection)
        3. Find queue tail (farthest vehicle still part of queue)
        4. Calculate distance between head and tail
        
        Args:
            vehicle_positions: List of (x, y) positions in pixels
            
        Returns:
            Queue length in meters
        """
        if len(vehicle_positions) < 2:
            return 0.0
        
        queue_length_pixels = self._calculate_queue_length_pixels(vehicle_positions)
        return queue_length_pixels * self.pixels_to_meters
    
    def _calculate_queue_length_pixels(self, vehicle_positions: List[Tuple[int, int]]) -> float:
        """
        Calculate queue length in pixels.
        
        Args:
            vehicle_positions: List of (x, y) positions
            
        Returns:
            Queue length in pixels
        """
        if not vehicle_positions:
            return 0.0
        
        if len(vehicle_positions) == 1:
            return 0.0
        
        # Sort vehicles by distance from origin (approximation of lane direction)
        # In a real system, this would use lane direction vector
        sorted_vehicles = sorted(vehicle_positions, 
                                key=lambda pos: math.sqrt(pos[0]**2 + pos[1]**2))
        
        # Find queue head (closest to intersection - smallest distance)
        head = sorted_vehicles[0]
        
        # Find queue tail by checking spacing between consecutive vehicles
        tail = head
        for i in range(1, len(sorted_vehicles)):
            prev_pos = sorted_vehicles[i-1]
            curr_pos = sorted_vehicles[i]
            
            # Calculate spacing between vehicles
            spacing = self._calculate_distance(prev_pos, curr_pos)
            
            # If spacing is below threshold, vehicle is part of queue
            if spacing < self.QUEUE_SPACING_THRESHOLD:
                tail = curr_pos
            else:
                # Queue ends here - large gap indicates end of queue
                break
        
        # Calculate queue length as distance from head to tail
        queue_length = self._calculate_distance(head, tail)
        return queue_length
    
    def _calculate_distance(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
        """
        Calculate Euclidean distance between two positions.
        
        Args:
            pos1: First position (x, y)
            pos2: Second position (x, y)
            
        Returns:
            Distance in pixels
        """
        dx = pos2[0] - pos1[0]
        dy = pos2[1] - pos1[1]
        return math.sqrt(dx**2 + dy**2)
    
    def _find_queue_endpoints(self, vehicle_positions: List[Tuple[int, int]]) -> Tuple[Tuple[int, int], Tuple[int, int]]:
        """
        Find head and tail positions of the queue.
        
        Args:
            vehicle_positions: List of (x, y) positions
            
        Returns:
            Tuple of (head_position, tail_position)
        """
        if not vehicle_positions:
            return ((0, 0), (0, 0))
        
        if len(vehicle_positions) == 1:
            return (vehicle_positions[0], vehicle_positions[0])
        
        # Sort vehicles by distance from origin
        sorted_vehicles = sorted(vehicle_positions, 
                                key=lambda pos: math.sqrt(pos[0]**2 + pos[1]**2))
        
        # Head is closest to intersection
        head = sorted_vehicles[0]
        
        # Find tail using same logic as queue length calculation
        tail = head
        for i in range(1, len(sorted_vehicles)):
            prev_pos = sorted_vehicles[i-1]
            curr_pos = sorted_vehicles[i]
            spacing = self._calculate_distance(prev_pos, curr_pos)
            
            if spacing < self.QUEUE_SPACING_THRESHOLD:
                tail = curr_pos
            else:
                break
        
        return (head, tail)
    
    def detect_queue_spillback(self, queue_length: float, lane_length: float) -> bool:
        """
        Detect if queue is spilling back beyond acceptable limits.
        
        Spillback occurs when the queue extends too far back in the lane,
        potentially blocking upstream intersections or access points.
        
        Args:
            queue_length: Current queue length in meters
            lane_length: Total lane length in meters
            
        Returns:
            True if spillback detected, False otherwise
        """
        if lane_length <= 0:
            return False
        
        queue_ratio = queue_length / lane_length
        return queue_ratio >= self.spillback_threshold
    
    def _detect_spillback_heuristic(self, queue_length_meters: float, vehicle_count: int) -> bool:
        """
        Detect spillback using heuristic when lane length is unknown.
        
        Uses the ratio of queue length to expected length based on vehicle count.
        If queue is much longer than expected, it suggests congestion/spillback.
        
        Args:
            queue_length_meters: Queue length in meters
            vehicle_count: Number of vehicles in queue
            
        Returns:
            True if spillback likely, False otherwise
        """
        if vehicle_count == 0:
            return False
        
        # Expected queue length based on average vehicle spacing
        expected_length = vehicle_count * self.AVERAGE_VEHICLE_LENGTH
        
        # If actual queue is much longer than expected, suggests spillback
        # (vehicles are more spread out, indicating backed up traffic)
        return queue_length_meters > expected_length * 1.5
    
    def predict_clearance_time(self, queue_metrics: QueueMetrics, green_time: float) -> float:
        """
        Predict time required to clear the queue.
        
        Uses standard traffic engineering saturation flow rate to estimate
        how long it will take to clear the current queue.
        
        Args:
            queue_metrics: Current queue metrics
            green_time: Allocated green time in seconds
            
        Returns:
            Predicted clearance time in seconds
        """
        if queue_metrics.vehicle_count == 0:
            return 0.0
        
        # Saturation flow rate: vehicles per hour per lane
        # Convert to vehicles per second
        flow_rate_per_second = self.SATURATION_FLOW_RATE / 3600.0
        
        # Time to clear queue = number of vehicles / flow rate
        clearance_time = queue_metrics.vehicle_count / flow_rate_per_second
        
        return clearance_time
