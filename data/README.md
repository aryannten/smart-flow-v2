# Data Directory

This directory is for storing input video files and configuration files.

## Video Files

Place your traffic intersection video files here. Supported formats include:
- MP4 (recommended)
- AVI
- MOV
- Any format supported by OpenCV

### Getting Sample Videos

#### Option 1: Free Stock Video Sites
- **Pexels**: https://www.pexels.com/search/videos/traffic%20intersection/
- **Pixabay**: https://pixabay.com/videos/search/traffic/
- **Videvo**: https://www.videvo.net/free-stock-video-footage/traffic/

#### Option 2: Traffic Camera Datasets
- **UA-DETRAC**: http://detrac-db.rit.albany.edu/
  - Large-scale vehicle detection dataset
  - Multiple intersection views
  - High quality annotations

- **KITTI Dataset**: http://www.cvlibs.net/datasets/kitti/
  - Autonomous driving dataset
  - Includes traffic scenarios

#### Option 3: YouTube Traffic Cameras
Use `yt-dlp` to download traffic camera footage:

```bash
# Install yt-dlp
pip install yt-dlp

# Download a traffic video
yt-dlp -f "best[height<=720]" -o "data/traffic_video.mp4" "YOUTUBE_URL"
```

### Video Requirements

For best results, your video should have:
- **View angle**: Overhead or elevated view of intersection
- **Resolution**: 720p (1280x720) or higher
- **Frame rate**: 25-30 FPS
- **Duration**: Any length (system processes frame-by-frame)
- **Lighting**: Good visibility of vehicles
- **Coverage**: Shows all four lanes/directions clearly

### Example Video Characteristics

Good video examples:
- ✅ Clear overhead view of 4-way intersection
- ✅ Vehicles clearly visible and distinguishable
- ✅ Stable camera (not shaky)
- ✅ Good lighting conditions

Avoid:
- ❌ Ground-level or driver perspective
- ❌ Heavily occluded views
- ❌ Very low resolution (< 480p)
- ❌ Extreme weather conditions (heavy rain, fog)

## Configuration Files

### Lane Configuration

The `lane_config_example.json` file shows how to define custom lane regions. 

**Default behavior**: The system automatically divides the frame into four quadrants (North, South, East, West).

**Custom configuration**: Create a JSON file with lane regions:

```json
{
  "lanes": {
    "north": {
      "x": 0,
      "y": 0,
      "width": 640,
      "height": 360
    },
    "south": {
      "x": 640,
      "y": 360,
      "width": 640,
      "height": 360
    },
    "east": {
      "x": 640,
      "y": 0,
      "width": 640,
      "height": 360
    },
    "west": {
      "x": 0,
      "y": 360,
      "width": 640,
      "height": 360
    }
  }
}
```

**Coordinates**:
- `x`, `y`: Top-left corner of the region
- `width`, `height`: Dimensions of the region
- All values in pixels

**Usage**:
```python
from src.models import LaneConfiguration
config = LaneConfiguration.from_json('data/my_custom_lanes.json')
```

## Directory Structure

```
data/
├── README.md                    # This file
├── lane_config_example.json     # Example lane configuration
├── traffic_video.mp4            # Your video files (not in repo)
└── intersection.avi             # Your video files (not in repo)
```

## Notes

- Video files are not included in the repository (they're in .gitignore)
- You must provide your own video files
- The system creates the `data/` directory automatically if it doesn't exist
- Large video files (>100MB) should not be committed to version control
