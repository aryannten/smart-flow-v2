# SMART FLOW v2 API Documentation

## Overview

The SMART FLOW v2 API provides programmatic access to the traffic management system through REST endpoints and WebSocket connections. This documentation covers all available endpoints, data formats, and integration patterns.

## Base URL

```
http://localhost:8080
```

Default port is 8080, configurable via `--port` flag or dashboard configuration.

## Authentication

Currently, the API does not require authentication. For production deployments, implement authentication middleware.

## API Endpoints

### System Status

#### GET /api/status

Get current system status and health information.

**Request:**
```http
GET /api/status HTTP/1.1
Host: localhost:8080
```

**Response:**
```json
{
  "status": "running",
  "uptime_seconds": 3600.5,
  "connected_clients": 3,
  "pending_commands": 0,
  "video_source": "rtsp://camera.ip/stream",
  "is_live": true,
  "frame_rate": 29.8,
  "last_update": 1234567890.123
}
```

**Status Codes:**
- `200 OK` - System is running normally
- `503 Service Unavailable` - System is not ready

---

### Traffic Metrics

#### GET /api/metrics

Get current real-time traffic metrics for all lanes.

**Request:**
```http
GET /api/metrics HTTP/1.1
Host: localhost:8080
```

**Response:**
```json
{
  "timestamp": 1234567890.123,
  "lanes": {
    "north": {
      "vehicle_count": 8,
      "density": 0.45,
      "signal_state": "green",
      "remaining_time": 15.2,
      "queue_length_meters": 25.5,
      "throughput_per_hour": 450,
      "average_wait_time": 18.5,
      "vehicle_types": {
        "car": 6,
        "truck": 1,
        "bus": 1
      }
    },
    "south": {
      "vehicle_count": 5,
      "density": 0.28,
      "signal_state": "red",
      "remaining_time": 8.3,
      "queue_length_meters": 15.2,
      "throughput_per_hour": 380,
      "average_wait_time": 22.1,
      "vehicle_types": {
        "car": 4,
        "truck": 1
      }
    }
  },
  "pedestrians": {
    "north_crosswalk": {
      "count": 3,
      "walk_signal": "dont_walk",
      "crossing_needed": true
    }
  },
  "emergency_active": false,
  "network_metrics": {
    "total_throughput": 1800,
    "average_travel_time": 45.2,
    "stops_per_vehicle": 1.2,
    "coordination_quality": 0.85
  },
  "environmental": {
    "total_idle_time": 1234.5,
    "estimated_co2_kg": 105.2
  }
}
```

**Status Codes:**
- `200 OK` - Metrics retrieved successfully
- `503 Service Unavailable` - System not ready

---

#### GET /api/metrics/history

Get historical metrics data for time-series analysis.

**Query Parameters:**
- `metric` (required): Metric name (e.g., "throughput", "wait_time", "density")
- `lane` (optional): Specific lane (e.g., "north", "south")
- `start_time` (optional): Start timestamp (Unix time)
- `end_time` (optional): End timestamp (Unix time)
- `interval` (optional): Data aggregation interval in seconds (default: 60)

**Request:**
```http
GET /api/metrics/history?metric=throughput&lane=north&start_time=1234567800&end_time=1234567900&interval=60 HTTP/1.1
Host: localhost:8080
```

**Response:**
```json
{
  "metric": "throughput",
  "lane": "north",
  "interval_seconds": 60,
  "data": [
    {
      "timestamp": 1234567800,
      "value": 450
    },
    {
      "timestamp": 1234567860,
      "value": 480
    }
  ],
  "statistics": {
    "min": 420,
    "max": 520,
    "average": 465,
    "std_dev": 28.5
  }
}
```

**Status Codes:**
- `200 OK` - Historical data retrieved
- `400 Bad Request` - Invalid parameters
- `404 Not Found` - Metric not found

---

### Intersection Management

#### GET /api/intersections

