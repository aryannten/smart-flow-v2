# Component Reference Guide

## Component Hierarchy

```
App
├── DashboardProvider (Context)
│   └── Router
│       └── Layout
│           ├── Dashboard (Page)
│           │   ├── MetricsCard (x4)
│           │   ├── MultiCameraGrid
│           │   │   └── VideoFeed (x1-4)
│           │   ├── SignalStateIndicator
│           │   ├── TrafficHeatmap
│           │   ├── ThroughputChart
│           │   ├── SignalOverrideControl
│           │   ├── ParameterAdjustment
│           │   └── AlertNotifications
│           └── Historical (Page)
│               ├── TrendAnalysis
│               ├── TimeSeriesChart (x2)
│               └── ComparisonView
```

## Component Catalog

### Layout Components

#### Layout
**File**: `src/components/Layout.tsx`

**Purpose**: Main application layout with navigation

**Props**: 
- `children: ReactNode` - Page content

**Features**:
- App bar with title and connection status
- Drawer menu for navigation
- Responsive design

**Usage**:
```tsx
<Layout>
  <YourPageComponent />
</Layout>
```

---

### Video Components

#### VideoFeed
**File**: `src/components/VideoFeed.tsx`

**Purpose**: Display live video stream with controls

**Props**:
- `streamUrl: string` - URL of video stream
- `title?: string` - Display title (default: "Live Feed")

**Features**:
- Play/pause control
- Playback speed adjustment (0.25x - 2.0x)
- Fullscreen mode
- 16:9 aspect ratio

**Usage**:
```tsx
<VideoFeed 
  streamUrl="http://localhost:8080/stream"
  title="Main Intersection"
/>
```

#### MultiCameraGrid
**File**: `src/components/MultiCameraGrid.tsx`

**Purpose**: Grid layout for multiple camera feeds

**Props**:
- `cameras: Camera[]` - Array of camera objects

**Camera Interface**:
```typescript
interface Camera {
  id: string;
  name: string;
  streamUrl: string;
}
```

**Features**:
- 1x1, 1x2, 2x2 layout options
- Responsive grid
- Layout toggle buttons

**Usage**:
```tsx
<MultiCameraGrid cameras={[
  { id: '1', name: 'North', streamUrl: 'http://...' },
  { id: '2', name: 'South', streamUrl: 'http://...' }
]} />
```

---

### Metrics Components

#### MetricsCard
**File**: `src/components/MetricsCard.tsx`

**Purpose**: Display a single metric with trend

**Props**:
- `title: string` - Metric name
- `value: string | number` - Current value
- `unit?: string` - Unit of measurement
- `trend?: 'up' | 'down' | 'flat'` - Trend direction
- `trendValue?: string` - Trend percentage
- `color?: 'primary' | 'secondary' | 'success' | 'error' | 'warning' | 'info'`
- `icon?: ReactNode` - Icon to display

**Usage**:
```tsx
<MetricsCard
  title="Total Vehicles"
  value={142}
  unit="vehicles"
  trend="up"
  trendValue="+12%"
  color="primary"
  icon={<DirectionsCar />}
/>
```

#### SignalStateIndicator
**File**: `src/components/SignalStateIndicator.tsx`

**Purpose**: Display current signal states for all lanes

**Props**:
- `lanes: LaneSignal[]` - Array of lane signal states

**LaneSignal Interface**:
```typescript
interface LaneSignal {
  lane: string;
  state: 'red' | 'yellow' | 'green';
  timeRemaining?: number;
}
```

**Features**:
- Color-coded signal lights
- Time remaining countdown
- Responsive layout

**Usage**:
```tsx
<SignalStateIndicator lanes={[
  { lane: 'North', state: 'green', timeRemaining: 25 },
  { lane: 'South', state: 'red', timeRemaining: 45 }
]} />
```

#### TrafficHeatmap
**File**: `src/components/TrafficHeatmap.tsx`

**Purpose**: Visual representation of traffic density

**Props**:
- `data: HeatmapCell[]` - Array of density data

**HeatmapCell Interface**:
```typescript
interface HeatmapCell {
  lane: string;
  density: number; // 0-1 normalized
  label: string;
}
```

