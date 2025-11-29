"""
Unit tests for VideoProcessor module.
"""
import pytest
import numpy as np
import cv2
import tempfile
from pathlib import Path
from src.video_processor import VideoProcessor


@pytest.fixture
def sample_video():
    """Create a sample video file for testing."""
    with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp_file:
        video_path = tmp_file.name
    
    # Create a simple video with known properties
    width, height, fps, num_frames = 320, 240, 30, 10
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(video_path, fourcc, float(fps), (width, height))
    
    for i in range(num_frames):
        # Create frames with different colors
        color_value = int((i / max(num_frames - 1, 1)) * 255)
        frame = np.full((height, width, 3), color_value, dtype=np.uint8)
        out.write(frame)
    
    out.release()
    
    yield video_path, width, height, fps, num_frames
    
    # Cleanup
    Path(video_path).unlink(missing_ok=True)


def test_load_valid_video(sample_video):
    """Test loading a valid video file."""
    video_path, width, height, fps, num_frames = sample_video
    
    processor = VideoProcessor(video_path)
    result = processor.load_video()
    
    assert result is True, "Should successfully load valid video"
    assert processor._is_loaded is True, "Processor should be marked as loaded"
    assert processor.capture is not None, "Capture should be initialized"
    assert processor._width == width, f"Width should be {width}"
    assert processor._height == height, f"Height should be {height}"
    assert processor._fps == fps, f"FPS should be {fps}"
    
    processor.release()


def test_load_missing_file():
    """Test error handling for missing video file."""
    processor = VideoProcessor("nonexistent_video.mp4")
    result = processor.load_video()
    
    assert result is False, "Should fail to load missing file"
    assert processor._is_loaded is False, "Processor should not be marked as loaded"
    assert processor.capture is None, "Capture should be None"


def test_load_invalid_extension():
    """Test error handling for unsupported file format."""
    with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as tmp_file:
        tmp_file.write(b"This is not a video file")
        invalid_path = tmp_file.name
    
    try:
        processor = VideoProcessor(invalid_path)
        result = processor.load_video()
        
        assert result is False, "Should reject unsupported file format"
        assert processor._is_loaded is False, "Processor should not be marked as loaded"
        
    finally:
        Path(invalid_path).unlink(missing_ok=True)


def test_frame_extraction(sample_video):
    """Test extracting frames from video."""
    video_path, width, height, fps, num_frames = sample_video
    
    processor = VideoProcessor(video_path)
    processor.load_video()
    
    # Extract first frame
    frame = processor.get_next_frame()
    
    assert frame is not None, "Should extract first frame"
    assert frame.frame_number == 0, "First frame should have frame_number 0"
    assert frame.timestamp == 0.0, "First frame should have timestamp 0.0"
    assert frame.image.shape == (height, width, 3), "Frame should have correct dimensions"
    
    processor.release()


def test_frame_extraction_sequence(sample_video):
    """Test extracting multiple frames in sequence."""
    video_path, width, height, fps, num_frames = sample_video
    
    processor = VideoProcessor(video_path)
    processor.load_video()
    
    frames = []
    while True:
        frame = processor.get_next_frame()
        if frame is None:
            break
        frames.append(frame)
    
    # Verify we extracted frames
    assert len(frames) > 0, "Should extract at least one frame"
    
    # Verify frame numbers are sequential
    for i, frame in enumerate(frames):
        assert frame.frame_number == i, f"Frame {i} should have frame_number {i}"
    
    processor.release()


def test_get_frame_metadata(sample_video):
    """Test retrieving frame metadata."""
    video_path, width, height, fps, num_frames = sample_video
    
    processor = VideoProcessor(video_path)
    processor.load_video()
    
    # Extract a frame first
    frame = processor.get_next_frame()
    assert frame is not None
    
    # Get metadata
    metadata = processor.get_frame_metadata()
    
    assert metadata.frame_number == 0, "Metadata should reflect current frame"
    assert metadata.width == width, f"Metadata width should be {width}"
    assert metadata.height == height, f"Metadata height should be {height}"
    assert metadata.fps == fps, f"Metadata FPS should be {fps}"
    
    processor.release()


def test_get_next_frame_without_loading():
    """Test that get_next_frame returns None when video is not loaded."""
    processor = VideoProcessor("dummy.mp4")
    
    frame = processor.get_next_frame()
    
    assert frame is None, "Should return None when video is not loaded"


def test_release():
    """Test releasing video resources."""
    with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp_file:
        video_path = tmp_file.name
    
    # Create a minimal video
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(video_path, fourcc, 30.0, (320, 240))
    frame = np.zeros((240, 320, 3), dtype=np.uint8)
    out.write(frame)
    out.release()
    
    try:
        processor = VideoProcessor(video_path)
        processor.load_video()
        
        assert processor._is_loaded is True
        assert processor.capture is not None
        
        processor.release()
        
        assert processor._is_loaded is False, "Should be marked as not loaded after release"
        assert processor.capture is None, "Capture should be None after release"
        assert processor.current_frame_number == 0, "Frame number should be reset"
        
    finally:
        Path(video_path).unlink(missing_ok=True)


def test_context_manager(sample_video):
    """Test using VideoProcessor as a context manager."""
    video_path, width, height, fps, num_frames = sample_video
    
    with VideoProcessor(video_path) as processor:
        assert processor._is_loaded is True, "Should be loaded in context"
        
        frame = processor.get_next_frame()
        assert frame is not None, "Should be able to extract frames in context"
    
    # After exiting context, resources should be released
    assert processor._is_loaded is False, "Should be released after context exit"
    assert processor.capture is None, "Capture should be None after context exit"


def test_end_of_video(sample_video):
    """Test behavior when reaching end of video."""
    video_path, width, height, fps, num_frames = sample_video
    
    processor = VideoProcessor(video_path)
    processor.load_video()
    
    # Extract all frames
    frame_count = 0
    while True:
        frame = processor.get_next_frame()
        if frame is None:
            break
        frame_count += 1
    
    # Verify we extracted expected number of frames
    assert frame_count > 0, "Should extract at least one frame"
    
    # Verify subsequent calls return None
    frame = processor.get_next_frame()
    assert frame is None, "Should return None after video ends"
    
    processor.release()
