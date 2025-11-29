/**
 * Main dashboard page with live monitoring and controls
 */

import React from 'react';
import { Box, Typography, Grid } from '@mui/material';
import {
  DirectionsCar,
  Timer,
  Speed,
  ShowChart,
} from '@mui/icons-material';
import { useDashboard } from '../context/DashboardContext';
import MultiCameraGrid from '../components/MultiCameraGrid';
import MetricsCard from '../components/MetricsCard';
import SignalStateIndicator from '../components/SignalStateIndicator';
import TrafficHeatmap from '../components/TrafficHeatmap';
import ThroughputChart from '../components/ThroughputChart';
import SignalOverrideControl from '../components/SignalOverrideControl';
import ParameterAdjustment from '../components/ParameterAdjustment';
import AlertNotifications from '../components/AlertNotifications';

// Mock data for demonstration
const mockCameras = [
  {
    id: 'cam1',
    name: 'Main Intersection',
    streamUrl: 'http://localhost:8080/stream',
  },
];

const mockLanes = ['North', 'South', 'East', 'West'];

const mockSignalStates = [
  { lane: 'North', state: 'green' as const, timeRemaining: 25 },
  { lane: 'South', state: 'red' as const, timeRemaining: 45 },
  { lane: 'East', state: 'red' as const, timeRemaining: 45 },
  { lane: 'West', state: 'yellow' as const, timeRemaining: 3 },
];

const mockHeatmapData = [
  { lane: 'North', density: 0.7, label: '42 vehicles' },
  { lane: 'South', density: 0.4, label: '24 vehicles' },
  { lane: 'East', density: 0.9, label: '58 vehicles' },
  { lane: 'West', density: 0.3, label: '18 vehicles' },
];

const generateMockChartData = () => {
  const data = [];
  const now = Date.now() / 1000;
  for (let i = 30; i >= 0; i--) {
    data.push({
      timestamp: now - i * 2,
      throughput: 300 + Math.random() * 200,
      waitTime: 20 + Math.random() * 30,
    });
  }
  return data;
};

const Dashboard: React.FC = () => {
  const { metrics, isConnected } = useDashboard();

  // Use real metrics if available, otherwise use mock data
  const totalVehicles = metrics?.intersection?.total_vehicles || 142;
  const avgWaitTime = metrics?.intersection?.average_wait_time || 28.5;
  const throughput = metrics?.intersection?.throughput || 420;
  const efficiency = metrics?.intersection?.efficiency || 0.78;

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Live Dashboard
      </Typography>

      <Grid container spacing={3}>
        {/* Metrics Cards */}
        <Grid item xs={12} sm={6} md={3}>
          <MetricsCard
            title="Total Vehicles"
            value={totalVehicles}
            unit="vehicles"
            trend="up"
            trendValue="+12%"
            color="primary"
            icon={<DirectionsCar sx={{ fontSize: 40 }} />}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricsCard
            title="Avg Wait Time"
            value={avgWaitTime.toFixed(1)}
            unit="seconds"
            trend="down"
            trendValue="-8%"
            color="success"
            icon={<Timer sx={{ fontSize: 40 }} />}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricsCard
            title="Throughput"
            value={throughput}
            unit="veh/hr"
            trend="up"
            trendValue="+15%"
            color="info"
            icon={<Speed sx={{ fontSize: 40 }} />}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricsCard
            title="Efficiency"
            value={(efficiency * 100).toFixed(0)}
            unit="%"
            trend="flat"
            trendValue="0%"
            color="warning"
            icon={<ShowChart sx={{ fontSize: 40 }} />}
          />
        </Grid>

        {/* Video Feed */}
        <Grid item xs={12} lg={8}>
          <MultiCameraGrid cameras={mockCameras} />
        </Grid>

        {/* Signal States */}
        <Grid item xs={12} lg={4}>
          <SignalStateIndicator lanes={mockSignalStates} />
        </Grid>

        {/* Traffic Heatmap */}
        <Grid item xs={12} lg={6}>
          <TrafficHeatmap data={mockHeatmapData} />
        </Grid>

        {/* Throughput Chart */}
        <Grid item xs={12} lg={6}>
          <ThroughputChart data={generateMockChartData()} />
        </Grid>

        {/* Control Panels */}
        <Grid item xs={12} lg={6}>
          <SignalOverrideControl lanes={mockLanes} />
        </Grid>

        <Grid item xs={12} lg={6}>
          <ParameterAdjustment />
        </Grid>

        {/* Alerts */}
        <Grid item xs={12}>
          <AlertNotifications />
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;
