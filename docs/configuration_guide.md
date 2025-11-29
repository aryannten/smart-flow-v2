# SMART FLOW v2 Configuration Guide

This guide explains how to configure SMART FLOW v2 for single intersections, multi-intersection networks, and dashboard settings.

## Table of Contents

1. [Configuration File Formats](#configuration-file-formats)
2. [Single Intersection Configuration](#single-intersection-configuration)
3. [Multi-Intersection Network Configuration](#multi-intersection-network-configuration)
4. [Dashboard Configuration](#dashboard-configuration)
5. [Configuration Validation](#configuration-validation)
6. [Examples](#examples)

## Configuration File Formats

SMART FLOW v2 supports both JSON and YAML configuration files:

- **JSON**: `.json` extension
- **YAML**: `.yaml` or `.yml` extension

Both formats are functionally equivalent. Choose the format you prefer.

## Single Intersection Configuration

### Basic Structure

```yaml
intersection:
  id: string              # Unique identifier for the intersection
  name: string            # Human-readable name
  video_source: string    # Path to video file or stream URL

lanes:
  <lane_name>:
    region: [x1, y1, x2, y2]  # Bounding box coordinates
    direction: string          # north, south, east, west
    type: string              # through, turn, mixed (optional, default: through)

turn_lanes:              # Optional
  <turn_lane_name>:
    region: [x1, y1, x2, y2]
    turn_type: string          # left, right, u_turn
    parent_lane: string        # Reference to parent lane (optional)
    conflicting_movements: [string]  # List of conflicting lanes
    minimum_green: int         # Minimum green time in seconds (default: 5)
    maximum_green: int         # Maximum green time in seconds (default: 30)

crosswalks:              # Optional
  <crosswalk_name>:
    region: [x1, y1, x2, y2]
    crossing_distance: float   # Distance in meters
    conflicting_lanes: [string]  # List of conflicting lanes

signal_timing:           # Optional
  minimum_green: int           # Default: 10 seconds
  maximum_green: int           # Default: 60 seconds
  yellow_duration: int         # Default: 3 seconds
  all_red_duration: int        # Default: 2 seconds
  pedestrian_walk_speed: float # Default: 1.2 m/s

detection:               # Optional
  model_path: string           # Default: yolov8n.pt
  confidence_threshold: float  # Default: 0.5 (range: 0-1)
  tracking_enabled: bool       # Default: true

vehicle_weights:         # Optional
  car: float                   # Default: 1.0
  truck: float                 # Default: 1.5
  bus: float                   # Default: 2.0
  motorcycle: float            # Default: 0.8
  bicycle: float               # Default: 0.5
```

### Region Coordinates

Regions are defined as bounding boxes with coordinates `[x1, y1, x2, y2]`:
- `x1, y1`: Top-left corner
- `x2, y2`: Bottom-right corner

Coordinates are in pixels relative to the video frame.

### Video Sources

Supported video source formats:
- **Local file**: `data/video.mp4`
- **YouTube Live**: `https://youtube.com/watch?v=...`
- **RTSP stream**: `rtsp://camera.ip.address/stream`
- **Webcam**: `webcam:0` (device ID)

### Minimal Example

```yaml
intersection:
  id: simple_intersection
  name: Simple 4-Way Intersection
  video_source: data/testvid.mp4

lanes:
  north:
    region: [100, 0, 300, 400]
    direction: north
  south:
    region: [400, 200, 600, 600]
    direction: south
  east:
    region: [300, 100, 700, 300]
    direction: east
  west:
    region: [0, 300, 400, 500]
    direction: west
```

### Complete Example with Turn Lanes and Crosswalks

See `config/comprehensive_intersection_example.yaml` for a full example.

## Multi-Intersection Network Configuration

### Basic Structure

```yaml
network:
  name: string                    # Network name
  coordination_enabled: bool      # Enable signal coordination
  target_speed_mph: float         # Target speed for green wave
  update_interval: float          # Update interval in seconds

intersections:
  <intersection_id>:
    id: string
    name: string
    video_source: string
    lanes: { ... }                # Same as single intersection
    turn_lanes: { ... }           # Optional
    crosswalks: { ... }           # Optional
    signal_timing: { ... }        # Optional
    detection: { ... }            # Optional
    vehicle_weights: { ... }      # Optional

connections:
  - from: string                  # Source intersection ID
    to: string                    # Destination intersection ID
    distance_meters: float        # Distance between intersections
    travel_time_seconds: float    # Expected travel time

corridors:                        # Optional
  - name: string
    intersections: [string]       # Ordered list of intersection IDs
    direction: string             # Primary direction (north, south, east, west)
    priority: string              # normal, high, low (default: normal)
```

### Network Coordination

When `coordination_enabled` is `true`, the system will:
1. Calculate optimal signal offsets between intersections
2. Create green waves along corridors
3. Synchronize signal timing across the network
4. Minimize stops for through-traffic

### Connections

Connections define the physical relationships between intersections:
- `distance_meters`: Physical distance for offset calculation
- `travel_time_seconds`: Expected travel time at target speed

### Corridors

Corridors define priority routes through the network:
- List intersections in order of travel
- Specify direction for green wave optimization
- Set priority level for allocation decisions

### Example

See `config/multi_intersection_network_example.yaml` for a complete example.

## Dashboard Configuration

### Basic Structure

```yaml
dashboard:
  port: int                       # Web server port (default: 8080)
  host: string                    # Host address (default: 0.0.0.0)
  enable_cors: bool               # Enable CORS (default: true)
  allowed_origins: [string]       # CORS origins (default: ["*"])
  websocket_update_interval: float  # Update interval in seconds (default: 0.5)
  video_stream_fps: int           # Video stream FPS (default: 15)
  video_stream_quality: int       # JPEG quality 0-100 (default: 80)

visualization:                    # Optional
  show_heatmap: bool              # Default: true
  show_trajectories: bool         # Default: true
  show_queue_visualization: bool  # Default: true
  show_metrics_overlay: bool      # Default: true
  heatmap_opacity: float          # Default: 0.4
  trajectory_length: int          # Default: 30 frames

metrics:                          # Optional
  update_interval: float          # Default: 1.0 seconds
  history_length: int             # Default: 3600 seconds
  display_metrics: [string]       # List of metrics to display

alerts:                           # Optional
  enable_emergency_alerts: bool   # Default: true
  enable_congestion_alerts: bool  # Default: true
  congestion_threshold: float     # Default: 0.8
  alert_sound: bool               # Default: false
```

### Example

See `config/dashboard_config.json` for a complete example.

## Configuration Validation

The configuration loader automatically validates all configurations:

### Intersection Validation

- ✓ Required fields: `id`, `name`, `video_source`
- ✓ At least one lane must be configured
- ✓ Turn lane references must point to existing lanes
- ✓ Crosswalk references must point to existing lanes
- ✓ Signal timing values must be positive
- ✓ Confidence threshold must be between 0 and 1

### Network Validation

- ✓ All intersection validations apply
- ✓ Connection references must point to existing intersections
- ✓ Distance and travel time must be positive
- ✓ Corridor references must point to existing intersections
- ✓ Target speed must be positive

### Error Handling

If validation fails, the loader will raise a `ValueError` with detailed error messages:

```python
from src.config_loader import load_config

try:
    config = load_config('config/my_config.json')
except ValueError as e:
    print(f"Configuration error: {e}")
```

## Examples

### Loading Configurations in Python

```python
from src.config_loader import load_config, ConfigLoader

# Auto-detect configuration type
config = load_config('config/single_intersection_config.json')

# Explicitly specify type
config = load_config('config/network.yaml', config_type='network')

# Load and validate separately
loader = ConfigLoader()
intersection_config = loader.load_intersection_config('config/intersection.json')
errors = loader.validate_intersection_config(intersection_config)
if errors:
    print("Validation errors:", errors)
```

### Example Configurations

The `config/` directory contains several example configurations:

1. **simple_intersection_example.yaml**
   - Minimal 4-way intersection
   - No turn lanes or crosswalks
   - Good starting point for basic setups

2. **comprehensive_intersection_example.yaml**
   - Full-featured intersection
   - Multiple turn lanes
   - Four crosswalks
   - Demonstrates all available options

3. **single_intersection_config.json**
   - Production-ready single intersection
   - Includes turn lanes and crosswalks
   - JSON format example

4. **multi_intersection_network_example.yaml**
   - Three-intersection corridor
   - Coordinated signal control
   - Multiple corridors
   - Demonstrates network features

5. **multi_intersection_config.json**
   - Two-intersection network
   - JSON format example
   - Production-ready network setup

### Creating Your Own Configuration

1. **Start with a template**: Copy one of the example files
2. **Adjust video source**: Point to your video file or stream
3. **Define regions**: Use a video player to identify pixel coordinates
4. **Configure lanes**: Define all through-traffic lanes
5. **Add turn lanes** (optional): Define protected turn movements
6. **Add crosswalks** (optional): Define pedestrian crossing areas
7. **Tune timing**: Adjust signal timing parameters as needed
8. **Validate**: Load the configuration to check for errors

### Tips for Region Definition

1. **Use a video editor**: Open your video in a tool that shows pixel coordinates
2. **Pause at a clear frame**: Find a frame with good visibility
3. **Mark lane boundaries**: Note the coordinates of each lane's bounding box
4. **Test and adjust**: Load the config and visualize to verify regions
5. **Account for perspective**: Regions should cover the lane area in the camera view

### Common Configuration Patterns

#### High-Traffic Intersection
```yaml
signal_timing:
  minimum_green: 15
  maximum_green: 90
  yellow_duration: 4
  all_red_duration: 2

vehicle_weights:
  bus: 3.0  # Higher priority for public transit
  truck: 2.0
  car: 1.0
```

#### Pedestrian-Heavy Area
```yaml
signal_timing:
  pedestrian_walk_speed: 1.0  # Slower for elderly/children
  minimum_green: 12
  
crosswalks:
  # Define all crosswalks with adequate crossing time
```

#### Emergency Vehicle Priority
```yaml
detection:
  confidence_threshold: 0.4  # Lower threshold for emergency detection
  tracking_enabled: true     # Essential for emergency tracking
```

## Troubleshooting

### Common Issues

1. **"Configuration file not found"**
   - Check the file path is correct
   - Use absolute paths or paths relative to working directory

2. **"Invalid JSON/YAML"**
   - Validate syntax using a JSON/YAML validator
   - Check for missing commas, brackets, or quotes

3. **"Region must have 4 coordinates"**
   - Ensure all regions are `[x1, y1, x2, y2]` format
   - Check for typos in coordinate lists

4. **"References non-existent lane"**
   - Verify all lane names match exactly
   - Check turn lane and crosswalk references

5. **"Confidence threshold must be between 0 and 1"**
   - Use decimal values like `0.5`, not percentages like `50`

### Getting Help

- Review example configurations in `config/` directory
- Check validation error messages for specific issues
- Consult the design document for detailed specifications
- Test with minimal configurations first, then add complexity

## Advanced Topics

### Dynamic Configuration Updates

Currently, configurations are loaded at startup. To change configuration:
1. Stop the system
2. Update the configuration file
3. Restart the system

Future versions may support hot-reloading.

### Multiple Video Sources

For multi-intersection networks, each intersection can have a different video source:
- Mix local files and live streams
- Use different camera types
- Support heterogeneous deployments

### Custom Vehicle Weights

Adjust vehicle weights based on your priorities:
- **Transit priority**: Increase bus weight (e.g., 3.0)
- **Freight priority**: Increase truck weight (e.g., 2.5)
- **Bicycle-friendly**: Increase bicycle weight (e.g., 1.5)

### Performance Tuning

For high-resolution video or multiple intersections:
```yaml
detection:
  confidence_threshold: 0.6  # Higher threshold = faster processing
  tracking_enabled: false    # Disable if not needed

dashboard:
  video_stream_fps: 10       # Lower FPS = less bandwidth
  video_stream_quality: 60   # Lower quality = faster streaming
```

## Schema Reference

For programmatic access to configuration schemas, see:
- `src/config_loader.py` - Configuration classes and validation
- Type hints provide schema information
- Dataclasses define structure and defaults
