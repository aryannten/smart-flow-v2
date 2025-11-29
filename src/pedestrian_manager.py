"""
Pedestrian Manager Module for SMART FLOW v2

Manages pedestrian detection and crosswalk signals.
"""

from typing import Dict, List
from dataclasses import dataclass
from enum import Enum


class WalkSignalState(Enum):
    """Walk signal states"""
    DONT_WALK = "dont_walk"
    WALK = "walk"
    FLASHING_DONT_WALK = "flashing_dont_walk"


@dataclass
class CrosswalkRegion:
    """Crosswalk region definition"""
    name: str
    region: tuple  # (x1, y1, x2, y2)
    conflicting_lanes: List[str]
    crossing_distance: float  # meters


class PedestrianManager:
    """
    Manages pedestrian detection and crosswalk signals.
    
    Tracks pedestrians at crosswalks, calculates crossing times,
    and manages walk signal states.
    """
    
    # Constants for crossing time calculation
    BASE_CROSSING_TIME = 7.0  # Base time in seconds for one pedestrian
    ADDITIONAL_TIME_PER_PEDESTRIAN = 1.0  # Additional seconds per extra pedestrian
    WALKING_SPEED = 1.2  # meters per second (typical pedestrian walking speed)
    
    # Minimum pedestrian count to trigger crossing
    MIN_PEDESTRIANS_FOR_CROSSING = 1
    
    def __init__(self, crosswalk_config: Dict[str, CrosswalkRegion]):
        """
        Initialize pedestrian manager.
        
        Args:
            crosswalk_config: Dictionary of crosswalk configurations
        """
        self.crosswalk_config = crosswalk_config
        
        # Track pedestrian counts by crosswalk
        self.pedestrian_counts: Dict[str, int] = {
            name: 0 for name in crosswalk_config.keys()
        }
        
        # Track walk signal states by crosswalk
        self.walk_signal_states: Dict[str, WalkSignalState] = {
            name: WalkSignalState.DONT_WALK for name in crosswalk_config.keys()
        }
        
        # Track time remaining in current signal state
        self.signal_time_remaining: Dict[str, float] = {
            name: 0.0 for name in crosswalk_config.keys()
        }
    
    def detect_pedestrians(self, detections: List) -> Dict[str, int]:
        """
        Detect pedestrians by crosswalk.
        
        Counts pedestrians in each crosswalk region based on their bounding box center.
        
        Args:
            detections: List of pedestrian detections (Detection objects)
            
        Returns:
            Dictionary mapping crosswalk name to pedestrian count
        """
        # Reset counts
        counts = {name: 0 for name in self.crosswalk_config.keys()}
        
        # Count pedestrians in each crosswalk region
        for detection in detections:
            # Calculate center point of detection bounding box
            bbox = detection.bbox  # (x, y, width, height)
            center_x = bbox[0] + bbox[2] // 2
            center_y = bbox[1] + bbox[3] // 2
            
            # Check which crosswalk region contains this pedestrian
            for crosswalk_name, crosswalk in self.crosswalk_config.items():
                region = crosswalk.region  # (x1, y1, x2, y2)
                x1, y1, x2, y2 = region
                
                # Check if center point is within crosswalk region
                if x1 <= center_x <= x2 and y1 <= center_y <= y2:
                    counts[crosswalk_name] += 1
                    break  # Each pedestrian only counted in one crosswalk
        
        # Update internal state
        self.pedestrian_counts = counts
        
        return counts
    
    def calculate_crossing_time(self, crosswalk: str, count: int) -> float:
        """
        Calculate required crossing time based on pedestrian count and crossing distance.
        
        Uses the crosswalk distance and typical walking speed to calculate base time,
        then adds additional time for larger groups.
        
        Args:
            crosswalk: Crosswalk identifier
            count: Number of pedestrians
            
        Returns:
            Required crossing time in seconds
        """
        if crosswalk not in self.crosswalk_config:
            raise ValueError(f"Unknown crosswalk: {crosswalk}")
        
        if count <= 0:
            return 0.0
        
        # Get crossing distance for this crosswalk
        crossing_distance = self.crosswalk_config[crosswalk].crossing_distance
        
        # Calculate base time from distance and walking speed
        base_time = crossing_distance / self.WALKING_SPEED
        
        # Add extra time for larger groups (they take longer to start/finish crossing)
        if count > 1:
            additional_time = (count - 1) * self.ADDITIONAL_TIME_PER_PEDESTRIAN
            total_time = base_time + additional_time
        else:
            total_time = base_time
        
        # Ensure minimum crossing time
        return max(total_time, self.BASE_CROSSING_TIME)
    
    def is_crossing_needed(self, crosswalk: str) -> bool:
        """
        Check if crossing is needed for a crosswalk.
        
        A crossing is needed if there are pedestrians waiting at the crosswalk.
        
        Args:
            crosswalk: Crosswalk identifier
            
        Returns:
            True if crossing needed, False otherwise
        """
        if crosswalk not in self.crosswalk_config:
            raise ValueError(f"Unknown crosswalk: {crosswalk}")
        
        # Check if there are enough pedestrians waiting
        count = self.pedestrian_counts.get(crosswalk, 0)
        return count >= self.MIN_PEDESTRIANS_FOR_CROSSING
    
    def get_walk_signal_state(self, crosswalk: str) -> WalkSignalState:
        """
        Get current walk signal state for a crosswalk.
        
        Args:
            crosswalk: Crosswalk identifier
            
        Returns:
            Current walk signal state
        """
        if crosswalk not in self.crosswalk_config:
            raise ValueError(f"Unknown crosswalk: {crosswalk}")
        
        return self.walk_signal_states.get(crosswalk, WalkSignalState.DONT_WALK)
    
    def set_walk_signal_state(self, crosswalk: str, state: WalkSignalState, duration: float = 0.0) -> None:
        """
        Set walk signal state for a crosswalk.
        
        Args:
            crosswalk: Crosswalk identifier
            state: New walk signal state
            duration: Duration for this state in seconds (0 means indefinite)
        """
        if crosswalk not in self.crosswalk_config:
            raise ValueError(f"Unknown crosswalk: {crosswalk}")
        
        self.walk_signal_states[crosswalk] = state
        self.signal_time_remaining[crosswalk] = duration
    
    def update(self, elapsed_time: float) -> None:
        """
        Update signal states based on elapsed time.
        
        Handles automatic transitions between walk signal states.
        
        Args:
            elapsed_time: Time elapsed since last update in seconds
        """
        for crosswalk in self.crosswalk_config.keys():
            if self.signal_time_remaining[crosswalk] > 0:
                self.signal_time_remaining[crosswalk] -= elapsed_time
                
                # Check if time expired
                if self.signal_time_remaining[crosswalk] <= 0:
                    current_state = self.walk_signal_states[crosswalk]
                    
                    # Transition to next state
                    if current_state == WalkSignalState.WALK:
                        # After WALK, go to FLASHING_DONT_WALK
                        self.walk_signal_states[crosswalk] = WalkSignalState.FLASHING_DONT_WALK
                        self.signal_time_remaining[crosswalk] = 5.0  # 5 seconds of flashing
                    elif current_state == WalkSignalState.FLASHING_DONT_WALK:
                        # After FLASHING, go to DONT_WALK
                        self.walk_signal_states[crosswalk] = WalkSignalState.DONT_WALK
                        self.signal_time_remaining[crosswalk] = 0.0
    
    def activate_crossing(self, crosswalk: str) -> float:
        """
        Activate pedestrian crossing for a crosswalk.
        
        Sets the walk signal to WALK and returns the required crossing time.
        
        Args:
            crosswalk: Crosswalk identifier
            
        Returns:
            Required crossing time in seconds
        """
        if crosswalk not in self.crosswalk_config:
            raise ValueError(f"Unknown crosswalk: {crosswalk}")
        
        count = self.pedestrian_counts.get(crosswalk, 0)
        crossing_time = self.calculate_crossing_time(crosswalk, count)
        
        # Set walk signal
        self.set_walk_signal_state(crosswalk, WalkSignalState.WALK, crossing_time)
        
        return crossing_time
    
    def get_conflicting_lanes(self, crosswalk: str) -> List[str]:
        """
        Get list of lanes that conflict with a crosswalk.
        
        Args:
            crosswalk: Crosswalk identifier
            
        Returns:
            List of conflicting lane names
        """
        if crosswalk not in self.crosswalk_config:
            raise ValueError(f"Unknown crosswalk: {crosswalk}")
        
        return self.crosswalk_config[crosswalk].conflicting_lanes
