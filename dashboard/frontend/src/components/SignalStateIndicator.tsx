/**
 * Signal state indicator component
 */

import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Stack,
  Chip,
} from '@mui/material';
import { Circle } from '@mui/icons-material';
import { SignalState } from '../types';

interface LaneSignal {
  lane: string;
  state: SignalState;
  timeRemaining?: number;
}

interface SignalStateIndicatorProps {
  lanes: LaneSignal[];
}

const SignalStateIndicator: React.FC<SignalStateIndicatorProps> = ({ lanes }) => {
  const getSignalColor = (state: SignalState): string => {
    switch (state) {
      case 'red':
        return '#f44336';
      case 'yellow':
        return '#ff9800';
      case 'green':
        return '#4caf50';
      default:
        return '#9e9e9e';
    }
  };

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Signal States
        </Typography>
        <Stack spacing={2}>
          {lanes.map((lane) => (
            <Box
              key={lane.lane}
              sx={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                p: 1,
                borderRadius: 1,
                backgroundColor: 'rgba(255, 255, 255, 0.05)',
              }}
            >
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Circle
                  sx={{
                    color: getSignalColor(lane.state),
                    fontSize: 20,
                  }}
                />
                <Typography variant="body1">{lane.lane}</Typography>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Chip
                  label={lane.state.toUpperCase()}
                  size="small"
                  sx={{
                    backgroundColor: getSignalColor(lane.state),
                    color: 'white',
                    fontWeight: 'bold',
                  }}
                />
                {lane.timeRemaining !== undefined && (
                  <Typography variant="body2" color="text.secondary">
                    {lane.timeRemaining}s
                  </Typography>
                )}
              </Box>
            </Box>
          ))}
        </Stack>
      </CardContent>
    </Card>
  );
};

export default SignalStateIndicator;
