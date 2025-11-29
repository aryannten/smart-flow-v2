# SMART FLOW v2 Dashboard Frontend - Implementation Guide

## Overview

The SMART FLOW v2 Dashboard is a React-based web application built with TypeScript and Material-UI. It provides real-time monitoring and control capabilities for the traffic management system.

## Architecture

### Technology Stack

- **React 18.2**: UI framework
- **TypeScript 4.9**: Type-safe development
- **Material-UI 5.14**: Component library and design system
- **Recharts 2.8**: Data visualization
- **React Router 6.15**: Client-side routing
- **Axios 1.5**: HTTP client
- **WebSocket**: Real-time communication

### Project Structure

```
dashboard/frontend/
├── public/
│   └── index.html              # HTML template
├── src/
│   ├── components/             # Reusable UI components
│   │   ├── AlertNotifications.tsx
│   │   ├── ComparisonView.tsx
│   │   ├── Layout.tsx
│   │   ├── MetricsCard.tsx
│   │   ├── MultiCameraGrid.tsx
│   │   ├── ParameterAdjustment.tsx
│   │   ├── SignalOverrideControl.tsx
│   │   ├── SignalStateIndicator.tsx
│   │   ├── ThroughputChart.tsx
│   │   ├── TimeSeriesChart.tsx
│   │   ├── TrafficHeatmap.tsx
│   │   ├── TrendAnalysis.tsx
│   │   └── VideoFeed.tsx
│   ├── context/                # React context for state management
│   │   └── DashboardContext.tsx
│   ├── pages/                  # Page components
│   │   ├── Dashboard.tsx
│   │   └── Historical.tsx
│   ├── services/               # API and WebSocket services
│   │   ├── api.ts
│   │   └── websocket.ts
│   ├── types/                  # TypeScript type definitions
│   │   └── index.ts
│   ├── App.tsx                 # Main app component
│   ├── index.tsx               # Entry point
│   └── index.css               # Global styles
├── package.json
├── tsconfig.json
└── README.md
```

## Components

### Core Components

#### 1. Layout
- Main application layout with navigation
- Displays connection status
- Drawer menu for navigation

#### 2. VideoFeed
- Displays live video stream from backend
- Play/pause controls
- Playback speed adjustment
- Fullscreen support

#### 3. MultiCameraGrid
- Grid layout for multiple camera feeds
- Supports 1x1, 1x2, and 2x2 layouts
- Dynamic camera switching

### Metrics Components

#### 4. MetricsCard
- Reusable card for displaying key metrics
- Supports trend indicators (up/down/flat)
- Customizable colors and icons

#### 5. SignalStateIndicator
- Real-time signal state display
- Color-coded signal lights
- Time remaining countdown

#### 6. TrafficHeatmap
- Visual representation of traffic density
- Color gradient from green (low) to red (high)
- Lane-by-lane breakdown

#### 7. ThroughputChart
- Line chart for throughput and wait time
- Dual Y-axis for different metrics
- Real-time updates

### Control Components

#### 8. SignalOverrideControl
- Manual signal override interface
- Lane selection dropdown
- Signal state selection (red/yellow/green)
- Duration input
- Confirmation and error handling

#### 9. ParameterAdjustment
- Slider controls for system parameters
- Real-time parameter updates
- Predefined parameter ranges

#### 10. AlertNotifications
- Display system alerts and notifications
- Color-coded by severity (info/warning/error)
- Scrollable list with timestamps
- Clear all functionality

### Historical Data Components

#### 11. TimeSeriesChart
- Line or area charts for historical data
- Time range selector (15m, 1h, 6h, 24h, all)
- Multiple metrics on same chart
- Responsive design

#### 12. TrendAnalysis
- Statistical insights for metrics
- Current, average, min, max values
- Trend indicators with percentage change
- Grid layout for multiple metrics

#### 13. ComparisonView
- Bar chart for comparing metrics across lanes
- Metric selector dropdown
- Useful for identifying bottlenecks

## State Management

### DashboardContext

The application uses React Context for global state management:

