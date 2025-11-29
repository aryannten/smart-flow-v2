# Web Dashboard Usage Guide

## Overview

The SMART FLOW v2 Web Dashboard provides real-time monitoring and control of the traffic signal system through a web-based interface. It includes REST API endpoints, WebSocket support for live updates, and video streaming capabilities.

## Features

- **Real-time Metrics**: Live vehicle counts, densities, and signal states
- **Video Streaming**: Live annotated video feed from the intersection
- **Manual Control**: Override signals and adjust parameters remotely
- **Alert System**: Real-time notifications for system events
- **WebSocket Updates**: Push-based updates for responsive UI

## Quick Start

### Starting the Dashboard

```python
from src.web_dashboard import WebDashboard

# Create dashboard instance
dashboard = WebDashboard(port=8080)

# Start the web server
dashboard.start()

# Dashboard is now running at http://localhost:8080
```

### Updating Data

```python
import numpy as np

# Update video feed
frame = np.zeros((480, 640, 3), dtype=np.uint8)
dashboard.update_video_feed(frame)

# Update metrics
metrics = {
    "lanes": {
        "north": {"count": 5, "density": 0.3, "signal": "green"},
        "south": {"count": 3, "density": 0.2, "signal": "red"}
    },
    "throughput": 120,
    "average_wait": 15.5
}
dashboard.update_metrics(metrics)

# Broadcast alert
dashboard.broadcast_alert("High traffic detected", "warning")
```

### Receiving Commands

```python
# Get user commands from dashboard
commands = dashboard.get_user_commands()

for command in commands:
    if command.command_type == CommandType.OVERRIDE_SIGNAL:
        # Handle signal override
        lane = command.target
        state = command.value["state"]
        duration = command.value["duration"]
        print(f"Override {lane} to {state} for {duration}s")
    
    elif command.command_type == CommandType.ADJUST_PARAMETER:
        # Handle parameter adjustment
        parameter = command.target
        value = command.value
        print(f"Adjust {parameter} to {value}")
```

## API Endpoints

### GET /api/status

Get system status.

**Response:**
```json
{
  "status": "running",
  "connected_clients": 2,
  "pending_commands": 0
}
```

### GET /api/metrics

Get current traffic metrics.

**Response:**
```json
{
  "lanes": {
    "north": {"count": 5, "density": 0.3, "signal": "green"},
    "south": {"count": 3, "density": 0.2, "signal": "red"}
  },
  "throughput": 120,
  "average_wait": 15.5
}
```

### POST /api/override

Override a signal manually.

**Request:**
```json
{
  "lane": "north",
  "state": "green",
  "duration": 30.0
}
```

**Response:**
```json
{
  "success": true,
  "message": "Override command queued for lane north"
}
```

### POST /api/adjust

Adjust a system parameter.

**Request:**
```json
{
  "parameter": "min_green",
  "value": 15.0
}
```

**Response:**
```json
{
  "success": true,
  "message": "Parameter adjustment queued for min_green"
}
```

### GET /api/history/{metric}

Get historical data for a metric (placeholder for future implementation).

**Response:**
```json
{
  "metric": "throughput",
  "data": [],
  "message": "Historical data integration pending"
}
```

### GET /api/intersections

Get list of intersections (placeholder for multi-intersection support).

**Response:**
```json
{
  "intersections": [],
  "message": "Multi-intersection integration pending"
}
```

### GET /stream

Video streaming endpoint using multipart/x-mixed-replace format.

Access via: `http://localhost:8080/stream`

### WebSocket /ws

WebSocket endpoint for real-time updates.

Connect via: `ws://localhost:8080/ws`

**Message Types:**

1. **Metrics Update**
```json
{
  "type": "metrics_update",
  "data": {
    "lanes": {...},
    "throughput": 120
  }
}
```

2. **Alert**
```json
{
  "type": "alert",
  "data": {
    "message": "High traffic detected",
    "level": "warning",
    "timestamp": 1234567890.123
  }
}
```

## Command Types

### OVERRIDE_SIGNAL

Override a lane's signal state.

```python
Command(
    command_type=CommandType.OVERRIDE_SIGNAL,
    target="north",
    value={"state": "green", "duration": 30.0},
    timestamp=time.time()
)
```

### ADJUST_PARAMETER

Adjust a system parameter.

```python
Command(
    command_type=CommandType.ADJUST_PARAMETER,
    target="min_green",
    value=15.0,
    timestamp=time.time()
)
```

### RESET_SYSTEM

Reset the system (reserved for future use).

### EMERGENCY_STOP

Emergency stop command (reserved for future use).

## Alert Levels

- **INFO**: Informational messages
- **WARNING**: Warning messages requiring attention
- **ERROR**: Error messages indicating problems

## Integration Example

```python
import time
import numpy as np
from src.web_dashboard import WebDashboard
from src.signal_controller import SignalController

# Initialize components
dashboard = WebDashboard(port=8080)
controller = SignalController(...)

# Start dashboard
dashboard.start()

# Main loop
while True:
    # Process video frame
    frame = get_next_frame()
    
    # Update dashboard
    dashboard.update_video_feed(frame)
    dashboard.update_metrics({
        "lanes": controller.get_lane_metrics(),
        "throughput": controller.get_throughput()
    })
    
    # Handle user commands
    commands = dashboard.get_user_commands()
    for command in commands:
        if command.command_type == CommandType.OVERRIDE_SIGNAL:
            controller.override_signal(
                command.target,
                command.value["state"],
                command.value["duration"]
            )
    
    time.sleep(0.033)  # 30 FPS
```

## CORS Configuration

The dashboard is configured with permissive CORS settings for development:

```python
allow_origins=["*"]
allow_credentials=True
allow_methods=["*"]
allow_headers=["*"]
```

**For production**, restrict origins to specific domains:

```python
allow_origins=["https://yourdomain.com"]
```

## Threading Model

The dashboard runs the FastAPI server in a separate daemon thread, allowing the main application to continue processing while the web server handles requests.

## Stopping the Dashboard

```python
dashboard.stop()
```

This will gracefully shut down the web server and clean up resources.

## Demo Script

Run the included demo to see the dashboard in action:

```bash
python examples/web_dashboard_demo.py
```

Then open your browser to:
- http://localhost:8080/api/status
- http://localhost:8080/api/metrics
- http://localhost:8080/stream

## Requirements

- FastAPI >= 0.104.1
- uvicorn >= 0.24.0
- websockets >= 12.0
- python-multipart >= 0.0.6
- opencv-python >= 4.8.0
- numpy >= 1.24.0

## Future Enhancements

- Historical data visualization
- Multi-intersection network view
- User authentication and authorization
- Persistent configuration storage
- Advanced analytics dashboard
- Mobile-responsive frontend
