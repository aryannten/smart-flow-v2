# Configuration Schema Documentation

## Overview

SMART FLOW v2 uses JSON or YAML configuration files to define intersection layouts, signal timing parameters, and system behavior. This document describes the complete configuration schema with examples and validation rules.

## Configuration File Formats

### JSON Format

```json
{
  "intersection": { },
  "lanes": { },
  "turn_lanes": { },
  "crosswalks": { },
  "signal_timing": { },
  "detection": { },
  "features": { }
}
```

### YAML Format

```yaml
intersection:
  # Intersection configuration

lanes:
  # Lane definitions

turn_lanes:
  # Turn lane definitions

crosswalks:
  # Crosswalk definitions

signal_timing:
  # Signal timing parameters

detection:
  # Detection parameters

features:
  # Feature flags
```

## Schema Sections

### 1. Intersection Configuration

Defines basic intersection properties.

```json
{
  "intersection": {
    "name": "Main Street & 5th Avenue",
    "id": "intersection_001",
    "location": {
      "latitude": 40.7128,
      "longitude": -74.0060,
      "address": "Main St & 5th Ave, City, State"
    },
    "video_source": "data/intersection.mp4",
    "video_source_type": "file",
    "frame_width": 1920,
    "frame_height": 1080
  }
}
```

**Fields:**
- `name` (string, required): Human-readable intersection name
- `id` (string, optional): Unique identifier for multi-intersection networks
- `location` (object, optional): Geographic location
  - `latitude` (number): Latitude coordinate
  - `longitude` (number): Longitude coordinate
  - `address` (string): Street address
- `video_source` (string, required): Video source path or URL
- `video_source_type` (string, optional): "file", "youtube", "rtsp", "webcam" (auto-detected if omitted)
- `frame_width` (integer, optional): Expected frame width in pixels
- `frame_height` (integer, optional): Expected frame height in pixels

### 2. Lane Configuration

Defines traffic lanes and their regions.

```json
{
  "lanes": {
    "north": {
      "region": [100, 0, 300, 400],
      "direction": "north",
      "minimum_green": 10,
      "maximum_green": 60,
      "priority_weight": 1.0,
      "conflicting_lanes": ["south"],
      "compatible_lanes": ["north_left", "north_right"]
    },
    "south": {
      "region": [300, 400, 500, 800],
      "direction": "south",
      "minimum_green": 10,
      "maximum_green": 60,
      "priority_weight": 1.0,
      "conflicting_lanes": ["north"],
      "compatible_lanes": ["south_left", "south_right"]
    }
  }
}
```

**Fields:**
- `region` (array[4], required): Bounding box [x1, y1, x2, y2] in pixels
  - `x1, y1`: Top-left corner
  - `x2, y2`: Bottom-right corner
- `direction` (string, required): "north", "south", "east", "west", "northeast", etc.
- `minimum_green` (integer, required): Minimum green time in seconds (5-30)
- `maximum_green` (integer, required): Maximum green time in seconds (30-120)
- `priority_weight` (number, optional): Base priority weight (0.5-2.0, default: 1.0)
- `conflicting_lanes` (array[string], optional): Lanes that cannot be green simultaneously
- `compatible_lanes` (array[string], optional): Lanes that can be green simultaneously

**Validation Rules:**
- Region coordinates must be within frame dimensions
- `x2 > x1` and `y2 > y1`
- `minimum_green < maximum_green`
- `minimum_green >= 5` and `maximum_green <= 120`

### 3. Turn Lane Configuration

Defines dedicated turn lanes with protected phases.

```json
{
  "turn_lanes": {
    "north_left": {
      "region": [100, 0, 200, 400],
      "turn_type": "left",
      "parent_lane": "north",
      "minimum_green": 5,
      "maximum_green": 30,
      "activation_threshold": 3,
      "conflicting_movements": ["south", "east_left", "west"],
      "protected_phase_required": true
    },
    "east_right": {
      "region": [600, 200, 700, 400],
      "turn_type": "right",
      "parent_lane": "east",
      "minimum_green": 5,
      "maximum_green": 20,
      "activation_threshold": 5,
      "conflicting_movements": ["north_crosswalk"],
      "protected_phase_required": false,
      "permissive_allowed": true
    }
  }
}
```

