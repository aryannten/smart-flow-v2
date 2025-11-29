"""
Unit tests for SignalController module.
"""
import pytest
from src.signal_controller import SignalController
from src.models import SignalState


class TestSignalController:
    """Unit tests for SignalController class."""
    
    def test_initialization(self):
        """Test SignalController initialization with default parameters."""
        controller = SignalController()
        
        assert controller.min_green == 10
        assert controller.max_green == 60
        assert controller.yellow_duration == 3
    
    def test_initialization_custom_parameters(self):
        """Test SignalController initialization with custom parameters."""
        controller = SignalController(min_green=15, max_green=45, yellow_duration=4)
        
        assert controller.min_green == 15
        assert controller.max_green == 45
        assert controller.yellow_duration == 4
    
    def test_allocate_green_time_equal_ratios(self):
        """Test green time allocation with equal density ratios."""
        controller = SignalController()
        
        # Equal ratios (0.25 each for 4 lanes)
        density_ratios = {
            'north': 0.25,
            'south': 0.25,
            'east': 0.25,
            'west': 0.25
        }
        
        green_times = controller.allocate_green_time(density_ratios)
        
        # All lanes should get equal time (10 seconds, the minimum)
        assert green_times['north'] == 10
        assert green_times['south'] == 10
        assert green_times['east'] == 10
        assert green_times['west'] == 10
    
    def test_allocate_green_time_unequal_ratios(self):
        """Test green time allocation with unequal density ratios."""
        controller = SignalController()
        
        # Unequal ratios
        density_ratios = {
            'north': 0.5,   # 50% of traffic
            'south': 0.3,   # 30% of traffic
            'east': 0.15,   # 15% of traffic
            'west': 0.05    # 5% of traffic
        }
        
        green_times = controller.allocate_green_time(density_ratios)
        
        # Verify proportionality: higher ratio should get more time
        assert green_times['north'] >= green_times['south']
        assert green_times['south'] >= green_times['east']
        assert green_times['east'] >= green_times['west']
        
        # Verify bounds
        for lane, time in green_times.items():
            assert time >= 10, f"Green time for {lane} should be >= 10"
            assert time <= 60, f"Green time for {lane} should be <= 60"
    
    def test_allocate_green_time_enforces_min_bound(self):
        """Test that green time allocation enforces minimum bound."""
        controller = SignalController(min_green=10)
        
        # Very low ratio that would result in < 10 seconds
        density_ratios = {
            'north': 0.01,  # 1% of traffic
            'south': 0.99   # 99% of traffic
        }
        
        green_times = controller.allocate_green_time(density_ratios)
        
        # Even with 1% ratio, should get at least 10 seconds
        assert green_times['north'] >= 10
    
    def test_allocate_green_time_enforces_max_bound(self):
        """Test that green time allocation enforces maximum bound."""
        controller = SignalController(max_green=60)
        
        # Very high ratio that would result in > 60 seconds
        density_ratios = {
            'north': 0.99,  # 99% of traffic
            'south': 0.01   # 1% of traffic
        }
        
        green_times = controller.allocate_green_time(density_ratios)
        
        # Even with 99% ratio, should not exceed 60 seconds
        assert green_times['north'] <= 60
    
    def test_start_cycle_initializes_all_red(self):
        """Test that start_cycle initializes all lanes to red."""
        controller = SignalController()
        
        green_times = {
            'north': 20,
            'south': 15,
            'east': 25,
            'west': 10
        }
        
        controller.start_cycle(green_times)
        
        # Get initial states
        states = controller.get_current_states()
        
        # First lane should be green (highest green time)
        assert states['east'] == SignalState.GREEN
        
        # Others should be red
        assert states['north'] == SignalState.RED
        assert states['south'] == SignalState.RED
        assert states['west'] == SignalState.RED
    
    def test_start_cycle_orders_by_green_time(self):
        """Test that start_cycle orders lanes by green time (highest first)."""
        controller = SignalController()
        
        green_times = {
            'north': 10,
            'south': 30,
            'east': 20,
            'west': 15
        }
        
        controller.start_cycle(green_times)
        
        # First lane should be the one with highest green time (south: 30)
        states = controller.get_current_states()
        assert states['south'] == SignalState.GREEN
    
    def test_update_state_green_to_yellow_transition(self):
        """Test state transition from green to yellow."""
        controller = SignalController(yellow_duration=3)
        
        green_times = {'north': 15}
        controller.start_cycle(green_times)
        
        # Initial state should be green
        states = controller.get_current_states()
        assert states['north'] == SignalState.GREEN
        
        # Simulate green time passing
        controller.update_state(15.0)
        
        # Should transition to yellow
        states = controller.get_current_states()
        assert states['north'] == SignalState.YELLOW
    
    def test_update_state_yellow_to_red_transition(self):
        """Test state transition from yellow to red."""
        controller = SignalController(yellow_duration=3)
        
        green_times = {'north': 15}
        controller.start_cycle(green_times)
        
        # Advance through green
        controller.update_state(15.0)
        
        # Should be yellow now
        states = controller.get_current_states()
        assert states['north'] == SignalState.YELLOW
        
        # Advance through yellow
        controller.update_state(3.0)
        
        # Should transition to red
        states = controller.get_current_states()
        assert states['north'] == SignalState.RED
    
    def test_update_state_advances_to_next_lane(self):
        """Test that update_state advances to next lane after red."""
        controller = SignalController(yellow_duration=3)
        
        green_times = {
            'north': 10,
            'south': 15
        }
        controller.start_cycle(green_times)
        
        # First lane (south with 15s) should be green
        states = controller.get_current_states()
        assert states['south'] == SignalState.GREEN
        assert states['north'] == SignalState.RED
        
        # Advance through south's green and yellow
        controller.update_state(15.0)  # Green expires
        controller.update_state(3.0)   # Yellow expires
        
        # Now north should be green
        states = controller.get_current_states()
        assert states['north'] == SignalState.GREEN
        assert states['south'] == SignalState.RED
    
    def test_get_current_states_returns_copy(self):
        """Test that get_current_states returns a copy, not reference."""
        controller = SignalController()
        
        green_times = {'north': 15}
        controller.start_cycle(green_times)
        
        states1 = controller.get_current_states()
        states2 = controller.get_current_states()
        
        # Should be equal but not the same object
        assert states1 == states2
        assert states1 is not states2
    
    def test_get_remaining_times(self):
        """Test get_remaining_times returns correct values."""
        controller = SignalController()
        
        green_times = {'north': 20}
        controller.start_cycle(green_times)
        
        # Initial remaining time should be 20 seconds
        remaining = controller.get_remaining_times()
        assert remaining['north'] == 20.0
        
        # Advance 5 seconds
        controller.update_state(5.0)
        
        # Remaining time should be 15 seconds
        remaining = controller.get_remaining_times()
        assert remaining['north'] == 15.0
    
    def test_timing_constraints(self):
        """Test that timing constraints are properly enforced."""
        controller = SignalController(min_green=10, max_green=60)
        
        # Test with extreme ratios
        density_ratios = {
            'north': 0.001,  # Very low
            'south': 0.999   # Very high
        }
        
        green_times = controller.allocate_green_time(density_ratios)
        
        # Both should be within bounds
        assert 10 <= green_times['north'] <= 60
        assert 10 <= green_times['south'] <= 60
