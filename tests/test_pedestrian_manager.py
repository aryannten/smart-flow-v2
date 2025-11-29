"""
Unit tests for PedestrianManager
"""

import pytest
from src.pedestrian_manager import PedestrianManager, CrosswalkRegion, WalkSignalState
from src.models import Detection


class TestPedestrianManager:
    """Test suite for PedestrianManager"""
    
    @pytest.fixture
    def crosswalk_config(self):
        """Create sample crosswalk configuration"""
        return {
            "north": CrosswalkRegion(
                name="north",
                region=(100, 0, 200, 50),  # (x1, y1, x2, y2)
                conflicting_lanes=["south", "east", "west"],
                crossing_distance=10.0  # meters
            ),
            "south": CrosswalkRegion(
                name="south",
                region=(100, 450, 200, 500),
                conflicting_lanes=["north", "east", "west"],
                crossing_distance=10.0
            ),
            "east": CrosswalkRegion(
                name="east",
                region=(450, 200, 500, 300),
                conflicting_lanes=["north", "south", "west"],
                crossing_distance=12.0
            ),
            "west": CrosswalkRegion(
                name="west",
                region=(0, 200, 50, 300),
                conflicting_lanes=["north", "south", "east"],
                crossing_distance=12.0
            )
        }
    
    @pytest.fixture
    def manager(self, crosswalk_config):
        """Create PedestrianManager instance"""
        return PedestrianManager(crosswalk_config)
    
    def test_initialization(self, manager, crosswalk_config):
        """Test manager initializes correctly"""
        assert manager.crosswalk_config == crosswalk_config
        assert len(manager.pedestrian_counts) == 4
        assert all(count == 0 for count in manager.pedestrian_counts.values())
        assert all(state == WalkSignalState.DONT_WALK for state in manager.walk_signal_states.values())
    
    def test_detect_pedestrians_empty(self, manager):
        """Test detecting pedestrians with no detections"""
        counts = manager.detect_pedestrians([])
        assert all(count == 0 for count in counts.values())
    
    def test_detect_pedestrians_single_crosswalk(self, manager):
        """Test detecting pedestrians in a single crosswalk"""
        # Create pedestrian detection in north crosswalk (100, 0, 200, 50)
        detections = [
            Detection(bbox=(140, 20, 20, 40), confidence=0.9, class_name="person")
        ]
        
        counts = manager.detect_pedestrians(detections)
        assert counts["north"] == 1
        assert counts["south"] == 0
        assert counts["east"] == 0
        assert counts["west"] == 0
    
    def test_detect_pedestrians_multiple_crosswalks(self, manager):
        """Test detecting pedestrians in multiple crosswalks"""
        detections = [
            Detection(bbox=(140, 20, 20, 40), confidence=0.9, class_name="person"),  # north
            Detection(bbox=(140, 460, 20, 40), confidence=0.9, class_name="person"),  # south
            Detection(bbox=(460, 240, 20, 40), confidence=0.9, class_name="person"),  # east
        ]
        
        counts = manager.detect_pedestrians(detections)
        assert counts["north"] == 1
        assert counts["south"] == 1
        assert counts["east"] == 1
        assert counts["west"] == 0
    
    def test_detect_pedestrians_multiple_in_same_crosswalk(self, manager):
        """Test detecting multiple pedestrians in same crosswalk"""
        detections = [
            Detection(bbox=(140, 20, 20, 40), confidence=0.9, class_name="person"),
            Detection(bbox=(160, 25, 20, 40), confidence=0.9, class_name="person"),
            Detection(bbox=(180, 30, 20, 40), confidence=0.9, class_name="person"),
        ]
        
        counts = manager.detect_pedestrians(detections)
        assert counts["north"] == 3
    
    def test_calculate_crossing_time_single_pedestrian(self, manager):
        """Test crossing time calculation for single pedestrian"""
        # North crosswalk has 10m distance
        # At 1.2 m/s, base time = 10/1.2 = 8.33 seconds
        # But minimum is 7.0 seconds, so should return max(8.33, 7.0) = 8.33
        time = manager.calculate_crossing_time("north", 1)
        expected = 10.0 / 1.2  # distance / speed
        assert abs(time - expected) < 0.1
    
    def test_calculate_crossing_time_multiple_pedestrians(self, manager):
        """Test crossing time calculation for multiple pedestrians"""
        # Base time + additional time per extra pedestrian
        time = manager.calculate_crossing_time("north", 3)
        base_time = 10.0 / 1.2
        additional_time = 2 * 1.0  # 2 extra pedestrians * 1 second each
        expected = base_time + additional_time
        assert abs(time - expected) < 0.1
    
    def test_calculate_crossing_time_zero_pedestrians(self, manager):
        """Test crossing time with zero pedestrians"""
        time = manager.calculate_crossing_time("north", 0)
        assert time == 0.0
    
    def test_calculate_crossing_time_different_distances(self, manager):
        """Test crossing time accounts for different crosswalk distances"""
        time_north = manager.calculate_crossing_time("north", 1)  # 10m
        time_east = manager.calculate_crossing_time("east", 1)    # 12m
        assert time_east > time_north
    
    def test_calculate_crossing_time_invalid_crosswalk(self, manager):
        """Test crossing time with invalid crosswalk raises error"""
        with pytest.raises(ValueError, match="Unknown crosswalk"):
            manager.calculate_crossing_time("invalid", 1)
    
    def test_is_crossing_needed_no_pedestrians(self, manager):
        """Test crossing not needed when no pedestrians"""
        manager.pedestrian_counts["north"] = 0
        assert not manager.is_crossing_needed("north")
    
    def test_is_crossing_needed_with_pedestrians(self, manager):
        """Test crossing needed when pedestrians present"""
        manager.pedestrian_counts["north"] = 2
        assert manager.is_crossing_needed("north")
    
    def test_is_crossing_needed_minimum_threshold(self, manager):
        """Test crossing needed at minimum threshold"""
        manager.pedestrian_counts["north"] = 1
        assert manager.is_crossing_needed("north")
    
    def test_is_crossing_needed_invalid_crosswalk(self, manager):
        """Test is_crossing_needed with invalid crosswalk raises error"""
        with pytest.raises(ValueError, match="Unknown crosswalk"):
            manager.is_crossing_needed("invalid")
    
    def test_get_walk_signal_state_initial(self, manager):
        """Test initial walk signal state is DONT_WALK"""
        state = manager.get_walk_signal_state("north")
        assert state == WalkSignalState.DONT_WALK
    
    def test_get_walk_signal_state_invalid_crosswalk(self, manager):
        """Test get_walk_signal_state with invalid crosswalk raises error"""
        with pytest.raises(ValueError, match="Unknown crosswalk"):
            manager.get_walk_signal_state("invalid")
    
    def test_set_walk_signal_state(self, manager):
        """Test setting walk signal state"""
        manager.set_walk_signal_state("north", WalkSignalState.WALK, 10.0)
        assert manager.get_walk_signal_state("north") == WalkSignalState.WALK
        assert manager.signal_time_remaining["north"] == 10.0
    
    def test_set_walk_signal_state_invalid_crosswalk(self, manager):
        """Test set_walk_signal_state with invalid crosswalk raises error"""
        with pytest.raises(ValueError, match="Unknown crosswalk"):
            manager.set_walk_signal_state("invalid", WalkSignalState.WALK)
    
    def test_update_signal_timing(self, manager):
        """Test signal state updates with elapsed time"""
        manager.set_walk_signal_state("north", WalkSignalState.WALK, 10.0)
        
        # Update with 3 seconds elapsed
        manager.update(3.0)
        assert manager.signal_time_remaining["north"] == 7.0
        assert manager.get_walk_signal_state("north") == WalkSignalState.WALK
    
    def test_update_signal_transition_walk_to_flashing(self, manager):
        """Test transition from WALK to FLASHING_DONT_WALK"""
        manager.set_walk_signal_state("north", WalkSignalState.WALK, 2.0)
        
        # Update past the duration
        manager.update(3.0)
        assert manager.get_walk_signal_state("north") == WalkSignalState.FLASHING_DONT_WALK
        assert manager.signal_time_remaining["north"] == 5.0
    
    def test_update_signal_transition_flashing_to_dont_walk(self, manager):
        """Test transition from FLASHING_DONT_WALK to DONT_WALK"""
        manager.set_walk_signal_state("north", WalkSignalState.FLASHING_DONT_WALK, 2.0)
        
        # Update past the duration
        manager.update(3.0)
        assert manager.get_walk_signal_state("north") == WalkSignalState.DONT_WALK
        assert manager.signal_time_remaining["north"] == 0.0
    
    def test_activate_crossing(self, manager):
        """Test activating pedestrian crossing"""
        manager.pedestrian_counts["north"] = 2
        
        crossing_time = manager.activate_crossing("north")
        
        assert manager.get_walk_signal_state("north") == WalkSignalState.WALK
        assert crossing_time > 0
        assert manager.signal_time_remaining["north"] == crossing_time
    
    def test_activate_crossing_invalid_crosswalk(self, manager):
        """Test activate_crossing with invalid crosswalk raises error"""
        with pytest.raises(ValueError, match="Unknown crosswalk"):
            manager.activate_crossing("invalid")
    
    def test_get_conflicting_lanes(self, manager):
        """Test getting conflicting lanes for a crosswalk"""
        conflicting = manager.get_conflicting_lanes("north")
        assert set(conflicting) == {"south", "east", "west"}
    
    def test_get_conflicting_lanes_invalid_crosswalk(self, manager):
        """Test get_conflicting_lanes with invalid crosswalk raises error"""
        with pytest.raises(ValueError, match="Unknown crosswalk"):
            manager.get_conflicting_lanes("invalid")
    
    def test_full_crossing_cycle(self, manager):
        """Test complete crossing cycle from detection to completion"""
        # Detect pedestrians
        detections = [
            Detection(bbox=(140, 20, 20, 40), confidence=0.9, class_name="person"),
            Detection(bbox=(160, 25, 20, 40), confidence=0.9, class_name="person"),
        ]
        counts = manager.detect_pedestrians(detections)
        assert counts["north"] == 2
        
        # Check crossing is needed
        assert manager.is_crossing_needed("north")
        
        # Activate crossing
        crossing_time = manager.activate_crossing("north")
        assert manager.get_walk_signal_state("north") == WalkSignalState.WALK
        
        # Simulate time passing during WALK phase
        manager.update(crossing_time + 1.0)
        assert manager.get_walk_signal_state("north") == WalkSignalState.FLASHING_DONT_WALK
        
        # Simulate time passing during FLASHING phase
        manager.update(6.0)
        assert manager.get_walk_signal_state("north") == WalkSignalState.DONT_WALK
