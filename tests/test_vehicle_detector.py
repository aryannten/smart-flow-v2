"""
Unit tests for VehicleDetector module.
"""
import pytest
import numpy as np
from src.vehicle_detector import VehicleDetector
from src.models import Detection, Region, LaneConfiguration, Frame


def test_vehicle_detector_initialization():
    """Test YOLO model loading during initialization."""
    detector = VehicleDetector(confidence_threshold=0.5)
    
    assert detector is not None, "Detector should be initialized"
    assert detector.model is not None, "YOLO model should be loaded"
    assert detector.confidence_threshold == 0.5, "Confidence threshold should be set"


def test_vehicle_detector_custom_threshold():
    """Test VehicleDetector with custom confidence threshold."""
    detector = VehicleDetector(confidence_threshold=0.7)
    
    assert detector.confidence_threshold == 0.7, "Should use custom threshold"


def test_lane_classification_logic():
    """Test lane classification based on spatial position."""
    detector = VehicleDetector(confidence_threshold=0.0)
    
    # Create a simple lane configuration
    frame_width = 800
    frame_height = 600
    lane_config = LaneConfiguration.create_four_way(frame_width, frame_height)
    
    # Create detections in different quadrants
    detections = [
        # North lane (top-left quadrant)
        Detection(bbox=(100, 100, 50, 50), confidence=0.9, class_name='car', lane=None),
        # South lane (bottom-right quadrant)
        Detection(bbox=(500, 400, 50, 50), confidence=0.9, class_name='truck', lane=None),
        # East lane (top-right quadrant)
        Detection(bbox=(500, 100, 50, 50), confidence=0.9, class_name='bus', lane=None),
        # West lane (bottom-left quadrant)
        Detection(bbox=(100, 400, 50, 50), confidence=0.9, class_name='motorcycle', lane=None),
    ]
    
    # Count by lane
    lane_counts = detector.count_by_lane(detections, lane_config.lanes)
    
    # Verify each lane has exactly one vehicle
    assert lane_counts['north'] == 1, "North lane should have 1 vehicle"
    assert lane_counts['south'] == 1, "South lane should have 1 vehicle"
    assert lane_counts['east'] == 1, "East lane should have 1 vehicle"
    assert lane_counts['west'] == 1, "West lane should have 1 vehicle"
    
    # Verify detections were assigned to correct lanes
    assert detections[0].lane == 'north', "First detection should be in north lane"
    assert detections[1].lane == 'south', "Second detection should be in south lane"
    assert detections[2].lane == 'east', "Third detection should be in east lane"
    assert detections[3].lane == 'west', "Fourth detection should be in west lane"


def test_multiple_vehicles_in_same_lane():
    """Test counting multiple vehicles in the same lane."""
    detector = VehicleDetector(confidence_threshold=0.0)
    
    frame_width = 800
    frame_height = 600
    lane_config = LaneConfiguration.create_four_way(frame_width, frame_height)
    
    # Create multiple detections in the north lane
    detections = [
        Detection(bbox=(100, 100, 50, 50), confidence=0.9, class_name='car', lane=None),
        Detection(bbox=(150, 120, 50, 50), confidence=0.9, class_name='car', lane=None),
        Detection(bbox=(200, 140, 50, 50), confidence=0.9, class_name='truck', lane=None),
    ]
    
    lane_counts = detector.count_by_lane(detections, lane_config.lanes)
    
    # All three should be in north lane
    assert lane_counts['north'] == 3, "North lane should have 3 vehicles"
    assert lane_counts['south'] == 0, "South lane should have 0 vehicles"
    assert lane_counts['east'] == 0, "East lane should have 0 vehicles"
    assert lane_counts['west'] == 0, "West lane should have 0 vehicles"


def test_empty_detections_list():
    """Test handling empty detections list."""
    detector = VehicleDetector(confidence_threshold=0.5)
    
    frame_width = 800
    frame_height = 600
    lane_config = LaneConfiguration.create_four_way(frame_width, frame_height)
    
    detections = []
    lane_counts = detector.count_by_lane(detections, lane_config.lanes)
    
    # All lanes should have zero count
    assert lane_counts['north'] == 0, "North lane should have 0 vehicles"
    assert lane_counts['south'] == 0, "South lane should have 0 vehicles"
    assert lane_counts['east'] == 0, "East lane should have 0 vehicles"
    assert lane_counts['west'] == 0, "West lane should have 0 vehicles"


def test_point_in_region():
    """Test the _point_in_region helper method."""
    detector = VehicleDetector(confidence_threshold=0.5)
    
    region = Region(x=100, y=100, width=200, height=150, lane_name="test")
    
    # Point inside region
    assert detector._point_in_region(150, 150, region) is True
    
    # Point at top-left corner (inclusive)
    assert detector._point_in_region(100, 100, region) is True
    
    # Point at bottom-right corner (exclusive)
    assert detector._point_in_region(300, 250, region) is False
    
    # Point outside region
    assert detector._point_in_region(50, 50, region) is False
    assert detector._point_in_region(350, 300, region) is False


def test_detection_on_sample_frame():
    """Test detection on a sample frame with simple shapes."""
    detector = VehicleDetector(confidence_threshold=0.3)
    
    # Create a simple test frame (black image)
    image = np.zeros((480, 640, 3), dtype=np.uint8)
    frame = Frame(image=image, frame_number=0, timestamp=0.0)
    
    # Run detection (may not detect anything on black image, but should not crash)
    detections = detector.detect(frame)
    
    # Verify it returns a list (even if empty)
    assert isinstance(detections, list), "detect() should return a list"
    
    # Verify all detections have required attributes
    for detection in detections:
        assert hasattr(detection, 'bbox'), "Detection should have bbox"
        assert hasattr(detection, 'confidence'), "Detection should have confidence"
        assert hasattr(detection, 'class_name'), "Detection should have class_name"
        assert detection.confidence >= detector.confidence_threshold, \
            "All detections should meet confidence threshold"
