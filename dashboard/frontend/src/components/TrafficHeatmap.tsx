/**
 * Traffic density heatmap visualization
 */

import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Grid,
} from '@mui/material';

interface HeatmapCell {
  lane: string;
  density: number; // 0-1 normalized
  label: string;
}

interface TrafficHeatmapProps {
  data: HeatmapCell[];
}

const TrafficHeatmap: React.FC<TrafficHeatmapProps> = ({ data }) => {
  const getHeatmapColor = (density: number): string => {
    // Green (low) -> Yellow (medium) -> Red (high)
    if (density < 0.33) {
      const intensity = Math.floor(density * 3 * 255);
      return `rgb(0, ${255 - intensity}, 0)`;
    } else if (density < 0.67) {
      const intensity = Math.floor((density - 0.33) * 3 * 255);
      return `rgb(${intensity}, ${255 - intensity}, 0)`;
    } else {
      const intensity = Math.floor((density - 0.67) * 3 * 255);
      return `rgb(255, ${255 - intensity}, 0)`;
    }
  };

  const getDensityLabel = (density: number): string => {
    if (density < 0.33) return 'Low';
    if (density < 0.67) return 'Medium';
    return 'High';
  };

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Traffic Density Heatmap
        </Typography>
        <Grid container spacing={1}>
          {data.map((cell) => (
            <Grid item xs={12} sm={6} md={4} key={cell.lane}>
              <Box
                sx={{
                  p: 2,
                  borderRadius: 1,
                  backgroundColor: getHeatmapColor(cell.density),
                  color: cell.density > 0.5 ? 'white' : 'black',
                  textAlign: 'center',
                  transition: 'all 0.3s ease',
                }}
              >
                <Typography variant="body2" fontWeight="bold">
                  {cell.lane}
                </Typography>
                <Typography variant="h6">
                  {cell.label}
                </Typography>
                <Typography variant="caption">
                  {getDensityLabel(cell.density)}
                </Typography>
              </Box>
            </Grid>
          ))}
        </Grid>
        
        {/* Legend */}
        <Box sx={{ mt: 2, display: 'flex', alignItems: 'center', gap: 2 }}>
          <Typography variant="caption" color="text.secondary">
            Density:
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Box
              sx={{
                width: 20,
                height: 20,
                backgroundColor: getHeatmapColor(0.1),
                borderRadius: 0.5,
              }}
            />
            <Typography variant="caption">Low</Typography>
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Box
              sx={{
                width: 20,
                height: 20,
                backgroundColor: getHeatmapColor(0.5),
                borderRadius: 0.5,
              }}
            />
            <Typography variant="caption">Medium</Typography>
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Box
              sx={{
                width: 20,
                height: 20,
                backgroundColor: getHeatmapColor(0.9),
                borderRadius: 0.5,
              }}
            />
            <Typography variant="caption">High</Typography>
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
};

export default TrafficHeatmap;
