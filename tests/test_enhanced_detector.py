"""
Unit tests for EnhancedDetector module.
"""
import pytest
import numpy as np
from src.enhanced_detector import (
    EnhancedDetector, Detection, DetectionResult, TrackedObject,
    VehicleType, SimpleTracker
)


def test_enhanced_detector_initialization():
    """Test EnhancedDetector initialization."""
    detector = EnhancedDetector(model_path="yolov8n.pt", confidence_threshold=0.5)
    
    assert detector is not None, "Detector should be initialized"
    assert detector.model is not None, "YOLO model should be loaded"
    assert detector.confidence_threshold == 0.5, "Confidence threshold should be set"
    assert detector.tracker is not None, "Tracker should be initialized"


def test_detection_result_structure():
    """Test DetectionResult dataclass structure."""
    vehicles = [Detection(bbox=(10, 10, 50, 50), confidence=0.9, class_id=2, class_name='car')]
    pedestrians = [Detection(bbox=(100, 100, 30, 60), confidence=0.8, class_id=0, class_name='person')]
    emergency = []
    
    result = DetectionResult(
        vehicles=vehicles,
        pedestrians=pedestrians,
        emergency_vehicles=emergency,
        timestamp=1.0
    )
    
    assert len(result.vehicles) == 1, "Should have 1 vehicle"
    assert len(result.pedestrians) == 1, "Should have 1 pedestrian"
    assert len(result.emergency_vehicles) == 0, "Should have 0 emergency vehicles"
    assert result.timestamp == 1.0, "Timestamp should be set"


def test_detection_center_calculation():
    """Test that Detection automatically calculates center point."""
    detection = Detection(bbox=(100, 200, 50, 60), confidence=0.9, class_id=2, class_name='car')
    
    # Center should be (x + w/2, y + h/2) = (100 + 25, 200 + 30) = (125, 230)
    assert detection.center == (125, 230), "Center should be calculated correctly"


def test_classify_vehicle_type_car():
    """Test vehicle type classification for car."""
    detector = EnhancedDetector(model_path="yolov8n.pt", confidence_threshold=0.5)
    
    detection = Detection(bbox=(10, 10, 50, 50), confidence=0.9, class_id=2, class_name='car')
    vehicle_type = detector.classify_vehicle_type(detection)
    
    assert vehicle_type == VehicleType.CAR, "Should classify as CAR"


def test_classify_vehicle_type_truck():
    """Test vehicle type classification for truck."""
    detector = EnhancedDetector(model_path="yolov8n.pt", confidence_threshold=0.5)
    
    detection = Detection(bbox=(10, 10, 80, 100), confidence=0.9, class_id=7, class_name='truck')
    vehicle_type = detector.classify_vehicle_type(detection)
    
    assert vehicle_type == VehicleType.TRUCK, "Should classify as TRUCK"


def test_classify_vehicle_type_bus():
    """Test vehicle type classification for bus."""
    detector = EnhancedDetector(model_path="yolov8n.pt", confidence_threshold=0.5)
    
    detection = Detection(bbox=(10, 10, 100, 120), confidence=0.9, class_id=5, class_name='bus')
    vehicle_type = detector.classify_vehicle_type(detection)
    
    assert vehicle_type == VehicleType.BUS, "Should classify as BUS"


def test_classify_vehicle_type_motorcycle():
    """Test vehicle type classification for motorcycle."""
    detector = EnhancedDetector(model_path="yolov8n.pt", confidence_threshold=0.5)
    
    detection = Detection(bbox=(10, 10, 30, 40), confidence=0.9, class_id=3, class_name='motorcycle')
    vehicle_type = detector.classify_vehicle_type(detection)
    
    assert vehicle_type == VehicleType.MOTORCYCLE, "Should classify as MOTORCYCLE"


