"""
Video Processor module for SMART FLOW traffic signal simulation system.

Handles video file I/O, frame extraction, and metadata management.
"""

import cv2
from pathlib import Path
from typing import Optional
from src.models import Frame, FrameMetadata


class VideoProcessor:
    """
    Handles video file loading, frame extraction, and metadata management.
    
    This class provides an interface for reading video files, extracting frames
    sequentially, and accessing video metadata such as resolution and frame rate.
    """
    
    def __init__(self, video_path: str):
        """
        Initialize VideoProcessor with a video file path.
        
        Args:
            video_path: Path to the video file to process
        """
        self.video_path = Path(video_path)
        self.capture: Optional[cv2.VideoCapture] = None
        self.current_frame_number = 0
        self._width = 0
        self._height = 0
        self._fps = 0.0
        self._total_frames = 0
        self._is_loaded = False
    
    def load_video(self) -> bool:
        """
        Load and validate the video file.
        
        Validates the video file format and opens it for processing.
        Extracts video metadata (resolution, FPS, frame count).
        
        Returns:
            bool: True if video loaded successfully, False otherwise
        """
        # Check if file exists
        if not self.video_path.exists():
            print(f"Error: Video file not found: {self.video_path}")
            return False
        
        # Check if file has a valid video extension
        valid_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.webm'}
        if self.video_path.suffix.lower() not in valid_extensions:
            print(f"Error: Unsupported video format: {self.video_path.suffix}")
            return False
        
        # Try to open the video file
        try:
            self.capture = cv2.VideoCapture(str(self.video_path))
            
            # Check if video opened successfully
            if not self.capture.isOpened():
                print(f"Error: Failed to open video file: {self.video_path}")
                self.capture = None
                return False
            
            # Extract video metadata
            self._width = int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH))
            self._height = int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
            self._fps = self.capture.get(cv2.CAP_PROP_FPS)
            self._total_frames = int(self.capture.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # Validate metadata
            if self._width <= 0 or self._height <= 0 or self._fps <= 0:
                print(f"Error: Invalid video metadata (width={self._width}, height={self._height}, fps={self._fps})")
                self.release()
                return False
            
            self._is_loaded = True
            self.current_frame_number = 0
            return True
            
        except Exception as e:
            print(f"Error: Exception while loading video: {e}")
            if self.capture is not None:
                self.capture.release()
                self.capture = None
            return False
    
    def get_next_frame(self) -> Optional[Frame]:
        """
        Extract and return the next frame from the video.
        
        Returns:
            Optional[Frame]: Frame object containing image data and metadata,
                           or None if video has ended or is not loaded
        """
        if not self._is_loaded or self.capture is None:
            return None
        
        ret, image = self.capture.read()
        
        if not ret or image is None:
            # End of video reached
            return None
        
        # Calculate timestamp based on frame number and FPS
        timestamp = self.current_frame_number / self._fps if self._fps > 0 else 0.0
        
        frame = Frame(
            image=image,
            frame_number=self.current_frame_number,
            timestamp=timestamp
        )
        
        self.current_frame_number += 1
        
        return frame
    
    def get_frame_metadata(self) -> FrameMetadata:
        """
        Get metadata about the current video state.
        
        Returns:
            FrameMetadata: Object containing frame number, timestamp, resolution, and FPS
        """
        timestamp = (self.current_frame_number - 1) / self._fps if self._fps > 0 else 0.0
        
        return FrameMetadata(
            frame_number=self.current_frame_number - 1,
            timestamp=timestamp,
            width=self._width,
            height=self._height,
            fps=self._fps
        )
    
    def release(self) -> None:
        """
        Release video resources and clean up.
        
        Should be called when done processing the video to free resources.
        """
        if self.capture is not None:
            self.capture.release()
            self.capture = None
        
        self._is_loaded = False
        self.current_frame_number = 0
    
    def __enter__(self):
        """Context manager entry."""
        self.load_video()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.release()
        return False