**Fields:**
- `region` (array[4], required): Bounding box for turn lane
- `turn_type` (string, required): "left", "right", "u_turn"
- `parent_lane` (string, required): Associated through lane
- `minimum_green` (integer, required): Minimum protected phase duration (3-15)
- `maximum_green` (integer, required): Maximum protected phase duration (10-45)
- `activation_threshold` (integer, required): Minimum vehicles to activate protected phase
- `conflicting_movements` (array[string], required): Conflicting lanes/crosswalks
- `protected_phase_required` (boolean, optional): Always use protected phase (default: false)
- `permissive_allowed` (boolean, optional): Allow permissive turns (default: true)

**Turn Types:**
- `left`: Left turn
- `right`: Right turn
- `u_turn`: U-turn

### 4. Crosswalk Configuration

Defines pedestrian crosswalks.

```json
{
  "crosswalks": {
    "north_crosswalk": {
      "region": [250, 380, 450, 420],
      "crossing_distance": 15.0,
      "conflicting_lanes": ["east", "west", "east_right", "west_right"],
      "minimum_crossing_time": 7,
      "pedestrian_speed_mps": 1.2,
      "activation_threshold": 1,
      "walk_signal_duration": 10,
      "flashing_dont_walk_duration": 5
    },
    "east_crosswalk": {
      "region": [480, 150, 520, 350],
      "crossing_distance": 12.0,
      "conflicting_lanes": ["north", "south", "north_left", "south_left"],
      "minimum_crossing_time": 6,
      "pedestrian_speed_mps": 1.2,
      "activation_threshold": 1
    }
  }
}
```

**Fields:**
- `region` (array[4], required): Detection region for waiting pedestrians
- `crossing_distance` (number, required): Crosswalk width in meters
- `conflicting_lanes` (array[string], required): Lanes that must be red during crossing
- `minimum_crossing_time` (integer, required): Minimum walk signal duration (5-15)
- `pedestrian_speed_mps` (number, optional): Average pedestrian speed in m/s (default: 1.2)
- `activation_threshold` (integer, optional): Minimum pedestrians to activate (default: 1)
- `walk_signal_duration` (integer, optional): Walk signal duration in seconds
- `flashing_dont_walk_duration` (integer, optional): Flashing don't walk duration

**Validation Rules:**
- `crossing_distance > 0`
- `minimum_crossing_time >= crossing_distance / pedestrian_speed_mps`
- `pedestrian_speed_mps` typically 0.8-1.5 m/s

### 5. Signal Timing Configuration

Defines global signal timing parameters.

```json
{
  "signal_timing": {
    "yellow_duration": 3,
    "all_red_duration": 2,
    "cycle_interval_frames": 30,
    "minimum_cycle_time": 30,
    "maximum_cycle_time": 180,
    "default_min_green": 10,
    "default_max_green": 60,
    "emergency_preemption_enabled": true,
    "coordination_enabled": false
  }
}
```

**Fields:**
- `yellow_duration` (integer, required): Yellow phase duration in seconds (3-5)
- `all_red_duration` (integer, required): All-red clearance time in seconds (1-3)
- `cycle_interval_frames` (integer, required): Frames between signal updates (15-60)
- `minimum_cycle_time` (integer, optional): Minimum total cycle time in seconds (30-60)
- `maximum_cycle_time` (integer, optional): Maximum total cycle time in seconds (120-300)
- `default_min_green` (integer, optional): Default minimum green time (5-15)
- `default_max_green` (integer, optional): Default maximum green time (30-90)
- `emergency_preemption_enabled` (boolean, optional): Enable emergency vehicle priority (default: true)
- `coordination_enabled` (boolean, optional): Enable multi-intersection coordination (default: false)

**Validation Rules:**
- `yellow_duration >= 3` (safety requirement)
- `all_red_duration >= 1`
- `minimum_cycle_time < maximum_cycle_time`

### 6. Detection Configuration

Defines object detection parameters.

```json
{
  "detection": {
    "model_path": "yolov8n.pt",
    "confidence_threshold": 0.5,
    "iou_threshold": 0.45,
    "enable_tracking": true,
    "tracking_algorithm": "sort",
    "max_tracking_age": 30,
    "min_tracking_hits": 3,
    "vehicle_classes": [2, 3, 5, 7],
    "pedestrian_classes": [0],
    "emergency_vehicle_detection": true,
    "vehicle_type_classification": true
  }
}
```