def test_classify_vehicle_type_bicycle():
    """Test vehicle type classification for bicycle."""
    detector = EnhancedDetector(model_path="yolov8n.pt", confidence_threshold=0.5)
    
    detection = Detection(bbox=(10, 10, 25, 35), confidence=0.9, class_id=1, class_name='bicycle')
    vehicle_type = detector.classify_vehicle_type(detection)
    
    assert vehicle_type == VehicleType.BICYCLE, "Should classify as BICYCLE"


def test_is_emergency_vehicle_small_car():
    """Test that small cars are not classified as emergency vehicles."""
    detector = EnhancedDetector(model_path="yolov8n.pt", confidence_threshold=0.5)
    
    # Small car
    detection = Detection(bbox=(10, 10, 50, 50), confidence=0.9, class_id=2, class_name='car')
    
    assert not detector.is_emergency_vehicle(detection), "Small car should not be emergency vehicle"


def test_is_emergency_vehicle_large_truck():
    """Test that large trucks might be classified as emergency vehicles."""
    detector = EnhancedDetector(model_path="yolov8n.pt", confidence_threshold=0.5)
    
    # Large truck (area > 50000)
    detection = Detection(bbox=(10, 10, 300, 200), confidence=0.9, class_id=7, class_name='truck')
    
    # Large trucks have a chance of being emergency vehicles based on size heuristic
    result = detector.is_emergency_vehicle(detection)
    assert isinstance(result, bool), "Should return boolean"


def test_detect_all_on_black_frame():
    """Test detect_all on a simple black frame."""
    detector = EnhancedDetector(model_path="yolov8n.pt", confidence_threshold=0.5)
    
    # Create black frame
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    
    result = detector.detect_all(frame, timestamp=1.0)
    
    assert isinstance(result, DetectionResult), "Should return DetectionResult"
    assert isinstance(result.vehicles, list), "Vehicles should be a list"
    assert isinstance(result.pedestrians, list), "Pedestrians should be a list"
    assert isinstance(result.emergency_vehicles, list), "Emergency vehicles should be a list"
    assert result.timestamp == 1.0, "Timestamp should be set"


def test_simple_tracker_initialization():
    """Test SimpleTracker initialization."""
    tracker = SimpleTracker(max_age=30, min_hits=3, iou_threshold=0.3)
    
    assert tracker.max_age == 30, "Max age should be set"
    assert tracker.min_hits == 3, "Min hits should be set"
    assert tracker.iou_threshold == 0.3, "IoU threshold should be set"
    assert len(tracker.tracks) == 0, "Should start with no tracks"
    assert tracker.next_id == 0, "Next ID should start at 0"


def test_simple_tracker_single_detection():
    """Test tracking a single detection."""
    tracker = SimpleTracker(max_age=30, min_hits=1, iou_threshold=0.3)
    
    detection = Detection(bbox=(100, 100, 50, 50), confidence=0.9, class_id=2, class_name='car')
    
    tracked = tracker.update([detection], fps=30.0)
    
    # With min_hits=1, should get one tracked object
    assert len(tracked) == 1, "Should have 1 tracked object"
    assert tracked[0].object_id == 0, "First object should have ID 0"
    assert len(tracked[0].trajectory) == 1, "Should have 1 point in trajectory"


def test_simple_tracker_multiple_frames():
    """Test tracking across multiple frames."""
    tracker = SimpleTracker(max_age=30, min_hits=1, iou_threshold=0.3)
    
    # Frame 1
    detection1 = Detection(bbox=(100, 100, 50, 50), confidence=0.9, class_id=2, class_name='car')
    tracked1 = tracker.update([detection1], fps=30.0)
    
    # Frame 2 - same object moved slightly
    detection2 = Detection(bbox=(105, 105, 50, 50), confidence=0.9, class_id=2, class_name='car')
    tracked2 = tracker.update([detection2], fps=30.0)
    
    assert len(tracked2) == 1, "Should still have 1 tracked object"
    assert tracked2[0].object_id == 0, "Should maintain same ID"
    assert len(tracked2[0].trajectory) == 2, "Should have 2 points in trajectory"


