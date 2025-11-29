"""
Unit tests for TimeWeatherAdapter.
"""
import pytest
from datetime import datetime, time
from unittest.mock import Mock, patch
from src.time_weather_adapter import (
    TimeWeatherAdapter,
    TimeOfDay,
    WeatherCondition,
    TimingAdjustment
)


class TestTimeOfDayDetection:
    """Tests for time of day detection."""
    
    def test_detect_peak_morning(self):
        """Test detection of peak morning hours."""
        adapter = TimeWeatherAdapter()
        
        # 8:00 AM should be peak morning
        test_time = datetime(2024, 1, 15, 8, 0, 0)
        result = adapter.detect_time_of_day(test_time)
        
        assert result == TimeOfDay.PEAK_MORNING
    
    def test_detect_peak_evening(self):
        """Test detection of peak evening hours."""
        adapter = TimeWeatherAdapter()
        
        # 5:30 PM should be peak evening
        test_time = datetime(2024, 1, 15, 17, 30, 0)
        result = adapter.detect_time_of_day(test_time)
        
        assert result == TimeOfDay.PEAK_EVENING
    
    def test_detect_off_peak(self):
        """Test detection of off-peak hours."""
        adapter = TimeWeatherAdapter()
        
        # 2:00 PM should be off-peak
        test_time = datetime(2024, 1, 15, 14, 0, 0)
        result = adapter.detect_time_of_day(test_time)
        
        assert result == TimeOfDay.OFF_PEAK
    
    def test_detect_night(self):
        """Test detection of night hours."""
        adapter = TimeWeatherAdapter()
        
        # 11:00 PM should be night
        test_time = datetime(2024, 1, 15, 23, 0, 0)
        result = adapter.detect_time_of_day(test_time)
        
        assert result == TimeOfDay.NIGHT
        
        # 3:00 AM should also be night
        test_time = datetime(2024, 1, 15, 3, 0, 0)
        result = adapter.detect_time_of_day(test_time)
        
        assert result == TimeOfDay.NIGHT
    
    def test_detect_current_time(self):
        """Test detection without providing time (uses current time)."""
        adapter = TimeWeatherAdapter()
        
        # Should not raise an error
        result = adapter.detect_time_of_day()
        
        assert isinstance(result, TimeOfDay)


class TestTimeBasedAdjustment:
    """Tests for time-based timing adjustments."""
    
    def test_peak_hours_adjustment(self):
        """Test that peak hours get aggressive timing."""
        adapter = TimeWeatherAdapter()
        
        adjustment = adapter.get_time_based_adjustment(TimeOfDay.PEAK_MORNING)
        
        # Peak hours should have increased green time
        assert adjustment.green_time_multiplier > 1.0
        # Cycle time should be longer
        assert adjustment.cycle_time_multiplier > 1.0
    
    def test_night_adjustment(self):
        """Test that night hours get minimal timing."""
        adapter = TimeWeatherAdapter()
        
        adjustment = adapter.get_time_based_adjustment(TimeOfDay.NIGHT)
        
        # Night should have reduced green time
        assert adjustment.green_time_multiplier < 1.0
        # Cycle time should be shorter
        assert adjustment.cycle_time_multiplier < 1.0
    
    def test_off_peak_adjustment(self):
        """Test that off-peak hours get balanced timing."""
        adapter = TimeWeatherAdapter()
        
        adjustment = adapter.get_time_based_adjustment(TimeOfDay.OFF_PEAK)
        
        # Off-peak should have standard timing (multiplier = 1.0)
        assert adjustment.green_time_multiplier == 1.0
        assert adjustment.yellow_time_multiplier == 1.0
        assert adjustment.minimum_green_multiplier == 1.0
        assert adjustment.cycle_time_multiplier == 1.0


