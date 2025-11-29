"""
Unit tests for StreamManager module.

Tests cover:
- File loading
- Webcam connection
- RTSP stream connection (mocked)
- YouTube URL parsing
- Reconnection logic

Requirements: 1.1, 1.2, 1.3, 1.4, 1.5
"""
import pytest
import numpy as np
import cv2
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from src.stream_manager import StreamManager, StreamMetadata, Frame


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


class TestStreamManagerFileLoading:
    """Test file loading functionality."""
    
    def test_detect_file_source_type(self, sample_video):
        """Test auto-detection of file source type."""
        video_path, _, _, _, _ = sample_video
        
        manager = StreamManager(video_path, source_type='auto')
        
        assert manager.source_type == 'file', "Should detect file source type"
    
    def test_load_valid_video_file(self, sample_video):
        """Test loading a valid video file."""
        video_path, width, height, fps, num_frames = sample_video
        
        manager = StreamManager(video_path, source_type='file')
        result = manager.connect()
        
        assert result is True, "Should successfully connect to valid video file"
        assert manager.is_connected is True, "Should be marked as connected"
        assert manager.capture is not None, "Capture should be initialized"
        
        manager.release()
    
    def test_load_missing_file(self):
        """Test error handling for missing video file."""
        manager = StreamManager("nonexistent_video.mp4", source_type='file')
        result = manager.connect()
        
        assert result is False, "Should fail to connect to missing file"
        assert manager.is_connected is False, "Should not be marked as connected"
    
    def test_is_live_returns_false_for_file(self, sample_video):
        """Test that file sources are not marked as live."""
        video_path, _, _, _, _ = sample_video
        
        manager = StreamManager(video_path, source_type='file')
        
        assert manager.is_live() is False, "File sources should not be live"
    
    def test_get_metadata_from_file(self, sample_video):
        """Test retrieving metadata from video file."""
        video_path, width, height, fps, num_frames = sample_video
        
        manager = StreamManager(video_path, source_type='file')
        manager.connect()
        
        metadata = manager.get_metadata()
        
        assert isinstance(metadata, StreamMetadata), "Should return StreamMetadata object"
        assert metadata.source == video_path, "Source should match"
        assert metadata.source_type == 'file', "Source type should be file"
        assert metadata.width == width, f"Width should be {width}"
        assert metadata.height == height, f"Height should be {height}"
        assert metadata.fps == fps, f"FPS should be {fps}"
        assert metadata.is_live is False, "File should not be live"
        
        manager.release()
    
    def test_get_next_frame_from_file(self, sample_video):
        """Test extracting frames from video file."""
        video_path, width, height, fps, num_frames = sample_video
        
        manager = StreamManager(video_path, source_type='file')
        manager.connect()
        
        frame = manager.get_next_frame()
        
        assert frame is not None, "Should extract first frame"
        assert isinstance(frame, Frame), "Should return Frame object"
        assert frame.frame_number == 1, "First frame should have frame_number 1"
        assert frame.image.shape == (height, width, 3), "Frame should have correct dimensions"
        assert frame.source_type == 'file', "Frame should have correct source type"
        assert frame.is_live is False, "Frame should not be marked as live"
        
        manager.release()
    
    def test_get_multiple_frames_from_file(self, sample_video):
        """Test extracting multiple frames in sequence."""
        video_path, width, height, fps, num_frames = sample_video
        
        manager = StreamManager(video_path, source_type='file')
        manager.connect()
        
        frames = []
        for _ in range(3):
            frame = manager.get_next_frame()
            if frame is not None:
                frames.append(frame)
        
        assert len(frames) == 3, "Should extract 3 frames"
        
        # Verify frame numbers are sequential
        for i, frame in enumerate(frames):
            assert frame.frame_number == i + 1, f"Frame {i} should have frame_number {i + 1}"
        
        manager.release()
    
    def test_file_end_returns_none(self, sample_video):
        """Test that None is returned when file ends."""
        video_path, _, _, _, num_frames = sample_video
        
        manager = StreamManager(video_path, source_type='file')
        manager.connect()
        
        # Extract all frames
        frame_count = 0
        while True:
            frame = manager.get_next_frame()
            if frame is None:
                break
            frame_count += 1
            if frame_count > num_frames + 5:  # Safety limit
                break
        
        # Verify we extracted frames
        assert frame_count > 0, "Should extract at least one frame"
        
        # Verify subsequent calls return None
        frame = manager.get_next_frame()
        assert frame is None, "Should return None after file ends"
        
        manager.release()


