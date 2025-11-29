/**
 * Comparison view component for comparing metrics across lanes or time periods
 */

import React, { useState } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  SelectChangeEvent,
} from '@mui/material';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

interface ComparisonDataPoint {
  name: string;
  [key: string]: string | number;
}

interface ComparisonViewProps {
  data: ComparisonDataPoint[];
  metrics: Array<{
    key: string;
    label: string;
    color: string;
  }>;
  title?: string;
}

const ComparisonView: React.FC<ComparisonViewProps> = ({
  data,
  metrics,
  title = 'Comparison View',
}) => {
  const [selectedMetric, setSelectedMetric] = useState<string>(metrics[0]?.key || '');

  const handleMetricChange = (event: SelectChangeEvent) => {
    setSelectedMetric(event.target.value);
  };

  const selectedMetricData = metrics.find((m) => m.key === selectedMetric);

  return (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6">{title}</Typography>
          <FormControl size="small" sx={{ minWidth: 200 }}>
            <InputLabel>Metric</InputLabel>
            <Select
              value={selectedMetric}
              label="Metric"
              onChange={handleMetricChange}
            >
              {metrics.map((metric) => (
                <MenuItem key={metric.key} value={metric.key}>
                  {metric.label}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Box>

        {data.length === 0 ? (
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <Typography variant="body2" color="text.secondary">
              No data available for comparison
            </Typography>
          </Box>
        ) : (
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={data}>
              <CartesianGrid strokeDasharray="3 3" stroke="#444" />
              <XAxis dataKey="name" stroke="#888" />
              <YAxis stroke="#888" />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#132f4c',
                  border: '1px solid #2196f3',
                }}
              />
              <Legend />
              <Bar
                dataKey={selectedMetric}
                fill={selectedMetricData?.color || '#2196f3'}
                name={selectedMetricData?.label || selectedMetric}
              />
            </BarChart>
          </ResponsiveContainer>
        )}
      </CardContent>
    </Card>
  );
};

export default ComparisonView;
