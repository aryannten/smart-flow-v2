"""
Unit tests for TrafficAnalyzer module.
"""
import pytest
from src.traffic_analyzer import TrafficAnalyzer


class TestTrafficAnalyzer:
    """Unit tests for TrafficAnalyzer class."""
    
    def test_calculate_density_with_various_counts(self):
        """Test density calculation with various vehicle counts."""
        analyzer = TrafficAnalyzer()
        
        # Test with different counts
        lane_counts = {
            'north': 10,
            'south': 5,
            'east': 15,
            'west': 0
        }
        
        densities = analyzer.calculate_density(lane_counts)
        
        # Verify all lanes are present
        assert set(densities.keys()) == {'north', 'south', 'east', 'west'}
        
        # Verify density values match counts
        assert densities['north'] == 10.0
        assert densities['south'] == 5.0
        assert densities['east'] == 15.0
        assert densities['west'] == 0.0
    
    def test_calculate_density_with_zero_counts(self):
        """Test density calculation when all counts are zero."""
        analyzer = TrafficAnalyzer()
        
        lane_counts = {
            'north': 0,
            'south': 0,
            'east': 0,
            'west': 0
        }
        
        densities = analyzer.calculate_density(lane_counts)
        
        # All densities should be 0.0
        for lane, density in densities.items():
            assert density == 0.0
    
    def test_identify_max_density_clear_winner(self):
        """Test max identification when one lane has clearly highest density."""
        analyzer = TrafficAnalyzer()
        
        densities = {
            'north': 5.0,
            'south': 10.0,
            'east': 3.0,
            'west': 7.0
        }
        
        max_lane = analyzer.identify_max_density_lane(densities)
        
        # South should be identified as max
        assert max_lane == 'south'
    
    def test_identify_max_density_with_tie(self):
        """Test max identification with equal densities (tie-breaking)."""
        analyzer = TrafficAnalyzer()
        
        # Test with two lanes tied for max
        densities = {
            'north': 10.0,
            'south': 10.0,
            'east': 5.0,
            'west': 3.0
        }
        
        max_lane = analyzer.identify_max_density_lane(densities)
        
        # Should select 'north' (alphabetically first among tied lanes)
        assert max_lane == 'north'
    
    def test_identify_max_density_all_equal(self):
        """Test max identification when all lanes have equal density."""
        analyzer = TrafficAnalyzer()
        
        densities = {
            'north': 8.0,
            'south': 8.0,
            'east': 8.0,
            'west': 8.0
        }
        
        max_lane = analyzer.identify_max_density_lane(densities)
        
        # Should select 'east' (alphabetically first)
        assert max_lane == 'east'
    
    def test_identify_max_density_empty_raises_error(self):
        """Test that empty densities dictionary raises ValueError."""
        analyzer = TrafficAnalyzer()
        
        with pytest.raises(ValueError, match="Cannot identify max density lane from empty densities"):
            analyzer.identify_max_density_lane({})
    
    def test_get_density_ratios_normal_case(self):
        """Test density ratio calculation with normal values."""
        analyzer = TrafficAnalyzer()
        
        densities = {
            'north': 10.0,
            'south': 20.0,
            'east': 30.0,
            'west': 40.0
        }
        
        ratios = analyzer.get_density_ratios(densities)
        
        # Total is 100, so ratios should be proportional
        assert ratios['north'] == pytest.approx(0.1)
        assert ratios['south'] == pytest.approx(0.2)
        assert ratios['east'] == pytest.approx(0.3)
        assert ratios['west'] == pytest.approx(0.4)
        
        # Ratios should sum to 1.0
        assert sum(ratios.values()) == pytest.approx(1.0)
    
    def test_get_density_ratios_zero_total(self):
        """Test density ratio calculation when total density is zero."""
        analyzer = TrafficAnalyzer()
        
        densities = {
            'north': 0.0,
            'south': 0.0,
            'east': 0.0,
            'west': 0.0
        }
        
        ratios = analyzer.get_density_ratios(densities)
        
        # Should distribute equally (0.25 each)
        for lane, ratio in ratios.items():
            assert ratio == pytest.approx(0.25)
        
        # Ratios should sum to 1.0
        assert sum(ratios.values()) == pytest.approx(1.0)
    
    def test_get_density_ratios_single_lane_with_traffic(self):
        """Test density ratio calculation when only one lane has traffic."""
        analyzer = TrafficAnalyzer()
        
        densities = {
            'north': 0.0,
            'south': 50.0,
            'east': 0.0,
            'west': 0.0
        }
        
        ratios = analyzer.get_density_ratios(densities)
        
        # South should get 100% of the ratio
        assert ratios['south'] == pytest.approx(1.0)
        assert ratios['north'] == pytest.approx(0.0)
        assert ratios['east'] == pytest.approx(0.0)
        assert ratios['west'] == pytest.approx(0.0)
        
        # Ratios should sum to 1.0
        assert sum(ratios.values()) == pytest.approx(1.0)