class TestStreamManagerWebcam:
    """Test webcam connection functionality."""
    
    def test_detect_webcam_source_type(self):
        """Test auto-detection of webcam source type."""
        manager = StreamManager("webcam:0", source_type='auto')
        
        assert manager.source_type == 'webcam', "Should detect webcam source type"
    
    def test_is_live_returns_true_for_webcam(self):
        """Test that webcam sources are marked as live."""
        manager = StreamManager("webcam:0", source_type='webcam')
        
        assert manager.is_live() is True, "Webcam sources should be live"
    
    @patch('cv2.VideoCapture')
    def test_connect_to_webcam(self, mock_video_capture):
        """Test connecting to webcam device."""
        # Mock successful webcam connection
        mock_capture = MagicMock()
        mock_capture.isOpened.return_value = True
        mock_video_capture.return_value = mock_capture
        
        manager = StreamManager("webcam:0", source_type='webcam')
        result = manager.connect()
        
        assert result is True, "Should successfully connect to webcam"
        assert manager.is_connected is True, "Should be marked as connected"
        mock_video_capture.assert_called_once_with(0)
        
        manager.release()
    
    @patch('cv2.VideoCapture')
    def test_connect_to_webcam_device_1(self, mock_video_capture):
        """Test connecting to webcam device 1."""
        # Mock successful webcam connection
        mock_capture = MagicMock()
        mock_capture.isOpened.return_value = True
        mock_video_capture.return_value = mock_capture
        
        manager = StreamManager("webcam:1", source_type='webcam')
        result = manager.connect()
        
        assert result is True, "Should successfully connect to webcam"
        mock_video_capture.assert_called_once_with(1)
        
        manager.release()
    
    @patch('cv2.VideoCapture')
    def test_webcam_connection_failure(self, mock_video_capture):
        """Test handling webcam connection failure."""
        # Mock failed webcam connection
        mock_capture = MagicMock()
        mock_capture.isOpened.return_value = False
        mock_video_capture.return_value = mock_capture
        
        manager = StreamManager("webcam:0", source_type='webcam')
        result = manager.connect()
        
        assert result is False, "Should fail to connect to unavailable webcam"
        assert manager.is_connected is False, "Should not be marked as connected"


class TestStreamManagerRTSP:
    """Test RTSP stream connection functionality (mocked)."""
    
    def test_detect_rtsp_source_type(self):
        """Test auto-detection of RTSP source type."""
        manager = StreamManager("rtsp://192.168.1.100/stream", source_type='auto')
        
        assert manager.source_type == 'rtsp', "Should detect RTSP source type"
    
    def test_is_live_returns_true_for_rtsp(self):
        """Test that RTSP sources are marked as live."""
        manager = StreamManager("rtsp://192.168.1.100/stream", source_type='rtsp')
        
        assert manager.is_live() is True, "RTSP sources should be live"
    
    @patch('cv2.VideoCapture')
    def test_connect_to_rtsp_stream(self, mock_video_capture):
        """Test connecting to RTSP stream."""
        # Mock successful RTSP connection
        mock_capture = MagicMock()
        mock_capture.isOpened.return_value = True
        mock_video_capture.return_value = mock_capture
        
        rtsp_url = "rtsp://192.168.1.100/stream"
        manager = StreamManager(rtsp_url, source_type='rtsp')
        result = manager.connect()
        
        assert result is True, "Should successfully connect to RTSP stream"
        assert manager.is_connected is True, "Should be marked as connected"
        mock_video_capture.assert_called_once_with(rtsp_url)
        
        manager.release()
    
    @patch('cv2.VideoCapture')
    def test_rtsp_connection_failure(self, mock_video_capture):
        """Test handling RTSP connection failure."""
        # Mock failed RTSP connection
        mock_capture = MagicMock()
        mock_capture.isOpened.return_value = False
        mock_video_capture.return_value = mock_capture
        
        manager = StreamManager("rtsp://192.168.1.100/stream", source_type='rtsp')
        result = manager.connect()
        
        assert result is False, "Should fail to connect to unavailable RTSP stream"
        assert manager.is_connected is False, "Should not be marked as connected"