**Features**:
- Color gradient (green → yellow → red)
- Density labels (Low/Medium/High)
- Legend
- Responsive grid

**Usage**:
```tsx
<TrafficHeatmap data={[
  { lane: 'North', density: 0.7, label: '42 vehicles' },
  { lane: 'South', density: 0.4, label: '24 vehicles' }
]} />
```

#### ThroughputChart
**File**: `src/components/ThroughputChart.tsx`

**Purpose**: Line chart for throughput and wait time

**Props**:
- `data: ChartDataPoint[]` - Array of data points
- `title?: string` - Chart title

**ChartDataPoint Interface**:
```typescript
interface ChartDataPoint {
  timestamp: number;
  throughput: number;
  waitTime: number;
}
```

**Features**:
- Dual Y-axis
- Responsive
- Formatted timestamps
- Custom tooltips

**Usage**:
```tsx
<ThroughputChart data={chartData} title="Performance" />
```

---

### Control Components

#### SignalOverrideControl
**File**: `src/components/SignalOverrideControl.tsx`

**Purpose**: Manual signal override interface

**Props**:
- `lanes: string[]` - Array of lane names

**Features**:
- Lane selection dropdown
- Signal state selection
- Duration input
- Confirmation snackbar
- Error handling

**Usage**:
```tsx
<SignalOverrideControl lanes={['North', 'South', 'East', 'West']} />
```

#### ParameterAdjustment
**File**: `src/components/ParameterAdjustment.tsx`

**Purpose**: Adjust system parameters

**Props**: None (uses predefined parameters)

**Features**:
- Slider controls
- Real-time value display
- Apply button per parameter
- Confirmation feedback

**Predefined Parameters**:
- Minimum Green Time (5-60s)
- Maximum Green Time (30-180s)
- Yellow Phase Duration (2-10s)
- Detection Confidence Threshold (0.3-0.9)

**Usage**:
```tsx
<ParameterAdjustment />
```

#### AlertNotifications
**File**: `src/components/AlertNotifications.tsx`

**Purpose**: Display system alerts

**Props**: None (uses DashboardContext)

**Features**:
- Color-coded by severity
- Scrollable list
- Timestamps
- Clear all button
- Auto-updates from WebSocket

**Usage**:
```tsx
<AlertNotifications />
```

---

### Historical Data Components

#### TimeSeriesChart
**File**: `src/components/TimeSeriesChart.tsx`

**Purpose**: Time-series visualization with filtering

**Props**:
- `data: TimeSeriesDataPoint[]` - Array of data points
- `title: string` - Chart title
- `metrics: MetricConfig[]` - Metrics to display
- `chartType?: 'line' | 'area'` - Chart type

**MetricConfig Interface**:
```typescript
interface MetricConfig {
  key: string;
  label: string;
  color: string;
}
```

**Features**:
- Time range selector (15m, 1h, 6h, 24h, all)
- Multiple metrics on same chart
- Line or area chart
- Responsive

**Usage**:
```tsx
<TimeSeriesChart
  data={historicalData}
  title="Traffic Trends"
  metrics={[
    { key: 'throughput', label: 'Throughput', color: '#2196f3' },
    { key: 'waitTime', label: 'Wait Time', color: '#f50057' }
  ]}
  chartType="line"
/>
```

#### TrendAnalysis
**File**: `src/components/TrendAnalysis.tsx`

**Purpose**: Statistical insights for metrics

**Props**:
- `trends: TrendData[]` - Array of trend data

**TrendData Interface**:
```typescript
interface TrendData {
  metric: string;
  current: number;
  average: number;
  min: number;
  max: number;
  trend: 'up' | 'down' | 'flat';
  changePercent: number;
  unit: string;
}
```

**Features**:
- Current, average, min, max values
- Trend indicators
- Percentage change
- Responsive grid

**Usage**:
```tsx
<TrendAnalysis trends={trendData} />
```

#### ComparisonView
**File**: `src/components/ComparisonView.tsx`

**Purpose**: Compare metrics across lanes

**Props**:
- `data: ComparisonDataPoint[]` - Array of comparison data
- `metrics: MetricConfig[]` - Available metrics
- `title?: string` - Chart title

