# SMART FLOW v2 Setup Guide

Complete setup instructions for SMART FLOW v2 development and deployment.

## Prerequisites

### Required Software

- **Python 3.8 or higher**
- **pip** (Python package manager)
- **Git**
- **Node.js 16+ and npm** (for dashboard frontend, Task 18)

### Optional Software

- **CUDA** (for GPU acceleration with YOLO)
- **FFmpeg** (for advanced video codec support)
- **Docker** (for containerized deployment)

## Installation Steps

### 1. Clone Repository

```bash
git clone <repository-url>
cd smart-flow-v2
```

### 2. Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- OpenCV for video processing
- Ultralytics YOLOv8 for object detection
- FastAPI for web dashboard backend
- Hypothesis for property-based testing
- And all other required packages

### 4. Download YOLO Model

The YOLOv8 nano model will be downloaded automatically on first run. For other models:

```bash
# YOLOv8 small (more accurate, slower)
wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8s.pt

# YOLOv8 medium (balanced)
wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8m.pt

# YOLOv8 large (most accurate, slowest)
wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8l.pt
```

### 5. Verify Installation

```bash
# Run tests to verify installation
pytest

# Check Python dependencies
pip list
```

## Dashboard Setup (Task 18)

The dashboard frontend will be set up in Task 18. Placeholder files are already created.

### Backend (Already Configured)

The FastAPI backend is included in the Python dependencies and will be implemented in Task 17.

### Frontend (To be implemented in Task 18)

```bash
cd dashboard/frontend

# Initialize React app (Task 18)
npx create-react-app . --template typescript

# Install dependencies (Task 18)
npm install

# Start development server (Task 18)
npm start
```

## Configuration

### 1. Single Intersection Setup

Edit `config/single_intersection_config.json`:

```json
{
  "intersection": {
    "video_source": "data/your_video.mp4"
  },
  "lanes": {
    "north": {"region": [x1, y1, x2, y2], "direction": "north"},
    "south": {"region": [x1, y1, x2, y2], "direction": "south"},
    "east": {"region": [x1, y1, x2, y2], "direction": "east"},
    "west": {"region": [x1, y1, x2, y2], "direction": "west"}
  }
}
```

**Finding Lane Regions:**

1. Open your video in a video player
2. Note the pixel coordinates for each lane
3. Use format: [x1, y1, x2, y2] where (x1,y1) is top-left, (x2,y2) is bottom-right

### 2. Multi-Intersection Setup

Edit `config/multi_intersection_config.json` to add your intersections and connections.

### 3. Dashboard Configuration

Edit `config/dashboard_config.json` to customize dashboard settings.

## Video Sources

### Local Video Files

Place video files in the `data/` directory:

```bash
python main.py --source data/your_video.mp4
```

### YouTube Live Streams

```bash
python main.py --source "https://youtube.com/watch?v=VIDEO_ID"
```

**Note**: Requires `yt-dlp` which is included in requirements.txt

### RTSP Network Cameras

```bash
python main.py --source "rtsp://username:password@camera_ip:port/stream"
```

### Webcam

```bash
# Default webcam
python main.py --source "webcam:0"

# Second webcam
python main.py --source "webcam:1"
```

## Running the System

### Basic Usage

```bash
# Single intersection with video file
python main.py --source data/testvid.mp4

# With configuration file
python main.py --config config/single_intersection_config.json

# With web dashboard
python main.py --source data/testvid.mp4 --dashboard --port 8080
```

### Advanced Options

```bash
# Save annotated video
python main.py --source data/testvid.mp4 --save-video --output output/result.mp4

# Custom YOLO model
python main.py --source data/testvid.mp4 --model yolov8m.pt

# Adjust confidence threshold
python main.py --source data/testvid.mp4 --confidence 0.6

# Run without display (headless)
python main.py --source data/testvid.mp4 --no-display

# Enable debug logging
python main.py --source data/testvid.mp4 --log-level DEBUG
```

