/**
 * Historical data page with time-series charts and trend analysis
 */

import React, { useState, useEffect } from 'react';
import { Box, Typography, Grid } from '@mui/material';
import TimeSeriesChart from '../components/TimeSeriesChart';
import TrendAnalysis from '../components/TrendAnalysis';
import ComparisonView from '../components/ComparisonView';

// Mock data for demonstration
const generateMockTimeSeriesData = () => {
  const data = [];
  const now = Date.now() / 1000;
  for (let i = 100; i >= 0; i--) {
    data.push({
      timestamp: now - i * 60,
      throughput: 300 + Math.random() * 200,
      waitTime: 20 + Math.random() * 30,
      vehicles: 50 + Math.random() * 50,
    });
  }
  return data;
};

const mockTrends = [
  {
    metric: 'Average Wait Time',
    current: 28.5,
    average: 25.3,
    min: 15.2,
    max: 42.1,
    trend: 'up' as const,
    changePercent: 12.6,
    unit: 's',
  },
  {
    metric: 'Throughput',
    current: 420,
    average: 385,
    min: 280,
    max: 520,
    trend: 'up' as const,
    changePercent: 9.1,
    unit: 'veh/hr',
  },
  {
    metric: 'Queue Length',
    current: 8.2,
    average: 10.5,
    min: 3.1,
    max: 18.7,
    trend: 'down' as const,
    changePercent: -21.9,
    unit: 'm',
  },
  {
    metric: 'Cycle Time',
    current: 90,
    average: 90,
    min: 60,
    max: 120,
    trend: 'flat' as const,
    changePercent: 0,
    unit: 's',
  },
  {
    metric: 'Efficiency',
    current: 0.78,
    average: 0.72,
    min: 0.55,
    max: 0.85,
    trend: 'up' as const,
    changePercent: 8.3,
    unit: '',
  },
  {
    metric: 'CO2 Emissions',
    current: 145,
    average: 168,
    min: 120,
    max: 220,
    trend: 'down' as const,
    changePercent: -13.7,
    unit: 'kg',
  },
];

const mockComparisonData = [
  { name: 'North', throughput: 420, waitTime: 28, vehicles: 85 },
  { name: 'South', throughput: 380, waitTime: 32, vehicles: 78 },
  { name: 'East', throughput: 450, waitTime: 25, vehicles: 92 },
  { name: 'West', throughput: 390, waitTime: 30, vehicles: 80 },
];

const Historical: React.FC = () => {
  const [timeSeriesData, setTimeSeriesData] = useState(generateMockTimeSeriesData());

  useEffect(() => {
    // Simulate real-time updates
    const interval = setInterval(() => {
      setTimeSeriesData(generateMockTimeSeriesData());
    }, 60000); // Update every minute

    return () => clearInterval(interval);
  }, []);

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Historical Data Analysis
      </Typography>

      <Grid container spacing={3}>
        {/* Trend Analysis */}
        <Grid item xs={12}>
          <TrendAnalysis trends={mockTrends} />
        </Grid>

        {/* Time Series Charts */}
        <Grid item xs={12} lg={6}>
          <TimeSeriesChart
            data={timeSeriesData}
            title="Throughput & Wait Time"
            metrics={[
              { key: 'throughput', label: 'Throughput (veh/hr)', color: '#2196f3' },
              { key: 'waitTime', label: 'Wait Time (s)', color: '#f50057' },
            ]}
            chartType="line"
          />
        </Grid>

        <Grid item xs={12} lg={6}>
          <TimeSeriesChart
            data={timeSeriesData}
            title="Vehicle Count"
            metrics={[
              { key: 'vehicles', label: 'Vehicles', color: '#4caf50' },
            ]}
            chartType="area"
          />
        </Grid>

        {/* Comparison Views */}
        <Grid item xs={12}>
          <ComparisonView
            data={mockComparisonData}
            metrics={[
              { key: 'throughput', label: 'Throughput (veh/hr)', color: '#2196f3' },
              { key: 'waitTime', label: 'Wait Time (s)', color: '#f50057' },
              { key: 'vehicles', label: 'Vehicles', color: '#4caf50' },
            ]}
            title="Lane Comparison"
          />
        </Grid>
      </Grid>
    </Box>
  );
};

export default Historical;
