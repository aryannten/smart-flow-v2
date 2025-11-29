# WebSocket Protocol Documentation

## Overview

The SMART FLOW v2 WebSocket protocol provides real-time bidirectional communication between the traffic management system and connected clients. This enables live updates, instant notifications, and interactive control.

## Connection

### Endpoint

```
ws://localhost:8080/ws
```

For secure connections (production):
```
wss://yourdomain.com/ws
```

### Connection Lifecycle

```javascript
const ws = new WebSocket('ws://localhost:8080/ws');

// Connection opened
ws.onopen = (event) => {
  console.log('Connected to SMART FLOW');
  // Send initial subscription
  ws.send(JSON.stringify({
    type: 'subscribe',
    channels: ['metrics', 'alerts', 'emergency']
  }));
};

// Message received
ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  handleMessage(message);
};

// Error occurred
ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};

// Connection closed
ws.onclose = (event) => {
  console.log('Disconnected:', event.code, event.reason);
  // Implement reconnection logic
  setTimeout(() => reconnect(), 5000);
};
```

## Message Format

All messages follow this structure:

```json
{
  "type": "message_type",
  "timestamp": 1234567890.123,
  "data": {
    // Message-specific data
  }
}
```

## Server-to-Client Messages

### 1. Connection Acknowledgment

Sent immediately after connection is established.

```json
{
  "type": "connection",
  "timestamp": 1234567890.123,
  "data": {
    "status": "connected",
    "client_id": "client_abc123",
    "server_version": "2.0.0",
    "available_channels": ["metrics", "alerts", "emergency", "signals", "status"]
  }
}
```

### 2. Metrics Update

Sent periodically (default: every 0.5 seconds) with current traffic metrics.

```json
{
  "type": "metrics_update",
  "timestamp": 1234567890.123,
  "data": {
    "lanes": {
      "north": {
        "vehicle_count": 8,
        "density": 0.45,
        "signal_state": "green",
        "remaining_time": 15.2,
        "queue_length_meters": 25.5,
        "throughput_per_hour": 450,
        "average_wait_time": 18.5
      },
      "south": {
        "vehicle_count": 5,
        "density": 0.28,
        "signal_state": "red",
        "remaining_time": 8.3
      }
    },
    "pedestrians": {
      "north_crosswalk": {
        "count": 3,
        "walk_signal": "dont_walk"
      }
    },
    "emergency_active": false,
    "total_throughput": 1800
  }
}
```

### 3. Alert Notification

Sent when system events or conditions require attention.

```json
{
  "type": "alert",
  "timestamp": 1234567890.123,
  "data": {
    "id": "alert_1234567890",
    "level": "warning",
    "category": "congestion",
    "message": "High traffic detected on north lane",
    "lane": "north",
    "metric": "density",
    "value": 0.85,
    "threshold": 0.75,
    "action_required": false,
    "auto_dismiss": true,
    "dismiss_after_seconds": 30
  }
}
```

**Alert Levels:**
- `info`: Informational (blue)
- `warning`: Requires attention (yellow)
- `error`: Problem detected (orange)
- `critical`: Immediate action required (red)

**Alert Categories:**
- `congestion`: Traffic congestion
- `emergency`: Emergency vehicle
- `system`: System status
- `detection`: Detection issues
- `connection`: Connection problems
- `configuration`: Configuration changes

### 4. Emergency Event

Sent when emergency vehicles are detected or emergency priority changes.

```json
{
  "type": "emergency",
  "timestamp": 1234567890.123,
  "data": {
    "event": "activated",
    "event_id": "emerg_1234567890",
    "lane": "east",
    "vehicle_type": "ambulance",
    "priority_level": 1,
    "estimated_clearance_time": 15.0,
    "affected_lanes": ["north", "south", "west"]
  }
}
```

**Event Types:**
- `activated`: Emergency priority activated
- `cleared`: Emergency vehicle cleared intersection
- `updated`: Emergency status updated

**Vehicle Types:**
- `ambulance`
- `fire_truck`
- `police`
- `unknown`

### 5. Signal State Change

Sent when any signal state changes.

