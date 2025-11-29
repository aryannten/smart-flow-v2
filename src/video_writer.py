"""
Video Writer Module for SMART FLOW v2

Saves annotated video output with efficient compression.
"""

from typing import Tuple, Optional
import numpy as np
import cv2
import os


class VideoWriter:
    """
    Saves annotated video output with codec selection and fallback.
    
    Handles frame writing with OpenCV, codec selection with fallback,
    efficient compression, and proper finalization and cleanup.
    """
    
    # Codec priority list (in order of preference)
    CODEC_PRIORITY = [
        ('mp4v', '.mp4'),  # MPEG-4
        ('avc1', '.mp4'),  # H.264
        ('XVID', '.avi'),  # Xvid
        ('MJPG', '.avi'),  # Motion JPEG
    ]
    
    def __init__(self, output_path: str, fps: float, resolution: Tuple[int, int]):
        """
        Initialize video writer.
        
        Args:
            output_path: Path to output video file
            fps: Frames per second
            resolution: (width, height) tuple
        """
        self.output_path = output_path
        self.fps = fps
        self.resolution = resolution
        self.writer: Optional[cv2.VideoWriter] = None
        self.is_initialized = False
        self.frames_written = 0
        
        # Ensure output directory exists
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
    
    def _initialize_writer(self, frame: np.ndarray) -> bool:
        """
        Initialize the video writer with codec fallback.
        
        Args:
            frame: First frame to determine properties
            
        Returns:
            True if initialization successful, False otherwise
        """
        if self.is_initialized:
            return True
        
        # Get frame dimensions
        height, width = frame.shape[:2]
        
        # If resolution was specified, use it; otherwise use frame dimensions
        if self.resolution:
            width, height = self.resolution
        
        # Try each codec in priority order
        for codec_name, extension in self.CODEC_PRIORITY:
            try:
                # Adjust output path extension if needed
                output_path = self.output_path
                if not output_path.endswith(extension):
                    base_path = os.path.splitext(output_path)[0]
                    output_path = base_path + extension
                    self.output_path = output_path
                
                # Create fourcc code
                fourcc = cv2.VideoWriter_fourcc(*codec_name)
                
                # Try to create writer
                writer = cv2.VideoWriter(
                    output_path,
                    fourcc,
                    self.fps,
                    (width, height)
                )
                
                # Check if writer was opened successfully
                if writer.isOpened():
                    self.writer = writer
                    self.is_initialized = True
                    self.resolution = (width, height)
                    return True
                else:
                    writer.release()
                    
            except Exception:
                # Try next codec
                continue
        
        # All codecs failed
        return False
    
    def write_frame(self, frame: np.ndarray) -> None:
        """
        Write a frame to video.
        
        Args:
            frame: Frame to write (numpy array in BGR format)
            
        Raises:
            RuntimeError: If writer initialization fails
            ValueError: If frame dimensions don't match expected resolution
        """
        if frame is None or frame.size == 0:
            raise ValueError("Cannot write empty or None frame")
        
        # Initialize writer on first frame
        if not self.is_initialized:
            if not self._initialize_writer(frame):
                raise RuntimeError(
                    f"Failed to initialize video writer for {self.output_path}. "
                    "All codec options failed."
                )
        
        # Resize frame if needed to match expected resolution
        height, width = frame.shape[:2]
        expected_width, expected_height = self.resolution
        
        if (width, height) != (expected_width, expected_height):
            frame = cv2.resize(frame, (expected_width, expected_height))
        
        # Ensure frame is in correct format (BGR, uint8)
        if frame.dtype != np.uint8:
            frame = frame.astype(np.uint8)
        
        if len(frame.shape) == 2:
            # Grayscale - convert to BGR
            frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
        elif frame.shape[2] == 4:
            # RGBA - convert to BGR
            frame = cv2.cvtColor(frame, cv2.COLOR_RGBA2BGR)
        
        # Write frame
        try:
            self.writer.write(frame)
            self.frames_written += 1
        except Exception as e:
            raise RuntimeError(f"Failed to write frame: {e}")
    
    def finalize(self) -> None:
        """
        Finalize and close video file.
        
        Properly releases the video writer and ensures all data is flushed to disk.
        """
        if self.writer is not None:
            try:
                self.writer.release()
            except Exception:
                pass  # Ignore errors during release
            finally:
                self.writer = None
                self.is_initialized = False
    
    def get_output_path(self) -> str:
        """
        Get output file path.
        
        Returns:
            Output path
        """
        return self.output_path
    
    def get_frames_written(self) -> int:
        """
        Get number of frames written.
        
        Returns:
            Number of frames written
        """
        return self.frames_written
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensures finalization."""
        self.finalize()
        return False
    
    def __del__(self):
        """Destructor - ensures cleanup."""
        self.finalize()
