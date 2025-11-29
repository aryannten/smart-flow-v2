/**
 * Time-series chart component for historical data
 */

import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from '@mui/material';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

interface TimeSeriesDataPoint {
  timestamp: number;
  [key: string]: number;
}

interface TimeSeriesChartProps {
  data: TimeSeriesDataPoint[];
  title: string;
  metrics: Array<{
    key: string;
    label: string;
    color: string;
  }>;
  chartType?: 'line' | 'area';
}

const TimeSeriesChart: React.FC<TimeSeriesChartProps> = ({
  data,
  title,
  metrics,
  chartType = 'line',
}) => {
  const [timeRange, setTimeRange] = React.useState<string>('1h');

  const formatTimestamp = (timestamp: number): string => {
    const date = new Date(timestamp * 1000);
    return date.toLocaleTimeString();
  };

  const formatDate = (timestamp: number): string => {
    const date = new Date(timestamp * 1000);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
  };

  const filterDataByTimeRange = (data: TimeSeriesDataPoint[]): TimeSeriesDataPoint[] => {
    if (data.length === 0) return data;

    const now = Date.now() / 1000;
    let cutoff = now;

    switch (timeRange) {
      case '15m':
        cutoff = now - 15 * 60;
        break;
      case '1h':
        cutoff = now - 60 * 60;
        break;
      case '6h':
        cutoff = now - 6 * 60 * 60;
        break;
      case '24h':
        cutoff = now - 24 * 60 * 60;
        break;
      case 'all':
        return data;
    }

    return data.filter((point) => point.timestamp >= cutoff);
  };

  const filteredData = filterDataByTimeRange(data);

  const ChartComponent = chartType === 'area' ? AreaChart : LineChart;
  const DataComponent = chartType === 'area' ? Area : Line;

  return (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6">{title}</Typography>
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Time Range</InputLabel>
            <Select
              value={timeRange}
              label="Time Range"
              onChange={(e) => setTimeRange(e.target.value)}
            >
              <MenuItem value="15m">Last 15 min</MenuItem>
              <MenuItem value="1h">Last 1 hour</MenuItem>
              <MenuItem value="6h">Last 6 hours</MenuItem>
              <MenuItem value="24h">Last 24 hours</MenuItem>
              <MenuItem value="all">All time</MenuItem>
            </Select>
          </FormControl>
        </Box>

        {filteredData.length === 0 ? (
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <Typography variant="body2" color="text.secondary">
              No data available for the selected time range
            </Typography>
          </Box>
        ) : (
          <ResponsiveContainer width="100%" height={300}>
            <ChartComponent data={filteredData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#444" />
              <XAxis
                dataKey="timestamp"
                tickFormatter={formatTimestamp}
                stroke="#888"
              />
              <YAxis stroke="#888" />
              <Tooltip
                labelFormatter={formatDate}
                contentStyle={{
                  backgroundColor: '#132f4c',
                  border: '1px solid #2196f3',
                }}
              />
              <Legend />
              {metrics.map((metric) => (
                <DataComponent
                  key={metric.key}
                  type="monotone"
                  dataKey={metric.key}
                  stroke={metric.color}
                  fill={metric.color}
                  name={metric.label}
                  strokeWidth={2}
                  dot={false}
                />
              ))}
            </ChartComponent>
          </ResponsiveContainer>
        )}
      </CardContent>
    </Card>
  );
};

export default TimeSeriesChart;
