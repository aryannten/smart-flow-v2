"""
Stream Manager Module for SMART FLOW v2

Handles multiple video input sources with unified interface:
- Local video files
- YouTube Live streams
- RTSP network cameras
- Webcam devices
"""

from typing import Optional, Tuple, Deque
from dataclasses import dataclass
from collections import deque
import numpy as np
import cv2
import time
import os
import logging
from pathlib import Path

from src.error_handler import ErrorHandler, ErrorSeverity

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class StreamMetadata:
    """Metadata about a video stream"""
    source: str
    source_type: str
    width: int
    height: int
    fps: float
    is_live: bool
    codec: str


@dataclass
class Frame:
    """Enhanced frame with metadata"""
    image: np.ndarray
    frame_number: int
    timestamp: float
    source_type: str
    is_live: bool


class StreamManager:
    """
    Unified interface for multiple video input sources.
    
    Supports:
    - Local files: path/to/video.mp4
    - YouTube Live: https://youtube.com/watch?v=...
    - RTSP streams: rtsp://camera.ip.address/stream
    - Webcams: webcam:0 or webcam:1
    """
    
    # Frame buffer size for live streams
    BUFFER_SIZE = 30
    
    # Reconnection settings
    MAX_RETRIES = 5
    INITIAL_BACKOFF = 1.0  # seconds
    MAX_BACKOFF = 30.0  # seconds
    
    def __init__(self, source: str, source_type: str = 'auto', error_handler: Optional[ErrorHandler] = None):
        """
        Initialize stream manager.
        
        Args:
            source: Path or URL to video source
            source_type: Type of source ('auto', 'file', 'youtube', 'rtsp', 'webcam')
            error_handler: Optional error handler for comprehensive error management
        """
        self.source = source
        self.source_type = self._detect_source_type(source) if source_type == 'auto' else source_type
        self.capture: Optional[cv2.VideoCapture] = None
        self.frame_number = 0
        self.start_time = time.time()
        self.frame_buffer: Deque[Frame] = deque(maxlen=self.BUFFER_SIZE)
        self.retry_count = 0
        self.last_connection_attempt = 0.0
        self.is_connected = False
        self.error_handler = error_handler
        self.consecutive_failures = 0
        self.max_consecutive_failures = 10
        
        logger.info(f"StreamManager initialized: source={source}, type={self.source_type}")
    
    def _detect_source_type(self, source: str) -> str:
        """
        Auto-detect source type from URL/path.
        
        Args:
            source: Path or URL to video source
            
        Returns:
            Detected source type: 'file', 'youtube', 'rtsp', 'webcam'
        """
        source_lower = source.lower()
        
        # Check for webcam
        if source_lower.startswith('webcam:'):
            return 'webcam'
        
        # Check for YouTube
        if 'youtube.com' in source_lower or 'youtu.be' in source_lower:
            return 'youtube'
        
        # Check for RTSP
        if source_lower.startswith('rtsp://'):
            return 'rtsp'
        
        # Check if it's a file path
        if os.path.exists(source) or Path(source).suffix in ['.mp4', '.avi', '.mov', '.mkv', '.flv']:
            return 'file'
        
        # Default to file
        logger.warning(f"Could not detect source type for {source}, defaulting to 'file'")
        return 'file'
    
    def connect(self) -> bool:
        """
        Establish connection to video source.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            if self.source_type == 'webcam':
                # Extract device ID from "webcam:0" format
                device_id = int(self.source.split(':')[1])
                self.capture = cv2.VideoCapture(device_id)
                logger.info(f"Connecting to webcam device {device_id}")
                
            elif self.source_type == 'youtube':
                # For YouTube, we need yt-dlp to get the actual stream URL
                try:
                    import yt_dlp
                    
                    ydl_opts = {
                        'format': 'best[ext=mp4]',
                        'quiet': True,
                        'no_warnings': True,
                    }
                    
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(self.source, download=False)
                        stream_url = info['url']
                        self.capture = cv2.VideoCapture(stream_url)
                        logger.info(f"Connecting to YouTube stream: {self.source}")
                        
                except ImportError as e:
                    error_msg = "yt-dlp not installed. Install with: pip install yt-dlp"
                    logger.error(error_msg)
                    if self.error_handler:
                        self.error_handler.handle_exception(
                            component="StreamManager",
                            operation="connect_youtube",
                            exception=e,
                            severity=ErrorSeverity.ERROR
                        )
                    return False
                except Exception as e:
                    logger.error(f"Failed to extract YouTube stream URL: {e}")
                    if self.error_handler:
                        self.error_handler.handle_exception(
                            component="StreamManager",
                            operation="connect_youtube",
                            exception=e,
                            severity=ErrorSeverity.ERROR
                        )
                    return False
                    
            elif self.source_type == 'rtsp':
                # RTSP stream
                self.capture = cv2.VideoCapture(self.source)
                logger.info(f"Connecting to RTSP stream: {self.source}")
                
            elif self.source_type == 'file':
                # Local file
                if not os.path.exists(self.source):
                    error_msg = f"Video file not found: {self.source}"
                    logger.error(error_msg)
                    if self.error_handler:
                        self.error_handler.handle_exception(
                            component="StreamManager",
                            operation="connect_file",
                            exception=FileNotFoundError(error_msg),
                            severity=ErrorSeverity.ERROR
                        )
                    return False
                self.capture = cv2.VideoCapture(self.source)
                logger.info(f"Opening video file: {self.source}")
                
            else:
                error_msg = f"Unknown source type: {self.source_type}"
                logger.error(error_msg)
                if self.error_handler:
                    self.error_handler.handle_exception(
                        component="StreamManager",
                        operation="connect",
                        exception=ValueError(error_msg),
                        severity=ErrorSeverity.ERROR
                    )
                return False
            
            # Verify connection
            if self.capture is None or not self.capture.isOpened():
                error_msg = f"Failed to open video source: {self.source}"
                logger.error(error_msg)
                if self.error_handler:
                    self.error_handler.handle_exception(
                        component="StreamManager",
                        operation="connect",
                        exception=RuntimeError(error_msg),
                        severity=ErrorSeverity.ERROR
                    )
                return False
            
            # Reset counters
            self.frame_number = 0
            self.start_time = time.time()
            self.is_connected = True
            self.retry_count = 0
            self.consecutive_failures = 0
            
            logger.info(f"Successfully connected to {self.source_type} source")
            if self.error_handler:
                self.error_handler.restore_component("StreamManager")
            return True
            
        except Exception as e:
            logger.error(f"Error connecting to video source: {e}")
            if self.error_handler:
                self.error_handler.handle_exception(
                    component="StreamManager",
                    operation="connect",
                    exception=e,
                    severity=ErrorSeverity.ERROR
                )
            return False
    
    def get_next_frame(self) -> Optional[Frame]:
        """
        Get next frame from stream with retry logic for live streams.
        
        Returns:
            Frame object or None if stream ended
        """
        if not self.is_connected or self.capture is None:
            logger.warning("Stream not connected, attempting to connect")
            if not self.connect():
                self.consecutive_failures += 1
                if self.consecutive_failures >= self.max_consecutive_failures:
                    if self.error_handler:
                        self.error_handler.handle_exception(
                            component="StreamManager",
                            operation="get_next_frame",
                            exception=RuntimeError(f"Max consecutive failures ({self.max_consecutive_failures}) reached"),
                            severity=ErrorSeverity.CRITICAL
                        )
                return None
        
        try:
            ret, image = self.capture.read()
            
            if not ret or image is None:
                self.consecutive_failures += 1
                
                # For live streams, try to reconnect
                if self.is_live():
                    logger.warning("Failed to read frame from live stream, attempting reconnection")
                    if self.error_handler:
                        self.error_handler.handle_exception(
                            component="StreamManager",
                            operation="read_frame",
                            exception=RuntimeError("Failed to read frame from live stream"),
                            severity=ErrorSeverity.WARNING
                        )
                    
                    if self.consecutive_failures < self.max_consecutive_failures:
                        if self.reconnect():
                            # Try reading again after reconnection
                            ret, image = self.capture.read()
                            if not ret or image is None:
                                return None
                        else:
                            return None
                    else:
                        if self.error_handler:
                            self.error_handler.handle_exception(
                                component="StreamManager",
                                operation="get_next_frame",
                                exception=RuntimeError(f"Max consecutive failures ({self.max_consecutive_failures}) reached"),
                                severity=ErrorSeverity.CRITICAL
                            )
                        return None
                else:
                    # File ended
                    logger.info("Video file ended")
                    return None
            
            # Reset failure counter on success
            self.consecutive_failures = 0
            
            # Create frame object
            self.frame_number += 1
            timestamp = time.time() - self.start_time
            
            frame = Frame(
                image=image,
                frame_number=self.frame_number,
                timestamp=timestamp,
                source_type=self.source_type,
                is_live=self.is_live()
            )
            
            # Buffer frame for live streams
            if self.is_live():
                self.frame_buffer.append(frame)
            
            return frame
            
        except Exception as e:
            logger.error(f"Error reading frame: {e}")
            self.consecutive_failures += 1
            
            if self.error_handler:
                self.error_handler.handle_exception(
                    component="StreamManager",
                    operation="get_next_frame",
                    exception=e,
                    severity=ErrorSeverity.ERROR
                )
            
            if self.is_live() and self.consecutive_failures < self.max_consecutive_failures:
                # Try reconnection for live streams
                if self.reconnect():
                    return self.get_next_frame()
            return None
    
    def get_metadata(self) -> StreamMetadata:
        """
        Get stream metadata.
        
        Returns:
            StreamMetadata object
        """
        if not self.is_connected or self.capture is None:
            raise RuntimeError("Stream not connected. Call connect() first.")
        
        width = int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = self.capture.get(cv2.CAP_PROP_FPS)
        
        # Get codec (fourcc)
        fourcc = int(self.capture.get(cv2.CAP_PROP_FOURCC))
        codec = "".join([chr((fourcc >> 8 * i) & 0xFF) for i in range(4)])
        
        return StreamMetadata(
            source=self.source,
            source_type=self.source_type,
            width=width,
            height=height,
            fps=fps if fps > 0 else 30.0,  # Default to 30 if not available
            is_live=self.is_live(),
            codec=codec
        )
    
    def is_live(self) -> bool:
        """
        Check if source is a live stream.
        
        Returns:
            True if live stream, False if file
        """
        return self.source_type in ['youtube', 'rtsp', 'webcam']
    
    def reconnect(self) -> bool:
        """
        Attempt to reconnect to live stream after failure.
        
        Returns:
            True if reconnection successful, False otherwise
        """
        if not self.is_live():
            logger.warning("Reconnection only supported for live streams")
            return False
        
        # Check if we've exceeded max retries
        if self.retry_count >= self.MAX_RETRIES:
            logger.error(f"Max reconnection attempts ({self.MAX_RETRIES}) reached")
            return False
        
        # Calculate backoff time with exponential backoff
        backoff_time = min(
            self.INITIAL_BACKOFF * (2 ** self.retry_count),
            self.MAX_BACKOFF
        )
        
        # Check if enough time has passed since last attempt
        time_since_last_attempt = time.time() - self.last_connection_attempt
        if time_since_last_attempt < backoff_time:
            wait_time = backoff_time - time_since_last_attempt
            logger.info(f"Waiting {wait_time:.1f}s before reconnection attempt")
            time.sleep(wait_time)
        
        # Attempt reconnection
        self.retry_count += 1
        self.last_connection_attempt = time.time()
        
        logger.info(f"Reconnection attempt {self.retry_count}/{self.MAX_RETRIES}")
        
        # Release old connection
        if self.capture is not None:
            self.capture.release()
            self.capture = None
        
        self.is_connected = False
        
        # Try to connect again
        if self.connect():
            logger.info("Reconnection successful")
            self.retry_count = 0  # Reset retry count on success
            return True
        else:
            logger.warning(f"Reconnection attempt {self.retry_count} failed")
            return False
    
    def get_connection_health(self) -> dict:
        """
        Monitor connection health.
        
        Returns:
            Dictionary with health metrics
        """
        health = {
            'is_connected': self.is_connected,
            'retry_count': self.retry_count,
            'frames_processed': self.frame_number,
            'buffer_size': len(self.frame_buffer) if self.is_live() else 0,
            'source_type': self.source_type,
            'is_live': self.is_live()
        }
        
        if self.capture is not None and self.is_connected:
            health['capture_opened'] = self.capture.isOpened()
        else:
            health['capture_opened'] = False
        
        return health
    
    def release(self) -> None:
        """Release stream resources"""
        logger.info("Releasing stream resources")
        
        if self.capture is not None:
            self.capture.release()
            self.capture = None
        
        self.is_connected = False
        self.frame_buffer.clear()
        
        logger.info("Stream resources released")
