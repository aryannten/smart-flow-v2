/**
 * Trend analysis component with statistical insights
 */

import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Grid,
  Chip,
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  TrendingFlat,
} from '@mui/icons-material';

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

interface TrendAnalysisProps {
  trends: TrendData[];
}

const TrendAnalysis: React.FC<TrendAnalysisProps> = ({ trends }) => {
  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'up':
        return <TrendingUp />;
      case 'down':
        return <TrendingDown />;
      case 'flat':
        return <TrendingFlat />;
      default:
        return <TrendingFlat />;
    }
  };

  const getTrendColor = (trend: string): 'success' | 'error' | 'default' => {
    switch (trend) {
      case 'up':
        return 'success';
      case 'down':
        return 'error';
      default:
        return 'default';
    }
  };

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Trend Analysis
        </Typography>
        <Grid container spacing={2}>
          {trends.map((trend) => (
            <Grid item xs={12} sm={6} md={4} key={trend.metric}>
              <Box
                sx={{
                  p: 2,
                  borderRadius: 1,
                  backgroundColor: 'rgba(255, 255, 255, 0.05)',
                  border: '1px solid rgba(255, 255, 255, 0.1)',
                }}
              >
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  {trend.metric}
                </Typography>
                
                <Box sx={{ display: 'flex', alignItems: 'baseline', gap: 1, mb: 1 }}>
                  <Typography variant="h5">
                    {trend.current.toFixed(1)}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {trend.unit}
                  </Typography>
                </Box>

                <Chip
                  icon={getTrendIcon(trend.trend)}
                  label={`${trend.changePercent > 0 ? '+' : ''}${trend.changePercent.toFixed(1)}%`}
                  size="small"
                  color={getTrendColor(trend.trend)}
                  sx={{ mb: 1 }}
                />

                <Box sx={{ mt: 1 }}>
                  <Typography variant="caption" color="text.secondary">
                    Avg: {trend.average.toFixed(1)} {trend.unit}
                  </Typography>
                  <br />
                  <Typography variant="caption" color="text.secondary">
                    Range: {trend.min.toFixed(1)} - {trend.max.toFixed(1)} {trend.unit}
                  </Typography>
                </Box>
              </Box>
            </Grid>
          ))}
        </Grid>
      </CardContent>
    </Card>
  );
};

export default TrendAnalysis;
