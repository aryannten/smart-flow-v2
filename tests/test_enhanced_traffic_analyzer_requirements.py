"""
Requirements verification tests for EnhancedTrafficAnalyzer.

These tests verify that the implementation meets the specific requirements
from the design document:
- Requirement 5.2: Incorporate queue length in density calculation
- Requirement 6.2: Apply weighting factors based on vehicle types
- Requirement 12.2: Record vehicles per hour for throughput
"""
import pytest
import time
from src.enhanced_traffic_analyzer import (
    EnhancedTrafficAnalyzer, 
    LaneData,
    CongestionTrend
)
from src.queue_estimator import QueueMetrics
from src.enhanced_detector import VehicleType


class TestRequirement5_2:
    """
    Requirement 5.2: WHEN calculating density THEN the System SHALL 
    incorporate queue length in addition to vehicle count
    """
    
    def test_density_incorporates_queue_length(self):
        """Verify that density calculation includes queue length."""
        analyzer = EnhancedTrafficAnalyzer()
        
        lane_counts = {'north': 10}
        
        # Without queue metrics
        density_without_queue = analyzer.calculate_density(lane_counts)
        
        # With queue metrics
        queue_metrics = {
            'north': QueueMetrics(
                length_meters=40.0,
                vehicle_count=10,
                density=0.25,
                head_position=(100, 100),
                tail_position=(200, 200),
                is_spillback=False
            )
        }
        density_with_queue = analyzer.calculate_density(lane_counts, queue_metrics)
        
        # Density with queue should be higher than without
        assert density_with_queue['north'] > density_without_queue['north']
        
        # Verify the queue contribution is included
        # Expected: 10 + (40 * 0.5) = 30.0
        assert density_with_queue['north'] == pytest.approx(30.0)
    
    def test_longer_queue_increases_density_more(self):
        """Verify that longer queues result in higher density values."""
        analyzer = EnhancedTrafficAnalyzer()
        
        lane_counts = {'north': 10}
        
        # Short queue
        short_queue = {
            'north': QueueMetrics(
                length_meters=20.0,
                vehicle_count=10,
                density=0.5,
                head_position=(100, 100),
                tail_position=(150, 150),
                is_spillback=False
            )
        }
        
        # Long queue
        long_queue = {
            'north': QueueMetrics(
                length_meters=60.0,
                vehicle_count=10,
                density=0.17,
                head_position=(100, 100),
                tail_position=(250, 250),
                is_spillback=False
            )
        }
        
        density_short = analyzer.calculate_density(lane_counts, short_queue)
        density_long = analyzer.calculate_density(lane_counts, long_queue)
        
        # Longer queue should result in higher density
        assert density_long['north'] > density_short['north']


class TestRequirement6_2:
    """
    Requirement 6.2: WHEN calculating lane priority THEN the System SHALL 
    apply weighting factors based on vehicle types
    """
    
    def test_priority_applies_vehicle_type_weights(self):
        """Verify that different vehicle types receive different weights."""
        analyzer = EnhancedTrafficAnalyzer()
        
        # Lane with only cars
        lane_cars = LaneData(
            vehicle_count=10,
            queue_length=0.0,
            wait_time=0.0,
            vehicle_types={VehicleType.CAR: 10},
            has_emergency=False,
            pedestrian_count=0
        )
        
        # Lane with only trucks (weight 1.5)
        lane_trucks = LaneData(
            vehicle_count=10,
            queue_length=0.0,
            wait_time=0.0,
            vehicle_types={VehicleType.TRUCK: 10},
            has_emergency=False,
            pedestrian_count=0
        )
        
        # Lane with only buses (weight 2.0)
        lane_buses = LaneData(
            vehicle_count=10,
            queue_length=0.0,
            wait_time=0.0,
            vehicle_types={VehicleType.BUS: 10},
            has_emergency=False,
            pedestrian_count=0
        )
        
        priority_cars = analyzer.calculate_weighted_priority(lane_cars)
        priority_trucks = analyzer.calculate_weighted_priority(lane_trucks)
        priority_buses = analyzer.calculate_weighted_priority(lane_buses)
        
        # Verify weights are applied correctly
        # Cars: weight 1.0
        # Trucks: weight 1.5
        # Buses: weight 2.0
        assert priority_trucks == pytest.approx(priority_cars * 1.5)
        assert priority_buses == pytest.approx(priority_cars * 2.0)
    
    def test_mixed_vehicle_types_weighted_average(self):
        """Verify that mixed vehicle types use weighted average."""
        analyzer = EnhancedTrafficAnalyzer()
        
        # Lane with mixed vehicles: 5 cars (weight 1.0) + 5 buses (weight 2.0)
        # Expected average weight: (5*1.0 + 5*2.0) / 10 = 1.5
        lane_mixed = LaneData(
            vehicle_count=10,
            queue_length=0.0,
            wait_time=0.0,
            vehicle_types={
                VehicleType.CAR: 5,
                VehicleType.BUS: 5
            },
            has_emergency=False,
            pedestrian_count=0
        )
        
        # Lane with only cars for comparison
        lane_cars = LaneData(
            vehicle_count=10,
            queue_length=0.0,
            wait_time=0.0,
            vehicle_types={VehicleType.CAR: 10},
            has_emergency=False,
            pedestrian_count=0
        )
        
        priority_mixed = analyzer.calculate_weighted_priority(lane_mixed)
        priority_cars = analyzer.calculate_weighted_priority(lane_cars)
        
        # Mixed should have 1.5x priority of cars
        assert priority_mixed == pytest.approx(priority_cars * 1.5)
    
    def test_bus_receives_higher_priority_weight(self):
        """
        Requirement 6.3: WHEN a bus is detected THEN the System SHALL 
        apply higher priority weight to support public transit
        """
        analyzer = EnhancedTrafficAnalyzer()
        
        lane_car = LaneData(
            vehicle_count=1,
            queue_length=0.0,
            wait_time=0.0,
            vehicle_types={VehicleType.CAR: 1},
            has_emergency=False,
            pedestrian_count=0
        )
        
        lane_bus = LaneData(
            vehicle_count=1,
            queue_length=0.0,
            wait_time=0.0,
            vehicle_types={VehicleType.BUS: 1},
            has_emergency=False,
            pedestrian_count=0
        )
        
        priority_car = analyzer.calculate_weighted_priority(lane_car)
        priority_bus = analyzer.calculate_weighted_priority(lane_bus)
        
        # Bus should have significantly higher priority
        assert priority_bus > priority_car
        # Specifically, bus weight is 2.0 vs car weight 1.0
        assert priority_bus == pytest.approx(priority_car * 2.0)