```json
{
  "type": "signal_change",
  "timestamp": 1234567890.123,
  "data": {
    "lane": "north",
    "old_state": "green",
    "new_state": "yellow",
    "duration": 3.0,
    "reason": "normal_cycle",
    "next_state": "red",
    "cycle_number": 42
  }
}
```

**Reasons:**
- `normal_cycle`: Regular signal cycle
- `emergency_override`: Emergency vehicle priority
- `manual_override`: Manual control
- `coordination`: Multi-intersection coordination
- `pedestrian_request`: Pedestrian crossing

### 6. System Status Update

Sent when system status changes.

```json
{
  "type": "status",
  "timestamp": 1234567890.123,
  "data": {
    "status": "running",
    "message": "System operating normally",
    "uptime_seconds": 3600.5,
    "frame_rate": 29.8,
    "connected_clients": 3,
    "video_source_status": "connected",
    "detection_status": "active"
  }
}
```

**Status Values:**
- `starting`: System initializing
- `running`: Normal operation
- `degraded`: Operating with reduced functionality
- `error`: Error state
- `stopping`: Shutting down

### 7. Pedestrian Activity

Sent when pedestrian activity changes significantly.

```json
{
  "type": "pedestrian",
  "timestamp": 1234567890.123,
  "data": {
    "crosswalk": "north_crosswalk",
    "pedestrian_count": 5,
    "walk_signal": "walk",
    "crossing_time_allocated": 15.0,
    "crossing_time_remaining": 12.5,
    "crossing_active": true
  }
}
```

### 8. Queue Update

Sent when queue conditions change significantly.

```json
{
  "type": "queue",
  "timestamp": 1234567890.123,
  "data": {
    "lane": "north",
    "queue_length_meters": 45.5,
    "vehicle_count": 15,
    "density": 0.33,
    "is_spillback": true,
    "spillback_severity": "moderate",
    "estimated_clearance_time": 25.0
  }
}
```

### 9. Network Coordination Update

Sent when multi-intersection coordination status changes.

```json
{
  "type": "coordination",
  "timestamp": 1234567890.123,
  "data": {
    "network_id": "downtown_corridor",
    "coordination_active": true,
    "coordination_quality": 0.85,
    "synchronized_intersections": ["intersection_1", "intersection_2", "intersection_3"],
    "average_travel_time": 45.2,
    "stops_per_vehicle": 1.2,
    "green_wave_active": true
  }
}
```

### 10. Command Acknowledgment

Sent in response to client commands.

```json
{
  "type": "command_ack",
  "timestamp": 1234567890.123,
  "data": {
    "command_id": "cmd_1234567890",
    "status": "accepted",
    "message": "Override command queued for lane north",
    "estimated_execution_time": 1234567891.5
  }
}
```

**Status Values:**
- `accepted`: Command accepted and queued
- `executing`: Command is being executed
- `completed`: Command completed successfully
- `failed`: Command failed
- `rejected`: Command rejected

## Client-to-Server Messages

### 1. Subscribe to Channels

Subscribe to specific message types.

```json
{
  "type": "subscribe",
  "channels": ["metrics", "alerts", "emergency", "signals"]
}
```

**Available Channels:**
- `metrics`: Traffic metrics updates
- `alerts`: Alert notifications
- `emergency`: Emergency events
- `signals`: Signal state changes
- `status`: System status updates
- `pedestrians`: Pedestrian activity
- `queues`: Queue updates
- `coordination`: Network coordination
- `all`: All channels

**Response:**
```json
{
  "type": "subscription_ack",
  "timestamp": 1234567890.123,
  "data": {
    "subscribed_channels": ["metrics", "alerts", "emergency", "signals"],
    "update_interval": 0.5
  }
}
```

### 2. Unsubscribe from Channels

Unsubscribe from specific message types.

```json
{
  "type": "unsubscribe",
  "channels": ["queues", "pedestrians"]
}
```

### 3. Override Signal

Request manual signal override.

```json
{
  "type": "command",
  "command": "override",
  "data": {
    "lane": "north",
    "state": "green",
    "duration": 30.0,
    "reason": "Manual test override"
  }
}
```

### 4. Adjust Parameter

Request parameter adjustment.

