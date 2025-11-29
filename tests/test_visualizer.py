"""
Unit tests for Visualizer module.
"""
import numpy as np
import pytest
from src.visualizer import Visualizer
from src.models import Frame, Detection, SignalState


class TestVisualizer:
    """Unit tests for the Visualizer class."""
    
    def test_draw_detections_with_bounding_boxes(self):
        """
        Test that bounding boxes are rendered for all detections.
        
        Requirements: 6.1
        """
        # Create a test frame
        image = np.zeros((480, 640, 3), dtype=np.uint8)
        frame = Frame(image=image, frame_number=0, timestamp=0.0)
        
        # Create test detections
        detections = [
            Detection(bbox=(100, 100, 50, 50), confidence=0.9, class_name='car', lane='north'),
            Detection(bbox=(200, 200, 60, 60), confidence=0.85, class_name='truck', lane='south'),
            Detection(bbox=(300, 150, 40, 40), confidence=0.95, class_name='bus', lane='east')
        ]
        
        # Create visualizer and draw detections
        visualizer = Visualizer()
        result_frame = visualizer.draw_detections(frame, detections)
        
        # Verify that the frame was modified
        assert result_frame is not None
        assert result_frame.image is not None
        assert result_frame.image.shape == frame.image.shape
        
        # Verify that something was drawn (image is no longer all zeros)
        assert np.any(result_frame.image > 0), "Bounding boxes should be drawn on the image"
        
        # Verify frame metadata is preserved
        assert result_frame.frame_number == frame.frame_number
        assert result_frame.timestamp == frame.timestamp
    
    def test_draw_detections_empty_list(self):
        """
        Test that drawing with no detections doesn't crash.
        
        Requirements: 6.1
        """
        # Create a test frame
        image = np.zeros((480, 640, 3), dtype=np.uint8)
        frame = Frame(image=image, frame_number=0, timestamp=0.0)
        
        # Create visualizer and draw empty detections list
        visualizer = Visualizer()
        result_frame = visualizer.draw_detections(frame, [])
        
        # Verify that the frame is returned unchanged
        assert result_frame is not None
        assert result_frame.image.shape == frame.image.shape
        assert result_frame.frame_number == frame.frame_number
        assert result_frame.timestamp == frame.timestamp
    
    def test_draw_signal_states_with_colored_indicators(self):
        """
        Test that signal states are displayed with correct colors.
        
        Requirements: 6.2, 6.3
        """
        # Create a test frame
        image = np.zeros((600, 800, 3), dtype=np.uint8)
        frame = Frame(image=image, frame_number=0, timestamp=0.0)
        
        # Create signal states (one green, rest red)
        states = {
            'north': SignalState.GREEN,
            'south': SignalState.RED,
            'east': SignalState.RED,
            'west': SignalState.RED
        }
        
        remaining_times = {
            'north': 25.0,
            'south': 0.0,
            'east': 0.0,
            'west': 0.0
        }
        
        # Create visualizer and draw signal states
        visualizer = Visualizer()
        result_frame = visualizer.draw_signal_states(frame, states, remaining_times)
        
        # Verify that the frame was modified
        assert result_frame is not None
        assert result_frame.image is not None
        assert result_frame.image.shape == frame.image.shape
        
        # Verify that something was drawn
        assert np.any(result_frame.image > 0), "Signal states should be drawn on the image"
        
        # Verify that green color is present (0, 255, 0) in BGR
        green_pixels = np.any((result_frame.image[:, :, 0] == 0) & 
                             (result_frame.image[:, :, 1] == 255) & 
                             (result_frame.image[:, :, 2] == 0))
        assert green_pixels, "Green signal color should be present in the image"
        
        # Verify frame metadata is preserved
        assert result_frame.frame_number == frame.frame_number
        assert result_frame.timestamp == frame.timestamp
    
    def test_draw_signal_states_all_red(self):
        """
        Test that all red signals are displayed correctly.
        
        Requirements: 6.2
        """
        # Create a test frame
        image = np.zeros((600, 800, 3), dtype=np.uint8)
        frame = Frame(image=image, frame_number=0, timestamp=0.0)
        
        # Create signal states (all red)
        states = {
            'north': SignalState.RED,
            'south': SignalState.RED,
            'east': SignalState.RED,
            'west': SignalState.RED
        }
        
        remaining_times = {
            'north': 0.0,
            'south': 0.0,
            'east': 0.0,
            'west': 0.0
        }
        
        # Create visualizer and draw signal states
        visualizer = Visualizer()
        result_frame = visualizer.draw_signal_states(frame, states, remaining_times)
        
        # Verify that the frame was modified
        assert result_frame is not None
        assert np.any(result_frame.image > 0), "Signal states should be drawn"
        
        # Verify that red color is present (0, 0, 255) in BGR
        red_pixels = np.any((result_frame.image[:, :, 0] == 0) & 
                           (result_frame.image[:, :, 1] == 0) & 
                           (result_frame.image[:, :, 2] == 255))
        assert red_pixels, "Red signal color should be present in the image"
    
    def test_draw_signal_states_yellow_transition(self):
        """
        Test that yellow signal state is displayed correctly.
        
        Requirements: 6.2
        """
        # Create a test frame
        image = np.zeros((600, 800, 3), dtype=np.uint8)
        frame = Frame(image=image, frame_number=0, timestamp=0.0)
        
        # Create signal states (one yellow, rest red)
        states = {
            'north': SignalState.YELLOW,
            'south': SignalState.RED,
            'east': SignalState.RED,
            'west': SignalState.RED
        }
        
        remaining_times = {
            'north': 2.5,
            'south': 0.0,
            'east': 0.0,
            'west': 0.0
        }
        
        # Create visualizer and draw signal states
        visualizer = Visualizer()
        result_frame = visualizer.draw_signal_states(frame, states, remaining_times)
        
        # Verify that the frame was modified
        assert result_frame is not None
        assert np.any(result_frame.image > 0), "Signal states should be drawn"
        
        # Verify that yellow color is present (0, 255, 255) in BGR
        yellow_pixels = np.any((result_frame.image[:, :, 0] == 0) & 
                              (result_frame.image[:, :, 1] == 255) & 
                              (result_frame.image[:, :, 2] == 255))
        assert yellow_pixels, "Yellow signal color should be present in the image"
    
    def test_draw_vehicle_counts_overlay(self):
        """
        Test that vehicle counts are displayed as text overlay.
        
        Requirements: 6.3
        """
        # Create a test frame
        image = np.zeros((600, 800, 3), dtype=np.uint8)
        frame = Frame(image=image, frame_number=0, timestamp=0.0)
        
        # Create vehicle counts
        counts = {
            'north': 12,
            'south': 8,
            'east': 15,
            'west': 5
        }
        
        # Create visualizer and draw vehicle counts
        visualizer = Visualizer()
        result_frame = visualizer.draw_vehicle_counts(frame, counts)
        
        # Verify that the frame was modified
        assert result_frame is not None
        assert result_frame.image is not None
        assert result_frame.image.shape == frame.image.shape
        
        # Verify that something was drawn
        assert np.any(result_frame.image > 0), "Vehicle counts should be drawn on the image"
        
        # Verify frame metadata is preserved
        assert result_frame.frame_number == frame.frame_number
        assert result_frame.timestamp == frame.timestamp
    
    def test_draw_vehicle_counts_zero_vehicles(self):
        """
        Test that zero vehicle counts are displayed correctly.
        
        Requirements: 6.3
        """
        # Create a test frame
        image = np.zeros((600, 800, 3), dtype=np.uint8)
        frame = Frame(image=image, frame_number=0, timestamp=0.0)
        
        # Create vehicle counts (all zero)
        counts = {
            'north': 0,
            'south': 0,
            'east': 0,
            'west': 0
        }
        
        # Create visualizer and draw vehicle counts
        visualizer = Visualizer()
        result_frame = visualizer.draw_vehicle_counts(frame, counts)
        
        # Verify that the frame was modified (text is still drawn even with zero counts)
        assert result_frame is not None
        assert np.any(result_frame.image > 0), "Count labels should be drawn even with zero counts"
    
    def test_combined_visualization(self):
        """
        Test that all visualization elements can be combined on one frame.
        
        Requirements: 6.1, 6.2, 6.3
        """
        # Create a test frame
        image = np.zeros((600, 800, 3), dtype=np.uint8)
        frame = Frame(image=image, frame_number=0, timestamp=0.0)
        
        # Create test data
        detections = [
            Detection(bbox=(100, 100, 50, 50), confidence=0.9, class_name='car', lane='north'),
            Detection(bbox=(200, 200, 60, 60), confidence=0.85, class_name='truck', lane='south')
        ]
        
        counts = {
            'north': 12,
            'south': 8,
            'east': 15,
            'west': 5
        }
        
        states = {
            'north': SignalState.GREEN,
            'south': SignalState.RED,
            'east': SignalState.RED,
            'west': SignalState.RED
        }
        
        remaining_times = {
            'north': 20.0,
            'south': 0.0,
            'east': 0.0,
            'west': 0.0
        }
        
        # Create visualizer and apply all visualizations
        visualizer = Visualizer()
        result_frame = visualizer.draw_detections(frame, detections)
        result_frame = visualizer.draw_vehicle_counts(result_frame, counts)
        result_frame = visualizer.draw_signal_states(result_frame, states, remaining_times)
        
        # Verify that the final frame has all elements
        assert result_frame is not None
        assert result_frame.image is not None
        assert result_frame.image.shape == frame.image.shape
        
        # Verify that the image has been significantly modified
        difference = np.sum(np.abs(result_frame.image.astype(int) - frame.image.astype(int)))
        assert difference > 1000, "Combined visualization should significantly modify the image"
        
        # Verify frame metadata is preserved
        assert result_frame.frame_number == frame.frame_number
        assert result_frame.timestamp == frame.timestamp
