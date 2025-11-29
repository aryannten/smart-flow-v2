"""
Signal Controller module for SMART FLOW traffic signal simulation system.

Manages signal states and timing allocation based on traffic density.
"""

from typing import Dict, Optional
from src.models import SignalState


class SignalController:
    """
    Manages traffic signal states and timing allocation.
    
    This class implements a signal state machine that transitions lanes through
    green, yellow, and red states based on traffic density. It ensures mutual
    exclusion (only one lane green at a time) and enforces timing constraints.
    """
    
    def __init__(self, min_green: int = 10, max_green: int = 60, yellow_duration: int = 3):
        """
        Initialize the signal controller with timing parameters.
        
        Args:
            min_green: Minimum green time in seconds (default: 10)
            max_green: Maximum green time in seconds (default: 60)
            yellow_duration: Yellow signal duration in seconds (default: 3)
        """
        self.min_green = min_green
        self.max_green = max_green
        self.yellow_duration = yellow_duration
        
        # Current signal states for all lanes
        self._states: Dict[str, SignalState] = {}
        
        # Allocated green times for current cycle
        self._green_times: Dict[str, int] = {}
        
        # Remaining time for current state
        self._remaining_times: Dict[str, float] = {}
        
        # Current active lane (the one that's green or yellow)
        self._active_lane: Optional[str] = None
        
        # Queue of lanes to process in current cycle
        self._lane_queue: list = []
        
    def allocate_green_time(self, density_ratios: Dict[str, float]) -> Dict[str, int]:
        """
        Calculate green time allocation based on density ratios.
        
        Implements proportional allocation where lanes with higher density
        receive more green time, subject to min/max constraints.
        
        Args:
            density_ratios: Dictionary mapping lane names to density ratios (0.0 to 1.0)
            
        Returns:
            Dict[str, int]: Dictionary mapping lane names to green time in seconds
        """
        # Base time to distribute (40 seconds total)
        base_time = 40
        
        green_times = {}
        for lane, ratio in density_ratios.items():
            # Calculate proportional time
            time = int(base_time * ratio)
            
            # Enforce min/max bounds
            time = max(self.min_green, min(self.max_green, time))
            
            green_times[lane] = time
        
        return green_times
    
    def start_cycle(self, green_times: Dict[str, int]) -> None:
        """
        Start a new signal cycle with the given green time allocations.
        
        Initializes all lanes to red state and sets up the queue for
        sequential green signal allocation.
        
        Args:
            green_times: Dictionary mapping lane names to green time in seconds
        """
        # Store green times for this cycle
        self._green_times = green_times.copy()
        
        # Initialize all lanes to red
        self._states = {lane: SignalState.RED for lane in green_times.keys()}
        self._remaining_times = {lane: 0.0 for lane in green_times.keys()}
        
        # Create queue of lanes sorted by green time (highest first)
        self._lane_queue = sorted(
            green_times.keys(),
            key=lambda lane: green_times[lane],
            reverse=True
        )
        
        # Start with first lane
        self._active_lane = None
        self._advance_to_next_lane()
    
    def _advance_to_next_lane(self) -> None:
        """
        Advance to the next lane in the queue.
        
        Transitions the next lane to green state and sets its timer.
        """
        if self._lane_queue:
            # Get next lane from queue
            next_lane = self._lane_queue.pop(0)
            
            # Set it to green
            self._states[next_lane] = SignalState.GREEN
            self._remaining_times[next_lane] = float(self._green_times[next_lane])
            self._active_lane = next_lane
        else:
            # No more lanes in queue
            self._active_lane = None
    
    def update_state(self, elapsed_time: float) -> None:
        """
        Update signal states based on elapsed time.
        
        Advances the signal state machine, transitioning lanes through
        green → yellow → red sequence.
        
        Args:
            elapsed_time: Time elapsed since last update in seconds
        """
        if self._active_lane is None:
            return
        
        # Decrease remaining time for active lane
        self._remaining_times[self._active_lane] -= elapsed_time
        
        # Check if time expired
        if self._remaining_times[self._active_lane] <= 0:
            current_state = self._states[self._active_lane]
            
            if current_state == SignalState.GREEN:
                # Transition to yellow
                self._states[self._active_lane] = SignalState.YELLOW
                self._remaining_times[self._active_lane] = float(self.yellow_duration)
                
            elif current_state == SignalState.YELLOW:
                # Transition to red
                self._states[self._active_lane] = SignalState.RED
                self._remaining_times[self._active_lane] = 0.0
                
                # Advance to next lane
                self._advance_to_next_lane()
    
    def get_current_states(self) -> Dict[str, SignalState]:
        """
        Get current signal states for all lanes.
        
        Returns:
            Dict[str, SignalState]: Dictionary mapping lane names to current signal states
        """
        return self._states.copy()
    
    def get_remaining_times(self) -> Dict[str, float]:
        """
        Get remaining time for current state for all lanes.
        
        Returns:
            Dict[str, float]: Dictionary mapping lane names to remaining time in seconds
        """
        return self._remaining_times.copy()
