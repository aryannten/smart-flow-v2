# SMART FLOW v2 Dashboard - Quick Start Guide

## Overview

The SMART FLOW v2 Dashboard provides real-time monitoring and control of the traffic management system through a web interface.

## Prerequisites

- Python 3.8+ (for backend)
- Node.js 16+ and npm (for frontend)
- Modern web browser (Chrome, Firefox, Safari, or Edge)

## Quick Start

### 1. Start the Backend

The backend FastAPI server must be running before starting the frontend.

```bash
# From project root
python examples/web_dashboard_demo.py
```

The backend will start on http://localhost:8080

### 2. Start the Frontend

In a new terminal:

```bash
# Navigate to frontend directory
cd dashboard/frontend

# Install dependencies (first time only)
npm install

# Start development server
npm start
```

The dashboard will open automatically at http://localhost:3000

## Features

### Live Dashboard (/)

- **Real-time Metrics**: Vehicle counts, wait times, throughput, efficiency
- **Video Feed**: Live annotated video stream from traffic cameras
- **Signal States**: Current signal states for all lanes with countdown timers
- **Traffic Heatmap**: Visual representation of traffic density by lane
- **Throughput Chart**: Real-time chart of throughput and wait times
- **Manual Controls**: Override signals and adjust system parameters
- **Alerts**: System notifications and warnings

### Historical Data (/historical)

- **Trend Analysis**: Statistical insights with current, average, min, max values
- **Time-Series Charts**: Historical data visualization with time range filtering
- **Comparison Views**: Compare metrics across different lanes
- **Export**: Download data for further analysis (coming soon)

## Configuration

### Backend Configuration

Edit the backend configuration to change:
- Port number (default: 8080)
- CORS settings
- Video stream settings

### Frontend Configuration

Create a `.env` file in `dashboard/frontend/`:

```env
REACT_APP_API_URL=http://localhost:8080
REACT_APP_WS_URL=localhost:8080
```

Adjust these values if your backend runs on a different host/port.

## Usage

### Monitoring Traffic

1. Open the dashboard at http://localhost:3000
2. View real-time metrics in the cards at the top
3. Watch the live video feed with annotations
4. Check signal states and timing in the signal panel
5. Monitor traffic density in the heatmap
6. Track throughput trends in the chart

### Manual Signal Override

1. Navigate to the "Manual Signal Override" panel
2. Select a lane from the dropdown
3. Choose the desired signal state (red/yellow/green)
4. Set the duration in seconds
5. Click "Apply Override"
6. The system will resume normal operation after the duration expires

### Adjusting Parameters

1. Navigate to the "Parameter Adjustment" panel
2. Use the sliders to adjust system parameters:
   - Minimum Green Time
   - Maximum Green Time
   - Yellow Phase Duration
   - Detection Confidence Threshold
3. Click "Apply" for each parameter you want to change
4. Changes take effect immediately

### Viewing Historical Data

1. Click the menu icon (☰) in the top-left
2. Select "Historical Data"
3. View trend analysis for key metrics
4. Explore time-series charts with different time ranges
5. Compare metrics across lanes using the comparison view

## Troubleshooting

### Dashboard Won't Connect

**Problem**: Dashboard shows "Disconnected" status

**Solutions**:
1. Ensure backend is running: `curl http://localhost:8080/api/status`
2. Check backend logs for errors
3. Verify REACT_APP_API_URL in .env matches backend URL
4. Check browser console for connection errors

### Video Stream Not Loading

**Problem**: Video feed shows black screen or "Paused"

**Solutions**:
1. Verify video source is configured in backend
2. Test stream directly: http://localhost:8080/stream
3. Check that video file/camera is accessible
4. Review backend logs for video processing errors

### Metrics Not Updating

**Problem**: Metrics show stale data

**Solutions**:
1. Check WebSocket connection status (top-right indicator)
2. Verify backend is processing video frames
3. Check browser console for WebSocket errors
4. Try refreshing the page

### Build Errors

**Problem**: `npm start` or `npm build` fails

**Solutions**:
1. Delete `node_modules/` and `package-lock.json`
2. Run `npm install` again
3. Check Node.js version: `node --version` (should be 16+)
4. Clear npm cache: `npm cache clean --force`

## Performance Tips

### For Better Video Streaming

- Use a local video file for testing (faster than live streams)
- Reduce video resolution if experiencing lag
- Use a wired network connection instead of WiFi
- Close other browser tabs to free up resources

### For Smoother Charts

- Limit time range to recent data (15m or 1h)
- Reduce chart update frequency if needed
- Use Chrome or Edge for best performance

## Development

### Running in Development Mode

```bash
cd dashboard/frontend
npm start
```

- Hot reload enabled
- Source maps for debugging
- React DevTools support

### Building for Production

```bash
cd dashboard/frontend
npm run build
```

- Optimized bundle
- Minified code
- Ready for deployment

### Serving Production Build

```bash
# Install serve globally
npm install -g serve

# Serve the build
serve -s build -p 3000
```

## Architecture

```
┌─────────────────┐
│   Web Browser   │
│  (React App)    │
└────────┬────────┘
         │
         │ HTTP/WebSocket
         │
┌────────▼────────┐
│  FastAPI Server │
│   (Backend)     │
└────────┬────────┘
         │
         │
┌────────▼────────┐
│ Traffic System  │
│  (Processing)   │
└─────────────────┘
```

## API Endpoints

### REST API

- `GET /api/status` - System status
- `GET /api/metrics` - Current metrics
- `GET /api/history/{metric}` - Historical data
- `POST /api/override` - Manual signal override
- `POST /api/adjust` - Parameter adjustment
- `GET /api/intersections` - List intersections
- `GET /stream` - Video stream (MJPEG)

### WebSocket

- `ws://localhost:8080/ws` - Real-time updates
  - `metrics_update` - New metrics available
  - `alert` - System alert/notification
  - `status_update` - Status change

## Next Steps

1. **Explore the Dashboard**: Familiarize yourself with all features
2. **Test Controls**: Try manual overrides and parameter adjustments
3. **Review Historical Data**: Analyze trends and patterns
4. **Customize**: Modify theme, layout, or add new features
5. **Deploy**: Build for production and deploy to a server

## Support

For issues or questions:
1. Check the IMPLEMENTATION.md for detailed documentation
2. Review backend logs for errors
3. Check browser console for frontend errors
4. Refer to the main README.md for system-wide information

## What's Next?

The dashboard is fully functional and ready for use. Future enhancements may include:

- User authentication
- Multi-intersection support
- Advanced analytics
- Mobile app
- Export/reporting features
- Real-time alerts via email/SMS

Enjoy monitoring your smart traffic system! 🚦
