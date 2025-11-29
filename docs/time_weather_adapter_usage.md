# TimeWeatherAdapter Usage Guide

## Overview

The `TimeWeatherAdapter` class provides time-of-day and weather-based signal timing adjustments for the SMART FLOW v2 traffic management system.

## Basic Usage

### Initialize the Adapter

```python
from src.time_weather_adapter import TimeWeatherAdapter

# Without weather API (time-based only)
adapter = TimeWeatherAdapter()

# With weather API integration
adapter = TimeWeatherAdapter(
    weather_api_key="your_openweathermap_api_key",
    location="Seattle,WA"
)
```

### Detect Time of Day

```python
from datetime import datetime

# Detect current time
time_of_day = adapter.detect_time_of_day()
print(f"Current time classification: {time_of_day}")

# Detect specific time
specific_time = datetime(2024, 1, 15, 8, 30, 0)  # 8:30 AM
time_of_day = adapter.detect_time_of_day(specific_time)
# Returns: TimeOfDay.PEAK_MORNING
```

### Get Time-Based Adjustments

```python
# Get adjustment for current time
adjustment = adapter.get_time_based_adjustment()

print(f"Green time multiplier: {adjustment.green_time_multiplier}")
print(f"Yellow time multiplier: {adjustment.yellow_time_multiplier}")
print(f"Cycle time multiplier: {adjustment.cycle_time_multiplier}")
```

### Detect Weather

```python
# Requires weather_api_key and location to be set
weather = adapter.detect_weather()
print(f"Current weather: {weather}")
```

### Get Weather-Based Adjustments

```python
# Get adjustment for current weather
adjustment = adapter.get_weather_based_adjustment()

# Or specify weather condition
from src.time_weather_adapter import WeatherCondition
adjustment = adapter.get_weather_based_adjustment(WeatherCondition.RAIN)
```

### Get Combined Adjustments

```python
# Combines both time and weather factors
combined = adapter.get_combined_adjustment()

# Apply to base timing values
adjusted_timing = adapter.apply_adjustment_to_timing(
    base_green_time=30.0,      # seconds
    base_yellow_time=3.0,      # seconds
    base_minimum_green=10.0,   # seconds
    adjustment=combined
)

print(f"Adjusted green time: {adjusted_timing['green_time']}")
print(f"Adjusted yellow time: {adjusted_timing['yellow_time']}")
print(f"Adjusted minimum green: {adjusted_timing['minimum_green']}")
```

## Time Classifications

- **PEAK_MORNING**: 7:00 AM - 9:30 AM
- **PEAK_EVENING**: 4:30 PM - 7:00 PM
- **NIGHT**: 10:00 PM - 6:00 AM
- **OFF_PEAK**: All other times

## Weather Conditions

- **CLEAR**: Normal conditions
- **RAIN**: Light to moderate rain
- **HEAVY_RAIN**: Heavy or extreme rain
- **SNOW**: Light to moderate snow
- **HEAVY_SNOW**: Heavy or extreme snow
- **FOG**: Reduced visibility conditions
- **UNKNOWN**: Weather data unavailable

## Adjustment Factors

### Peak Hours (Morning/Evening)
- Green time: +20% (1.2x)
- Cycle time: +10% (1.1x)
- Minimum green: -10% (0.9x)

### Night Hours
- Green time: -30% (0.7x)
- Cycle time: -30% (0.7x)
- Minimum green: -20% (0.8x)

### Off-Peak Hours
- All factors: 1.0x (no adjustment)

### Weather Adjustments
- **Heavy Rain/Snow**: Yellow time +50% (1.5x)
- **Rain/Snow**: Yellow time +30% (1.3x)
- **Fog**: Yellow time +40% (1.4x)
- **Clear**: No adjustment (1.0x)

## Integration Example

```python
from src.time_weather_adapter import TimeWeatherAdapter
from src.advanced_signal_controller import AdvancedSignalController

# Initialize adapter
adapter = TimeWeatherAdapter(
    weather_api_key="your_api_key",
    location="Seattle,WA"
)

# Get current adjustments
adjustment = adapter.get_combined_adjustment()

# Apply to signal controller
base_green = 30.0
base_yellow = 3.0
base_minimum = 10.0

adjusted = adapter.apply_adjustment_to_timing(
    base_green_time=base_green,
    base_yellow_time=base_yellow,
    base_minimum_green=base_minimum
)

# Use adjusted values in signal controller
controller = AdvancedSignalController(config)
# ... apply adjusted timing values to controller
```

## Weather API Setup

To use weather detection, you need an OpenWeatherMap API key:

1. Sign up at https://openweathermap.org/api
2. Get your free API key
3. Pass it to the TimeWeatherAdapter constructor

The adapter caches weather data for 10 minutes to minimize API calls.

## Notes

- Weather detection is optional; the adapter works with time-based adjustments only
- Combined adjustments multiply time and weather factors
- All timing adjustments are multiplicative factors (not absolute values)
- The adapter is stateless except for weather caching