**Features**:
- Metric selector dropdown
- Bar chart visualization
- Responsive

**Usage**:
```tsx
<ComparisonView
  data={comparisonData}
  metrics={[
    { key: 'throughput', label: 'Throughput', color: '#2196f3' }
  ]}
  title="Lane Comparison"
/>
```

---

### Context & Services

#### DashboardContext
**File**: `src/context/DashboardContext.tsx`

**Purpose**: Global state management

**Provides**:
- `metrics: Metrics | null` - Current metrics
- `alerts: Alert[]` - System alerts
- `status: SystemStatus | null` - System status
- `isConnected: boolean` - WebSocket connection status
- `addAlert: (alert: Alert) => void` - Add alert
- `clearAlerts: () => void` - Clear all alerts

**Usage**:
```tsx
const { metrics, isConnected } = useDashboard();
```

#### API Service
**File**: `src/services/api.ts`

**Purpose**: REST API communication

**Methods**:
- `getStatus()` - Get system status
- `getMetrics()` - Get current metrics
- `getHistory(metric)` - Get historical data
- `overrideSignal(lane, state, duration)` - Override signal
- `adjustParameter(parameter, value)` - Adjust parameter
- `getIntersections()` - Get intersections

**Usage**:
```tsx
import { apiService } from '../services/api';

const metrics = await apiService.getMetrics();
```

#### WebSocket Service
**File**: `src/services/websocket.ts`

**Purpose**: Real-time communication

**Methods**:
- `connect()` - Connect to WebSocket
- `disconnect()` - Disconnect
- `subscribe(handler)` - Subscribe to messages
- `send(data)` - Send message
- `isConnected()` - Check connection status

**Usage**:
```tsx
import { websocketService } from '../services/websocket';

websocketService.connect();
const unsubscribe = websocketService.subscribe((message) => {
  console.log(message);
});
```

---

## Page Components

### Dashboard
**File**: `src/pages/Dashboard.tsx`

**Purpose**: Main dashboard page

**Features**:
- Real-time metrics cards
- Video feed
- Signal states
- Traffic heatmap
- Throughput chart
- Control panels
- Alerts

### Historical
**File**: `src/pages/Historical.tsx`

**Purpose**: Historical data analysis page

**Features**:
- Trend analysis
- Time-series charts
- Comparison views
- Time range filtering

---

## Styling

All components use Material-UI's styling system:

```tsx
// Inline styles with sx prop
<Box sx={{ p: 2, backgroundColor: 'primary.main' }}>

// Theme access
const theme = useTheme();
```

## Best Practices

1. **Props**: Always define TypeScript interfaces for props
2. **State**: Use local state for UI, context for global state
3. **Effects**: Clean up subscriptions in useEffect
4. **Memoization**: Use React.memo for expensive components
5. **Error Handling**: Always handle API errors gracefully
6. **Accessibility**: Include ARIA labels and keyboard support

## Adding New Components

1. Create component file in `src/components/`
2. Define TypeScript interfaces for props
3. Implement component with Material-UI
4. Export from component file
5. Import and use in pages
6. Update this documentation

## Testing Components

```tsx
import { render, screen } from '@testing-library/react';
import MetricsCard from './MetricsCard';

test('renders metric value', () => {
  render(<MetricsCard title="Test" value={42} />);
  expect(screen.getByText('42')).toBeInTheDocument();
});
```

## Performance Tips

- Use `React.memo` for components that render frequently
- Avoid inline function definitions in render
- Use `useCallback` for event handlers
- Debounce rapid updates (e.g., slider changes)
- Lazy load heavy components with `React.lazy`

## Common Patterns

### Conditional Rendering
```tsx
{data.length === 0 ? (
  <EmptyState />
) : (
  <DataDisplay data={data} />
)}
```

### Loading States
```tsx
const [loading, setLoading] = useState(false);

{loading ? <CircularProgress /> : <Content />}
```

### Error Handling
```tsx
try {
  await apiService.doSomething();
  setSuccess(true);
} catch (error) {
  setError(error.message);
}
```

---

For more details, see IMPLEMENTATION.md
