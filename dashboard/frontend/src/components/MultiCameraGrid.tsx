/**
 * Multi-camera grid view component
 */

import React, { useState } from 'react';
import {
  Box,
  Grid,
  ToggleButtonGroup,
  ToggleButton,
  Typography,
} from '@mui/material';
import {
  ViewModule,
  ViewQuilt,
  ViewStream,
} from '@mui/icons-material';
import VideoFeed from './VideoFeed';

interface Camera {
  id: string;
  name: string;
  streamUrl: string;
}

interface MultiCameraGridProps {
  cameras: Camera[];
}

type GridLayout = '1x1' | '2x2' | '1x2';

const MultiCameraGrid: React.FC<MultiCameraGridProps> = ({ cameras }) => {
  const [layout, setLayout] = useState<GridLayout>('2x2');

  const handleLayoutChange = (
    _event: React.MouseEvent<HTMLElement>,
    newLayout: GridLayout | null,
  ) => {
    if (newLayout !== null) {
      setLayout(newLayout);
    }
  };

  const getGridColumns = (): number => {
    switch (layout) {
      case '1x1':
        return 1;
      case '2x2':
        return 2;
      case '1x2':
        return 2;
      default:
        return 2;
    }
  };

  const getCamerasToDisplay = (): Camera[] => {
    switch (layout) {
      case '1x1':
        return cameras.slice(0, 1);
      case '2x2':
        return cameras.slice(0, 4);
      case '1x2':
        return cameras.slice(0, 2);
      default:
        return cameras;
    }
  };

  if (cameras.length === 0) {
    return (
      <Box sx={{ textAlign: 'center', py: 4 }}>
        <Typography variant="h6" color="text.secondary">
          No cameras available
        </Typography>
      </Box>
    );
  }

  return (
    <Box>
      <Box sx={{ mb: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h5">Video Feeds</Typography>
        <ToggleButtonGroup
          value={layout}
          exclusive
          onChange={handleLayoutChange}
          aria-label="grid layout"
          size="small"
        >
          <ToggleButton value="1x1" aria-label="single view">
            <ViewModule />
          </ToggleButton>
          <ToggleButton value="1x2" aria-label="two columns">
            <ViewStream />
          </ToggleButton>
          <ToggleButton value="2x2" aria-label="grid view">
            <ViewQuilt />
          </ToggleButton>
        </ToggleButtonGroup>
      </Box>

      <Grid container spacing={2}>
        {getCamerasToDisplay().map((camera) => (
          <Grid item xs={12} md={12 / getGridColumns()} key={camera.id}>
            <VideoFeed streamUrl={camera.streamUrl} title={camera.name} />
          </Grid>
        ))}
      </Grid>
    </Box>
  );
};

export default MultiCameraGrid;
