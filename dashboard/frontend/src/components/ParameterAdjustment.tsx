/**
 * Parameter adjustment control component
 */

import React, { useState } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Slider,
  Button,
  Alert,
  Snackbar,
  Stack,
} from '@mui/material';
import { Settings } from '@mui/icons-material';
import { apiService } from '../services/api';

interface Parameter {
  name: string;
  label: string;
  min: number;
  max: number;
  step: number;
  defaultValue: number;
  unit: string;
}

const PARAMETERS: Parameter[] = [
  {
    name: 'min_green_time',
    label: 'Minimum Green Time',
    min: 5,
    max: 60,
    step: 5,
    defaultValue: 10,
    unit: 's',
  },
  {
    name: 'max_green_time',
    label: 'Maximum Green Time',
    min: 30,
    max: 180,
    step: 10,
    defaultValue: 90,
    unit: 's',
  },
  {
    name: 'yellow_time',
    label: 'Yellow Phase Duration',
    min: 2,
    max: 10,
    step: 1,
    defaultValue: 3,
    unit: 's',
  },
  {
    name: 'detection_threshold',
    label: 'Detection Confidence Threshold',
    min: 0.3,
    max: 0.9,
    step: 0.05,
    defaultValue: 0.5,
    unit: '',
  },
];

const ParameterAdjustment: React.FC = () => {
  const [values, setValues] = useState<Record<string, number>>(
    PARAMETERS.reduce((acc, param) => {
      acc[param.name] = param.defaultValue;
      return acc;
    }, {} as Record<string, number>)
  );
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

  const handleValueChange = (paramName: string, value: number) => {
    setValues((prev) => ({ ...prev, [paramName]: value }));
  };

  const handleApply = async (param: Parameter) => {
    setLoading(true);
    try {
      await apiService.adjustParameter(param.name, values[param.name]);
      setSnackbar({
        open: true,
        message: `${param.label} updated successfully`,
        severity: 'success',
      });
    } catch (error) {
      setSnackbar({
        open: true,
        message: `Failed to update ${param.label}`,
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
            <Settings color="primary" />
            <Typography variant="h6">Parameter Adjustment</Typography>
          </Box>

          <Stack spacing={3}>
            {PARAMETERS.map((param) => (
              <Box key={param.name}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2" color="text.secondary">
                    {param.label}
                  </Typography>
                  <Typography variant="body2" fontWeight="bold">
                    {values[param.name]}
                    {param.unit}
                  </Typography>
                </Box>
                <Slider
                  value={values[param.name]}
                  onChange={(_, value) => handleValueChange(param.name, value as number)}
                  min={param.min}
                  max={param.max}
                  step={param.step}
                  marks
                  valueLabelDisplay="auto"
                />
                <Button
                  variant="outlined"
                  size="small"
                  onClick={() => handleApply(param)}
                  disabled={loading}
                  sx={{ mt: 1 }}
                >
                  Apply
                </Button>
              </Box>
            ))}
          </Stack>

          <Alert severity="info" sx={{ mt: 2 }}>
            Parameter changes take effect immediately but can be reverted by restarting the system.
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

export default ParameterAdjustment;
