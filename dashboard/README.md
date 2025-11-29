# SMART FLOW v2 Web Dashboard

Real-time traffic monitoring and control interface for SMART FLOW v2.

## Overview

The web dashboard provides:
- Live video feeds with annotations
- Real-time traffic metrics and analytics
- Traffic density heatmaps
- Signal timing visualizations
- Manual override controls
- Historical data analysis
- Alert notifications

## Technology Stack

### Backend
- **FastAPI**: Modern async web framework
- **WebSockets**: Real-time bidirectional communication
- **Uvicorn**: ASGI server

### Frontend (To be implemented in Task 18)
- **React**: UI framework
- **TypeScript**: Type-safe JavaScript
- **Material-UI or Tailwind CSS**: UI components
- **Recharts or Chart.js**: Data visualization
- **WebSocket Client**: Real-time updates

## Setup Instructions

### Backend Setup

The backend is integrated with the main Python application. Dependencies are already included in `requirements.txt`.

To start the dashboard backend:
```bash
# The dashboard will start automatically when running main.py with --dashboard flag
python main.py --dashboard --port 8080
```

### Frontend Setup (Task 18)

The frontend will be set up in Task 18. It will include:

1. **Initialize React Project**
   ```bash
   cd dashboard/frontend
   npx create-react-app . --template typescript
   ```

2. **Install Dependencies**
   ```bash
   npm install @mui/material @emotion/react @emotion/styled
   npm install recharts
   npm install react-router-dom
   npm install axios
   ```

3. **Development Server**
   ```bash
   npm start
   ```

4. **Production Build**
   ```bash
   npm run build
   ```

## API Endpoints

### REST API

- `GET /api/status` - System status
- `GET /api/metrics` - Current metrics
- `GET /api/history/{metric}` - Historical data
- `POST /api/override` - Manual signal override
- `GET /api/intersections` - List of intersections
- `GET /api/config` - System configuration

### WebSocket

- `ws://localhost:8080/ws` - Real-time updates

WebSocket message format:
```json
{
  "type": "metrics_update",
  "timestamp": 1234567890.123,
  "data": {
    "vehicle_counts": {...},
    "signal_states": {...},
    "throughput": {...}
  }
}
```

### Video Stream

- `GET /stream` - Live video stream (MJPEG or HLS)

## Configuration

Dashboard configuration is in `config/dashboard_config.json`:

```json
{
  "dashboard": {
    "port": 8080,
    "host": "0.0.0.0",
    "websocket_update_interval": 0.5
  }
}
```

## Features

### Live Video Feed
- Real-time video with detection overlays
- Multi-camera grid view
- Zoom and pan controls

### Metrics Dashboard
- Vehicle counts by lane
- Throughput rates
- Average wait times
- Queue lengths
- Signal states

### Visualizations
- Traffic density heatmaps
- Vehicle trajectories
- Queue visualization
- Signal timing diagrams

### Controls
- Manual signal overrides
- Parameter adjustments
- Emergency mode activation

### Alerts
- Emergency vehicle detection
- Congestion warnings
- System errors

## Development

### Backend Development

The backend is implemented in `src/web_dashboard.py` and will be completed in Task 17.

### Frontend Development

The frontend will be implemented in Task 18 with:
- Component structure
- State management
- WebSocket integration
- Responsive design

## Deployment

### Development
```bash
# Backend
python main.py --dashboard

# Frontend (after Task 18)
cd dashboard/frontend
npm start
```

### Production
```bash
# Backend
uvicorn main:app --host 0.0.0.0 --port 8080

# Frontend (after Task 18)
cd dashboard/frontend
npm run build
# Serve build folder with nginx or similar
```

## Security Considerations

- CORS configuration for production
- Authentication/authorization (future enhancement)
- Rate limiting for API endpoints
- Secure WebSocket connections (WSS)

## Browser Support

- Chrome/Edge (recommended)
- Firefox
- Safari

## Notes

- The frontend implementation will be completed in Task 18
- Backend API will be implemented in Task 17
- This README will be updated as features are implemented