Get list of all intersections in the network.

**Request:**
```http
GET /api/intersections HTTP/1.1
Host: localhost:8080
```

**Response:**
```json
{
  "intersections": [
    {
      "id": "intersection_1",
      "name": "Main & 1st",
      "location": "Center",
      "lanes": ["north", "south", "east", "west"],
      "status": "active",
      "coordination_enabled": true
    },
    {
      "id": "intersection_2",
      "name": "Main & 2nd",
      "location": "North",
      "lanes": ["north", "south", "east", "west"],
      "status": "active",
      "coordination_enabled": true
    }
  ],
  "network": {
    "coordination_active": true,
    "target_speed_mph": 35,
    "coordination_quality": 0.85
  }
}
```

**Status Codes:**
- `200 OK` - Intersections retrieved
- `404 Not Found` - No intersections configured

---

#### GET /api/intersections/{intersection_id}

Get detailed information about a specific intersection.

**Request:**
```http
GET /api/intersections/intersection_1 HTTP/1.1
Host: localhost:8080
```

**Response:**
```json
{
  "id": "intersection_1",
  "name": "Main & 1st",
  "location": "Center",
  "video_source": "rtsp://camera1.ip/stream",
  "lanes": {
    "north": {
      "vehicle_count": 8,
      "signal_state": "green",
      "remaining_time": 15.2
    }
  },
  "turn_lanes": {
    "north_left": {
      "vehicle_count": 3,
      "protected_phase_active": false
    }
  },
  "crosswalks": {
    "north_crosswalk": {
      "pedestrian_count": 2,
      "walk_signal": "dont_walk"
    }
  },
  "coordination": {
    "offset_seconds": 0.0,
    "connected_to": ["intersection_2"],
    "sync_quality": 0.92
  }
}
```

**Status Codes:**
- `200 OK` - Intersection details retrieved
- `404 Not Found` - Intersection not found

---

### Signal Control

#### POST /api/override

Manually override a signal state.

**Request:**
```http
POST /api/override HTTP/1.1
Host: localhost:8080
Content-Type: application/json

{
  "lane": "north",
  "state": "green",
  "duration": 30.0,
  "reason": "Manual override for testing"
}
```

**Request Body:**
- `lane` (required): Lane identifier (e.g., "north", "south")
- `state` (required): Signal state ("green", "yellow", "red")
- `duration` (required): Duration in seconds
- `reason` (optional): Reason for override

**Response:**
```json
{
  "success": true,
  "message": "Override command queued for lane north",
  "command_id": "cmd_1234567890",
  "estimated_execution_time": 1234567891.5
}
```

**Status Codes:**
- `200 OK` - Override command accepted
- `400 Bad Request` - Invalid parameters
- `403 Forbidden` - Override not allowed (e.g., emergency active)

---

#### POST /api/adjust

Adjust system parameters dynamically.

**Request:**
```http
POST /api/adjust HTTP/1.1
Host: localhost:8080
Content-Type: application/json

{
  "parameter": "min_green",
  "value": 15.0,
  "scope": "global"
}
```

**Request Body:**
- `parameter` (required): Parameter name
- `value` (required): New value
- `scope` (optional): "global" or specific lane/intersection

**Adjustable Parameters:**
- `min_green`: Minimum green time (seconds)
- `max_green`: Maximum green time (seconds)
- `yellow_duration`: Yellow phase duration (seconds)
- `confidence_threshold`: Detection confidence (0.0-1.0)
- `cycle_interval`: Frames between updates

**Response:**
```json
{
  "success": true,
  "message": "Parameter adjustment queued for min_green",
  "command_id": "cmd_1234567891",
  "old_value": 10.0,
  "new_value": 15.0
}
```

**Status Codes:**
- `200 OK` - Adjustment accepted
- `400 Bad Request` - Invalid parameter or value
- `403 Forbidden` - Parameter adjustment not allowed

---

#### POST /api/emergency

