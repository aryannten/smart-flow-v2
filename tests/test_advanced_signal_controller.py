"""
Unit tests for AdvancedSignalController module.
"""
import pytest
import time
from src.advanced_signal_controller import (
    AdvancedSignalController, 
    SignalConfig, 
    LaneData, 
    SignalPlan,
    StateTransition
)
from src.models import SignalState, PhaseType


class TestAdvancedSignalController:
    """Unit tests for AdvancedSignalController class."""
    
    def test_initialization_default_config(self):
        """Test AdvancedSignalController initialization with default config."""
        controller = AdvancedSignalController()
        
        assert controller.config.min_green == 10
        assert controller.config.max_green == 60
        assert controller.config.yellow_duration == 3
        assert controller.config.min_cycle_time == 40
        assert controller.config.max_cycle_time == 180
    
    def test_initialization_custom_config(self):
        """Test AdvancedSignalController initialization with custom config."""
        config = SignalConfig(
            min_green=15,
            max_green=45,
            yellow_duration=4,
            min_cycle_time=50,
            max_cycle_time=150
        )
        controller = AdvancedSignalController(config)
        
        assert controller.config.min_green == 15
        assert controller.config.max_green == 45
        assert controller.config.yellow_duration == 4
        assert controller.config.min_cycle_time == 50
        assert controller.config.max_cycle_time == 150
    
    def test_allocate_time_basic(self):
        """Test basic time allocation with simple lane data."""
        controller = AdvancedSignalController()
        
        lane_data = {
            'north': LaneData(
                vehicle_count=10,
                queue_length=20.0,
                wait_time=5.0,
                vehicle_types={'car': 10},
                has_emergency=False,
                pedestrian_count=0
            ),
            'south': LaneData(
                vehicle_count=5,
                queue_length=10.0,
                wait_time=3.0,
                vehicle_types={'car': 5},
                has_emergency=False,
                pedestrian_count=0
            )
        }
        
        plan = controller.allocate_time(lane_data)
        
        assert isinstance(plan, SignalPlan)
        assert len(plan.phases) > 0
        assert plan.total_cycle_time > 0
        assert not plan.emergency_override
    
    def test_allocate_time_with_emergency(self):
        """Test time allocation with emergency vehicle."""
        controller = AdvancedSignalController()
        
        lane_data = {
            'north': LaneData(
                vehicle_count=10,
                queue_length=20.0,
                wait_time=5.0,
                vehicle_types={'car': 10},
                has_emergency=True,  # Emergency vehicle present
                pedestrian_count=0
            ),
            'south': LaneData(
                vehicle_count=5,
                queue_length=10.0,
                wait_time=3.0,
                vehicle_types={'car': 5},
                has_emergency=False,
                pedestrian_count=0
            )
        }
        
        plan = controller.allocate_time(lane_data)
        
        assert plan.emergency_override
        assert len(plan.phases) == 1
        assert plan.phases[0].phase_type == PhaseType.EMERGENCY
        assert plan.phases[0].lanes == ['north']
    
    def test_vehicle_type_weighting(self):
        """Test that buses get higher priority than cars."""
        controller = AdvancedSignalController()
        
        lane_data_bus = {
            'north': LaneData(
                vehicle_count=5,
                queue_length=10.0,
                wait_time=5.0,
                vehicle_types={'bus': 5},  # 5 buses
                has_emergency=False,
                pedestrian_count=0
            )
        }
        
        lane_data_car = {
            'south': LaneData(
                vehicle_count=5,
                queue_length=10.0,
                wait_time=5.0,
                vehicle_types={'car': 5},  # 5 cars
                has_emergency=False,
                pedestrian_count=0
            )
        }
        
        # Calculate priorities
        priorities_bus = controller._calculate_priorities(lane_data_bus)
        priorities_car = controller._calculate_priorities(lane_data_car)
        
        # Bus lane should have higher priority
        assert priorities_bus['north'] > priorities_car['south']
    
    def test_fairness_boost(self):
        """Test that lanes waiting too long get fairness boost."""
        controller = AdvancedSignalController()
        
        # Set last green time to simulate long wait
        current_time = time.time()
        controller._last_green_times['north'] = current_time - 150.0  # 150 seconds ago
        
        lane_data = {
            'north': LaneData(
                vehicle_count=5,
                queue_length=10.0,
                wait_time=5.0,
                vehicle_types={'car': 5},
                has_emergency=False,
                pedestrian_count=0
            ),
            'south': LaneData(
                vehicle_count=5,
                queue_length=10.0,
                wait_time=5.0,
                vehicle_types={'car': 5},
                has_emergency=False,
                pedestrian_count=0
            )
        }
        
        priorities = controller._calculate_priorities(lane_data)
        
        # North should have higher priority due to fairness boost
        assert priorities['north'] > priorities['south']
    
    def test_handle_emergency(self):
        """Test emergency handling."""
        controller = AdvancedSignalController()
        
        # Initialize states
        controller._states = {
            'north': SignalState.RED,
            'south': SignalState.GREEN
        }
        
        # Handle emergency on north
        controller.handle_emergency('north')
        
        assert controller.is_emergency_active()
        assert controller._emergency_lane == 'north'
        assert controller._states['north'] == SignalState.GREEN
        assert controller._states['south'] == SignalState.RED
    
    def test_add_pedestrian_phase(self):
        """Test adding pedestrian phase."""
        controller = AdvancedSignalController()
        
        controller.add_pedestrian_phase('crosswalk_1', 5)
        
        assert len(controller._pending_pedestrian_phases) == 1
        assert controller._pending_pedestrian_phases[0] == ('crosswalk_1', 5)
    
    def test_add_turn_phase(self):
        """Test adding turn phase."""
        controller = AdvancedSignalController()
        
        controller.add_turn_phase('left_turn_north', PhaseType.PROTECTED_LEFT, 8)
        
        assert len(controller._pending_turn_phases) == 1
        assert controller._pending_turn_phases[0] == ('left_turn_north', PhaseType.PROTECTED_LEFT, 8)
    
    def test_override_signal(self):
        """Test manual signal override."""
        controller = AdvancedSignalController()
        
        # Initialize states
        controller._states = {'north': SignalState.RED}
        
        # Override to green for 10 seconds
        controller.override_signal('north', SignalState.GREEN, 10.0)
        
        assert controller._manual_override_active
        assert controller._manual_override_lane == 'north'
        assert controller._states['north'] == SignalState.GREEN
    
    def test_override_signal_invalid_lane(self):
        """Test that override fails for invalid lane."""
        controller = AdvancedSignalController()
        
        with pytest.raises(ValueError):
            controller.override_signal('invalid_lane', SignalState.GREEN, 10.0)
    
    def test_clear_emergency(self):
        """Test clearing emergency state."""
        controller = AdvancedSignalController()
        
        controller._emergency_active = True
        controller._emergency_lane = 'north'
        
        controller.clear_emergency()
        
        assert not controller.is_emergency_active()
        assert controller._emergency_lane is None
    
    def test_multi_factor_allocation(self):
        """Test that allocation considers multiple factors."""
        controller = AdvancedSignalController()
        
        lane_data = {
            'north': LaneData(
                vehicle_count=10,  # High count
                queue_length=50.0,  # Long queue
                wait_time=10.0,  # Long wait
                vehicle_types={'bus': 2, 'car': 8},  # Has buses
                has_emergency=False,
                pedestrian_count=0
            ),
            'south': LaneData(
                vehicle_count=3,  # Low count
                queue_length=5.0,  # Short queue
                wait_time=2.0,  # Short wait
                vehicle_types={'car': 3},  # Only cars
                has_emergency=False,
                pedestrian_count=0
            )
        }
        
        priorities = controller._calculate_priorities(lane_data)
        
        # North should have much higher priority
        assert priorities['north'] > priorities['south']
    
    def test_cycle_time_constraints(self):
        """Test that cycle time is constrained to min/max."""
        config = SignalConfig(min_cycle_time=60, max_cycle_time=120)
        controller = AdvancedSignalController(config)
        
        # Very low demand
        lane_data = {
            'north': LaneData(
                vehicle_count=1,
                queue_length=1.0,
                wait_time=1.0,
                vehicle_types={'car': 1},
                has_emergency=False,
                pedestrian_count=0
            )
        }
        
        plan = controller.allocate_time(lane_data)
        
        # Should be at least min_cycle_time
        assert plan.total_cycle_time >= config.min_cycle_time
    
    def test_get_transition_history(self):
        """Test getting transition history."""
        controller = AdvancedSignalController()
        
        # Initialize states
        controller._states = {'north': SignalState.RED}
        
        # Override to trigger transition
        controller.override_signal('north', SignalState.GREEN, 10.0)
        
        history = controller.get_transition_history()
        
        assert len(history) > 0
        assert isinstance(history[0], StateTransition)
        assert history[0].lane == 'north'
        assert history[0].old_state == SignalState.RED
        assert history[0].new_state == SignalState.GREEN
    
    def test_queue_length_adjustment(self):
        """Test that long queues get extra time."""
        controller = AdvancedSignalController()
        
        lane_data_long_queue = {
            'north': LaneData(
                vehicle_count=10,
                queue_length=80.0,  # Very long queue
                wait_time=5.0,
                vehicle_types={'car': 10},
                has_emergency=False,
                pedestrian_count=0
            )
        }
        
        lane_data_short_queue = {
            'south': LaneData(
                vehicle_count=10,
                queue_length=10.0,  # Short queue
                wait_time=5.0,
                vehicle_types={'car': 10},
                has_emergency=False,
                pedestrian_count=0
            )
        }
        
        priorities_long = controller._calculate_priorities(lane_data_long_queue)
        priorities_short = controller._calculate_priorities(lane_data_short_queue)
        
        # Long queue should have higher priority
        assert priorities_long['north'] > priorities_short['south']
