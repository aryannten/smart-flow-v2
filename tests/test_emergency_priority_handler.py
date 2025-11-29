"""
Unit tests for EmergencyPriorityHandler module.
"""

import pytest
from src.emergency_priority_handler import EmergencyPriorityHandler, EmergencyEvent, SignalPlan
from src.enhanced_detector import Detection, DetectionResult, VehicleType
from src.models import Region


class TestEmergencyPriorityHandler:
    """Test suite for EmergencyPriorityHandler"""
    
    def test_initialization(self):
        """Test handler initialization with default parameters"""
        handler = EmergencyPriorityHandler()
        assert handler.emergency_green_duration == 30.0
        assert not handler.is_emergency_active()
        assert handler.get_active_emergency() is None
    
    def test_initialization_custom_duration(self):
        """Test handler initialization with custom duration"""
        handler = EmergencyPriorityHandler(emergency_green_duration=45.0)
        assert handler.emergency_green_duration == 45.0
    
    def test_detect_emergency_no_emergency_vehicles(self):
        """Test detection when no emergency vehicles present"""
        handler = EmergencyPriorityHandler()
        
        # Create regular vehicle detections
        detections = DetectionResult(
            vehicles=[Detection((100, 100, 50, 50), 0.9, 2, "car")],
            pedestrians=[],
            emergency_vehicles=[],
            timestamp=1000.0
        )
        
        result = handler.detect_emergency(detections, timestamp=1000.0)
        assert result is None
    
    def test_detect_emergency_with_emergency_vehicle(self):
        """Test detection when emergency vehicle is present"""
        handler = EmergencyPriorityHandler()
        
        # Create emergency vehicle detection
        emergency_detection = Detection((200, 200, 60, 80), 0.95, 7, "ambulance")
        detections = DetectionResult(
            vehicles=[Detection((100, 100, 50, 50), 0.9, 2, "car")],
            pedestrians=[],
            emergency_vehicles=[emergency_detection],
            timestamp=1000.0
        )
        
        result = handler.detect_emergency(detections, timestamp=1000.0)
        assert result is not None
        assert isinstance(result, EmergencyEvent)
        assert result.vehicle_type == "ambulance"
        assert result.timestamp == 1000.0
        assert result.priority_level == 1  # Ambulance has highest priority
    
    def test_detect_emergency_priority_levels(self):
        """Test that different emergency vehicle types have correct priority levels"""
        handler = EmergencyPriorityHandler()
        
        # Test ambulance (priority 1)
        ambulance = Detection((200, 200, 60, 80), 0.95, 7, "ambulance")
        detections = DetectionResult([], [], [ambulance], 1000.0)
        result = handler.detect_emergency(detections)
        assert result.priority_level == 1
        
        # Test fire truck (priority 2)
        fire_truck = Detection((200, 200, 60, 80), 0.95, 7, "fire_truck")
        detections = DetectionResult([], [], [fire_truck], 1000.0)
        result = handler.detect_emergency(detections)
        assert result.priority_level == 2
        
        # Test police (priority 3)
        police = Detection((200, 200, 60, 80), 0.95, 7, "police")
        detections = DetectionResult([], [], [police], 1000.0)
        result = handler.detect_emergency(detections)
        assert result.priority_level == 3
    
    def test_calculate_priority_lane_vehicle_in_lane(self):
        """Test calculating which lane contains the emergency vehicle"""
        handler = EmergencyPriorityHandler()
        
        # Create lane regions
        lanes = {
            "north": Region(0, 0, 320, 240, "north"),
            "south": Region(320, 240, 320, 240, "south"),
            "east": Region(320, 0, 320, 240, "east"),
            "west": Region(0, 240, 320, 240, "west")
        }
        
        # Create emergency vehicle in north lane
        emergency_detection = Detection((100, 100, 50, 50), 0.95, 7, "ambulance")
        
        lane = handler.calculate_priority_lane(emergency_detection, lanes)
        assert lane == "north"
    
    def test_calculate_priority_lane_with_tuple_regions(self):
        """Test calculating lane with tuple-based regions"""
        handler = EmergencyPriorityHandler()
        
        # Create lane regions as tuples
        lanes = {
            "north": (0, 0, 320, 240),
            "south": (320, 240, 320, 240),
            "east": (320, 0, 320, 240),
            "west": (0, 240, 320, 240)
        }
        
        # Create emergency vehicle in south lane
        emergency_detection = Detection((400, 300, 50, 50), 0.95, 7, "fire_truck")
        
        lane = handler.calculate_priority_lane(emergency_detection, lanes)
        assert lane == "south"
    
    def test_calculate_priority_lane_closest_when_outside(self):
        """Test that closest lane is returned when vehicle is outside all lanes"""
        handler = EmergencyPriorityHandler()
        
        lanes = {
            "north": Region(0, 0, 100, 100, "north"),
            "south": Region(200, 200, 100, 100, "south")
        }
        
        # Vehicle far from both lanes but closer to north
        emergency_detection = Detection((50, 150, 50, 50), 0.95, 7, "police")
        
        lane = handler.calculate_priority_lane(emergency_detection, lanes)
        assert lane in ["north", "south"]  # Should return one of them
    
    def test_create_emergency_plan(self):
        """Test creating an emergency signal plan"""
        handler = EmergencyPriorityHandler(emergency_green_duration=40.0)
        
        plan = handler.create_emergency_plan("north", timestamp=1000.0)
        
        assert isinstance(plan, SignalPlan)
        assert plan.emergency_lane == "north"
        assert plan.duration == 40.0
        assert plan.timestamp == 1000.0
    
    def test_activate_emergency(self):
        """Test activating an emergency event"""
        handler = EmergencyPriorityHandler()
        
        emergency_detection = Detection((100, 100, 50, 50), 0.95, 7, "ambulance")
        event = EmergencyEvent(
            vehicle_type="ambulance",
            lane="",
            detection=emergency_detection,
            timestamp=1000.0,
            priority_level=1
        )
        
        handler.activate_emergency(event, "north")
        
        assert handler.is_emergency_active()
        assert event.lane == "north"
        assert handler.get_active_emergency() == event
    
    def test_clear_emergency(self):
        """Test clearing emergency state"""
        handler = EmergencyPriorityHandler()
        
        # Activate emergency
        emergency_detection = Detection((100, 100, 50, 50), 0.95, 7, "ambulance")
        event = EmergencyEvent(
            vehicle_type="ambulance",
            lane="north",
            detection=emergency_detection,
            timestamp=1000.0,
            priority_level=1
        )
        handler.activate_emergency(event, "north")
        
        assert handler.is_emergency_active()
        
        # Clear emergency
        handler.clear_emergency()
        
        assert not handler.is_emergency_active()
        assert handler.get_active_emergency() is None
    
    def test_should_clear_emergency_before_duration(self):
        """Test that emergency should not clear before duration expires"""
        handler = EmergencyPriorityHandler(emergency_green_duration=30.0)
        
        # Activate emergency
        emergency_detection = Detection((100, 100, 50, 50), 0.95, 7, "ambulance")
        event = EmergencyEvent(
            vehicle_type="ambulance",
            lane="north",
            detection=emergency_detection,
            timestamp=1000.0,
            priority_level=1
        )
        handler.activate_emergency(event, "north")
        
        # Check before duration expires
        assert not handler.should_clear_emergency(current_time=1020.0)  # 20 seconds elapsed
    
    def test_should_clear_emergency_after_duration(self):
        """Test that emergency should clear after duration expires"""
        handler = EmergencyPriorityHandler(emergency_green_duration=30.0)
        
        # Activate emergency
        emergency_detection = Detection((100, 100, 50, 50), 0.95, 7, "ambulance")
        event = EmergencyEvent(
            vehicle_type="ambulance",
            lane="north",
            detection=emergency_detection,
            timestamp=1000.0,
            priority_level=1
        )
        handler.activate_emergency(event, "north")
        
        # Check after duration expires
        assert handler.should_clear_emergency(current_time=1031.0)  # 31 seconds elapsed
    
    def test_emergency_history(self):
        """Test that emergency events are tracked in history"""
        handler = EmergencyPriorityHandler()
        
        # Activate first emergency
        event1 = EmergencyEvent(
            vehicle_type="ambulance",
            lane="north",
            detection=Detection((100, 100, 50, 50), 0.95, 7, "ambulance"),
            timestamp=1000.0,
            priority_level=1
        )
        handler.activate_emergency(event1, "north")
        handler.clear_emergency()
        
        # Activate second emergency
        event2 = EmergencyEvent(
            vehicle_type="fire_truck",
            lane="south",
            detection=Detection((200, 200, 60, 80), 0.95, 7, "fire_truck"),
            timestamp=2000.0,
            priority_level=2
        )
        handler.activate_emergency(event2, "south")
        
        history = handler.get_emergency_history()
        assert len(history) == 2
        assert history[0] == event1
        assert history[1] == event2
    
    def test_full_emergency_lifecycle(self):
        """Test complete emergency vehicle lifecycle"""
        handler = EmergencyPriorityHandler(emergency_green_duration=30.0)
        
        lanes = {
            "north": Region(0, 0, 320, 240, "north"),
            "south": Region(320, 240, 320, 240, "south")
        }
        
        # 1. Detect emergency vehicle
        emergency_detection = Detection((100, 100, 50, 50), 0.95, 7, "ambulance")
        detections = DetectionResult([], [], [emergency_detection], 1000.0)
        
        event = handler.detect_emergency(detections, timestamp=1000.0)
        assert event is not None
        
        # 2. Calculate which lane
        lane = handler.calculate_priority_lane(event, lanes)
        assert lane == "north"
        
        # 3. Create emergency plan
        plan = handler.create_emergency_plan(lane, timestamp=1000.0)
        assert plan.emergency_lane == "north"
        assert plan.duration == 30.0
        
        # 4. Activate emergency
        handler.activate_emergency(event, lane)
        assert handler.is_emergency_active()
        
        # 5. Check during emergency
        assert not handler.should_clear_emergency(current_time=1020.0)
        
        # 6. Check after emergency duration
        assert handler.should_clear_emergency(current_time=1031.0)
        
        # 7. Clear emergency
        handler.clear_emergency()
        assert not handler.is_emergency_active()
        
        # 8. Verify history
        history = handler.get_emergency_history()
        assert len(history) == 1
        assert history[0].vehicle_type == "ambulance"
