"""
Unit tests for QueueEstimator module.
"""
import pytest
from src.queue_estimator import QueueEstimator, QueueMetrics
from dataclasses import dataclass
from typing import Tuple


@dataclass
class MockDetection:
    """Mock detection object for testing"""
    center: Tuple[int, int]
    bbox: Tuple[int, int, int, int] = (0, 0, 10, 10)


class TestQueueEstimator:
    """Unit tests for QueueEstimator class."""
    
    def test_initialization_default_parameters(self):
        """Test QueueEstimator initialization with default parameters."""
        estimator = QueueEstimator()
        
        assert estimator.pixels_to_meters == 0.1
        assert estimator.spillback_threshold == 0.85
    
    def test_initialization_custom_parameters(self):
        """Test QueueEstimator initialization with custom parameters."""
        estimator = QueueEstimator(pixels_to_meters=0.2, spillback_threshold=0.9)
        
        assert estimator.pixels_to_meters == 0.2
        assert estimator.spillback_threshold == 0.9
    
    def test_estimate_queue_empty_detections(self):
        """Test queue estimation with no vehicles."""
        estimator = QueueEstimator()
        
        metrics = estimator.estimate_queue([], "north")
        
        assert metrics.length_meters == 0.0
        assert metrics.vehicle_count == 0
        assert metrics.density == 0.0
        assert metrics.head_position == (0, 0)
        assert metrics.tail_position == (0, 0)
        assert metrics.is_spillback is False
    
    def test_estimate_queue_single_vehicle(self):
        """Test queue estimation with single vehicle."""
        estimator = QueueEstimator()
        
        detections = [MockDetection(center=(100, 100))]
        metrics = estimator.estimate_queue(detections, "north")
        
        assert metrics.vehicle_count == 1
        assert metrics.length_meters == 0.0  # Single vehicle has no queue length
        assert metrics.head_position == (100, 100)
        assert metrics.tail_position == (100, 100)
    
    def test_estimate_queue_multiple_vehicles_close_spacing(self):
        """Test queue estimation with multiple vehicles in close proximity."""
        estimator = QueueEstimator()
        
        # Create vehicles with spacing less than threshold (50 pixels)
        detections = [
            MockDetection(center=(100, 100)),
            MockDetection(center=(120, 120)),  # ~28 pixels away
            MockDetection(center=(140, 140)),  # ~28 pixels away
        ]
        
        metrics = estimator.estimate_queue(detections, "north")
        
        assert metrics.vehicle_count == 3
        assert metrics.length_meters > 0.0
        # Queue should include all vehicles since spacing is below threshold
        assert metrics.head_position == (100, 100)
        assert metrics.tail_position == (140, 140)
    
    def test_estimate_queue_multiple_vehicles_large_gap(self):
        """Test queue estimation with large gap between vehicles."""
        estimator = QueueEstimator()
        
        # Create vehicles with one large gap (> 50 pixels)
        detections = [
            MockDetection(center=(100, 100)),
            MockDetection(center=(120, 120)),  # ~28 pixels away
            MockDetection(center=(300, 300)),  # ~254 pixels away - breaks queue
        ]
        
        metrics = estimator.estimate_queue(detections, "north")
        
        assert metrics.vehicle_count == 3
        # Queue should only include first two vehicles
        # Tail should be at second vehicle, not third
        assert metrics.tail_position == (120, 120)
    
    def test_calculate_queue_length_empty_list(self):
        """Test queue length calculation with empty position list."""
        estimator = QueueEstimator()
        
        length = estimator.calculate_queue_length([])
        
        assert length == 0.0
    
    def test_calculate_queue_length_single_position(self):
        """Test queue length calculation with single position."""
        estimator = QueueEstimator()
        
        length = estimator.calculate_queue_length([(100, 100)])
        
        assert length == 0.0
    
    def test_calculate_queue_length_two_positions(self):
        """Test queue length calculation with two positions."""
        estimator = QueueEstimator()
        
        # Two positions 100 pixels apart horizontally
        positions = [(0, 0), (100, 0)]
        length = estimator.calculate_queue_length(positions)
        
        # 100 pixels * 0.1 = 10 meters
        assert length == pytest.approx(10.0)
    
    def test_calculate_queue_length_diagonal_positions(self):
        """Test queue length calculation with diagonal positions."""
        estimator = QueueEstimator()
        
        # Two positions forming a 3-4-5 right triangle (50 pixels apart)
        positions = [(0, 0), (30, 40)]
        length = estimator.calculate_queue_length(positions)
        
        # Distance = sqrt(30^2 + 40^2) = 50 pixels * 0.1 = 5 meters
        assert length == pytest.approx(5.0)
    
    def test_detect_queue_spillback_no_spillback(self):
        """Test spillback detection when queue is within limits."""
        estimator = QueueEstimator()
        
        # Queue is 50 meters, lane is 100 meters (50% < 85%)
        is_spillback = estimator.detect_queue_spillback(50.0, 100.0)
        
        assert is_spillback is False
    
    def test_detect_queue_spillback_at_threshold(self):
        """Test spillback detection at exact threshold."""
        estimator = QueueEstimator()
        
        # Queue is 85 meters, lane is 100 meters (85% = 85%)
        is_spillback = estimator.detect_queue_spillback(85.0, 100.0)
        
        assert is_spillback is True
    
    def test_detect_queue_spillback_exceeds_threshold(self):
        """Test spillback detection when queue exceeds threshold."""
        estimator = QueueEstimator()
        
        # Queue is 90 meters, lane is 100 meters (90% > 85%)
        is_spillback = estimator.detect_queue_spillback(90.0, 100.0)
        
        assert is_spillback is True
    
    def test_detect_queue_spillback_zero_lane_length(self):
        """Test spillback detection with zero lane length."""
        estimator = QueueEstimator()
        
        # Should return False for invalid lane length
        is_spillback = estimator.detect_queue_spillback(50.0, 0.0)
        
        assert is_spillback is False
    
    def test_detect_queue_spillback_custom_threshold(self):
        """Test spillback detection with custom threshold."""
        estimator = QueueEstimator(spillback_threshold=0.7)
        
        # Queue is 75 meters, lane is 100 meters (75% > 70%)
        is_spillback = estimator.detect_queue_spillback(75.0, 100.0)
        
        assert is_spillback is True
    
    def test_predict_clearance_time_empty_queue(self):
        """Test clearance time prediction for empty queue."""
        estimator = QueueEstimator()
        
        metrics = QueueMetrics(
            length_meters=0.0,
            vehicle_count=0,
            density=0.0,
            head_position=(0, 0),
            tail_position=(0, 0),
            is_spillback=False
        )
        
        clearance_time = estimator.predict_clearance_time(metrics, 30.0)
        
        assert clearance_time == 0.0
    
    def test_predict_clearance_time_small_queue(self):
        """Test clearance time prediction for small queue."""
        estimator = QueueEstimator()
        
        metrics = QueueMetrics(
            length_meters=25.0,
            vehicle_count=5,
            density=0.2,
            head_position=(0, 0),
            tail_position=(250, 0),
            is_spillback=False
        )
        
        clearance_time = estimator.predict_clearance_time(metrics, 30.0)
        
        # 5 vehicles / (1800 vehicles/hour / 3600 seconds/hour) = 10 seconds
        assert clearance_time == pytest.approx(10.0)
    
    def test_predict_clearance_time_large_queue(self):
        """Test clearance time prediction for large queue."""
        estimator = QueueEstimator()
        
        metrics = QueueMetrics(
            length_meters=100.0,
            vehicle_count=20,
            density=0.2,
            head_position=(0, 0),
            tail_position=(1000, 0),
            is_spillback=True
        )
        
        clearance_time = estimator.predict_clearance_time(metrics, 60.0)
        
        # 20 vehicles / (1800 vehicles/hour / 3600 seconds/hour) = 40 seconds
        assert clearance_time == pytest.approx(40.0)
    
    def test_queue_metrics_dataclass(self):
        """Test QueueMetrics dataclass creation."""
        metrics = QueueMetrics(
            length_meters=50.0,
            vehicle_count=10,
            density=0.2,
            head_position=(100, 100),
            tail_position=(600, 100),
            is_spillback=False
        )
        
        assert metrics.length_meters == 50.0
        assert metrics.vehicle_count == 10
        assert metrics.density == 0.2
        assert metrics.head_position == (100, 100)
        assert metrics.tail_position == (600, 100)
        assert metrics.is_spillback is False
    
    def test_estimate_queue_density_calculation(self):
        """Test that density is correctly calculated in estimate_queue."""
        estimator = QueueEstimator()
        
        # Create a queue with known length and vehicle count
        detections = [
            MockDetection(center=(0, 0)),
            MockDetection(center=(30, 40)),  # 50 pixels away
        ]
        
        metrics = estimator.estimate_queue(detections, "north")
        
        # Queue length = 50 pixels = 5 meters
        # Vehicle count = 2
        # Density = 2 / 5 = 0.4 vehicles per meter
        assert metrics.vehicle_count == 2
        assert metrics.length_meters == pytest.approx(5.0)
        assert metrics.density == pytest.approx(0.4)