class TestStreamManagerYouTube:
    """Test YouTube URL parsing and connection."""
    
    def test_detect_youtube_source_type(self):
        """Test auto-detection of YouTube source type."""
        manager = StreamManager("https://youtube.com/watch?v=test123", source_type='auto')
        
        assert manager.source_type == 'youtube', "Should detect YouTube source type"
    
    def test_detect_youtube_short_url(self):
        """Test auto-detection of YouTube short URL."""
        manager = StreamManager("https://youtu.be/test123", source_type='auto')
        
        assert manager.source_type == 'youtube', "Should detect YouTube short URL"
    
    def test_is_live_returns_true_for_youtube(self):
        """Test that YouTube sources are marked as live."""
        manager = StreamManager("https://youtube.com/watch?v=test123", source_type='youtube')
        
        assert manager.is_live() is True, "YouTube sources should be live"
    
    @patch('cv2.VideoCapture')
    def test_connect_to_youtube_stream(self, mock_video_capture):
        """Test connecting to YouTube stream."""
        # Mock yt-dlp module and extraction
        mock_ydl_instance = MagicMock()
        mock_ydl_instance.extract_info.return_value = {
            'url': 'https://manifest.googlevideo.com/test_stream'
        }
        
        mock_yt_dlp_class = MagicMock()
        mock_yt_dlp_class.return_value.__enter__.return_value = mock_ydl_instance
        
        # Mock successful video capture
        mock_capture = MagicMock()
        mock_capture.isOpened.return_value = True
        mock_video_capture.return_value = mock_capture
        
        youtube_url = "https://youtube.com/watch?v=test123"
        
        # Mock the yt_dlp import
        with patch.dict('sys.modules', {'yt_dlp': MagicMock(YoutubeDL=mock_yt_dlp_class)}):
            manager = StreamManager(youtube_url, source_type='youtube')
            result = manager.connect()
            
            assert result is True, "Should successfully connect to YouTube stream"
            assert manager.is_connected is True, "Should be marked as connected"
            mock_ydl_instance.extract_info.assert_called_once_with(youtube_url, download=False)
            
            manager.release()
    
    def test_youtube_connection_without_yt_dlp(self):
        """Test YouTube connection when yt-dlp is not available."""
        youtube_url = "https://youtube.com/watch?v=test123"
        
        # Mock the import to raise ImportError
        with patch.dict('sys.modules', {'yt_dlp': None}):
            manager = StreamManager(youtube_url, source_type='youtube')
            result = manager.connect()
            
            # Should fail gracefully when yt-dlp is not installed
            assert result is False, "Should fail when yt-dlp is not available"


class TestStreamManagerReconnection:
    """Test reconnection logic for live streams."""
    
    @patch('cv2.VideoCapture')
    @patch('time.sleep')
    def test_reconnect_to_live_stream(self, mock_sleep, mock_video_capture):
        """Test reconnection to live stream after failure."""
        # First connection succeeds
        mock_capture_1 = MagicMock()
        mock_capture_1.isOpened.return_value = True
        
        # Second connection (after reconnect) also succeeds
        mock_capture_2 = MagicMock()
        mock_capture_2.isOpened.return_value = True
        
        mock_video_capture.side_effect = [mock_capture_1, mock_capture_2]
        
        manager = StreamManager("rtsp://192.168.1.100/stream", source_type='rtsp')
        manager.connect()
        
        # Simulate connection loss
        manager.is_connected = False
        
        # Attempt reconnection
        result = manager.reconnect()
        
        assert result is True, "Should successfully reconnect"
        assert manager.is_connected is True, "Should be marked as connected"
        assert manager.retry_count == 0, "Retry count should be reset on success"
        # Sleep may or may not be called depending on timing, so we just verify reconnection worked
        
        manager.release()
    
    @patch('cv2.VideoCapture')
    @patch('time.sleep')
    def test_reconnect_exponential_backoff(self, mock_sleep, mock_video_capture):
        """Test exponential backoff during reconnection attempts."""
        # All connections fail
        mock_capture = MagicMock()
        mock_capture.isOpened.return_value = False
        mock_video_capture.return_value = mock_capture
        
        manager = StreamManager("rtsp://192.168.1.100/stream", source_type='rtsp')
        manager.connect()  # Initial connection fails
        
        # Reset last_connection_attempt to ensure backoff is triggered
        manager.last_connection_attempt = 0
        
        # Attempt multiple reconnections
        for i in range(3):
            manager.reconnect()
        
        # Verify retry attempts were made
        assert manager.retry_count == 3, "Should have 3 retry attempts"
        # Sleep should be called for backoff delays
        assert mock_sleep.call_count >= 1, "Should have waited at least once"
    
    @patch('cv2.VideoCapture')
    def test_reconnect_max_retries(self, mock_video_capture):
        """Test that reconnection stops after max retries."""
        # All connections fail
        mock_capture = MagicMock()
        mock_capture.isOpened.return_value = False
        mock_video_capture.return_value = mock_capture
        
        manager = StreamManager("rtsp://192.168.1.100/stream", source_type='rtsp')
        manager.connect()
        
        # Exhaust all retry attempts
        for _ in range(StreamManager.MAX_RETRIES):
            manager.reconnect()
        
        # Next reconnection should fail immediately
        result = manager.reconnect()
        
        assert result is False, "Should fail after max retries"
        assert manager.retry_count >= StreamManager.MAX_RETRIES, "Should have reached max retries"
    
    def test_reconnect_not_supported_for_files(self, sample_video):
        """Test that reconnection is not supported for file sources."""
        video_path, _, _, _, _ = sample_video
        
        manager = StreamManager(video_path, source_type='file')
        manager.connect()
        
        result = manager.reconnect()
        
        assert result is False, "Reconnection should not be supported for files"
    
    @patch('cv2.VideoCapture')
    def test_get_next_frame_with_reconnection(self, mock_video_capture):
        """Test that get_next_frame attempts reconnection on failure."""
        # First capture succeeds initially, then fails
        mock_capture_1 = MagicMock()
        mock_capture_1.isOpened.return_value = True
        mock_capture_1.read.side_effect = [(False, None), (True, np.zeros((240, 320, 3), dtype=np.uint8))]
        
        # Second capture (after reconnect) succeeds
        mock_capture_2 = MagicMock()
        mock_capture_2.isOpened.return_value = True
        mock_capture_2.read.return_value = (True, np.zeros((240, 320, 3), dtype=np.uint8))
        
        mock_video_capture.side_effect = [mock_capture_1, mock_capture_2]
        
        manager = StreamManager("rtsp://192.168.1.100/stream", source_type='rtsp')
        manager.connect()
        
        # First read fails, should trigger reconnection
        with patch('time.sleep'):  # Skip sleep delays
            frame = manager.get_next_frame()
        
        # Should have reconnected and returned a frame
        assert frame is not None, "Should return frame after reconnection"
        
        manager.release()


