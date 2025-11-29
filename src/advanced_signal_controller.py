"""
Advanced Signal Controller Module for SMART FLOW v2

Manages complex signal states with turn phases, pedestrian crossings, and emergency priority.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import time

from src.signal_controller import SignalController
from src.models import SignalState, SignalPhase, PhaseType


@dataclass
class StateTransition:
    """Represents a signal state transition"""
    lane: str
    old_state: SignalState
    new_state: SignalState
    timestamp: float


@dataclass
class SignalPlan:
    """Signal plan with phases"""
    phases: List[SignalPhase]
    total_cycle_time: float
    emergency_override: bool = False


@dataclass
class SignalConfig:
    """Configuration for advanced signal controller"""
    min_green: int = 10
    max_green: int = 60
    yellow_duration: int = 3
    min_cycle_time: int = 40
    max_cycle_time: int = 180
    fairness_threshold: float = 120.0  # Maximum wait time before fairness boost (seconds)
    fairness_boost_factor: float = 1.5  # Multiplier for fairness boost


@dataclass
class LaneData:
    """Comprehensive lane data for priority calculation"""
    vehicle_count: int
    queue_length: float  # in meters
    wait_time: float  # average wait time in seconds
    vehicle_types: Dict[str, int]
    has_emergency: bool
    pedestrian_count: int


class AdvancedSignalController(SignalController):
    """
    Advanced signal controller with complex phase management.
    
    Extends the basic SignalController with:
    - Multi-factor allocation (count, queue, wait time, vehicle type)
    - Emergency vehicle priority
    - Pedestrian crossing phases
    - Turn lane phases
    - Manual override capability
    - Starvation prevention
    """
    
    def __init__(self, config: Optional[SignalConfig] = None):
        """
        Initialize advanced signal controller.
        
        Args:
            config: Signal configuration (uses defaults if None)
        """
        self.config = config or SignalConfig()
        
        # Initialize base controller
        super().__init__(
            min_green=self.config.min_green,
            max_green=self.config.max_green,
            yellow_duration=self.config.yellow_duration
        )
        
        # Track wait times for fairness
        self._lane_wait_times: Dict[str, float] = {}
        self._last_green_times: Dict[str, float] = {}
        
        # Emergency override state
        self._emergency_active: bool = False
        self._emergency_lane: Optional[str] = None
        self._emergency_start_time: Optional[float] = None
        
        # Manual override state
        self._manual_override_active: bool = False
        self._manual_override_lane: Optional[str] = None
        self._manual_override_end_time: Optional[float] = None
        
        # Current signal plan
        self._current_plan: Optional[SignalPlan] = None
        self._current_phase_index: int = 0
        self._phase_start_time: float = 0.0
        
        # Pedestrian phases to add
        self._pending_pedestrian_phases: List[Tuple[str, int]] = []  # (crosswalk, demand)
        
        # Turn phases to add
        self._pending_turn_phases: List[Tuple[str, PhaseType, int]] = []  # (lane, phase_type, demand)
        
        # State transition history
        self._transition_history: List[StateTransition] = []
    
    def allocate_time(self, lane_data: Dict[str, LaneData]) -> SignalPlan:
        """
        Calculate signal plan with multi-factor allocation.
        
        Considers:
        - Vehicle count
        - Queue length
        - Wait time (with fairness boost)
        - Vehicle type weighting
        - Emergency priority
        - Pedestrian demand
        - Turn lane demand
        
        Args:
            lane_data: Dictionary mapping lane names to LaneData
            
        Returns:
            SignalPlan with phases and timing
        """
        # Check for emergency override
        emergency_override = any(data.has_emergency for data in lane_data.values())
        
        if emergency_override:
            # Find emergency lane
            emergency_lane = next(
                (lane for lane, data in lane_data.items() if data.has_emergency),
                None
            )
            if emergency_lane:
                return self._create_emergency_plan(emergency_lane)
        
        # Calculate priority scores for each lane
        priorities = self._calculate_priorities(lane_data)
        
        # Allocate green times based on priorities
        green_times = self._allocate_green_times(priorities, lane_data)
        
        # Create phases
        phases = self._create_phases(green_times, lane_data)
        
        # Calculate total cycle time
        total_cycle_time = sum(phase.duration for phase in phases)
        
        # Enforce cycle time constraints
        if total_cycle_time < self.config.min_cycle_time:
            # Scale up phases proportionally
            scale_factor = self.config.min_cycle_time / total_cycle_time
            for phase in phases:
                phase.duration *= scale_factor
            total_cycle_time = self.config.min_cycle_time
        elif total_cycle_time > self.config.max_cycle_time:
            # Scale down phases proportionally
            scale_factor = self.config.max_cycle_time / total_cycle_time
            for phase in phases:
                phase.duration *= scale_factor
            total_cycle_time = self.config.max_cycle_time
        
        plan = SignalPlan(
            phases=phases,
            total_cycle_time=total_cycle_time,
            emergency_override=False
        )
        
        self._current_plan = plan
        self._current_phase_index = 0
        self._phase_start_time = time.time()
        
        return plan
    
    def _calculate_priorities(self, lane_data: Dict[str, LaneData]) -> Dict[str, float]:
        """
        Calculate priority scores using multi-factor algorithm.
        
        Priority = (vehicle_count * 1.0) + 
                   (queue_length * 0.5) + 
                   (wait_time * 0.3) + 
                   (vehicle_type_weight * 0.2) +
                   (fairness_boost)
        
        Args:
            lane_data: Dictionary mapping lane names to LaneData
            
        Returns:
            Dictionary mapping lane names to priority scores
        """
        priorities = {}
        current_time = time.time()
        
        for lane, data in lane_data.items():
            # Base factors
            count_factor = data.vehicle_count * 1.0
            queue_factor = data.queue_length * 0.5
            wait_factor = data.wait_time * 0.3
            
            # Vehicle type weighting
            type_weight = 0.0
            for vehicle_type, count in data.vehicle_types.items():
                if vehicle_type == 'bus':
                    type_weight += count * 2.0  # Buses get double weight
                elif vehicle_type == 'truck':
                    type_weight += count * 1.5  # Trucks get 1.5x weight
                elif vehicle_type == 'bicycle':
                    type_weight += count * 0.8  # Bicycles get slightly less
                else:
                    type_weight += count * 1.0  # Cars get normal weight
            type_factor = type_weight * 0.2
            
            # Fairness boost for lanes waiting too long
            fairness_boost = 0.0
            last_green = self._last_green_times.get(lane, 0.0)
            if last_green > 0:
                time_since_green = current_time - last_green
                if time_since_green > self.config.fairness_threshold:
                    # Apply exponential boost for excessive wait
                    fairness_boost = (time_since_green - self.config.fairness_threshold) * self.config.fairness_boost_factor
            
            # Total priority
            priority = count_factor + queue_factor + wait_factor + type_factor + fairness_boost
            priorities[lane] = max(0.0, priority)  # Ensure non-negative
        
        return priorities
    
    def _allocate_green_times(self, priorities: Dict[str, float], 
                             lane_data: Dict[str, LaneData]) -> Dict[str, int]:
        """
        Allocate green times based on priority scores.
        
        Args:
            priorities: Priority scores for each lane
            lane_data: Lane data for constraints
            
        Returns:
            Dictionary mapping lane names to green time in seconds
        """
        total_priority = sum(priorities.values())
        
        if total_priority == 0:
            # No demand, use minimum times
            return {lane: self.config.min_green for lane in priorities.keys()}
        
        # Base allocation pool
        base_time = 60  # seconds to distribute
        
        green_times = {}
        for lane, priority in priorities.items():
            # Proportional allocation
            ratio = priority / total_priority
            time_allocated = int(base_time * ratio)
            
            # Enforce min/max bounds
            time_allocated = max(self.config.min_green, min(self.config.max_green, time_allocated))
            
            # Adjust for queue length if needed
            data = lane_data[lane]
            if data.queue_length > 50:  # Long queue (>50 meters)
                # Add extra time for long queues
                extra_time = min(10, int(data.queue_length / 10))
                time_allocated += extra_time
                time_allocated = min(self.config.max_green, time_allocated)
            
            green_times[lane] = time_allocated
        
        return green_times
    
    def _create_phases(self, green_times: Dict[str, int], 
                      lane_data: Dict[str, LaneData]) -> List[SignalPhase]:
        """
        Create signal phases including through, turn, and pedestrian phases.
        
        Args:
            green_times: Allocated green times for lanes
            lane_data: Lane data for phase decisions
            
        Returns:
            List of SignalPhase objects
        """
        phases = []
        
        # Sort lanes by green time (highest first)
        sorted_lanes = sorted(green_times.items(), key=lambda x: x[1], reverse=True)
        
        for lane, duration in sorted_lanes:
            # Skip lanes with no demand
            if duration <= 0:
                continue
            
            # Create through phase
            phase = SignalPhase(
                phase_type=PhaseType.THROUGH,
                lanes=[lane],
                duration=float(duration),
                state=SignalState.GREEN
            )
            phases.append(phase)
            
            # Add yellow phase
            yellow_phase = SignalPhase(
                phase_type=PhaseType.THROUGH,
                lanes=[lane],
                duration=float(self.config.yellow_duration),
                state=SignalState.YELLOW
            )
            phases.append(yellow_phase)
        
        # Add pending pedestrian phases
        for crosswalk, demand in self._pending_pedestrian_phases:
            # Calculate crossing time (base 7 seconds + 1 second per pedestrian)
            crossing_time = 7.0 + (demand - 1) * 1.0
            
            ped_phase = SignalPhase(
                phase_type=PhaseType.PEDESTRIAN,
                lanes=[crosswalk],
                duration=crossing_time,
                state=SignalState.GREEN
            )
            phases.append(ped_phase)
        
        # Clear pending pedestrian phases
        self._pending_pedestrian_phases = []
        
        # Add pending turn phases
        for lane, phase_type, demand in self._pending_turn_phases:
            # Turn phase duration based on demand
            turn_duration = max(10, min(30, demand * 3))
            
            turn_phase = SignalPhase(
                phase_type=phase_type,
                lanes=[lane],
                duration=float(turn_duration),
                state=SignalState.GREEN
            )
            phases.append(turn_phase)
            
            # Add yellow phase
            yellow_phase = SignalPhase(
                phase_type=phase_type,
                lanes=[lane],
                duration=float(self.config.yellow_duration),
                state=SignalState.YELLOW
            )
            phases.append(yellow_phase)
        
        # Clear pending turn phases
        self._pending_turn_phases = []
        
        return phases
    
    def _create_emergency_plan(self, emergency_lane: str) -> SignalPlan:
        """
        Create emergency signal plan.
        
        Gives immediate green to emergency lane for 30 seconds.
        
        Args:
            emergency_lane: Lane with emergency vehicle
            
        Returns:
            Emergency SignalPlan
        """
        emergency_phase = SignalPhase(
            phase_type=PhaseType.EMERGENCY,
            lanes=[emergency_lane],
            duration=30.0,
            state=SignalState.GREEN
        )
        
        plan = SignalPlan(
            phases=[emergency_phase],
            total_cycle_time=30.0,
            emergency_override=True
        )
        
        self._current_plan = plan
        self._current_phase_index = 0
        self._phase_start_time = time.time()
        
        return plan
    
    def handle_emergency(self, emergency_lane: str) -> None:
        """
        Handle emergency vehicle priority.
        
        Immediately transitions the emergency lane to green and holds it.
        
        Args:
            emergency_lane: Lane with emergency vehicle
        """
        self._emergency_active = True
        self._emergency_lane = emergency_lane
        self._emergency_start_time = time.time()
        
        # Create and apply emergency plan
        plan = self._create_emergency_plan(emergency_lane)
        
        # Immediately set emergency lane to green
        if emergency_lane in self._states:
            old_state = self._states[emergency_lane]
            self._states[emergency_lane] = SignalState.GREEN
            
            # Set all other lanes to red
            for lane in self._states.keys():
                if lane != emergency_lane:
                    self._states[lane] = SignalState.RED
            
            # Record transition
            transition = StateTransition(
                lane=emergency_lane,
                old_state=old_state,
                new_state=SignalState.GREEN,
                timestamp=time.time()
            )
            self._transition_history.append(transition)
    
    def add_pedestrian_phase(self, crosswalk: str, demand: int) -> None:
        """
        Add pedestrian crossing phase to next cycle.
        
        Args:
            crosswalk: Crosswalk identifier
            demand: Number of pedestrians waiting
        """
        self._pending_pedestrian_phases.append((crosswalk, demand))
    
    def add_turn_phase(self, lane: str, phase_type: PhaseType, demand: int) -> None:
        """
        Add turn phase to next cycle.
        
        Args:
            lane: Turn lane identifier
            phase_type: Type of turn phase (PROTECTED_LEFT, PROTECTED_RIGHT)
            demand: Number of vehicles in turn lane
        """
        self._pending_turn_phases.append((lane, phase_type, demand))
    
    def update_state(self, elapsed_time: float) -> List[StateTransition]:
        """
        Update signal states based on elapsed time.
        
        Returns list of state transitions that occurred.
        
        Args:
            elapsed_time: Time elapsed since last update in seconds
            
        Returns:
            List of StateTransition objects
        """
        transitions = []
        current_time = time.time()
        
        # Check manual override
        if self._manual_override_active:
            if current_time >= self._manual_override_end_time:
                # Override expired
                self._manual_override_active = False
                self._manual_override_lane = None
            else:
                # Override still active, don't update
                return transitions
        
        # Check emergency override
        if self._emergency_active:
            # Emergency lasts for 30 seconds or until cleared
            if self._emergency_start_time and (current_time - self._emergency_start_time) >= 30.0:
                self._emergency_active = False
                self._emergency_lane = None
                self._emergency_start_time = None
            else:
                # Emergency still active
                return transitions
        
        # Update using current plan
        if self._current_plan and self._current_phase_index < len(self._current_plan.phases):
            current_phase = self._current_plan.phases[self._current_phase_index]
            phase_elapsed = current_time - self._phase_start_time
            
            if phase_elapsed >= current_phase.duration:
                # Phase complete, transition to next
                for lane in current_phase.lanes:
                    if lane in self._states:
                        old_state = self._states[lane]
                        
                        # Transition based on current state
                        if current_phase.state == SignalState.GREEN:
                            # Green -> Yellow
                            new_state = SignalState.YELLOW
                        elif current_phase.state == SignalState.YELLOW:
                            # Yellow -> Red
                            new_state = SignalState.RED
                        else:
                            new_state = SignalState.RED
                        
                        self._states[lane] = new_state
                        
                        # Record last green time
                        if old_state == SignalState.GREEN:
                            self._last_green_times[lane] = current_time
                        
                        transition = StateTransition(
                            lane=lane,
                            old_state=old_state,
                            new_state=new_state,
                            timestamp=current_time
                        )
                        transitions.append(transition)
                
                # Move to next phase
                self._current_phase_index += 1
                self._phase_start_time = current_time
                
                # Start next phase if available
                if self._current_phase_index < len(self._current_plan.phases):
                    next_phase = self._current_plan.phases[self._current_phase_index]
                    for lane in next_phase.lanes:
                        if lane in self._states:
                            old_state = self._states[lane]
                            self._states[lane] = next_phase.state
                            
                            transition = StateTransition(
                                lane=lane,
                                old_state=old_state,
                                new_state=next_phase.state,
                                timestamp=current_time
                            )
                            transitions.append(transition)
        else:
            # No plan or plan complete, use base controller
            super().update_state(elapsed_time)
        
        return transitions
    
    def override_signal(self, lane: str, state: SignalState, duration: float) -> None:
        """
        Manually override signal state for a lane.
        
        Args:
            lane: Lane to override
            state: Signal state to set
            duration: Duration of override in seconds
        """
        if lane not in self._states:
            raise ValueError(f"Unknown lane: {lane}")
        
        old_state = self._states[lane]
        self._states[lane] = state
        
        self._manual_override_active = True
        self._manual_override_lane = lane
        self._manual_override_end_time = time.time() + duration
        
        # Record transition
        transition = StateTransition(
            lane=lane,
            old_state=old_state,
            new_state=state,
            timestamp=time.time()
        )
        self._transition_history.append(transition)
    
    def get_transition_history(self) -> List[StateTransition]:
        """
        Get history of state transitions.
        
        Returns:
            List of StateTransition objects
        """
        return self._transition_history.copy()
    
    def clear_emergency(self) -> None:
        """Clear emergency override state."""
        self._emergency_active = False
        self._emergency_lane = None
        self._emergency_start_time = None
    
    def is_emergency_active(self) -> bool:
        """Check if emergency override is active."""
        return self._emergency_active
    
    def get_current_plan(self) -> Optional[SignalPlan]:
        """Get current signal plan."""
        return self._current_plan