## Development Workflow

### 1. Running Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=src --cov-report=html

# Specific test file
pytest tests/test_stream_manager.py

# Property-based tests only
pytest -m property

# Unit tests only
pytest -m unit
```

### 2. Code Style

```bash
# Format code (if using black)
black src/ tests/

# Lint code (if using flake8)
flake8 src/ tests/
```

### 3. Adding New Features

1. Check task list: `.kiro/specs/smart-flow-v2/tasks.md`
2. Review design: `.kiro/specs/smart-flow-v2/design.md`
3. Implement feature
4. Write tests
5. Update documentation

## Troubleshooting

### Common Issues

#### 1. YOLO Model Not Found

```bash
# Download manually
wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt
```

#### 2. OpenCV Video Codec Issues

Install FFmpeg:

```bash
# Ubuntu/Debian
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
```

#### 3. CUDA/GPU Issues

```bash
# Check CUDA availability
python -c "import torch; print(torch.cuda.is_available())"

# Install CUDA-enabled PyTorch
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

#### 4. YouTube Stream Connection Issues

```bash
# Update yt-dlp
pip install --upgrade yt-dlp

# Test connection
yt-dlp --list-formats "https://youtube.com/watch?v=VIDEO_ID"
```

#### 5. Port Already in Use (Dashboard)

```bash
# Use different port
python main.py --dashboard --port 8081

# Or kill process using port 8080
# Windows:
netstat -ano | findstr :8080
taskkill /PID <PID> /F

# Linux/macOS:
lsof -ti:8080 | xargs kill -9
```

### Performance Optimization

#### 1. GPU Acceleration

Ensure CUDA is installed and PyTorch detects GPU:

```python
import torch
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"CUDA device: {torch.cuda.get_device_name(0)}")
```

#### 2. Video Processing

- Use lower resolution videos for faster processing
- Reduce detection confidence threshold
- Skip frames if real-time processing is not required

#### 3. Dashboard Performance

- Reduce WebSocket update interval in `config/dashboard_config.json`
- Lower video stream FPS
- Disable heavy visualizations (heatmaps, trajectories)

## Deployment

### Development Deployment

```bash
# Backend
python main.py --dashboard --port 8080

# Frontend (Task 18)
cd dashboard/frontend
npm start
```

### Production Deployment

```bash
# Backend with Uvicorn
uvicorn main:app --host 0.0.0.0 --port 8080 --workers 4

# Frontend (Task 18)
cd dashboard/frontend
npm run build
# Serve build/ with nginx or similar
```

### Docker Deployment (Future)

Docker support will be added in a future update.

## Environment Variables

Create a `.env` file for configuration:

```bash
# Video source
VIDEO_SOURCE=data/testvid.mp4

# YOLO model
YOLO_MODEL=yolov8n.pt

# Dashboard
DASHBOARD_PORT=8080
DASHBOARD_HOST=0.0.0.0

# Logging
LOG_LEVEL=INFO
```

## Getting Help

1. Check documentation: `README_V2.md`, `dashboard/README.md`
2. Review design: `.kiro/specs/smart-flow-v2/design.md`
3. Check task list: `.kiro/specs/smart-flow-v2/tasks.md`
4. Run tests to verify setup: `pytest`
5. Open an issue on GitHub

## Next Steps

1. ✅ Complete setup
2. 📹 Prepare video sources
3. ⚙️ Configure lanes and intersections
4. 🚀 Run the system
5. 📊 Monitor via dashboard
6. 📈 Analyze metrics

## Development Roadmap

See `.kiro/specs/smart-flow-v2/tasks.md` for the complete implementation plan.

Current status:
- ✅ Task 1: Project structure and dependencies
- 🔄 Task 2-23: Feature implementation in progress

---

For questions or issues, please refer to the documentation or open an issue.
