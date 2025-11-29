/**
 * Throughput and wait time chart component
 */

import React from 'react';
import {
  Card,
  CardContent,
  Typography,
} from '@mui/material';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

interface ChartDataPoint {
  timestamp: number;
  throughput: number;
  waitTime: number;
}

interface ThroughputChartProps {
  data: ChartDataPoint[];
  title?: string;
}

const ThroughputChart: React.FC<ThroughputChartProps> = ({
  data,
  title = 'Throughput & Wait Time',
}) => {
  const formatTimestamp = (timestamp: number): string => {
    const date = new Date(timestamp * 1000);
    return date.toLocaleTimeString();
  };

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          {title}
        </Typography>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#444" />
            <XAxis
              dataKey="timestamp"
              tickFormatter={formatTimestamp}
              stroke="#888"
            />
            <YAxis yAxisId="left" stroke="#2196f3" />
            <YAxis yAxisId="right" orientation="right" stroke="#f50057" />
            <Tooltip
              labelFormatter={formatTimestamp}
              contentStyle={{
                backgroundColor: '#132f4c',
                border: '1px solid #2196f3',
              }}
            />
            <Legend />
            <Line
              yAxisId="left"
              type="monotone"
              dataKey="throughput"
              stroke="#2196f3"
              name="Throughput (veh/hr)"
              strokeWidth={2}
              dot={false}
            />
            <Line
              yAxisId="right"
              type="monotone"
              dataKey="waitTime"
              stroke="#f50057"
              name="Wait Time (s)"
              strokeWidth={2}
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
};

export default ThroughputChart;
