"""
Visualizer module for SMART FLOW traffic signal simulation system.

Handles rendering of detection results and signal states on video frames.
"""

import cv2
import numpy as np
from typing import List, Dict
from src.models import Frame, Detection, SignalState


class Visualizer:
    """
    Renders detection results and signal states on video frames.
    
    This class provides methods for drawing bounding boxes, signal state indicators,
    vehicle counts, and displaying the annotated frames in a window.
    """
    
    # Color coding for signal states (BGR format for OpenCV)
    SIGNAL_COLORS = {
        SignalState.GREEN: (0, 255, 0),      # #00FF00
        SignalState.YELLOW: (0, 255, 255),   # #FFFF00
        SignalState.RED: (0, 0, 255)         # #FF0000
    }
    
    # Color for bounding boxes (BGR format)
    BBOX_COLOR = (255, 0, 0)  # Blue
    
    def __init__(self):
        """Initialize the Visualizer."""
        self.window_name = "SMART FLOW - Traffic Signal Simulation"
        # Display size limits (can be overridden)
        self.max_display_width = 1280
        self.max_display_height = 720
    
    def draw_detections(self, frame: Frame, detections: List[Detection]) -> Frame:
        """
        Draw bounding boxes around detected vehicles on the frame.
        
        Args:
            frame: Frame object containing the image to annotate
            detections: List of Detection objects to draw
            
        Returns:
            Frame: New Frame object with bounding boxes drawn
        """
        # Create a copy of the image to avoid modifying the original
        annotated_image = frame.image.copy()
        
        for detection in detections:
            x, y, width, height = detection.bbox
            
            # Draw rectangle
            cv2.rectangle(
                annotated_image,
                (x, y),
                (x + width, y + height),
                self.BBOX_COLOR,
                2
            )
            
            # Draw label with class name and confidence
            label = f"{detection.class_name} {detection.confidence:.2f}"
            label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            
            # Draw label background
            cv2.rectangle(
                annotated_image,
                (x, y - label_size[1] - 5),
                (x + label_size[0], y),
                self.BBOX_COLOR,
                -1
            )
            
            # Draw label text
            cv2.putText(
                annotated_image,
                label,
                (x, y - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                1
            )
        
        return Frame(
            image=annotated_image,
            frame_number=frame.frame_number,
            timestamp=frame.timestamp
        )
    
    def draw_signal_states(
        self,
        frame: Frame,
        states: Dict[str, SignalState],
        remaining_times: Dict[str, float]
    ) -> Frame:
        """
        Draw signal state indicators with colored indicators and remaining time.
        
        Args:
            frame: Frame object containing the image to annotate
            states: Dictionary mapping lane names to current signal states
            remaining_times: Dictionary mapping lane names to remaining time in seconds
            
        Returns:
            Frame: New Frame object with signal states drawn
        """
        annotated_image = frame.image.copy()
        height, width = annotated_image.shape[:2]
        
        # Create a semi-transparent overlay for the signal panel
        overlay = annotated_image.copy()
        
        # Panel dimensions
        panel_height = 150
        panel_y = height - panel_height
        
        # Draw panel background
        cv2.rectangle(
            overlay,
            (0, panel_y),
            (width, height),
            (50, 50, 50),
            -1
        )
        
        # Blend overlay with original image
        alpha = 0.7
        cv2.addWeighted(overlay, alpha, annotated_image, 1 - alpha, 0, annotated_image)
        
        # Draw signal states for each lane
        lane_names = sorted(states.keys())
        num_lanes = len(lane_names)
        
        # Handle case where no lanes are configured yet
        if num_lanes == 0:
            return Frame(image=annotated_image, frame_number=frame.frame_number, timestamp=frame.timestamp)
        
        lane_width = width // num_lanes
        
        for i, lane in enumerate(lane_names):
            state = states[lane]
            remaining = remaining_times.get(lane, 0.0)
            
            # Calculate position for this lane
            x_start = i * lane_width
            x_center = x_start + lane_width // 2
            
            # Draw lane name
            lane_text = lane.capitalize()
            text_size, _ = cv2.getTextSize(lane_text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
            cv2.putText(
                annotated_image,
                lane_text,
                (x_center - text_size[0] // 2, panel_y + 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2
            )
            
            # Draw signal indicator (circle)
            signal_color = self.SIGNAL_COLORS[state]
            cv2.circle(
                annotated_image,
                (x_center, panel_y + 70),
                20,
                signal_color,
                -1
            )
            
            # Draw signal state text
            state_text = state.value.upper()
            text_size, _ = cv2.getTextSize(state_text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
            cv2.putText(
                annotated_image,
                state_text,
                (x_center - text_size[0] // 2, panel_y + 110),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2
            )
            
            # Draw remaining time if not red
            if state != SignalState.RED and remaining > 0:
                time_text = f"{int(remaining)}s"
                text_size, _ = cv2.getTextSize(time_text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
                cv2.putText(
                    annotated_image,
                    time_text,
                    (x_center - text_size[0] // 2, panel_y + 135),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (255, 255, 255),
                    1
                )
        
        return Frame(
            image=annotated_image,
            frame_number=frame.frame_number,
            timestamp=frame.timestamp
        )
    
    def draw_vehicle_counts(
        self,
        frame: Frame,
        counts: Dict[str, int]
    ) -> Frame:
        """
        Draw vehicle count text overlay for each lane.
        
        Args:
            frame: Frame object containing the image to annotate
            counts: Dictionary mapping lane names to vehicle counts
            
        Returns:
            Frame: New Frame object with vehicle counts drawn
        """
        annotated_image = frame.image.copy()
        height, width = annotated_image.shape[:2]
        
        # Draw counts in top-left corner
        y_offset = 30
        
        for lane in sorted(counts.keys()):
            count = counts[lane]
            text = f"{lane.capitalize()}: {count} vehicles"
            
            # Draw text background
            text_size, _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
            cv2.rectangle(
                annotated_image,
                (10, y_offset - text_size[1] - 5),
                (10 + text_size[0] + 10, y_offset + 5),
                (0, 0, 0),
                -1
            )
            
            # Draw text
            cv2.putText(
                annotated_image,
                text,
                (15, y_offset),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2
            )
            
            y_offset += 35
        
        return Frame(
            image=annotated_image,
            frame_number=frame.frame_number,
            timestamp=frame.timestamp
        )
    
    def display(self, frame: Frame) -> bool:
        """
        Display the frame in an OpenCV window.
        
        Args:
            frame: Frame object containing the image to display
            
        Returns:
            bool: False if user closed the window, True otherwise
        """
        # Resize frame to fit screen if it's too large
        display_image = frame.image
        height, width = display_image.shape[:2]
        
        # Use configured maximum display size
        max_width = getattr(self, 'max_display_width', 1280)
        max_height = getattr(self, 'max_display_height', 720)
        
        # Calculate scaling factor if image is too large
        if width > max_width or height > max_height:
            scale_w = max_width / width
            scale_h = max_height / height
            scale = min(scale_w, scale_h)
            
            new_width = int(width * scale)
            new_height = int(height * scale)
            display_image = cv2.resize(display_image, (new_width, new_height), 
                                      interpolation=cv2.INTER_AREA)
        
        cv2.imshow(self.window_name, display_image)
        
        # Wait for 1ms and check if window was closed
        key = cv2.waitKey(1)
        
        # Check if window was closed (ESC key or window close button)
        if key == 27 or cv2.getWindowProperty(self.window_name, cv2.WND_PROP_VISIBLE) < 1:
            return False
        
        return True
    
    def close(self) -> None:
        """Close all OpenCV windows and clean up resources."""
        try:
            cv2.destroyAllWindows()
        except cv2.error:
            # GUI functions may not be available in headless environments
            pass
