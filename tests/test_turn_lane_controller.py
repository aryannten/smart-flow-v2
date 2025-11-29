"""
Unit tests for TurnLaneController module.

Tests turn lane management including:
- Turn demand calculation
- Protected phase activation logic
- Turn phase creation
- Conflict detection
"""

import pytest
from src.turn_lane_controller import TurnLaneController, TurnLaneConfig, TurnType
from src.models import PhaseType, SignalState
from dataclasses import dataclass
from typing import Tuple


@dataclass
class MockDetection:
    """Mock detection for testing"""
    bbox: Tuple[int, int, int, int]
    center: Tuple[int, int]


class TestTurnLaneController:
    """Test suite for TurnLaneController"""
    
    @pytest.fixture
    def sample_config(self):
        """Create sample turn lane configuration"""
        return {
            "north_left": TurnLaneConfig(
                lane_name="north_left",
                turn_type=TurnType.LEFT,
                region=(0, 0, 100, 200),
                conflicting_movements=["south_through", "south_left", "east_through"],
                minimum_green=10,
                maximum_green=30
            ),
            "south_right": TurnLaneConfig(
                lane_name="south_right",
                turn_type=TurnType.RIGHT,
                region=(200, 200, 100, 200),
                conflicting_movements=["east_pedestrian"],
                minimum_green=8,
                maximum_green=20
            ),
            "east_left": TurnLaneConfig(
                lane_name="east_left",
                turn_type=TurnType.LEFT,
                region=(300, 0, 100, 200),
                conflicting_movements=["west_through", "north_through"],
                minimum_green=10,
                maximum_green=30
            )
        }
    
    @pytest.fixture
    def controller(self, sample_config):
        """Create TurnLaneController instance"""
        return TurnLaneController(sample_config, protected_threshold=3)
    
    def test_initialization(self, sample_config):
        """Test controller initialization"""
        controller = TurnLaneController(sample_config, protected_threshold=5)
        
        assert controller.turn_lane_config == sample_config
        assert controller.protected_threshold == 5
    
    def test_calculate_turn_demand_empty(self, controller):
        """Test turn demand calculation with no detections"""
        detections = []
        demand = controller.calculate_turn_demand(detections)
        
        assert demand == {
            "north_left": 0,
            "south_right": 0,
            "east_left": 0
        }
    
    def test_calculate_turn_demand_single_lane(self, controller):
        """Test turn demand with vehicles in one lane"""
        detections = [
            MockDetection(bbox=(10, 10, 20, 20), center=(20, 20)),
            MockDetection(bbox=(30, 50, 20, 20), center=(40, 60)),
            MockDetection(bbox=(50, 100, 20, 20), center=(60, 110))
        ]
        
        demand = controller.calculate_turn_demand(detections)
        
        assert demand["north_left"] == 3
        assert demand["south_right"] == 0
        assert demand["east_left"] == 0
    
    def test_calculate_turn_demand_multiple_lanes(self, controller):
        """Test turn demand with vehicles in multiple lanes"""
        detections = [
            MockDetection(bbox=(10, 10, 20, 20), center=(20, 20)),  # north_left
            MockDetection(bbox=(30, 50, 20, 20), center=(40, 60)),  # north_left
            MockDetection(bbox=(220, 220, 20, 20), center=(230, 230)),  # south_right
            MockDetection(bbox=(320, 50, 20, 20), center=(330, 60)),  # east_left
            MockDetection(bbox=(350, 100, 20, 20), center=(360, 110))  # east_left
        ]
        
        demand = controller.calculate_turn_demand(detections)
        
        assert demand["north_left"] == 2
        assert demand["south_right"] == 1
        assert demand["east_left"] == 2
    
    def test_calculate_turn_demand_bbox_only(self, controller):
        """Test turn demand with detections that only have bbox"""
        @dataclass
        class BboxOnlyDetection:
            bbox: Tuple[int, int, int, int]
        
        detections = [
            BboxOnlyDetection(bbox=(10, 10, 20, 20)),  # center at (20, 20)
            BboxOnlyDetection(bbox=(30, 50, 20, 20)),  # center at (40, 60)
        ]
        
        demand = controller.calculate_turn_demand(detections)
        
        assert demand["north_left"] == 2
    
    def test_should_activate_protected_phase_below_threshold(self, controller):
        """Test protected phase activation below threshold"""
        assert not controller.should_activate_protected_phase("north_left", 2)
        assert not controller.should_activate_protected_phase("south_right", 0)
    
    def test_should_activate_protected_phase_at_threshold(self, controller):
        """Test protected phase activation at threshold"""
        assert controller.should_activate_protected_phase("north_left", 3)
        assert controller.should_activate_protected_phase("south_right", 3)
    
    def test_should_activate_protected_phase_above_threshold(self, controller):
        """Test protected phase activation above threshold"""
        assert controller.should_activate_protected_phase("north_left", 5)
        assert controller.should_activate_protected_phase("east_left", 10)
    
    def test_should_activate_protected_phase_invalid_lane(self, controller):
        """Test protected phase activation for non-existent lane"""
        assert not controller.should_activate_protected_phase("invalid_lane", 10)
    
    def test_create_turn_phase_left_turn(self, controller):
        """Test creating left turn phase"""
        phase = controller.create_turn_phase("north_left", TurnType.LEFT)
        
        assert phase.phase_type == PhaseType.PROTECTED_LEFT
        assert phase.lanes == ["north_left"]
        assert phase.duration == 10.0  # minimum_green
        assert phase.state == SignalState.GREEN
    
    def test_create_turn_phase_right_turn(self, controller):
        """Test creating right turn phase"""
        phase = controller.create_turn_phase("south_right", TurnType.RIGHT)
        
        assert phase.phase_type == PhaseType.PROTECTED_RIGHT
        assert phase.lanes == ["south_right"]
        assert phase.duration == 8.0  # minimum_green
        assert phase.state == SignalState.GREEN
    
    def test_create_turn_phase_u_turn(self, controller):
        """Test creating U-turn phase"""
        phase = controller.create_turn_phase("east_left", TurnType.U_TURN)
        
        assert phase.phase_type == PhaseType.PERMISSIVE_TURN
        assert phase.lanes == ["east_left"]
        assert phase.duration == 10.0
        assert phase.state == SignalState.GREEN
    
    def test_create_turn_phase_invalid_lane(self, controller):
        """Test creating phase for non-existent lane"""
        with pytest.raises(ValueError, match="not found in configuration"):
            controller.create_turn_phase("invalid_lane", TurnType.LEFT)
    
    def test_get_conflicting_movements_north_left(self, controller):
        """Test getting conflicts for north left turn"""
        conflicts = controller.get_conflicting_movements("north_left")
        
        assert conflicts == ["south_through", "south_left", "east_through"]
    
    def test_get_conflicting_movements_south_right(self, controller):
        """Test getting conflicts for south right turn"""
        conflicts = controller.get_conflicting_movements("south_right")
        
        assert conflicts == ["east_pedestrian"]
    
    def test_get_conflicting_movements_returns_copy(self, controller):
        """Test that conflicting movements returns a copy"""
        conflicts1 = controller.get_conflicting_movements("north_left")
        conflicts2 = controller.get_conflicting_movements("north_left")
        
        # Modify one list
        conflicts1.append("new_conflict")
        
        # Other list should be unchanged
        assert "new_conflict" not in conflicts2
        assert len(conflicts2) == 3
    
    def test_get_conflicting_movements_invalid_lane(self, controller):
        """Test getting conflicts for non-existent lane"""
        with pytest.raises(ValueError, match="not found in configuration"):
            controller.get_conflicting_movements("invalid_lane")
    
    def test_custom_threshold(self, sample_config):
        """Test controller with custom threshold"""
        controller = TurnLaneController(sample_config, protected_threshold=5)
        
        assert not controller.should_activate_protected_phase("north_left", 4)
        assert controller.should_activate_protected_phase("north_left", 5)
        assert controller.should_activate_protected_phase("north_left", 6)
    
    def test_edge_case_detection_on_boundary(self, controller):
        """Test detection exactly on region boundary"""
        # Detection at exact boundary of north_left region (0, 0, 100, 200)
        detections = [
            MockDetection(bbox=(0, 0, 10, 10), center=(0, 0)),  # Top-left corner
            MockDetection(bbox=(90, 190, 10, 10), center=(99, 199))  # Bottom-right inside
        ]
        
        demand = controller.calculate_turn_demand(detections)
        
        assert demand["north_left"] == 2
    
    def test_edge_case_detection_outside_all_regions(self, controller):
        """Test detection outside all configured regions"""
        detections = [
            MockDetection(bbox=(500, 500, 20, 20), center=(510, 510))
        ]
        
        demand = controller.calculate_turn_demand(detections)
        
        # Should not be counted in any lane
        assert all(count == 0 for count in demand.values())