```json
{
  "type": "command",
  "command": "adjust",
  "data": {
    "parameter": "min_green",
    "value": 15.0,
    "scope": "global"
  }
}
```

### 5. Request Snapshot

Request immediate metrics snapshot.

```json
{
  "type": "request",
  "request": "snapshot",
  "data": {
    "include": ["metrics", "status", "queues"]
  }
}
```

**Response:**
```json
{
  "type": "snapshot",
  "timestamp": 1234567890.123,
  "data": {
    "metrics": { /* current metrics */ },
    "status": { /* current status */ },
    "queues": { /* current queue data */ }
  }
}
```

### 6. Ping

Keep-alive ping message.

```json
{
  "type": "ping"
}
```

**Response:**
```json
{
  "type": "pong",
  "timestamp": 1234567890.123
}
```

### 7. Set Update Interval

Change the frequency of metrics updates.

```json
{
  "type": "configure",
  "setting": "update_interval",
  "value": 1.0
}
```

**Response:**
```json
{
  "type": "configuration_ack",
  "timestamp": 1234567890.123,
  "data": {
    "setting": "update_interval",
    "old_value": 0.5,
    "new_value": 1.0
  }
}
```

## Error Messages

When errors occur, the server sends error messages:

```json
{
  "type": "error",
  "timestamp": 1234567890.123,
  "data": {
    "code": "INVALID_COMMAND",
    "message": "Unknown command type: 'invalid'",
    "details": {
      "received_type": "invalid",
      "valid_types": ["subscribe", "unsubscribe", "command", "request", "ping"]
    }
  }
}
```

**Error Codes:**
- `INVALID_MESSAGE`: Malformed message
- `INVALID_COMMAND`: Unknown command
- `UNAUTHORIZED`: Not authorized for action
- `SYSTEM_ERROR`: Internal system error
- `COMMAND_FAILED`: Command execution failed
- `INVALID_PARAMETER`: Invalid parameter value

## Connection Management

### Heartbeat

The server sends periodic heartbeat messages to detect disconnections:

```json
{
  "type": "heartbeat",
  "timestamp": 1234567890.123
}
```

Clients should respond with a pong or ping message within 30 seconds.

### Reconnection

If connection is lost, implement exponential backoff:

```javascript
let reconnectDelay = 1000; // Start with 1 second
const maxDelay = 30000; // Max 30 seconds

function reconnect() {
  setTimeout(() => {
    const ws = new WebSocket('ws://localhost:8080/ws');
    
    ws.onopen = () => {
      reconnectDelay = 1000; // Reset delay on successful connection
      console.log('Reconnected');
    };
    
    ws.onerror = () => {
      reconnectDelay = Math.min(reconnectDelay * 2, maxDelay);
      reconnect();
    };
  }, reconnectDelay);
}
```

### Graceful Disconnection

Client should send close frame before disconnecting:

```javascript
ws.close(1000, 'Client closing connection');
```

**Close Codes:**
- `1000`: Normal closure
- `1001`: Going away
- `1002`: Protocol error
- `1003`: Unsupported data
- `1011`: Server error

## Best Practices

### 1. Message Handling

```javascript
ws.onmessage = (event) => {
  try {
    const message = JSON.parse(event.data);
    
    // Validate message structure
    if (!message.type || !message.timestamp) {
      console.error('Invalid message format');
      return;
    }
    
    // Route to appropriate handler
    switch (message.type) {
      case 'metrics_update':
        handleMetrics(message.data);
        break;
      case 'alert':
        handleAlert(message.data);
        break;
      // ... other cases
      default:
        console.warn('Unknown message type:', message.type);
    }
  } catch (error) {
    console.error('Error parsing message:', error);
  }
};
```

### 2. Subscription Management

```javascript
// Subscribe to only needed channels
function subscribeToChannels(channels) {
  ws.send(JSON.stringify({
    type: 'subscribe',
    channels: channels
  }));
}

// Start with minimal subscription
subscribeToChannels(['metrics', 'alerts']);

// Add more channels as needed
subscribeToChannels(['emergency', 'signals']);
```

### 3. Command Tracking

