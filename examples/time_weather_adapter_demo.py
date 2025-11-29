"""
Demo script for TimeWeatherAdapter functionality.

This script demonstrates how to use the TimeWeatherAdapter to adjust
signal timing based on time of day and weather conditions.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import datetime, time
from src.time_weather_adapter import (
    TimeWeatherAdapter,
    TimeOfDay,
    WeatherCondition
)


def demo_time_detection():
    """Demonstrate time of day detection."""
    print("=" * 60)
    print("TIME OF DAY DETECTION DEMO")
    print("=" * 60)
    
    adapter = TimeWeatherAdapter()
    
    # Test different times
    test_times = [
        (datetime(2024, 1, 15, 8, 0, 0), "8:00 AM"),
        (datetime(2024, 1, 15, 12, 0, 0), "12:00 PM"),
        (datetime(2024, 1, 15, 17, 30, 0), "5:30 PM"),
        (datetime(2024, 1, 15, 23, 0, 0), "11:00 PM"),
        (datetime(2024, 1, 15, 3, 0, 0), "3:00 AM"),
    ]
    
    for test_time, label in test_times:
        tod = adapter.detect_time_of_day(test_time)
        print(f"{label:12} -> {tod.value}")
    
    print()


def demo_time_adjustments():
    """Demonstrate time-based timing adjustments."""
    print("=" * 60)
    print("TIME-BASED ADJUSTMENT DEMO")
    print("=" * 60)
    
    adapter = TimeWeatherAdapter()
    
    # Base timing values
    base_green = 30.0
    base_yellow = 3.0
    base_minimum = 10.0
    
    print(f"Base timing values:")
    print(f"  Green time: {base_green}s")
    print(f"  Yellow time: {base_yellow}s")
    print(f"  Minimum green: {base_minimum}s")
    print()
    
    # Test different times of day
    times = [
        (TimeOfDay.PEAK_MORNING, "Peak Morning"),
        (TimeOfDay.PEAK_EVENING, "Peak Evening"),
        (TimeOfDay.OFF_PEAK, "Off-Peak"),
        (TimeOfDay.NIGHT, "Night"),
    ]
    
    for tod, label in times:
        adjustment = adapter.get_time_based_adjustment(tod)
        adjusted = adapter.apply_adjustment_to_timing(
            base_green, base_yellow, base_minimum, adjustment
        )
        
        print(f"{label}:")
        print(f"  Green time: {adjusted['green_time']:.1f}s "
              f"({adjustment.green_time_multiplier:.1f}x)")
        print(f"  Yellow time: {adjusted['yellow_time']:.1f}s "
              f"({adjustment.yellow_time_multiplier:.1f}x)")
        print(f"  Minimum green: {adjusted['minimum_green']:.1f}s "
              f"({adjustment.minimum_green_multiplier:.1f}x)")
        print()


def demo_weather_adjustments():
    """Demonstrate weather-based timing adjustments."""
    print("=" * 60)
    print("WEATHER-BASED ADJUSTMENT DEMO")
    print("=" * 60)
    
    adapter = TimeWeatherAdapter()
    
    # Base timing values
    base_green = 30.0
    base_yellow = 3.0
    base_minimum = 10.0
    
    print(f"Base timing values:")
    print(f"  Green time: {base_green}s")
    print(f"  Yellow time: {base_yellow}s")
    print(f"  Minimum green: {base_minimum}s")
    print()
    
    # Test different weather conditions
    conditions = [
        (WeatherCondition.CLEAR, "Clear"),
        (WeatherCondition.RAIN, "Rain"),
        (WeatherCondition.HEAVY_RAIN, "Heavy Rain"),
        (WeatherCondition.SNOW, "Snow"),
        (WeatherCondition.FOG, "Fog"),
    ]
    
    for weather, label in conditions:
        adjustment = adapter.get_weather_based_adjustment(weather)
        adjusted = adapter.apply_adjustment_to_timing(
            base_green, base_yellow, base_minimum, adjustment
        )
        
        print(f"{label}:")
        print(f"  Green time: {adjusted['green_time']:.1f}s "
              f"({adjustment.green_time_multiplier:.1f}x)")
        print(f"  Yellow time: {adjusted['yellow_time']:.1f}s "
              f"({adjustment.yellow_time_multiplier:.1f}x)")
        print(f"  Minimum green: {adjusted['minimum_green']:.1f}s "
              f"({adjustment.minimum_green_multiplier:.1f}x)")
        print()


def demo_combined_adjustments():
    """Demonstrate combined time and weather adjustments."""
    print("=" * 60)
    print("COMBINED ADJUSTMENT DEMO")
    print("=" * 60)
    
    adapter = TimeWeatherAdapter()
    
    # Base timing values
    base_green = 30.0
    base_yellow = 3.0
    base_minimum = 10.0
    
    print(f"Base timing values:")
    print(f"  Green time: {base_green}s")
    print(f"  Yellow time: {base_yellow}s")
    print(f"  Minimum green: {base_minimum}s")
    print()
    
    # Test combinations
    scenarios = [
        (TimeOfDay.PEAK_MORNING, WeatherCondition.CLEAR, 
         "Peak Morning + Clear"),
        (TimeOfDay.PEAK_EVENING, WeatherCondition.RAIN, 
         "Peak Evening + Rain"),
        (TimeOfDay.PEAK_MORNING, WeatherCondition.HEAVY_RAIN, 
         "Peak Morning + Heavy Rain"),
        (TimeOfDay.NIGHT, WeatherCondition.FOG, 
         "Night + Fog"),
        (TimeOfDay.OFF_PEAK, WeatherCondition.SNOW, 
         "Off-Peak + Snow"),
    ]
    
    for tod, weather, label in scenarios:
        adjustment = adapter.get_combined_adjustment(tod, weather)
        adjusted = adapter.apply_adjustment_to_timing(
            base_green, base_yellow, base_minimum, adjustment
        )
        
        print(f"{label}:")
        print(f"  Green time: {adjusted['green_time']:.1f}s "
              f"({adjustment.green_time_multiplier:.2f}x)")
        print(f"  Yellow time: {adjusted['yellow_time']:.1f}s "
              f"({adjustment.yellow_time_multiplier:.2f}x)")
        print(f"  Minimum green: {adjusted['minimum_green']:.1f}s "
              f"({adjustment.minimum_green_multiplier:.2f}x)")
        print()


def main():
    """Run all demos."""
    print("\n")
    print("*" * 60)
    print("TIMEWEATHERADAPTER DEMONSTRATION")
    print("*" * 60)
    print("\n")
    
    demo_time_detection()
    demo_time_adjustments()
    demo_weather_adjustments()
    demo_combined_adjustments()
    
    print("=" * 60)
    print("DEMO COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
