# SMART FLOW v2 Configuration Files

This directory contains example configuration files for SMART FLOW v2.

## Quick Start

Choose a configuration file based on your needs:

### Single Intersection

- **simple_intersection_example.yaml** - Minimal 4-way intersection (YAML)
- **single_intersection_config.json** - Basic intersection with turn lanes (JSON)
- **comprehensive_intersection_example.yaml** - Full-featured intersection (YAML)
- **comprehensive_intersection_example.json** - Full-featured intersection (JSON)

### Multi-Intersection Network

- **multi_intersection_network_example.yaml** - 3-intersection corridor (YAML)
- **multi_intersection_config.json** - 2-intersection network (JSON)
- **network_example.json** - Simple network example

### Dashboard

- **dashboard_config.json** - Web dashboard settings

## File Formats

Both JSON and YAML formats are supported:
- **JSON** (`.json`) - Strict syntax, widely supported
- **YAML** (`.yaml`, `.yml`) - Human-friendly, easier to read/write

## Usage

### Python

```python
from src.config_loader import load_config

# Load any configuration file
config = load_config('config/single_intersection_config.json')

# Auto-detect configuration type
config = load_config('config/multi_intersection_config.json')

# Explicitly specify type
config = load_config('config/dashboard_config.json', config_type='dashboard')
```

### Command Line

```bash
# Run with a configuration file
python main.py --config config/single_intersection_config.json

# Run with network configuration
python main.py --config config/multi_intersection_config.json
```

## Configuration Types

### 1. Single Intersection Configuration

Defines a single intersection with:
- Video source (file, stream, webcam)
- Lane definitions and regions
- Optional turn lanes
- Optional crosswalks
- Signal timing parameters
- Detection settings
- Vehicle priority weights

**Example**: `single_intersection_config.json`

### 2. Multi-Intersection Network Configuration

Defines a coordinated network with:
- Multiple intersections
- Connections between intersections
- Traffic corridors
- Network-wide coordination settings

**Example**: `multi_intersection_config.json`

### 3. Dashboard Configuration

Defines web dashboard settings:
- Server port and host
- WebSocket update intervals
- Video streaming parameters
- Visualization options
- Alert settings

**Example**: `dashboard_config.json`

## Example Files

### simple_intersection_example.yaml

Minimal configuration for a basic 4-way intersection. Good starting point for new setups.

**Features**:
- 4 through lanes (north, south, east, west)
- Basic signal timing
- Default detection settings

### comprehensive_intersection_example.yaml / .json

Full-featured intersection demonstrating all available options.

**Features**:
- 4 through lanes
- 5 turn lanes (left turns for all directions, right turn for north)
- 4 crosswalks (all sides)
- Custom signal timing
- Vehicle type weights
- Tracking enabled

### multi_intersection_network_example.yaml

Three-intersection corridor with coordinated signals.

**Features**:
- 3 intersections along Main Street
- Turn lanes at intersections 1 and 2
- Crosswalks at intersection 1
- Network coordination enabled
- Green wave corridors (northbound and southbound)
- Connection definitions with travel times

### single_intersection_config.json

Production-ready single intersection configuration.

**Features**:
- 4 through lanes
- 2 left turn lanes
- 2 crosswalks
- Optimized signal timing
- Vehicle weights configured

### multi_intersection_config.json

Production-ready two-intersection network.

**Features**:
- 2 intersections
- Network coordination
- Single corridor definition
- Connection with travel time

### dashboard_config.json

Web dashboard configuration with visualization options.

**Features**:
- Port 8080
- CORS enabled
- WebSocket updates every 0.5s
- Video streaming at 15 FPS
- Heatmap and trajectory visualization
- Alert notifications

## Creating Your Own Configuration

1. **Copy an example file** that matches your needs
2. **Update video source** to point to your video file or stream
3. **Define lane regions** using pixel coordinates from your video
4. **Add turn lanes** if needed for protected turn phases
5. **Add crosswalks** if pedestrian detection is required
6. **Adjust timing** parameters based on your traffic patterns
7. **Test and validate** by loading the configuration

## Region Coordinates

Regions are defined as `[x1, y1, x2, y2]` where:
- `(x1, y1)` is the top-left corner
- `(x2, y2)` is the bottom-right corner

Use a video player or image editor to identify pixel coordinates.

## Validation

All configurations are automatically validated when loaded:
- Required fields must be present
- References must point to existing entities
- Numeric values must be in valid ranges
- Regions must have exactly 4 coordinates

If validation fails, detailed error messages will indicate the issues.

## Documentation

For complete documentation, see:
- **docs/configuration_guide.md** - Comprehensive configuration guide
- **src/config_loader.py** - Configuration loader implementation
- **tests/test_config_loader.py** - Configuration tests and examples

## Support

If you encounter issues:
1. Check the validation error messages
2. Review the configuration guide
3. Compare with working examples
4. Verify file syntax (JSON/YAML validators)
5. Check file paths and references

## Tips

- Start with a simple configuration and add complexity gradually
- Use YAML for easier editing (comments, no commas)
- Use JSON for programmatic generation
- Test configurations with short video clips first
- Validate regions by visualizing the output
- Keep backup copies of working configurations
