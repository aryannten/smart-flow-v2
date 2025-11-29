/**
 * Alert notifications display component
 */

import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Chip,
  IconButton,
} from '@mui/material';
import {
  Info,
  Warning,
  Error as ErrorIcon,
  Clear,
} from '@mui/icons-material';
import { Alert } from '../types';
import { useDashboard } from '../context/DashboardContext';

const AlertNotifications: React.FC = () => {
  const { alerts, clearAlerts } = useDashboard();

  const getAlertIcon = (level: string) => {
    switch (level) {
      case 'info':
        return <Info color="info" />;
      case 'warning':
        return <Warning color="warning" />;
      case 'error':
        return <ErrorIcon color="error" />;
      default:
        return <Info />;
    }
  };

  const getAlertColor = (level: string): 'info' | 'warning' | 'error' => {
    switch (level) {
      case 'warning':
        return 'warning';
      case 'error':
        return 'error';
      default:
        return 'info';
    }
  };

  const formatTimestamp = (timestamp: number): string => {
    const date = new Date(timestamp * 1000);
    return date.toLocaleTimeString();
  };

  return (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6">Alerts</Typography>
          {alerts.length > 0 && (
            <IconButton size="small" onClick={clearAlerts} title="Clear all alerts">
              <Clear />
            </IconButton>
          )}
        </Box>

        {alerts.length === 0 ? (
          <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', py: 2 }}>
            No alerts
          </Typography>
        ) : (
          <List sx={{ maxHeight: 400, overflow: 'auto' }}>
            {alerts.slice().reverse().map((alert, index) => (
              <ListItem
                key={index}
                sx={{
                  borderLeft: 3,
                  borderColor: `${getAlertColor(alert.level)}.main`,
                  mb: 1,
                  backgroundColor: 'rgba(255, 255, 255, 0.05)',
                  borderRadius: 1,
                }}
              >
                <ListItemIcon>{getAlertIcon(alert.level)}</ListItemIcon>
                <ListItemText
                  primary={alert.message}
                  secondary={formatTimestamp(alert.timestamp)}
                />
                <Chip
                  label={alert.level.toUpperCase()}
                  size="small"
                  color={getAlertColor(alert.level)}
                />
              </ListItem>
            ))}
          </List>
        )}
      </CardContent>
    </Card>
  );
};

export default AlertNotifications;