Manually trigger or clear emergency priority.

**Request:**
```http
POST /api/emergency HTTP/1.1
Host: localhost:8080
Content-Type: application/json

{
  "action": "activate",
  "lane": "east",
  "vehicle_type": "ambulance"
}
```

**Request Body:**
- `action` (required): "activate" or "clear"
- `lane` (required for activate): Lane with emergency vehicle
- `vehicle_type` (optional): "ambulance", "fire_truck", "police"

**Response:**
```json
{
  "success": true,
  "message": "Emergency priority activated for lane east",
  "event_id": "emerg_1234567890"
}
```

**Status Codes:**
- `200 OK` - Emergency command processed
- `400 Bad Request` - Invalid parameters

---

### Video Streaming

#### GET /stream

Video stream endpoint using multipart/x-mixed-replace format.

**Request:**
```http
GET /stream HTTP/1.1
Host: localhost:8080
```

**Response:**
```http
HTTP/1.1 200 OK
Content-Type: multipart/x-mixed-replace; boundary=frame

--frame
Content-Type: image/jpeg

[JPEG image data]
--frame
Content-Type: image/jpeg

[JPEG image data]
--frame
...
```

**Usage in HTML:**
```html
<img src="http://localhost:8080/stream" alt="Live Traffic Feed">
```

**Status Codes:**
- `200 OK` - Stream active
- `503 Service Unavailable` - No video source available

---

### Configuration

#### GET /api/config

Get current system configuration.

**Request:**
```http
GET /api/config HTTP/1.1
Host: localhost:8080
```

**Response:**
```json
{
  "video_source": "rtsp://camera.ip/stream",
  "model": "yolov8n.pt",
  "confidence_threshold": 0.5,
  "signal_timing": {
    "min_green": 10,
    "max_green": 60,
    "yellow_duration": 3,
    "all_red_duration": 2
  },
  "features": {
    "pedestrians_enabled": true,
    "emergency_enabled": true,
    "turn_lanes_enabled": true,
    "queue_estimation_enabled": true,
    "tracking_enabled": true
  },
  "dashboard": {
    "port": 8080,
    "websocket_update_interval": 0.5
  }
}
```

**Status Codes:**
- `200 OK` - Configuration retrieved

---

#### PUT /api/config

Update system configuration (requires restart for some parameters).

**Request:**
```http
PUT /api/config HTTP/1.1
Host: localhost:8080
Content-Type: application/json

{
  "confidence_threshold": 0.6,
  "signal_timing": {
    "min_green": 12
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "Configuration updated",
  "restart_required": false,
  "updated_parameters": ["confidence_threshold", "signal_timing.min_green"]
}
```

**Status Codes:**
- `200 OK` - Configuration updated
- `400 Bad Request` - Invalid configuration

---

## WebSocket API

### Connection

Connect to the WebSocket endpoint for real-time updates:

```javascript
const ws = new WebSocket('ws://localhost:8080/ws');

ws.onopen = () => {
  console.log('Connected to SMART FLOW');
};

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  handleMessage(message);
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};

ws.onclose = () => {
  console.log('Disconnected from SMART FLOW');
};
```

### Message Types

#### 1. Metrics Update

Sent periodically (default: every 0.5 seconds) with current metrics.

```json
{
  "type": "metrics_update",
  "timestamp": 1234567890.123,
  "data": {
    "lanes": {
      "north": {
        "vehicle_count": 8,
        "signal_state": "green",
        "remaining_time": 15.2
      }
    }
  }
}
```

#### 2. Alert

Sent when system events occur.

```json
{
  "type": "alert",
  "timestamp": 1234567890.123,
  "data": {
    "level": "warning",
    "message": "High traffic detected on north lane",
    "lane": "north",
    "metric": "density",
    "value": 0.85
  }
}
```

**Alert Levels:**
- `info`: Informational messages
- `warning`: Warnings requiring attention
- `error`: Errors indicating problems
- `critical`: Critical issues requiring immediate action

