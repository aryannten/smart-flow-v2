"""
Turn Lane Controller Module for SMART FLOW v2

Manages turn lane signals and protected phases.
"""

from typing import Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum
from src.models import SignalPhase, PhaseType, SignalState


class TurnType(Enum):
    """Turn types"""
    LEFT = "left"
    RIGHT = "right"
    U_TURN = "u_turn"


@dataclass
class TurnLaneConfig:
    """Turn lane configuration"""
    lane_name: str
    turn_type: TurnType
    region: Tuple[int, int, int, int]  # (x, y, width, height)
    conflicting_movements: List[str]
    minimum_green: int
    maximum_green: int


class TurnLaneController:
    """
    Manages turn lane signals and protected phases.
    
    This controller handles:
    - Calculating turn demand from vehicle detections
    - Determining when to activate protected turn phases
    - Creating turn signal phases with appropriate timing
    - Identifying conflicting movements for safety
    """
    
    def __init__(self, turn_lane_config: Dict[str, TurnLaneConfig], 
                 protected_threshold: int = 3):
        """
        Initialize turn lane controller.
        
        Args:
            turn_lane_config: Dictionary mapping lane names to TurnLaneConfig
            protected_threshold: Minimum vehicles to activate protected phase (default: 3)
        """
        self.turn_lane_config = turn_lane_config
        self.protected_threshold = protected_threshold
    
    def calculate_turn_demand(self, detections: List) -> Dict[str, int]:
        """
        Calculate turn demand from detections.
        
        Counts vehicles in each turn lane region based on their position.
        
        Args:
            detections: List of vehicle detections with bbox and center attributes
            
        Returns:
            Dictionary mapping turn lane name to vehicle count
        """
        turn_demand = {lane: 0 for lane in self.turn_lane_config.keys()}
        
        for detection in detections:
            # Get detection center point
            if hasattr(detection, 'center'):
                center_x, center_y = detection.center
            elif hasattr(detection, 'bbox'):
                # Calculate center from bbox
                x, y, w, h = detection.bbox
                center_x = x + w // 2
                center_y = y + h // 2
            else:
                continue
            
            # Check which turn lane region contains this detection
            for lane_name, config in self.turn_lane_config.items():
                region_x, region_y, region_w, region_h = config.region
                
                # Check if detection center is within region
                if (region_x <= center_x < region_x + region_w and
                    region_y <= center_y < region_y + region_h):
                    turn_demand[lane_name] += 1
                    break  # Each detection belongs to at most one turn lane
        
        return turn_demand
    
    def should_activate_protected_phase(self, lane: str, demand: int) -> bool:
        """
        Determine if protected phase should be activated.
        
        Protected phases are activated when:
        1. Demand meets or exceeds the threshold
        2. The lane is configured in the system
        
        Args:
            lane: Turn lane identifier
            demand: Number of vehicles waiting
            
        Returns:
            True if protected phase should be activated, False otherwise
        """
        if lane not in self.turn_lane_config:
            return False
        
        # Activate protected phase if demand meets threshold
        return demand >= self.protected_threshold
    
    def create_turn_phase(self, lane: str, turn_type: TurnType) -> SignalPhase:
        """
        Create turn signal phase.
        
        Creates a SignalPhase object for the turn lane with appropriate
        phase type and timing based on configuration.
        
        Args:
            lane: Turn lane identifier
            turn_type: Type of turn (LEFT, RIGHT, U_TURN)
            
        Returns:
            SignalPhase for the turn movement
            
        Raises:
            ValueError: If lane is not configured
        """
        if lane not in self.turn_lane_config:
            raise ValueError(f"Turn lane '{lane}' not found in configuration")
        
        config = self.turn_lane_config[lane]
        
        # Map turn type to phase type
        if turn_type == TurnType.LEFT:
            phase_type = PhaseType.PROTECTED_LEFT
        elif turn_type == TurnType.RIGHT:
            phase_type = PhaseType.PROTECTED_RIGHT
        else:  # U_TURN or other
            phase_type = PhaseType.PERMISSIVE_TURN
        
        # Use minimum green time as default duration
        duration = float(config.minimum_green)
        
        # Create and return signal phase
        return SignalPhase(
            phase_type=phase_type,
            lanes=[lane],
            duration=duration,
            state=SignalState.GREEN
        )
    
    def get_conflicting_movements(self, turn_lane: str) -> List[str]:
        """
        Get conflicting movements for turn lane.
        
        Returns the list of lanes/movements that conflict with the given
        turn lane and must be stopped during a protected turn phase.
        
        Args:
            turn_lane: Turn lane identifier
            
        Returns:
            List of conflicting lane identifiers
            
        Raises:
            ValueError: If turn_lane is not configured
        """
        if turn_lane not in self.turn_lane_config:
            raise ValueError(f"Turn lane '{turn_lane}' not found in configuration")
        
        config = self.turn_lane_config[turn_lane]
        return config.conflicting_movements.copy()