class TestStreamManagerConnectionHealth:
    """Test connection health monitoring."""
    
    def test_get_connection_health_disconnected(self):
        """Test health metrics when disconnected."""
        manager = StreamManager("rtsp://192.168.1.100/stream", source_type='rtsp')
        
        health = manager.get_connection_health()
        
        assert health['is_connected'] is False, "Should report as disconnected"
        assert health['retry_count'] == 0, "Should have 0 retries"
        assert health['frames_processed'] == 0, "Should have 0 frames processed"
        assert health['source_type'] == 'rtsp', "Should report correct source type"
        assert health['is_live'] is True, "Should report as live stream"
        assert health['capture_opened'] is False, "Capture should not be opened"
    
    @patch('cv2.VideoCapture')
    def test_get_connection_health_connected(self, mock_video_capture):
        """Test health metrics when connected."""
        mock_capture = MagicMock()
        mock_capture.isOpened.return_value = True
        mock_video_capture.return_value = mock_capture
        
        manager = StreamManager("rtsp://192.168.1.100/stream", source_type='rtsp')
        manager.connect()
        
        health = manager.get_connection_health()
        
        assert health['is_connected'] is True, "Should report as connected"
        assert health['capture_opened'] is True, "Capture should be opened"
        
        manager.release()


class TestStreamManagerRelease:
    """Test resource cleanup."""
    
    def test_release_clears_resources(self, sample_video):
        """Test that release properly clears all resources."""
        video_path, _, _, _, _ = sample_video
        
        manager = StreamManager(video_path, source_type='file')
        manager.connect()
        manager.get_next_frame()
        
        assert manager.is_connected is True
        assert manager.capture is not None
        assert manager.frame_number > 0
        
        manager.release()
        
        assert manager.is_connected is False, "Should be marked as disconnected"
        assert manager.capture is None, "Capture should be None"
        assert len(manager.frame_buffer) == 0, "Frame buffer should be cleared"
    
    @patch('cv2.VideoCapture')
    def test_release_for_live_stream(self, mock_video_capture):
        """Test release for live stream with buffered frames."""
        mock_capture = MagicMock()
        mock_capture.isOpened.return_value = True
        mock_capture.read.return_value = (True, np.zeros((240, 320, 3), dtype=np.uint8))
        mock_video_capture.return_value = mock_capture
        
        manager = StreamManager("rtsp://192.168.1.100/stream", source_type='rtsp')
        manager.connect()
        
        # Get some frames to populate buffer
        for _ in range(5):
            manager.get_next_frame()
        
        assert len(manager.frame_buffer) > 0, "Buffer should have frames"
        
        manager.release()
        
        assert len(manager.frame_buffer) == 0, "Buffer should be cleared"
        mock_capture.release.assert_called_once()