class TestWeatherDetection:
    """Tests for weather detection."""
    
    def test_no_api_key_returns_unknown(self):
        """Test that without API key, weather is unknown."""
        adapter = TimeWeatherAdapter()
        
        weather = adapter.detect_weather()
        
        assert weather == WeatherCondition.UNKNOWN
    
    def test_weather_caching(self):
        """Test that weather is cached for 10 minutes."""
        adapter = TimeWeatherAdapter(weather_api_key="test_key", location="Seattle,WA")
        adapter.current_weather = WeatherCondition.RAIN
        adapter.last_weather_update = datetime.now()
        
        # Should return cached weather without API call
        weather = adapter.detect_weather()
        
        assert weather == WeatherCondition.RAIN
    
    @patch('src.time_weather_adapter.requests.get')
    def test_fetch_weather_clear(self, mock_get):
        """Test fetching clear weather from API."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "weather": [{"main": "Clear", "description": "clear sky"}]
        }
        mock_get.return_value = mock_response
        
        adapter = TimeWeatherAdapter(weather_api_key="test_key", location="Seattle,WA")
        weather = adapter._fetch_weather_from_api()
        
        assert weather == WeatherCondition.CLEAR
    
    @patch('src.time_weather_adapter.requests.get')
    def test_fetch_weather_rain(self, mock_get):
        """Test fetching rain weather from API."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "weather": [{"main": "Rain", "description": "light rain"}]
        }
        mock_get.return_value = mock_response
        
        adapter = TimeWeatherAdapter(weather_api_key="test_key", location="Seattle,WA")
        weather = adapter._fetch_weather_from_api()
        
        assert weather == WeatherCondition.RAIN
    
    @patch('src.time_weather_adapter.requests.get')
    def test_fetch_weather_heavy_rain(self, mock_get):
        """Test fetching heavy rain weather from API."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "weather": [{"main": "Rain", "description": "heavy intensity rain"}]
        }
        mock_get.return_value = mock_response
        
        adapter = TimeWeatherAdapter(weather_api_key="test_key", location="Seattle,WA")
        weather = adapter._fetch_weather_from_api()
        
        assert weather == WeatherCondition.HEAVY_RAIN
    
    @patch('src.time_weather_adapter.requests.get')
    def test_fetch_weather_snow(self, mock_get):
        """Test fetching snow weather from API."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "weather": [{"main": "Snow", "description": "light snow"}]
        }
        mock_get.return_value = mock_response
        
        adapter = TimeWeatherAdapter(weather_api_key="test_key", location="Seattle,WA")
        weather = adapter._fetch_weather_from_api()
        
        assert weather == WeatherCondition.SNOW
    
    @patch('src.time_weather_adapter.requests.get')
    def test_fetch_weather_fog(self, mock_get):
        """Test fetching fog weather from API."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "weather": [{"main": "Fog", "description": "fog"}]
        }
        mock_get.return_value = mock_response
        
        adapter = TimeWeatherAdapter(weather_api_key="test_key", location="Seattle,WA")
        weather = adapter._fetch_weather_from_api()
        
        assert weather == WeatherCondition.FOG


class TestWeatherBasedAdjustment:
    """Tests for weather-based timing adjustments."""
    
    def test_clear_weather_adjustment(self):
        """Test that clear weather has no adjustment."""
        adapter = TimeWeatherAdapter()
        
        adjustment = adapter.get_weather_based_adjustment(WeatherCondition.CLEAR)
        
        # Clear weather should have standard timing
        assert adjustment.green_time_multiplier == 1.0
        assert adjustment.yellow_time_multiplier == 1.0
        assert adjustment.minimum_green_multiplier == 1.0
        assert adjustment.cycle_time_multiplier == 1.0
    
    def test_rain_adjustment(self):
        """Test that rain increases yellow time for safety."""
        adapter = TimeWeatherAdapter()
        
        adjustment = adapter.get_weather_based_adjustment(WeatherCondition.RAIN)
        
        # Rain should increase yellow time
        assert adjustment.yellow_time_multiplier > 1.0
    
    def test_heavy_rain_adjustment(self):
        """Test that heavy rain significantly increases yellow time."""
        adapter = TimeWeatherAdapter()
        
        adjustment = adapter.get_weather_based_adjustment(WeatherCondition.HEAVY_RAIN)
        
        # Heavy rain should significantly increase yellow time
        assert adjustment.yellow_time_multiplier > 1.3
    
    def test_snow_adjustment(self):
        """Test that snow increases yellow time for safety."""
        adapter = TimeWeatherAdapter()
        
        adjustment = adapter.get_weather_based_adjustment(WeatherCondition.SNOW)
        
        # Snow should increase yellow time
        assert adjustment.yellow_time_multiplier > 1.0
    
    def test_fog_adjustment(self):
        """Test that fog increases yellow time for reduced visibility."""
        adapter = TimeWeatherAdapter()
        
        adjustment = adapter.get_weather_based_adjustment(WeatherCondition.FOG)
        
        # Fog should increase yellow time
        assert adjustment.yellow_time_multiplier > 1.0


class TestCombinedAdjustment:
    """Tests for combined time and weather adjustments."""
    
    def test_combined_adjustment_multiplies_factors(self):
        """Test that combined adjustment multiplies time and weather factors."""
        adapter = TimeWeatherAdapter()
        
        # Peak morning + rain
        combined = adapter.get_combined_adjustment(
            TimeOfDay.PEAK_MORNING,
            WeatherCondition.RAIN
        )
        
        time_adj = adapter.get_time_based_adjustment(TimeOfDay.PEAK_MORNING)
        weather_adj = adapter.get_weather_based_adjustment(WeatherCondition.RAIN)
        
        # Should multiply factors
        expected_green = time_adj.green_time_multiplier * weather_adj.green_time_multiplier
        expected_yellow = time_adj.yellow_time_multiplier * weather_adj.yellow_time_multiplier
        
        assert abs(combined.green_time_multiplier - expected_green) < 0.001
        assert abs(combined.yellow_time_multiplier - expected_yellow) < 0.001
    
    def test_peak_and_heavy_rain_combination(self):
        """Test that peak hours + heavy rain creates significant adjustments."""
        adapter = TimeWeatherAdapter()
        
        combined = adapter.get_combined_adjustment(
            TimeOfDay.PEAK_EVENING,
            WeatherCondition.HEAVY_RAIN
        )
        
        # Should have increased green time (from peak)
        assert combined.green_time_multiplier > 1.0
        # Should have significantly increased yellow time (from heavy rain)
        assert combined.yellow_time_multiplier > 1.3


class TestApplyAdjustment:
    """Tests for applying adjustments to timing values."""
    
    def test_apply_adjustment_to_timing(self):
        """Test applying adjustment to base timing values."""
        adapter = TimeWeatherAdapter()
        
        adjustment = TimingAdjustment(
            green_time_multiplier=1.2,
            yellow_time_multiplier=1.3,
            minimum_green_multiplier=1.1,
            cycle_time_multiplier=1.0
        )
        
        result = adapter.apply_adjustment_to_timing(
            base_green_time=30.0,
            base_yellow_time=3.0,
            base_minimum_green=10.0,
            adjustment=adjustment
        )
        
        assert abs(result["green_time"] - 36.0) < 0.001  # 30 * 1.2
        assert abs(result["yellow_time"] - 3.9) < 0.001  # 3 * 1.3
        assert abs(result["minimum_green"] - 11.0) < 0.001  # 10 * 1.1
    
    def test_apply_adjustment_without_providing_adjustment(self):
        """Test applying adjustment using current conditions."""
        adapter = TimeWeatherAdapter()
        
        result = adapter.apply_adjustment_to_timing(
            base_green_time=30.0,
            base_yellow_time=3.0,
            base_minimum_green=10.0
        )
        
        # Should return adjusted values
        assert "green_time" in result
        assert "yellow_time" in result
        assert "minimum_green" in result
        assert all(v > 0 for v in result.values())
