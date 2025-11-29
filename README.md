# SMART FLOW v2 - AI-Powered Adaptive Traffic Signal Management System

[![Tests](https://img.shields.io/badge/tests-378%20passed-brightgreen)](tests/)
[![Coverage](https://img.shields.io/badge/coverage-76%25-green)](htmlcov/)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue)](requirements.txt)

An advanced AI-powered traffic signal management system with real-time vehicle detection, pedestrian management, emergency vehicle priority, and web-based monitoring.

## ✨ Features

### Core Features
- 🚗 **Multi-source Video Input** - Files, YouTube Live, RTSP streams, webcams
- 🤖 **AI Detection** - YOLOv8-powered vehicle and pedestrian detection
- 🚦 **Adaptive Signals** - Dynamic signal timing based on real-time traffic
- 📊 **Real-time Analytics** - Comprehensive traffic metrics and statistics

### Advanced Features (v2)
- 🚶 **Pedestrian Management** - Crosswalk detection and walk signal control
- 🚨 **Emergency Priority** - Automatic priority for emergency vehicles
- ↪️ **Turn Lane Control** - Protected turn phases and conflict detection
- 📏 **Queue Estimation** - Spatial queue length measurement
- 🎯 **Object Tracking** - Track vehicles across frames
- 🗺️ **Traffic Heatmap** - Visual density representation
- 🌐 **Web Dashboard** - Real-time monitoring and control interface
- 🔗 **Multi-Intersection** - Coordinate multiple intersections for green waves

## 🚀 Quick Start

### Prerequisites

```bash
# Python 3.8 or higher
python --version

# Install dependencies
pip install -r requirements.txt
```

### Run in 3 Easy Ways

#### 1. Double-Click (Windows - Easiest!)
- **Basic**: Double-click `run_basic.bat`
- **With Dashboard**: Double-click `run_with_dashboard.bat`

#### 2. Interactive Launcher
```bash
python run_local.py
```

#### 3. Command Line
```bash
# Basic simulation
python main.py --source data/testvid.mp4

# Full features
python main.py --source data/testvid.mp4 \
  --enable-pedestrians \
  --enable-emergency \
  --enable-tracking \
  --enable-heatmap

# With web dashboard
python main.py --source data/testvid.mp4 \
  --dashboard \
  --dashboard-port 8080
```

## 📖 Documentation

- **[Quick Start Guide](QUICKSTART_LOCAL.md)** - Get started in minutes
- **[Setup Guide](SETUP_V2.md)** - Detailed installation instructions
- **[Configuration Guide](docs/configuration_guide.md)** - Configure intersections
- **[API Documentation](docs/api_documentation.md)** - REST API reference
- **[Dashboard Guide](docs/web_dashboard_usage.md)** - Web dashboard usage
- **[Deployment Guide](docs/deployment_guide.md)** - Production deployment

## 🎮 Usage Examples

### Basic Simulation
```bash
python main.py --source data/testvid.mp4
```

### All Features Enabled
```bash
python main.py --source data/testvid.mp4 \
  --enable-pedestrians \
  --enable-emergency \
  --enable-turn-lanes \
  --enable-queue-estimation \
  --enable-tracking \
  --enable-heatmap \
  --enable-trajectories \
  --save-video output/result.mp4
```

### Live Webcam
```bash
python main.py --source webcam:0 \
  --live \
  --enable-tracking \
  --enable-heatmap
```

### RTSP Camera Stream
```bash
python main.py --source rtsp://camera.ip/stream \
  --live \
  --enable-pedestrians \
  --enable-emergency \
  --dashboard
```

### Headless Mode (No Display)
```bash
python main.py --source data/testvid.mp4 \
  --no-display \
  --save-video output/result.mp4
```

## 🎯 Command-Line Options

### Input
- `--source PATH` - Video file, YouTube URL, RTSP stream, or webcam:N
- `--live` - Treat as live stream (enables reconnection)

### Detection
- `--model PATH` - YOLO model file (default: yolov8n.pt)
- `--confidence FLOAT` - Detection threshold 0.0-1.0 (default: 0.5)

### Signal Control
- `--min-green SECONDS` - Minimum green time (default: 10)
- `--max-green SECONDS` - Maximum green time (default: 60)
- `--cycle-interval FRAMES` - Frames between cycles (default: 30)

### Features
- `--enable-pedestrians` - Pedestrian detection and crosswalks
- `--enable-emergency` - Emergency vehicle priority
- `--enable-turn-lanes` - Turn lane management
- `--enable-queue-estimation` - Queue length estimation
- `--enable-tracking` - Object tracking

### Visualization
- `--enable-heatmap` - Traffic density heatmap
- `--enable-trajectories` - Vehicle trajectory lines
- `--no-display` - Headless mode

### Output
- `--output PATH` - Metrics log file
- `--save-video PATH` - Save annotated video

### Dashboard
- `--dashboard` - Enable web dashboard
- `--dashboard-port PORT` - Dashboard port (default: 8080)

## 📊 Output Files

```
logs/
  ├── simulation_metrics.json    # Detailed metrics
  └── error_log.txt              # System logs

output/
  └── annotated.mp4              # Annotated video

htmlcov/
  └── index.html                 # Test coverage report
```

## 🏗️ Architecture

```
Video Sources → Stream Manager → Object Detector → Traffic Analyzer
                                                          ↓
                                                   Signal Controller
                                                          ↓
                                    Visualizer ← Multi-Intersection Coordinator
                                         ↓
                              Video Writer + Web Dashboard
```

### Components
- **Stream Manager** - Multi-source video input handling
- **Enhanced Detector** - YOLOv8-based detection with tracking
- **Traffic Analyzer** - Density, queue, and throughput analysis
- **Signal Controller** - Adaptive signal timing with multi-factor allocation
- **Pedestrian Manager** - Crosswalk and walk signal management
- **Emergency Handler** - Emergency vehicle priority system
- **Turn Controller** - Protected turn phase management
- **Queue Estimator** - Spatial queue length estimation
- **Visualizer** - Enhanced visualization with heatmaps
- **Web Dashboard** - Real-time monitoring interface
- **Metrics Logger** - Comprehensive analytics

## 🧪 Testing

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test file
pytest tests/test_signal_controller.py -v
```

**Test Results:**
- ✅ 378 tests passing
- ✅ 76% code coverage
- ✅ Property-based tests included

## 🔧 Configuration

### Lane Configuration
```python
# Create custom lane configuration
lane_config = LaneConfiguration(lanes={
    'north': Region(x=0, y=0, width=320, height=180, lane_name='north'),
    'south': Region(x=320, y=180, width=320, height=180, lane_name='south'),
    # ... more lanes
})
```

### Signal Configuration
```python
signal_config = SignalConfig(
    min_green=10,      # Minimum green time (seconds)
    max_green=60,      # Maximum green time (seconds)
    yellow_duration=3  # Yellow light duration (seconds)
)
```

See [Configuration Guide](docs/configuration_guide.md) for more details.

## 🌐 Web Dashboard

Start the dashboard:
```bash
python main.py --source data/testvid.mp4 --dashboard --dashboard-port 8080
```

Access at: **http://localhost:8080**

Features:
- 📹 Live video feed with annotations
- 📊 Real-time metrics and charts
- 🗺️ Traffic heatmap visualization
- 🎛️ Manual signal override controls
- 📈 Historical data and trends
- 🚨 Alert notifications

## 🐛 Troubleshooting

### Video file not found
```bash
# Make sure video exists
ls data/testvid.mp4

# Or use your own video
python main.py --source path/to/your/video.mp4
```

### Model file not found
```bash
# Download YOLOv8 model
# Place yolov8n.pt in root directory
```

### Webcam not working
```bash
# Try different device
python main.py --source webcam:1 --live
```

### Dashboard not accessible
```bash
# Try different port
python main.py --source data/testvid.mp4 --dashboard --dashboard-port 8081
```

### Slow performance
```bash
# Increase confidence threshold
python main.py --source data/testvid.mp4 --confidence 0.6

# Disable heavy features
python main.py --source data/testvid.mp4 --enable-tracking
# (without heatmap and trajectories)
```

## 📈 Performance

- **Frame Rate**: 20-30 FPS (depending on hardware)
- **Detection Accuracy**: 85-95% (YOLOv8)
- **Latency**: < 100ms per frame
- **Memory Usage**: ~2-4 GB
- **CPU Usage**: 60-90% (single core)

**Optimization Tips:**
- Use GPU-enabled YOLO model for better performance
- Reduce confidence threshold for faster processing
- Disable visualization features in production
- Use headless mode for server deployment

## 🤝 Contributing

Contributions are welcome! Please see the spec files in `.kiro/specs/smart-flow-v2/` for:
- Requirements specification
- Design document
- Implementation tasks

## 📝 License

This project is for educational and research purposes.

## 🙏 Acknowledgments

- YOLOv8 by Ultralytics
- OpenCV for computer vision
- FastAPI for web framework
- React for dashboard frontend

## 📞 Support

- Documentation: See `docs/` directory
- Issues: Check error logs in `logs/error_log.txt`
- Configuration: See `docs/configuration_guide.md`

---

**SMART FLOW v2** - Making traffic smarter, one intersection at a time 🚦