#### 3. Emergency Event

Sent when emergency vehicles are detected.

```json
{
  "type": "emergency",
  "timestamp": 1234567890.123,
  "data": {
    "event": "activated",
    "lane": "east",
    "vehicle_type": "ambulance",
    "event_id": "emerg_1234567890"
  }
}
```

#### 4. Signal State Change

Sent when signal states change.

```json
{
  "type": "signal_change",
  "timestamp": 1234567890.123,
  "data": {
    "lane": "north",
    "old_state": "green",
    "new_state": "yellow",
    "duration": 3.0
  }
}
```

#### 5. System Status

Sent when system status changes.

```json
{
  "type": "status",
  "timestamp": 1234567890.123,
  "data": {
    "status": "running",
    "message": "System operating normally"
  }
}
```

### Client Commands

Clients can send commands through WebSocket:

```json
{
  "command": "override",
  "data": {
    "lane": "north",
    "state": "green",
    "duration": 30.0
  }
}
```

**Available Commands:**
- `override`: Override signal state
- `adjust`: Adjust parameter
- `subscribe`: Subscribe to specific events
- `unsubscribe`: Unsubscribe from events

---

## Data Models

### Lane Metrics

```typescript
interface LaneMetrics {
  vehicle_count: number;
  density: number;  // 0.0 to 1.0
  signal_state: "green" | "yellow" | "red";
  remaining_time: number;  // seconds
  queue_length_meters: number;
  throughput_per_hour: number;
  average_wait_time: number;  // seconds
  vehicle_types: {
    car: number;
    truck: number;
    bus: number;
    motorcycle: number;
    bicycle: number;
  };
}
```

### Signal State

```typescript
type SignalState = "green" | "yellow" | "red";
```

### Command

```typescript
interface Command {
  command_type: "override" | "adjust" | "emergency" | "reset";
  target: string;  // lane, parameter, etc.
  value: any;
  timestamp: number;
  reason?: string;
}
```

### Alert

```typescript
interface Alert {
  level: "info" | "warning" | "error" | "critical";
  message: string;
  timestamp: number;
  lane?: string;
  metric?: string;
  value?: number;
}
```

---

## Error Responses

All error responses follow this format:

```json
{
  "error": true,
  "message": "Error description",
  "code": "ERROR_CODE",
  "details": {
    "field": "Additional error details"
  }
}
```

### Common Error Codes

- `INVALID_PARAMETER`: Invalid parameter value
- `LANE_NOT_FOUND`: Specified lane does not exist
- `SYSTEM_NOT_READY`: System is not ready to accept commands
- `EMERGENCY_ACTIVE`: Cannot perform action during emergency
- `INVALID_STATE`: Invalid signal state
- `COMMAND_FAILED`: Command execution failed

---

## Rate Limiting

Currently, no rate limiting is implemented. For production:

- Implement rate limiting middleware
- Recommended: 100 requests per minute per client
- WebSocket: 1 connection per client

---

## CORS Configuration

### Development

```python
allow_origins=["*"]
allow_credentials=True
allow_methods=["*"]
allow_headers=["*"]
```

### Production

```python
allow_origins=["https://yourdomain.com"]
allow_credentials=True
allow_methods=["GET", "POST", "PUT"]
allow_headers=["Content-Type", "Authorization"]
```

---

## Code Examples

### Python Client

```python
import requests
import json

BASE_URL = "http://localhost:8080"

# Get current metrics
response = requests.get(f"{BASE_URL}/api/metrics")
metrics = response.json()
print(f"North lane count: {metrics['lanes']['north']['vehicle_count']}")

# Override signal
override_data = {
    "lane": "north",
    "state": "green",
    "duration": 30.0,
    "reason": "Manual test"
}
response = requests.post(f"{BASE_URL}/api/override", json=override_data)
result = response.json()
print(f"Override result: {result['message']}")

# Adjust parameter
adjust_data = {
    "parameter": "min_green",
    "value": 15.0
}
response = requests.post(f"{BASE_URL}/api/adjust", json=adjust_data)
result = response.json()
print(f"Adjustment result: {result['message']}")
```