```javascript
const pendingCommands = new Map();

function sendCommand(command, data) {
  const commandId = `cmd_${Date.now()}`;
  
  pendingCommands.set(commandId, {
    command,
    data,
    timestamp: Date.now()
  });
  
  ws.send(JSON.stringify({
    type: 'command',
    command_id: commandId,
    command,
    data
  }));
  
  return commandId;
}

// Handle acknowledgments
function handleCommandAck(ack) {
  const pending = pendingCommands.get(ack.command_id);
  if (pending) {
    console.log(`Command ${ack.command_id} ${ack.status}`);
    if (ack.status === 'completed' || ack.status === 'failed') {
      pendingCommands.delete(ack.command_id);
    }
  }
}
```

### 4. Error Handling

```javascript
ws.onerror = (error) => {
  console.error('WebSocket error:', error);
  
  // Log error details
  logError({
    type: 'websocket_error',
    error: error,
    timestamp: Date.now()
  });
  
  // Notify user
  showNotification('Connection error', 'error');
  
  // Attempt reconnection
  reconnect();
};
```

### 5. Performance Optimization

```javascript
// Throttle metrics updates
let lastMetricsUpdate = 0;
const metricsThrottle = 100; // ms

function handleMetrics(data) {
  const now = Date.now();
  if (now - lastMetricsUpdate < metricsThrottle) {
    return; // Skip this update
  }
  lastMetricsUpdate = now;
  
  // Process metrics
  updateDashboard(data);
}

// Batch commands
const commandQueue = [];
let commandTimer = null;

function queueCommand(command, data) {
  commandQueue.push({ command, data });
  
  if (!commandTimer) {
    commandTimer = setTimeout(() => {
      sendBatchCommands(commandQueue);
      commandQueue.length = 0;
      commandTimer = null;
    }, 100);
  }
}
```

## Security Considerations

### 1. Authentication

For production, implement token-based authentication:

```javascript
const token = getAuthToken();
const ws = new WebSocket(`ws://localhost:8080/ws?token=${token}`);
```

### 2. Message Validation

Always validate incoming messages:

```javascript
function validateMessage(message) {
  if (typeof message !== 'object') return false;
  if (!message.type || typeof message.type !== 'string') return false;
  if (!message.timestamp || typeof message.timestamp !== 'number') return false;
  if (!message.data || typeof message.data !== 'object') return false;
  return true;
}
```

### 3. Rate Limiting

Implement client-side rate limiting:

```javascript
const rateLimiter = {
  commands: [],
  maxPerMinute: 60,
  
  canSend() {
    const now = Date.now();
    this.commands = this.commands.filter(t => now - t < 60000);
    return this.commands.length < this.maxPerMinute;
  },
  
  recordSend() {
    this.commands.push(Date.now());
  }
};

function sendCommand(command, data) {
  if (!rateLimiter.canSend()) {
    console.warn('Rate limit exceeded');
    return;
  }
  
  rateLimiter.recordSend();
  ws.send(JSON.stringify({ type: 'command', command, data }));
}
```

## Testing

### Unit Test Example

```python
import pytest
import json
from fastapi.testclient import TestClient
from src.web_dashboard import app

def test_websocket_connection():
    client = TestClient(app)
    
    with client.websocket_connect("/ws") as websocket:
        # Receive connection acknowledgment
        data = websocket.receive_json()
        assert data["type"] == "connection"
        assert "client_id" in data["data"]
        
        # Subscribe to channels
        websocket.send_json({
            "type": "subscribe",
            "channels": ["metrics"]
        })
        
        # Receive subscription acknowledgment
        data = websocket.receive_json()
        assert data["type"] == "subscription_ack"
```

## Troubleshooting

### Connection Fails

- Check WebSocket URL and port
- Verify firewall settings
- Check browser console for errors
- Ensure server is running

### Messages Not Received

- Verify subscription to correct channels
- Check network connectivity
- Inspect browser developer tools
- Enable debug logging

### High Latency

- Reduce update interval
- Unsubscribe from unused channels
- Check network bandwidth
- Optimize message handling

## Support

For WebSocket protocol issues:
- Review this documentation
- Check `docs/api_documentation.md`
- See `examples/web_dashboard_demo.py`
- Open an issue on GitHub

---

## License

MIT License - See LICENSE file for details
