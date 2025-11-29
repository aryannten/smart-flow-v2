"""
Time and Weather Adaptation Module for SMART FLOW v2.

This module provides time-of-day and weather-based signal timing adjustments
to optimize traffic flow under different environmental conditions.
"""
from dataclasses import dataclass
from datetime import datetime, time
from enum import Enum
from typing import Optional, Dict
import requests


class TimeOfDay(Enum):
    """Time of day classifications."""
    PEAK_MORNING = "peak_morning"
    PEAK_EVENING = "peak_evening"
    OFF_PEAK = "off_peak"
    NIGHT = "night"


class WeatherCondition(Enum):
    """Weather condition classifications."""
    CLEAR = "clear"
    RAIN = "rain"
    SNOW = "snow"
    FOG = "fog"
    HEAVY_RAIN = "heavy_rain"
    HEAVY_SNOW = "heavy_snow"
    UNKNOWN = "unknown"


@dataclass
class TimingAdjustment:
    """Timing adjustment factors for signal control."""
    green_time_multiplier: float  # Multiplier for green time allocation
    yellow_time_multiplier: float  # Multiplier for yellow phase duration
    minimum_green_multiplier: float  # Multiplier for minimum green time
    cycle_time_multiplier: float  # Multiplier for total cycle time


class TimeWeatherAdapter:
    """
    Adapts signal timing based on time of day and weather conditions.
    
    This class detects the current time of day and weather conditions,
    then provides timing adjustment factors to optimize traffic flow.
    """
    
    # Peak hour definitions (24-hour format)
    PEAK_MORNING_START = time(7, 0)  # 7:00 AM
    PEAK_MORNING_END = time(9, 30)   # 9:30 AM
    PEAK_EVENING_START = time(16, 30)  # 4:30 PM
    PEAK_EVENING_END = time(19, 0)   # 7:00 PM
    NIGHT_START = time(22, 0)  # 10:00 PM
    NIGHT_END = time(6, 0)     # 6:00 AM
    
    def __init__(self, weather_api_key: Optional[str] = None, 
                 location: Optional[str] = None):
        """
        Initialize the TimeWeatherAdapter.
        
        Args:
            weather_api_key: Optional API key for weather service
            location: Optional location for weather detection (e.g., "Seattle,WA")
        """
        self.weather_api_key = weather_api_key
        self.location = location
        self.current_weather: WeatherCondition = WeatherCondition.UNKNOWN
        self.last_weather_update: Optional[datetime] = None
        
    def detect_time_of_day(self, current_time: Optional[datetime] = None) -> TimeOfDay:
        """
        Detect and classify the current time of day.
        
        Args:
            current_time: Optional datetime to classify. If None, uses current time.
            
        Returns:
            TimeOfDay classification
        """
        if current_time is None:
            current_time = datetime.now()
        
        current_time_only = current_time.time()
        
        # Check for peak morning hours
        if self.PEAK_MORNING_START <= current_time_only <= self.PEAK_MORNING_END:
            return TimeOfDay.PEAK_MORNING
        
        # Check for peak evening hours
        if self.PEAK_EVENING_START <= current_time_only <= self.PEAK_EVENING_END:
            return TimeOfDay.PEAK_EVENING
        
        # Check for night hours
        if current_time_only >= self.NIGHT_START or current_time_only <= self.NIGHT_END:
            return TimeOfDay.NIGHT
        
        # Otherwise, it's off-peak
        return TimeOfDay.OFF_PEAK
    
    def get_time_based_adjustment(self, time_of_day: Optional[TimeOfDay] = None) -> TimingAdjustment:
        """
        Get timing adjustment factors based on time of day.
        
        Args:
            time_of_day: Optional TimeOfDay classification. If None, detects current time.
            
        Returns:
            TimingAdjustment with multipliers for signal timing
        """
        if time_of_day is None:
            time_of_day = self.detect_time_of_day()
        
        if time_of_day == TimeOfDay.PEAK_MORNING or time_of_day == TimeOfDay.PEAK_EVENING:
            # Peak hours: aggressive timing to maximize throughput
            return TimingAdjustment(
                green_time_multiplier=1.2,  # 20% more green time
                yellow_time_multiplier=1.0,  # Standard yellow
                minimum_green_multiplier=0.9,  # Shorter minimum to be more responsive
                cycle_time_multiplier=1.1  # Slightly longer cycles
            )
        elif time_of_day == TimeOfDay.NIGHT:
            # Night: minimal timing to reduce wait times
            return TimingAdjustment(
                green_time_multiplier=0.7,  # 30% less green time
                yellow_time_multiplier=1.0,  # Standard yellow
                minimum_green_multiplier=0.8,  # Shorter minimum green
                cycle_time_multiplier=0.7  # Much shorter cycles
            )
        else:  # OFF_PEAK
            # Off-peak: balanced timing
            return TimingAdjustment(
                green_time_multiplier=1.0,  # Standard green time
                yellow_time_multiplier=1.0,  # Standard yellow
                minimum_green_multiplier=1.0,  # Standard minimum
                cycle_time_multiplier=1.0  # Standard cycle
            )
    
    def detect_weather(self) -> WeatherCondition:
        """
        Detect current weather conditions.
        
        If weather API is configured, fetches current weather.
        Otherwise, returns the last known weather or UNKNOWN.
        
        Returns:
            WeatherCondition classification
        """
        # If no API key or location, return cached or unknown
        if not self.weather_api_key or not self.location:
            return self.current_weather
        
        # Check if we need to update (cache for 10 minutes)
        if self.last_weather_update is not None:
            time_since_update = (datetime.now() - self.last_weather_update).total_seconds()
            if time_since_update < 600:  # 10 minutes
                return self.current_weather
        
        # Fetch weather from API
        try:
            weather = self._fetch_weather_from_api()
            self.current_weather = weather
            self.last_weather_update = datetime.now()
            return weather
        except Exception:
            # If API call fails, return cached or unknown
            return self.current_weather
    
    def _fetch_weather_from_api(self) -> WeatherCondition:
        """
        Fetch weather from OpenWeatherMap API.
        
        Returns:
            WeatherCondition based on API response
            
        Raises:
            Exception: If API call fails
        """
        # Using OpenWeatherMap API as an example
        url = "http://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": self.location,
            "appid": self.weather_api_key,
            "units": "metric"
        }
        
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        
        data = response.json()
        
        # Parse weather condition from response
        if "weather" in data and len(data["weather"]) > 0:
            weather_main = data["weather"][0]["main"].lower()
            weather_desc = data["weather"][0]["description"].lower()
            
            # Map API weather to our conditions
            if "rain" in weather_main or "rain" in weather_desc:
                if "heavy" in weather_desc or "extreme" in weather_desc:
                    return WeatherCondition.HEAVY_RAIN
                return WeatherCondition.RAIN
            elif "snow" in weather_main or "snow" in weather_desc:
                if "heavy" in weather_desc or "extreme" in weather_desc:
                    return WeatherCondition.HEAVY_SNOW
                return WeatherCondition.SNOW
            elif "fog" in weather_main or "mist" in weather_main or "fog" in weather_desc:
                return WeatherCondition.FOG
            else:
                return WeatherCondition.CLEAR
        
        return WeatherCondition.UNKNOWN
    
    def get_weather_based_adjustment(self, weather: Optional[WeatherCondition] = None) -> TimingAdjustment:
        """
        Get timing adjustment factors based on weather conditions.
        
        Args:
            weather: Optional WeatherCondition. If None, detects current weather.
            
        Returns:
            TimingAdjustment with multipliers for signal timing
        """
        if weather is None:
            weather = self.detect_weather()
        
        if weather == WeatherCondition.HEAVY_RAIN or weather == WeatherCondition.HEAVY_SNOW:
            # Severe weather: increase safety margins significantly
            return TimingAdjustment(
                green_time_multiplier=1.1,  # Slightly more green time
                yellow_time_multiplier=1.5,  # 50% longer yellow for safety
                minimum_green_multiplier=1.2,  # Longer minimum green
                cycle_time_multiplier=1.2  # Longer cycles
            )
        elif weather == WeatherCondition.RAIN or weather == WeatherCondition.SNOW:
            # Moderate adverse weather: increase safety margins
            return TimingAdjustment(
                green_time_multiplier=1.05,  # Slightly more green time
                yellow_time_multiplier=1.3,  # 30% longer yellow for safety
                minimum_green_multiplier=1.1,  # Longer minimum green
                cycle_time_multiplier=1.1  # Slightly longer cycles
            )
        elif weather == WeatherCondition.FOG:
            # Reduced visibility: increase yellow time
            return TimingAdjustment(
                green_time_multiplier=1.0,  # Standard green time
                yellow_time_multiplier=1.4,  # 40% longer yellow for safety
                minimum_green_multiplier=1.1,  # Longer minimum green
                cycle_time_multiplier=1.05  # Slightly longer cycles
            )
        else:  # CLEAR or UNKNOWN
            # Normal weather: no adjustment
            return TimingAdjustment(
                green_time_multiplier=1.0,
                yellow_time_multiplier=1.0,
                minimum_green_multiplier=1.0,
                cycle_time_multiplier=1.0
            )
    
    def get_combined_adjustment(self, 
                               time_of_day: Optional[TimeOfDay] = None,
                               weather: Optional[WeatherCondition] = None) -> TimingAdjustment:
        """
        Get combined timing adjustment based on both time and weather.
        
        Combines time-based and weather-based adjustments by multiplying factors.
        
        Args:
            time_of_day: Optional TimeOfDay classification
            weather: Optional WeatherCondition
            
        Returns:
            Combined TimingAdjustment
        """
        time_adj = self.get_time_based_adjustment(time_of_day)
        weather_adj = self.get_weather_based_adjustment(weather)
        
        # Combine adjustments by multiplying factors
        return TimingAdjustment(
            green_time_multiplier=time_adj.green_time_multiplier * weather_adj.green_time_multiplier,
            yellow_time_multiplier=time_adj.yellow_time_multiplier * weather_adj.yellow_time_multiplier,
            minimum_green_multiplier=time_adj.minimum_green_multiplier * weather_adj.minimum_green_multiplier,
            cycle_time_multiplier=time_adj.cycle_time_multiplier * weather_adj.cycle_time_multiplier
        )
    
    def apply_adjustment_to_timing(self, 
                                   base_green_time: float,
                                   base_yellow_time: float,
                                   base_minimum_green: float,
                                   adjustment: Optional[TimingAdjustment] = None) -> Dict[str, float]:
        """
        Apply timing adjustment to base timing values.
        
        Args:
            base_green_time: Base green time in seconds
            base_yellow_time: Base yellow time in seconds
            base_minimum_green: Base minimum green time in seconds
            adjustment: Optional TimingAdjustment. If None, uses combined current adjustment.
            
        Returns:
            Dictionary with adjusted timing values
        """
        if adjustment is None:
            adjustment = self.get_combined_adjustment()
        
        return {
            "green_time": base_green_time * adjustment.green_time_multiplier,
            "yellow_time": base_yellow_time * adjustment.yellow_time_multiplier,
            "minimum_green": base_minimum_green * adjustment.minimum_green_multiplier
        }