### JavaScript Client

```javascript
// Fetch metrics
async function getMetrics() {
  const response = await fetch('http://localhost:8080/api/metrics');
  const metrics = await response.json();
  console.log('Metrics:', metrics);
  return metrics;
}

// Override signal
async function overrideSignal(lane, state, duration) {
  const response = await fetch('http://localhost:8080/api/override', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      lane: lane,
      state: state,
      duration: duration
    })
  });
  const result = await response.json();
  console.log('Override result:', result);
  return result;
}

// WebSocket connection
const ws = new WebSocket('ws://localhost:8080/ws');

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  
  switch (message.type) {
    case 'metrics_update':
      updateDashboard(message.data);
      break;
    case 'alert':
      showAlert(message.data);
      break;
    case 'emergency':
      handleEmergency(message.data);
      break;
  }
};
```

### cURL Examples

```bash
# Get status
curl http://localhost:8080/api/status

# Get metrics
curl http://localhost:8080/api/metrics

# Override signal
curl -X POST http://localhost:8080/api/override \
  -H "Content-Type: application/json" \
  -d '{"lane":"north","state":"green","duration":30.0}'

# Adjust parameter
curl -X POST http://localhost:8080/api/adjust \
  -H "Content-Type: application/json" \
  -d '{"parameter":"min_green","value":15.0}'

# Get intersections
curl http://localhost:8080/api/intersections

# Get configuration
curl http://localhost:8080/api/config
```

---

## Testing

### Unit Tests

```python
import pytest
from src.web_dashboard import WebDashboard

def test_api_status():
    dashboard = WebDashboard(port=8081)
    dashboard.start()
    
    response = requests.get("http://localhost:8081/api/status")
    assert response.status_code == 200
    assert response.json()["status"] == "running"
    
    dashboard.stop()
```

### Integration Tests

See `tests/test_web_dashboard.py` for complete test suite.

---

## Security Considerations

### For Production Deployment

1. **Enable Authentication**: Implement JWT or OAuth2
2. **Use HTTPS**: Enable TLS/SSL encryption
3. **Restrict CORS**: Limit to specific domains
4. **Rate Limiting**: Prevent abuse
5. **Input Validation**: Validate all inputs
6. **Logging**: Log all API access
7. **Firewall**: Restrict access to trusted networks

### Example Authentication

```python
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer

security = HTTPBearer()

async def verify_token(credentials = Depends(security)):
    token = credentials.credentials
    if not validate_token(token):
        raise HTTPException(status_code=401, detail="Invalid token")
    return token

@app.get("/api/metrics", dependencies=[Depends(verify_token)])
async def get_metrics():
    # Protected endpoint
    pass
```

---

## Troubleshooting

### Connection Issues

**Problem**: Cannot connect to API  
**Solution**: 
- Verify dashboard is running
- Check port is not blocked by firewall
- Ensure correct URL and port

### WebSocket Disconnects

**Problem**: WebSocket connection drops frequently  
**Solution**:
- Check network stability
- Increase timeout settings
- Implement reconnection logic

### Slow Response Times

**Problem**: API responses are slow  
**Solution**:
- Reduce WebSocket update frequency
- Optimize metric calculations
- Use caching for frequently accessed data

---

## Changelog

### Version 2.0
- Initial API release
- REST endpoints for metrics and control
- WebSocket support for real-time updates
- Video streaming endpoint
- Multi-intersection support

---

## Support

For API issues or questions:
- Check this documentation
- Review `docs/web_dashboard_usage.md`
- Check `examples/web_dashboard_demo.py`
- Open an issue on GitHub

---

## License

MIT License - See LICENSE file for details
