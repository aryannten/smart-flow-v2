/**
 * Live video feed component with controls
 */

import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  IconButton,
  Slider,
  Typography,
  Stack,
  Tooltip,
} from '@mui/material';
import {
  PlayArrow,
  Pause,
  Speed,
  Fullscreen,
  FullscreenExit,
} from '@mui/icons-material';

interface VideoFeedProps {
  streamUrl: string;
  title?: string;
}

const VideoFeed: React.FC<VideoFeedProps> = ({ streamUrl, title = 'Live Feed' }) => {
  const [isPlaying, setIsPlaying] = useState(true);
  const [playbackSpeed, setPlaybackSpeed] = useState(1.0);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const videoRef = useRef<HTMLImageElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  const handlePlayPause = () => {
    setIsPlaying(!isPlaying);
  };

  const handleSpeedChange = (_event: Event, value: number | number[]) => {
    setPlaybackSpeed(value as number);
  };

  const handleFullscreen = () => {
    if (!containerRef.current) return;

    if (!isFullscreen) {
      if (containerRef.current.requestFullscreen) {
        containerRef.current.requestFullscreen();
      }
    } else {
      if (document.exitFullscreen) {
        document.exitFullscreen();
      }
    }
  };

  useEffect(() => {
    const handleFullscreenChange = () => {
      setIsFullscreen(!!document.fullscreenElement);
    };

    document.addEventListener('fullscreenchange', handleFullscreenChange);
    return () => {
      document.removeEventListener('fullscreenchange', handleFullscreenChange);
    };
  }, []);

  return (
    <Card ref={containerRef}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          {title}
        </Typography>
        
        <Box
          sx={{
            position: 'relative',
            width: '100%',
            paddingTop: '56.25%', // 16:9 aspect ratio
            backgroundColor: '#000',
            borderRadius: 1,
            overflow: 'hidden',
          }}
        >
          {isPlaying ? (
            <img
              ref={videoRef}
              src={streamUrl}
              alt="Live video feed"
              style={{
                position: 'absolute',
                top: 0,
                left: 0,
                width: '100%',
                height: '100%',
                objectFit: 'contain',
              }}
            />
          ) : (
            <Box
              sx={{
                position: 'absolute',
                top: 0,
                left: 0,
                width: '100%',
                height: '100%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'white',
              }}
            >
              <Typography variant="h6">Paused</Typography>
            </Box>
          )}
        </Box>

        <Stack direction="row" spacing={2} alignItems="center" sx={{ mt: 2 }}>
          <Tooltip title={isPlaying ? 'Pause' : 'Play'}>
            <IconButton onClick={handlePlayPause} color="primary">
              {isPlaying ? <Pause /> : <PlayArrow />}
            </IconButton>
          </Tooltip>

          <Speed />
          <Slider
            value={playbackSpeed}
            onChange={handleSpeedChange}
            min={0.25}
            max={2.0}
            step={0.25}
            marks
            valueLabelDisplay="auto"
            valueLabelFormat={(value) => `${value}x`}
            sx={{ flexGrow: 1, maxWidth: 200 }}
          />

          <Tooltip title={isFullscreen ? 'Exit Fullscreen' : 'Fullscreen'}>
            <IconButton onClick={handleFullscreen} color="primary">
              {isFullscreen ? <FullscreenExit /> : <Fullscreen />}
            </IconButton>
          </Tooltip>
        </Stack>
      </CardContent>
    </Card>
  );
};

export default VideoFeed;