**Fields:**
- `model_path` (string, required): Path to YOLO model file
- `confidence_threshold` (number, required): Detection confidence threshold (0.0-1.0)
- `iou_threshold` (number, optional): IoU threshold for NMS (0.0-1.0, default: 0.45)
- `enable_tracking` (boolean, optional): Enable object tracking (default: true)
- `tracking_algorithm` (string, optional): "sort" or "deepsort" (default: "sort")
- `max_tracking_age` (integer, optional): Max frames to keep lost tracks (default: 30)
- `min_tracking_hits` (integer, optional): Min detections to confirm track (default: 3)
- `vehicle_classes` (array[integer], optional): COCO class IDs for vehicles
- `pedestrian_classes` (array[integer], optional): COCO class IDs for pedestrians
- `emergency_vehicle_detection` (boolean, optional): Enable emergency detection (default: true)
- `vehicle_type_classification` (boolean, optional): Classify vehicle types (default: true)

**COCO Class IDs:**
- 0: person
- 2: car
- 3: motorcycle
- 5: bus
- 7: truck

### 7. Feature Configuration

Enables or disables specific features.

```json
{
  "features": {
    "pedestrian_management": true,
    "emergency_priority": true,
    "turn_lane_control": true,
    "queue_estimation": true,
    "object_tracking": true,
    "traffic_heatmap": true,
    "trajectory_visualization": true,
    "time_of_day_adaptation": false,
    "weather_adaptation": false,
    "multi_intersection_coordination": false
  }
}
```

**Fields:**
- `pedestrian_management` (boolean): Enable pedestrian detection and crosswalk management
- `emergency_priority` (boolean): Enable emergency vehicle priority
- `turn_lane_control` (boolean): Enable turn lane management
- `queue_estimation` (boolean): Enable queue length estimation
- `object_tracking` (boolean): Enable vehicle/pedestrian tracking
- `traffic_heatmap` (boolean): Enable traffic density heatmap visualization
- `trajectory_visualization` (boolean): Enable trajectory visualization
- `time_of_day_adaptation` (boolean): Enable time-based timing adjustments
- `weather_adaptation` (boolean): Enable weather-based timing adjustments
- `multi_intersection_coordination` (boolean): Enable network coordination

### 8. Dashboard Configuration

Configures web dashboard settings.

```json
{
  "dashboard": {
    "enabled": true,
    "port": 8080,
    "host": "0.0.0.0",
    "websocket_update_interval": 0.5,
    "enable_video_stream": true,
    "video_stream_fps": 15,
    "video_stream_quality": 80,
    "enable_manual_override": true,
    "enable_parameter_adjustment": true,
    "alert_thresholds": {
      "high_density": 0.75,
      "high_wait_time": 60,
      "queue_spillback": 0.9
    }
  }
}
```

**Fields:**
- `enabled` (boolean): Enable web dashboard
- `port` (integer): Dashboard port (1024-65535)
- `host` (string): Bind address ("0.0.0.0" for all interfaces)
- `websocket_update_interval` (number): Update interval in seconds (0.1-5.0)
- `enable_video_stream` (boolean): Enable video streaming
- `video_stream_fps` (integer): Video stream frame rate (5-30)
- `video_stream_quality` (integer): JPEG quality (1-100)
- `enable_manual_override` (boolean): Allow manual signal overrides
- `enable_parameter_adjustment` (boolean): Allow parameter adjustments
- `alert_thresholds` (object): Thresholds for automatic alerts

## Multi-Intersection Network Configuration

For coordinated networks, use a network configuration file:

```yaml
network:
  name: "Downtown Corridor"
  id: "network_001"
  coordination_enabled: true
  target_speed_mph: 35
  update_interval_seconds: 1.0
  optimization_objective: "minimize_stops"

intersections:
  intersection_1:
    name: "Main & 1st"
    config_file: "config/intersection_1.json"
    location:
      latitude: 40.7128
      longitude: -74.0060
  
  intersection_2:
    name: "Main & 2nd"
    config_file: "config/intersection_2.json"
    location:
      latitude: 40.7138
      longitude: -74.0060

connections:
  - from: "intersection_1"
    to: "intersection_2"
    travel_time_seconds: 30
    distance_meters: 400
    direction: "north"
  
  - from: "intersection_2"
    to: "intersection_3"
    travel_time_seconds: 25
    distance_meters: 350
    direction: "north"

coordination:
  algorithm: "green_wave"
  offset_optimization: "dynamic"
  sync_tolerance_seconds: 2.0
  reoptimize_interval_seconds: 300
```