class TestRequirement12_2:
    """
    Requirement 12.2: WHEN measuring throughput THEN the System SHALL 
    record vehicles per hour for each lane and the intersection total
    """
    
    def test_throughput_recorded_per_lane(self):
        """Verify that throughput is recorded for each lane separately."""
        analyzer = EnhancedTrafficAnalyzer()
        
        # Record vehicles for different lanes
        current_time = time.time()
        
        # North lane: 10 vehicles
        for i in range(10):
            analyzer.record_vehicle_cleared('north', current_time - 0.1 * i)
        
        # South lane: 5 vehicles
        for i in range(5):
            analyzer.record_vehicle_cleared('south', current_time - 0.1 * i)
        
        # Calculate throughput for each lane
        throughput_north = analyzer.calculate_throughput('north', time_window=1.0)
        throughput_south = analyzer.calculate_throughput('south', time_window=1.0)
        
        # North should have higher throughput
        assert throughput_north > throughput_south
        
        # Verify values are in vehicles per hour
        # 10 vehicles in 1 second = 36000 vehicles/hour
        assert throughput_north == pytest.approx(36000.0, rel=0.1)
        # 5 vehicles in 1 second = 18000 vehicles/hour
        assert throughput_south == pytest.approx(18000.0, rel=0.1)
    
    def test_throughput_summary_all_lanes(self):
        """Verify that throughput summary includes all lanes."""
        analyzer = EnhancedTrafficAnalyzer()
        
        current_time = time.time()
        
        # Record vehicles for multiple lanes
        for i in range(10):
            analyzer.record_vehicle_cleared('north', current_time - 0.1 * i)
        for i in range(5):
            analyzer.record_vehicle_cleared('south', current_time - 0.1 * i)
        for i in range(8):
            analyzer.record_vehicle_cleared('east', current_time - 0.1 * i)
        
        # Get summary
        summary = analyzer.get_throughput_summary(time_window=1.0)
        
        # Should have all three lanes
        assert 'north' in summary
        assert 'south' in summary
        assert 'east' in summary
        
        # All values should be positive
        assert summary['north'] > 0
        assert summary['south'] > 0
        assert summary['east'] > 0
    
    def test_throughput_in_vehicles_per_hour(self):
        """Verify that throughput is expressed in vehicles per hour."""
        analyzer = EnhancedTrafficAnalyzer()
        
        current_time = time.time()
        
        # Record 100 vehicles over 10 seconds
        for i in range(100):
            analyzer.record_vehicle_cleared('north', current_time - 0.1 * i)
        
        # Calculate throughput over 10 second window
        throughput = analyzer.calculate_throughput('north', time_window=10.0)
        
        # 100 vehicles in 10 seconds = 10 vehicles/second = 36000 vehicles/hour
        expected_throughput = (100 / 10.0) * 3600.0
        assert throughput == pytest.approx(expected_throughput, rel=0.1)


class TestAdditionalFeatures:
    """Test additional features mentioned in task 8.1"""
    
    def test_congestion_trend_detection(self):
        """Verify congestion trend detection works."""
        analyzer = EnhancedTrafficAnalyzer()
        
        # Add worsening trend
        for i in range(10):
            density = 10.0 + i * 3.0
            analyzer.detect_congestion_trend('north', density, int(density), density * 3)
        
        trend = analyzer.detect_congestion_trend('north', 40.0, 40, 120.0)
        assert trend == CongestionTrend.WORSENING
    
    def test_multi_factor_priority_calculation(self):
        """Verify that priority considers multiple factors."""
        analyzer = EnhancedTrafficAnalyzer()
        
        # Lane with high count, long queue, and long wait
        lane_high = LaneData(
            vehicle_count=20,
            queue_length=50.0,
            wait_time=60.0,
            vehicle_types={VehicleType.CAR: 20},
            has_emergency=False,
            pedestrian_count=0
        )
        
        # Lane with low count, short queue, and short wait
        lane_low = LaneData(
            vehicle_count=5,
            queue_length=10.0,
            wait_time=10.0,
            vehicle_types={VehicleType.CAR: 5},
            has_emergency=False,
            pedestrian_count=0
        )
        
        priority_high = analyzer.calculate_weighted_priority(lane_high)
        priority_low = analyzer.calculate_weighted_priority(lane_low)
        
        # High demand lane should have much higher priority
        assert priority_high > priority_low * 2
