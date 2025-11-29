/**
 * Manual signal override control component
 */

import React, { useState } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Select,
  MenuItem,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Alert,
  Snackbar,
} from '@mui/material';
import { Traffic } from '@mui/icons-material';
import { apiService } from '../services/api';
import { SignalState } from '../types';

interface SignalOverrideControlProps {
  lanes: string[];
}

const SignalOverrideControl: React.FC<SignalOverrideControlProps> = ({ lanes }) => {
  const [selectedLane, setSelectedLane] = useState<string>('');
  const [selectedState, setSelectedState] = useState<SignalState>('green');
  const [duration, setDuration] = useState<number>(30);
  const [loading, setLoading] = useState(false);
  const [snackbar, setSnackbar] = useState<{
    open: boolean;
    message: string;
    severity: 'success' | 'error';
  }>({
    open: false,
    message: '',
    severity: 'success',
  });

  const handleOverride = async () => {
    if (!selectedLane) {
      setSnackbar({
        open: true,
        message: 'Please select a lane',
        severity: 'error',
      });
      return;
    }

    setLoading(true);
    try {
      await apiService.overrideSignal(selectedLane, selectedState, duration);
      setSnackbar({
        open: true,
        message: `Override applied to ${selectedLane}`,
        severity: 'success',
      });
    } catch (error) {
      setSnackbar({
        open: true,
        message: 'Failed to apply override',
        severity: 'error',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleCloseSnackbar = () => {
    setSnackbar({ ...snackbar, open: false });
  };

  return (
    <>
      <Card>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
            <Traffic color="primary" />
            <Typography variant="h6">Manual Signal Override</Typography>
          </Box>

          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            <FormControl fullWidth>
              <InputLabel>Lane</InputLabel>
              <Select
                value={selectedLane}
                label="Lane"
                onChange={(e) => setSelectedLane(e.target.value)}
              >
                {lanes.map((lane) => (
                  <MenuItem key={lane} value={lane}>
                    {lane}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <FormControl fullWidth>
              <InputLabel>Signal State</InputLabel>
              <Select
                value={selectedState}
                label="Signal State"
                onChange={(e) => setSelectedState(e.target.value as SignalState)}
              >
                <MenuItem value="red">Red</MenuItem>
                <MenuItem value="yellow">Yellow</MenuItem>
                <MenuItem value="green">Green</MenuItem>
              </Select>
            </FormControl>

            <TextField
              label="Duration (seconds)"
              type="number"
              value={duration}
              onChange={(e) => setDuration(Number(e.target.value))}
              inputProps={{ min: 1, max: 300 }}
              fullWidth
            />

            <Button
              variant="contained"
              color="primary"
              onClick={handleOverride}
              disabled={loading || !selectedLane}
              fullWidth
            >
              {loading ? 'Applying...' : 'Apply Override'}
            </Button>
          </Box>

          <Alert severity="warning" sx={{ mt: 2 }}>
            Manual overrides should be used with caution. The system will resume normal operation
            after the specified duration.
          </Alert>
        </CardContent>
      </Card>

      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert onClose={handleCloseSnackbar} severity={snackbar.severity}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </>
  );
};

export default SignalOverrideControl;