**Network Fields:**
- `name` (string): Network name
- `id` (string): Unique network identifier
- `coordination_enabled` (boolean): Enable coordination
- `target_speed_mph` (number): Target vehicle speed for green wave
- `update_interval_seconds` (number): Coordination update interval
- `optimization_objective` (string): "minimize_stops", "minimize_delay", "maximize_throughput"

**Intersection Fields:**
- `name` (string): Intersection name
- `config_file` (string): Path to intersection config file
- `location` (object): Geographic coordinates

**Connection Fields:**
- `from` (string): Source intersection ID
- `to` (string): Destination intersection ID
- `travel_time_seconds` (number): Average travel time
- `distance_meters` (number): Distance between intersections
- `direction` (string): Travel direction

## Complete Example

See `config/comprehensive_intersection_example.json` for a complete configuration example with all features enabled.

## Validation

### Schema Validation

Use JSON Schema or YAML schema validation:

```python
import json
import jsonschema

# Load schema
with open('config/schema.json') as f:
    schema = json.load(f)

# Load configuration
with open('config/my_intersection.json') as f:
    config = json.load(f)

# Validate
try:
    jsonschema.validate(config, schema)
    print("Configuration is valid")
except jsonschema.ValidationError as e:
    print(f"Validation error: {e.message}")
```

### Runtime Validation

The system performs runtime validation:

```python
from src.config_loader import ConfigLoader

try:
    config = ConfigLoader.load('config/my_intersection.json')
    print("Configuration loaded successfully")
except ValueError as e:
    print(f"Configuration error: {e}")
```

## Configuration Best Practices

### 1. Start Simple

Begin with minimal configuration:

```json
{
  "intersection": {
    "name": "Test Intersection",
    "video_source": "data/test.mp4"
  },
  "lanes": {
    "north": {
      "region": [100, 0, 300, 400],
      "direction": "north",
      "minimum_green": 10,
      "maximum_green": 60
    }
  },
  "signal_timing": {
    "yellow_duration": 3,
    "all_red_duration": 2,
    "cycle_interval_frames": 30
  }
}
```

### 2. Incremental Enhancement

Add features incrementally:

1. Basic lanes
2. Turn lanes
3. Crosswalks
4. Advanced features

### 3. Use Comments (YAML)

YAML supports comments for documentation:

```yaml
lanes:
  north:
    region: [100, 0, 300, 400]  # Top-left quadrant
    direction: "north"
    minimum_green: 10  # Minimum 10 seconds for safety
    maximum_green: 60  # Maximum 60 seconds to prevent starvation
```

### 4. Validate Regions

Use visualization to verify lane regions:

```python
import cv2
import json

# Load config
with open('config/my_intersection.json') as f:
    config = json.load(f)

# Load frame
frame = cv2.imread('data/frame.jpg')

# Draw regions
for lane_name, lane_config in config['lanes'].items():
    x1, y1, x2, y2 = lane_config['region']
    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
    cv2.putText(frame, lane_name, (x1, y1-10), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

cv2.imshow('Lane Regions', frame)
cv2.waitKey(0)
```

### 5. Version Control

Include version information:

```json
{
  "config_version": "2.0",
  "created_date": "2024-01-15",
  "last_modified": "2024-01-20",
  "author": "Traffic Engineer Name",
  "notes": "Updated turn lane thresholds based on field observations"
}
```

## Troubleshooting

### Invalid Region Coordinates

**Error**: "Region coordinates out of bounds"  
**Solution**: Verify coordinates are within video frame dimensions

### Conflicting Lane Definitions

**Error**: "Lanes overlap excessively"  
**Solution**: Adjust region boundaries to minimize overlap

### Invalid Timing Parameters

**Error**: "minimum_green must be less than maximum_green"  
**Solution**: Check timing parameters follow validation rules

### Missing Required Fields

**Error**: "Missing required field: 'region'"  
**Solution**: Ensure all required fields are present

## Tools

### Configuration Generator

Use the configuration generator tool:

```bash
python tools/generate_config.py --video data/intersection.mp4 --output config/generated.json
```

### Configuration Validator

Validate configuration files:

```bash
python tools/validate_config.py config/my_intersection.json
```

### Region Selector

Interactive region selection tool:

```bash
python tools/select_regions.py --video data/intersection.mp4 --output config/regions.json
```

## Support

For configuration issues:
- Review this documentation
- Check example configurations in `config/`
- See `docs/configuration_guide.md`
- Open an issue on GitHub

---

## License

MIT License - See LICENSE file for details