def test_simple_tracker_new_object():
    """Test tracker creating new track for new object."""
    tracker = SimpleTracker(max_age=30, min_hits=1, iou_threshold=0.3)
    
    # Frame 1 - one object
    detection1 = Detection(bbox=(100, 100, 50, 50), confidence=0.9, class_id=2, class_name='car')
    tracked1 = tracker.update([detection1], fps=30.0)
    
    # Frame 2 - two objects (original + new one far away)
    detection2a = Detection(bbox=(105, 105, 50, 50), confidence=0.9, class_id=2, class_name='car')
    detection2b = Detection(bbox=(400, 400, 50, 50), confidence=0.9, class_id=2, class_name='car')
    tracked2 = tracker.update([detection2a, detection2b], fps=30.0)
    
    assert len(tracked2) == 2, "Should have 2 tracked objects"
    assert tracked2[0].object_id != tracked2[1].object_id, "Should have different IDs"


def test_simple_tracker_lost_track():
    """Test tracker aging out lost tracks."""
    tracker = SimpleTracker(max_age=2, min_hits=1, iou_threshold=0.3)
    
    # Frame 1 - one object
    detection1 = Detection(bbox=(100, 100, 50, 50), confidence=0.9, class_id=2, class_name='car')
    tracker.update([detection1], fps=30.0)
    
    # Frame 2 - no detections (object lost)
    tracker.update([], fps=30.0)
    
    # Frame 3 - still no detections
    tracker.update([], fps=30.0)
    
    # Frame 4 - still no detections (should be removed now, age > max_age)
    tracked = tracker.update([], fps=30.0)
    
    assert len(tracked) == 0, "Lost track should be removed after max_age"


def test_track_objects_integration():
    """Test track_objects method integration."""
    detector = EnhancedDetector(model_path="yolov8n.pt", confidence_threshold=0.5)
    
    detections = [
        Detection(bbox=(100, 100, 50, 50), confidence=0.9, class_id=2, class_name='car'),
        Detection(bbox=(200, 200, 50, 50), confidence=0.9, class_id=2, class_name='car')
    ]
    
    tracked = detector.track_objects(detections, fps=30.0)
    
    assert isinstance(tracked, list), "Should return list of tracked objects"
    # Note: With default min_hits=3, we won't see tracks until 3 frames
    # So this might be empty on first call


def test_iou_calculation():
    """Test IoU calculation in tracker."""
    tracker = SimpleTracker()
    
    # Identical boxes
    bbox1 = (100, 100, 50, 50)
    bbox2 = (100, 100, 50, 50)
    iou = tracker._calculate_iou(bbox1, bbox2)
    assert iou == 1.0, "Identical boxes should have IoU of 1.0"
    
    # Non-overlapping boxes
    bbox3 = (100, 100, 50, 50)
    bbox4 = (200, 200, 50, 50)
    iou = tracker._calculate_iou(bbox3, bbox4)
    assert iou == 0.0, "Non-overlapping boxes should have IoU of 0.0"
    
    # Partially overlapping boxes
    bbox5 = (100, 100, 50, 50)
    bbox6 = (125, 125, 50, 50)
    iou = tracker._calculate_iou(bbox5, bbox6)
    assert 0.0 < iou < 1.0, "Partially overlapping boxes should have IoU between 0 and 1"


def test_distance_calculation():
    """Test distance calculation in tracker."""
    tracker = SimpleTracker()
    
    # Same point
    point1 = (100, 100)
    point2 = (100, 100)
    distance = tracker._calculate_distance(point1, point2)
    assert distance == 0.0, "Same point should have distance 0"
    
    # Different points
    point3 = (0, 0)
    point4 = (3, 4)
    distance = tracker._calculate_distance(point3, point4)
    assert distance == 5.0, "Distance should be 5 (3-4-5 triangle)"
