# SMART FLOW v2 - Quick Start Guide (Local)

## Prerequisites

Make sure you have all dependencies installed:

```bash
pip install -r requirements.txt
```

## Quick Start Options

### Option 1: Interactive Launcher (Recommended)

Run the interactive launcher for easy testing:

```bash
python run_local.py
```

This will show you a menu with different configurations to choose from.

### Option 2: Direct Commands

#### Basic Simulation
Simple vehicle detection and signal control:

```bash
python main.py --source data/testvid.mp4
```

#### Full Features
All v2 features enabled:

```bash
python main.py --source data/testvid.mp4 \
  --enable-pedestrians \
  --enable-emergency \
  --enable-turn-lanes \
  --enable-queue-estimation \
  --enable-tracking \
  --enable-heatmap \
  --enable-trajectories \
  --save-video output/annotated.mp4
```

#### With Web Dashboard
Real-time monitoring and control:

```bash
python main.py --source data/testvid.mp4 \
  --enable-pedestrians \
  --enable-emergency \
  --enable-tracking \
  --dashboard \
  --dashboard-port 8080
```

Then open your browser to: **http://localhost:8080**

#### Headless Mode
No display window (good for servers):

```bash
python main.py --source data/testvid.mp4 \
  --enable-pedestrians \
  --enable-emergency \
  --enable-tracking \
  --no-display \
  --save-video output/annotated.mp4
```

#### Live Webcam
Real-time processing from webcam:

```bash
python main.py --source webcam:0 \
  --live \
  --enable-pedestrians \
  --enable-tracking \
  --enable-heatmap
```

## Command-Line Options

### Input Source
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
- `--enable-tracking` - Object tracking across frames

### Visualization
- `--enable-heatmap` - Traffic density heatmap
- `--enable-trajectories` - Vehicle trajectory lines
- `--no-display` - Headless mode (no window)

### Output
- `--output PATH` - Metrics log file (default: logs/simulation_metrics.json)
- `--save-video PATH` - Save annotated video

### Dashboard
- `--dashboard` - Enable web dashboard
- `--dashboard-port PORT` - Dashboard port (default: 8080)

## Output Files

After running, you'll find:

- **logs/simulation_metrics.json** - Detailed metrics and statistics
- **logs/error_log.txt** - Error and warning logs
- **output/annotated.mp4** - Annotated video (if --save-video used)
- **htmlcov/** - Test coverage reports

## Keyboard Controls

When display window is open:
- **ESC** - Stop simulation
- **Close window** - Stop simulation

## Troubleshooting

### "Failed to connect to video source"
- Check that the video file exists: `data/testvid.mp4`
- For webcam: Make sure no other app is using it
- For RTSP: Check network connection and URL

### "Model file not found"
- Download YOLOv8 model: `yolov8n.pt` should be in the root directory
- Or specify path: `--model path/to/model.pt`

### Dashboard not accessible
- Check firewall settings
- Try different port: `--dashboard-port 8081`
- Check console for "Dashboard started on port X"

### Slow performance
- Reduce confidence threshold: `--confidence 0.6`
- Disable heavy features: Remove `--enable-heatmap` or `--enable-trajectories`
- Use smaller model or lower resolution video

### Out of memory
- Close other applications
- Disable tracking: Remove `--enable-tracking`
- Process shorter video clips

## Examples

### Test with sample video
```bash
python run_local.py
# Choose option 1 (Basic Simulation)
```

### Full demo with dashboard
```bash
python run_local.py
# Choose option 3 (With Web Dashboard)
# Open browser to http://localhost:8080
```

### Quick test
```bash
python main.py --source data/testvid.mp4 --enable-tracking
```

## Next Steps

1. **View Results**: Check `logs/simulation_metrics.json` for detailed statistics
2. **Customize**: Modify lane configurations in the code
3. **Integrate**: Use the web dashboard API for external integration
4. **Deploy**: See `docs/deployment_guide.md` for production deployment

## Support

- Documentation: See `docs/` directory
- Configuration: See `docs/configuration_guide.md`
- API Reference: See `docs/api_documentation.md`
- Dashboard: See `docs/web_dashboard_usage.md`

## Performance Tips

- **For best performance**: Use GPU-enabled YOLO model
- **For real-time**: Reduce `--cycle-interval` to 15-20 frames
- **For accuracy**: Increase `--confidence` to 0.6-0.7
- **For live streams**: Always use `--live` flag for reconnection support