- **metrics**: Current traffic metrics from backend
- **alerts**: List of system alerts
- **status**: System status information
- **isConnected**: WebSocket connection status

### WebSocket Integration

The WebSocket service provides real-time updates:

- Automatic connection on mount
- Reconnection logic with exponential backoff
- Message type routing (metrics_update, alert, status_update)
- Subscription-based message handling

## API Integration

### REST API Endpoints

- `GET /api/status`: System status
- `GET /api/metrics`: Current metrics
- `GET /api/history/{metric}`: Historical data
- `POST /api/override`: Manual signal override
- `POST /api/adjust`: Parameter adjustment
- `GET /api/intersections`: List of intersections

### WebSocket Protocol

- `ws://localhost:8080/ws`: WebSocket endpoint
- Message format: `{ type: string, data: any }`
- Automatic reconnection on disconnect

## Development

### Setup

1. Install dependencies:
```bash
cd dashboard/frontend
npm install
```

2. Configure environment:
```bash
cp .env.example .env
# Edit .env to set API_URL and WS_URL
```

3. Start development server:
```bash
npm start
```

The app will open at http://localhost:3000

### Building for Production

```bash
npm run build
```

This creates an optimized production build in the `build/` directory.

### Testing

```bash
npm test
```

## Configuration

### Environment Variables

- `REACT_APP_API_URL`: Backend API URL (default: http://localhost:8080)
- `REACT_APP_WS_URL`: WebSocket URL (default: localhost:8080)

### Theme Customization

The app uses Material-UI's theming system. Edit `App.tsx` to customize:

```typescript
const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: { main: '#2196f3' },
    secondary: { main: '#f50057' },
  },
});
```

## Features Implemented

### Task 18.1: React Application Setup ✓
- TypeScript configuration
- Material-UI integration
- React Router setup
- WebSocket client
- Context-based state management

### Task 18.2: Live Video Feed ✓
- Video streaming component
- Play/pause controls
- Speed adjustment
- Multi-camera grid view
- Fullscreen support

### Task 18.3: Metrics Dashboard ✓
- Real-time metrics cards
- Traffic heatmap visualization
- Signal state indicators
- Throughput and wait time charts

### Task 18.4: Control Panel ✓
- Manual signal override controls
- Parameter adjustment sliders
- Alert notification display

### Task 18.5: Historical Data ✓
- Time-series charts
- Trend analysis graphs
- Comparison views
- Time range filtering

## Integration with Backend

The frontend is designed to work seamlessly with the FastAPI backend:

1. **Video Streaming**: Uses the `/stream` endpoint for MJPEG streaming
2. **Metrics Updates**: Receives real-time updates via WebSocket
3. **Control Commands**: Sends commands via REST API
4. **Historical Data**: Fetches historical data from API endpoints

## Future Enhancements

- User authentication and authorization
- Customizable dashboard layouts
- Export functionality for reports
- Mobile-responsive improvements
- Offline mode with cached data
- Advanced filtering and search
- Multi-language support

## Troubleshooting

### WebSocket Connection Issues

If WebSocket fails to connect:
1. Check that backend is running on correct port
2. Verify REACT_APP_WS_URL in .env
3. Check browser console for errors
4. Ensure CORS is properly configured on backend

### Video Stream Not Loading

If video stream doesn't display:
1. Verify backend `/stream` endpoint is working
2. Check that video source is properly configured
3. Test stream URL directly in browser
4. Check network tab for errors

### Build Errors

If build fails:
1. Delete node_modules and package-lock.json
2. Run `npm install` again
3. Check for TypeScript errors
4. Ensure all dependencies are compatible

## Performance Considerations

- Video streaming uses MJPEG for simplicity (consider WebRTC for production)
- Charts are optimized with `dot={false}` for smooth rendering
- WebSocket messages are throttled to prevent overwhelming the UI
- Historical data is paginated and filtered by time range
- Components use React.memo where appropriate for optimization

## Accessibility

- Semantic HTML elements
- ARIA labels on interactive elements
- Keyboard navigation support
- Color contrast meets WCAG standards
- Screen reader friendly

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## License

Part of SMART FLOW v2 project.
