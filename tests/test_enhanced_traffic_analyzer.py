"""
Unit tests for EnhancedTrafficAnalyzer module.
"""
import pytest
import time
from src.enhanced_traffic_analyzer import (
    EnhancedTrafficAnalyzer, 
    LaneData, 
    CongestionTrend,
    DensitySnapshot
)
from src.queue_estimator import QueueMetrics
from src.enhanced_detector import VehicleType


class TestEnhancedTrafficAnalyzer:
    """Unit tests for EnhancedTrafficAnalyzer class."""
    
    def test_calculate_density_without_queue_metrics(self):
        """Test density calculation without queue metrics (should behave like base class)."""
        analyzer = EnhancedTrafficAnalyzer()
        
        lane_counts = {
            'north': 10,
            'south': 5,
            'east': 15,
            'west': 0
        }
        
        densities = analyzer.calculate_density(lane_counts)
        
        # Should match base behavior
        assert densities['north'] == 10.0
        assert densities['south'] == 5.0
        assert densities['east'] == 15.0
        assert densities['west'] == 0.0
    
    def test_calculate_density_with_queue_metrics(self):
        """Test density calculation integrating queue length."""
        analyzer = EnhancedTrafficAnalyzer()
        
        lane_counts = {
            'north': 10,
            'south': 5
        }
        
        queue_metrics = {
            'north': QueueMetrics(
                length_meters=50.0,
                vehicle_count=10,
                density=0.2,
                head_position=(100, 100),
                tail_position=(200, 200),
                is_spillback=False
            ),
            'south': QueueMetrics(
                length_meters=20.0,
                vehicle_count=5,
                density=0.25,
                head_position=(100, 300),
                tail_position=(150, 350),
                is_spillback=False
            )
        }
        
        densities = analyzer.calculate_density(lane_counts, queue_metrics)
        
        # North: 10 + (50 * 0.5) = 35.0
        assert densities['north'] == pytest.approx(35.0)
        
        # South: 5 + (20 * 0.5) = 15.0
        assert densities['south'] == pytest.approx(15.0)
    
    def test_calculate_weighted_priority_basic(self):
        """Test weighted priority calculation with basic lane data."""
        analyzer = EnhancedTrafficAnalyzer()
        
        lane_data = LaneData(
            vehicle_count=10,
            queue_length=30.0,
            wait_time=20.0,
            vehicle_types={VehicleType.CAR: 10},
            has_emergency=False,
            pedestrian_count=0
        )
        
        priority = analyzer.calculate_weighted_priority(lane_data)
        
        # Should be positive and reasonable
        assert priority > 0
        # Base: 10 + (30 * 0.2) + (20 * 0.1) = 10 + 6 + 2 = 18
        # With type weight 1.0 and no emergency: 18 * 1.0 * 1.0 * 1.0 = 18
        assert priority == pytest.approx(18.0)
    
    def test_calculate_weighted_priority_with_bus(self):
        """Test that buses get higher priority weight."""
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
        
        # Lane with buses (same count)
        lane_buses = LaneData(
            vehicle_count=10,
            queue_length=0.0,
            wait_time=0.0,
            vehicle_types={VehicleType.BUS: 10},
            has_emergency=False,
            pedestrian_count=0
        )
        
        priority_cars = analyzer.calculate_weighted_priority(lane_cars)
        priority_buses = analyzer.calculate_weighted_priority(lane_buses)
        
        # Buses should have higher priority (weight 2.0 vs 1.0)
        assert priority_buses > priority_cars
        assert priority_buses == pytest.approx(priority_cars * 2.0)
    
    def test_calculate_weighted_priority_with_emergency(self):
        """Test that emergency vehicles dramatically increase priority."""
        analyzer = EnhancedTrafficAnalyzer()
        
        lane_normal = LaneData(
            vehicle_count=10,
            queue_length=0.0,
            wait_time=0.0,
            vehicle_types={VehicleType.CAR: 10},
            has_emergency=False,
            pedestrian_count=0
        )
        
        lane_emergency = LaneData(
            vehicle_count=10,
            queue_length=0.0,
            wait_time=0.0,
            vehicle_types={VehicleType.CAR: 10},
            has_emergency=True,
            pedestrian_count=0
        )
        
        priority_normal = analyzer.calculate_weighted_priority(lane_normal)
        priority_emergency = analyzer.calculate_weighted_priority(lane_emergency)
        
        # Emergency should be 10x higher
        assert priority_emergency == pytest.approx(priority_normal * 10.0)
    
    def test_calculate_weighted_priority_with_pedestrians(self):
        """Test that pedestrians provide a priority boost."""
        analyzer = EnhancedTrafficAnalyzer()
        
        lane_no_peds = LaneData(
            vehicle_count=10,
            queue_length=0.0,
            wait_time=0.0,
            vehicle_types={VehicleType.CAR: 10},
            has_emergency=False,
            pedestrian_count=0
        )
        
        lane_with_peds = LaneData(
            vehicle_count=10,
            queue_length=0.0,
            wait_time=0.0,
            vehicle_types={VehicleType.CAR: 10},
            has_emergency=False,
            pedestrian_count=5
        )
        
        priority_no_peds = analyzer.calculate_weighted_priority(lane_no_peds)
        priority_with_peds = analyzer.calculate_weighted_priority(lane_with_peds)
        
        # With pedestrians should be higher
        assert priority_with_peds > priority_no_peds
    
    def test_detect_congestion_trend_insufficient_data(self):
        """Test trend detection with insufficient historical data."""
        analyzer = EnhancedTrafficAnalyzer()
        
        # First call - no history
        trend = analyzer.detect_congestion_trend('north', 10.0, 10, 30.0)
        assert trend == CongestionTrend.STABLE
        
        # Second call - still not enough
        trend = analyzer.detect_congestion_trend('north', 12.0, 12, 35.0)
        assert trend == CongestionTrend.STABLE
    
    def test_detect_congestion_trend_worsening(self):
        """Test detection of worsening congestion."""
        analyzer = EnhancedTrafficAnalyzer()
        
        # Add increasing density values
        for i in range(10):
            density = 10.0 + i * 2.0  # Increasing from 10 to 28
            analyzer.detect_congestion_trend('north', density, int(density), density * 3)
        
        # Latest trend should be worsening
        trend = analyzer.detect_congestion_trend('north', 30.0, 30, 90.0)
        assert trend == CongestionTrend.WORSENING
    
    def test_detect_congestion_trend_improving(self):
        """Test detection of improving congestion."""
        analyzer = EnhancedTrafficAnalyzer()
        
        # Add decreasing density values
        for i in range(10):
            density = 30.0 - i * 2.0  # Decreasing from 30 to 12
            analyzer.detect_congestion_trend('north', density, int(density), density * 3)
        
        # Latest trend should be improving
        trend = analyzer.detect_congestion_trend('north', 10.0, 10, 30.0)
        assert trend == CongestionTrend.IMPROVING
    
    def test_detect_congestion_trend_stable(self):
        """Test detection of stable congestion."""
        analyzer = EnhancedTrafficAnalyzer()
        
        # Add stable density values
        for i in range(10):
            density = 15.0 + (i % 2) * 0.5  # Oscillating slightly around 15
            analyzer.detect_congestion_trend('north', density, int(density), density * 3)
        
        # Latest trend should be stable
        trend = analyzer.detect_congestion_trend('north', 15.0, 15, 45.0)
        assert trend == CongestionTrend.STABLE
    
    def test_calculate_throughput_empty(self):
        """Test throughput calculation with no data."""
        analyzer = EnhancedTrafficAnalyzer()
        
        throughput = analyzer.calculate_throughput('north')
        assert throughput == 0.0
    
    def test_calculate_throughput_with_data(self):
        """Test throughput calculation with recorded vehicles."""
        analyzer = EnhancedTrafficAnalyzer()
        
        # Record 10 vehicles in the last second
        current_time = time.time()
        for i in range(10):
            analyzer.record_vehicle_cleared('north', current_time - 0.1 * i)
        
        # Calculate throughput over 1 second window
        throughput = analyzer.calculate_throughput('north', time_window=1.0)
        
        # Should be 10 vehicles/second = 36000 vehicles/hour
        assert throughput == pytest.approx(36000.0, rel=0.1)
    
    def test_record_vehicle_cleared(self):
        """Test recording vehicle clearances."""
        analyzer = EnhancedTrafficAnalyzer()
        
        # Record some vehicles
        analyzer.record_vehicle_cleared('north')
        analyzer.record_vehicle_cleared('north')
        analyzer.record_vehicle_cleared('south')
        
        # Check that data was recorded
        assert 'north' in analyzer.throughput_data
        assert 'south' in analyzer.throughput_data
        assert len(analyzer.throughput_data['north']) == 2
        assert len(analyzer.throughput_data['south']) == 1
    
    def test_get_throughput_summary(self):
        """Test getting throughput summary for all lanes."""
        analyzer = EnhancedTrafficAnalyzer()
        
        # Record vehicles for multiple lanes
        current_time = time.time()
        for i in range(5):
            analyzer.record_vehicle_cleared('north', current_time - 0.1 * i)
        for i in range(3):
            analyzer.record_vehicle_cleared('south', current_time - 0.1 * i)
        
        summary = analyzer.get_throughput_summary(time_window=1.0)
        
        # Should have entries for both lanes
        assert 'north' in summary
        assert 'south' in summary
        assert summary['north'] > summary['south']
    
    def test_reset_history_all_lanes(self):
        """Test resetting history for all lanes."""
        analyzer = EnhancedTrafficAnalyzer()
        
        # Add some data
        analyzer.detect_congestion_trend('north', 10.0, 10, 30.0)
        analyzer.record_vehicle_cleared('north')
        analyzer.detect_congestion_trend('south', 15.0, 15, 45.0)
        analyzer.record_vehicle_cleared('south')
        
        # Reset all
        analyzer.reset_history()
        
        # Should be empty
        assert len(analyzer.density_history) == 0
        assert len(analyzer.throughput_data) == 0
    
    def test_reset_history_specific_lane(self):
        """Test resetting history for a specific lane."""
        analyzer = EnhancedTrafficAnalyzer()
        
        # Add data for multiple lanes
        analyzer.detect_congestion_trend('north', 10.0, 10, 30.0)
        analyzer.record_vehicle_cleared('north')
        analyzer.detect_congestion_trend('south', 15.0, 15, 45.0)
        analyzer.record_vehicle_cleared('south')
        
        # Reset only north
        analyzer.reset_history('north')
        
        # North should be empty, south should still have data
        assert len(analyzer.density_history.get('north', [])) == 0
        assert len(analyzer.throughput_data.get('north', [])) == 0
        assert len(analyzer.density_history.get('south', [])) > 0
        assert len(analyzer.throughput_data.get('south', [])) > 0
    
    def test_inheritance_from_base_class(self):
        """Test that EnhancedTrafficAnalyzer inherits base class methods."""
        analyzer = EnhancedTrafficAnalyzer()
        
        # Test inherited methods work
        densities = {'north': 10.0, 'south': 5.0}
        max_lane = analyzer.identify_max_density_lane(densities)
        assert max_lane == 'north'
        
        ratios = analyzer.get_density_ratios(densities)
        assert sum(ratios.values()) == pytest.approx(1.0)
