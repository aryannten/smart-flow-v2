"""
Enhanced Visualizer module for SMART FLOW v2 traffic signal simulation system.

Provides advanced visualization features including heatmaps, trajectories, queue visualization,
enhanced signal panels, metrics overlays, and multi-camera layouts.
"""

import cv2
import numpy as np
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass

# Import from existing modules
from src.models import Frame, SignalState, SignalPhase, PhaseType
from src.visualizer import Visualizer


# Import enhanced detection types
try:
    from src.enhanced_detector import DetectionResult, TrackedObject
except ImportError:
    # Fallback definitions if enhanced_detector not available
    @dataclass
    class DetectionResult:
        vehicles: List[Any]
        pedestrians: List[Any]
        emergency_vehicles: List[Any]
        timestamp: float
    
    @dataclass
    class TrackedObject:
        object_id: int
        detection: Any
        trajectory: List[Tuple[int, int]]
        velocity: Tuple[float, float]
        age: int


# Import queue metrics
try:
    from src.queue_estimator import QueueMetrics
except ImportError:
    # Fallback definition
    @dataclass
    class QueueMetrics:
        length_meters: float
        vehicle_count: int
        density: float
        head_position: Tuple[int, int]
        tail_position: Tuple[int, int]
        is_spillback: bool


class EnhancedVisualizer(Visualizer):
    """
    Enhanced visualizer with advanced features for SMART FLOW v2.
    
    Extends the base Visualizer with:
    - Traffic density heatmaps
    - Vehicle trajectory visualization
    - Queue visualization
    - Enhanced signal panel with phase information
    - Comprehensive metrics overlay
    - Split-view and multi-camera layouts
    """
    
    # Color schemes for heatmap (BGR format)
    HEATMAP_COLORS = {
        'low': (0, 255, 0),      # Green - light traffic
        'medium': (0, 255, 255),  # Yellow - moderate traffic
        'high': (0, 165, 255),    # Orange - heavy traffic
        'critical': (0, 0, 255)   # Red - critical congestion
    }
    
    # Trajectory colors (BGR format)
    TRAJECTORY_COLOR = (255, 128, 0)  # Cyan-blue
    TRAJECTORY_THICKNESS = 2
    
    # Queue visualization colors
    QUEUE_COLOR = (0, 0, 255)  # Red
    QUEUE_HEAD_COLOR = (0, 255, 255)  # Yellow
    
    def __init__(self, enable_heatmap: bool = True, enable_trajectories: bool = True):
        """
        Initialize the EnhancedVisualizer.
        
        Args:
            enable_heatmap: Whether to enable heatmap visualization
            enable_trajectories: Whether to enable trajectory visualization
        """
        super().__init__()
        self.enable_heatmap = enable_heatmap
        self.enable_trajectories = enable_trajectories
        self.window_name = "SMART FLOW v2 - Enhanced Traffic Visualization"
        
        # Display size limits (can be overridden)
        self.max_display_width = 1280
        self.max_display_height = 720
        
        # Heatmap accumulator for temporal smoothing
        self.heatmap_accumulator: Optional[np.ndarray] = None
        self.heatmap_alpha = 0.7  # Blending factor for temporal smoothing
    
    def draw_detections_enhanced(
        self,
        frame: Frame,
        result: DetectionResult
    ) -> Frame:
        """
        Draw enhanced detection visualization with vehicle types and emergency indicators.
        
        Args:
            frame: Frame object containing the image
            result: DetectionResult with vehicles, pedestrians, and emergency vehicles
            
        Returns:
            Frame with enhanced detection visualization
        """
        annotated_image = frame.image.copy()
        
        # Draw regular vehicles in blue
        for detection in result.vehicles:
            self._draw_detection_box(annotated_image, detection, (255, 0, 0), "Vehicle")
        
        # Draw pedestrians in green
        for detection in result.pedestrians:
            self._draw_detection_box(annotated_image, detection, (0, 255, 0), "Pedestrian")
        
        # Draw emergency vehicles in red with special indicator
        for detection in result.emergency_vehicles:
            self._draw_detection_box(annotated_image, detection, (0, 0, 255), "EMERGENCY", bold=True)
        
        return Frame(
            image=annotated_image,
            frame_number=frame.frame_number,
            timestamp=frame.timestamp
        )
    
    def _draw_detection_box(
        self,
        image: np.ndarray,
        detection: Any,
        color: Tuple[int, int, int],
        label_prefix: str,
        bold: bool = False
    ) -> None:
        """Helper method to draw a detection bounding box."""
        x, y, width, height = detection.bbox
        
        # Draw rectangle
        thickness = 3 if bold else 2
        cv2.rectangle(image, (x, y), (x + width, y + height), color, thickness)
        
        # Draw label
        label = f"{label_prefix} {detection.confidence:.2f}"
        font_scale = 0.6 if bold else 0.5
        font_thickness = 2 if bold else 1
        
        label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, font_scale, font_thickness)
        
        # Draw label background
        cv2.rectangle(
            image,
            (x, y - label_size[1] - 5),
            (x + label_size[0], y),
            color,
            -1
        )
        
        # Draw label text
        cv2.putText(
            image,
            label,
            (x, y - 5),
            cv2.FONT_HERSHEY_SIMPLEX,
            font_scale,
            (255, 255, 255),
            font_thickness
        )
    
    def draw_heatmap(
        self,
        frame: Frame,
        density_data: Dict[str, float]
    ) -> Frame:
        """
        Draw traffic density heatmap overlay on the frame.
        
        Args:
            frame: Frame object containing the image
            density_data: Dictionary mapping lane names to density values (0.0 to 1.0)
            
        Returns:
            Frame with heatmap overlay
        """
        if not self.enable_heatmap:
            return frame
        
        annotated_image = frame.image.copy()
        height, width = annotated_image.shape[:2]
        
        # Initialize heatmap accumulator if needed
        if self.heatmap_accumulator is None:
            self.heatmap_accumulator = np.zeros((height, width, 3), dtype=np.float32)
        
        # Create current heatmap
        current_heatmap = np.zeros((height, width, 3), dtype=np.float32)
        
        # Map density to colors for each region
        # For simplicity, divide frame into quadrants for each lane
        for lane_name, density in density_data.items():
            color = self._get_heatmap_color(density)
            region = self._get_lane_region(lane_name, width, height)
            
            if region:
                x, y, w, h = region
                current_heatmap[y:y+h, x:x+w] = color
        
        # Temporal smoothing
        self.heatmap_accumulator = (
            self.heatmap_alpha * current_heatmap +
            (1 - self.heatmap_alpha) * self.heatmap_accumulator
        )
        
        # Convert to uint8 and blend with original image
        heatmap_uint8 = self.heatmap_accumulator.astype(np.uint8)
        blended = cv2.addWeighted(annotated_image, 0.7, heatmap_uint8, 0.3, 0)
        
        return Frame(
            image=blended,
            frame_number=frame.frame_number,
            timestamp=frame.timestamp
        )
    
    def _get_heatmap_color(self, density: float) -> Tuple[float, float, float]:
        """
        Get heatmap color based on density value.
        
        Args:
            density: Density value from 0.0 (empty) to 1.0 (critical)
            
        Returns:
            BGR color tuple as floats
        """
        if density < 0.25:
            return self.HEATMAP_COLORS['low']
        elif density < 0.5:
            return self.HEATMAP_COLORS['medium']
        elif density < 0.75:
            return self.HEATMAP_COLORS['high']
        else:
            return self.HEATMAP_COLORS['critical']
    
    def _get_lane_region(
        self,
        lane_name: str,
        width: int,
        height: int
    ) -> Optional[Tuple[int, int, int, int]]:
        """
        Get region coordinates for a lane (simplified quadrant mapping).
        
        Args:
            lane_name: Name of the lane
            width: Frame width
            height: Frame height
            
        Returns:
            Tuple of (x, y, width, height) or None
        """
        half_w = width // 2
        half_h = height // 2
        
        regions = {
            'north': (0, 0, half_w, half_h),
            'south': (half_w, half_h, half_w, half_h),
            'east': (half_w, 0, half_w, half_h),
            'west': (0, half_h, half_w, half_h)
        }
        
        return regions.get(lane_name.lower())
    
    def draw_trajectories(
        self,
        frame: Frame,
        tracked_objects: List[TrackedObject]
    ) -> Frame:
        """
        Draw vehicle trajectories showing their paths through the intersection.
        
        Args:
            frame: Frame object containing the image
            tracked_objects: List of TrackedObject instances with trajectory data
            
        Returns:
            Frame with trajectory visualization
        """
        if not self.enable_trajectories:
            return frame
        
        annotated_image = frame.image.copy()
        
        for obj in tracked_objects:
            if len(obj.trajectory) < 2:
                continue
            
            # Draw trajectory line
            points = np.array(obj.trajectory, dtype=np.int32)
            cv2.polylines(
                annotated_image,
                [points],
                isClosed=False,
                color=self.TRAJECTORY_COLOR,
                thickness=self.TRAJECTORY_THICKNESS
            )
            
            # Draw direction arrow at the end
            if len(obj.trajectory) >= 2:
                pt1 = obj.trajectory[-2]
                pt2 = obj.trajectory[-1]
                cv2.arrowedLine(
                    annotated_image,
                    pt1,
                    pt2,
                    self.TRAJECTORY_COLOR,
                    self.TRAJECTORY_THICKNESS,
                    tipLength=0.3
                )
            
            # Draw object ID at current position
            if obj.trajectory:
                pos = obj.trajectory[-1]
                cv2.putText(
                    annotated_image,
                    f"ID:{obj.object_id}",
                    (pos[0] + 5, pos[1] - 5),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.4,
                    self.TRAJECTORY_COLOR,
                    1
                )
        
        return Frame(
            image=annotated_image,
            frame_number=frame.frame_number,
            timestamp=frame.timestamp
        )
    
    def draw_queue_visualization(
        self,
        frame: Frame,
        queue_metrics: Dict[str, QueueMetrics]
    ) -> Frame:
        """
        Draw queue visualization showing queue extent and spillback warnings.
        
        Args:
            frame: Frame object containing the image
            queue_metrics: Dictionary mapping lane names to QueueMetrics
            
        Returns:
            Frame with queue visualization
        """
        annotated_image = frame.image.copy()
        
        for lane_name, metrics in queue_metrics.items():
            if metrics.vehicle_count == 0:
                continue
            
            # Draw line from head to tail
            cv2.line(
                annotated_image,
                metrics.head_position,
                metrics.tail_position,
                self.QUEUE_COLOR,
                3
            )
            
            # Draw queue head marker
            cv2.circle(
                annotated_image,
                metrics.head_position,
                8,
                self.QUEUE_HEAD_COLOR,
                -1
            )
            
            # Draw queue tail marker
            cv2.circle(
                annotated_image,
                metrics.tail_position,
                8,
                self.QUEUE_COLOR,
                -1
            )
            
            # Draw queue length text
            mid_x = (metrics.head_position[0] + metrics.tail_position[0]) // 2
            mid_y = (metrics.head_position[1] + metrics.tail_position[1]) // 2
            
            queue_text = f"{metrics.length_meters:.1f}m ({metrics.vehicle_count}v)"
            cv2.putText(
                annotated_image,
                queue_text,
                (mid_x, mid_y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                2
            )
            
            # Draw spillback warning if applicable
            if metrics.is_spillback:
                cv2.putText(
                    annotated_image,
                    "SPILLBACK!",
                    (mid_x, mid_y - 20),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 0, 255),
                    2
                )
        
        return Frame(
            image=annotated_image,
            frame_number=frame.frame_number,
            timestamp=frame.timestamp
        )
    
    def draw_signal_panel(
        self,
        frame: Frame,
        states: Dict[str, SignalState],
        phases: List[SignalPhase],
        remaining_times: Optional[Dict[str, float]] = None
    ) -> Frame:
        """
        Draw enhanced signal panel with phase information.
        
        Args:
            frame: Frame object containing the image
            states: Dictionary mapping lane names to current signal states
            phases: List of SignalPhase objects in the current cycle
            remaining_times: Optional dictionary of remaining times per lane
            
        Returns:
            Frame with enhanced signal panel
        """
        annotated_image = frame.image.copy()
        height, width = annotated_image.shape[:2]
        
        if remaining_times is None:
            remaining_times = {}
        
        # Create semi-transparent overlay
        overlay = annotated_image.copy()
        
        # Panel dimensions
        panel_height = 180
        panel_y = height - panel_height
        
        # Draw panel background
        cv2.rectangle(overlay, (0, panel_y), (width, height), (40, 40, 40), -1)
        
        # Blend overlay
        alpha = 0.75
        cv2.addWeighted(overlay, alpha, annotated_image, 1 - alpha, 0, annotated_image)
        
        # Draw title
        cv2.putText(
            annotated_image,
            "Signal Status",
            (10, panel_y + 25),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )
        
        # Draw current phase information
        if phases:
            current_phase = phases[0]  # Assume first phase is current
            phase_text = f"Phase: {current_phase.phase_type.value.replace('_', ' ').title()}"
            cv2.putText(
                annotated_image,
                phase_text,
                (10, panel_y + 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (200, 200, 200),
                1
            )
        
        # Draw signal states for each lane
        lane_names = sorted(states.keys())
        num_lanes = len(lane_names)
        
        if num_lanes == 0:
            return Frame(image=annotated_image, frame_number=frame.frame_number, timestamp=frame.timestamp)
        
        lane_width = width // num_lanes
        
        for i, lane in enumerate(lane_names):
            state = states[lane]
            remaining = remaining_times.get(lane, 0.0)
            
            x_start = i * lane_width
            x_center = x_start + lane_width // 2
            
            # Draw lane name
            lane_text = lane.capitalize()
            text_size, _ = cv2.getTextSize(lane_text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
            cv2.putText(
                annotated_image,
                lane_text,
                (x_center - text_size[0] // 2, panel_y + 85),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2
            )
            
            # Draw signal indicator
            signal_color = self.SIGNAL_COLORS[state]
            cv2.circle(annotated_image, (x_center, panel_y + 115), 18, signal_color, -1)
            cv2.circle(annotated_image, (x_center, panel_y + 115), 18, (255, 255, 255), 2)
            
            # Draw state text
            state_text = state.value.upper()
            text_size, _ = cv2.getTextSize(state_text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            cv2.putText(
                annotated_image,
                state_text,
                (x_center - text_size[0] // 2, panel_y + 150),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                1
            )
            
            # Draw remaining time
            if remaining > 0:
                time_text = f"{int(remaining)}s"
                text_size, _ = cv2.getTextSize(time_text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
                cv2.putText(
                    annotated_image,
                    time_text,
                    (x_center - text_size[0] // 2, panel_y + 170),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (200, 200, 200),
                    1
                )
        
        return Frame(
            image=annotated_image,
            frame_number=frame.frame_number,
            timestamp=frame.timestamp
        )
    
    def draw_metrics_overlay(
        self,
        frame: Frame,
        metrics: Dict[str, Any]
    ) -> Frame:
        """
        Draw comprehensive metrics overlay on the frame.
        
        Args:
            frame: Frame object containing the image
            metrics: Dictionary of metrics to display
            
        Returns:
            Frame with metrics overlay
        """
        annotated_image = frame.image.copy()
        height, width = annotated_image.shape[:2]
        
        # Create semi-transparent background for metrics
        overlay = annotated_image.copy()
        metrics_width = 300
        metrics_height = min(400, height - 200)
        
        cv2.rectangle(
            overlay,
            (width - metrics_width - 10, 10),
            (width - 10, 10 + metrics_height),
            (30, 30, 30),
            -1
        )
        
        # Blend overlay
        alpha = 0.7
        cv2.addWeighted(overlay, alpha, annotated_image, 1 - alpha, 0, annotated_image)
        
        # Draw metrics title
        y_offset = 35
        cv2.putText(
            annotated_image,
            "System Metrics",
            (width - metrics_width + 10, y_offset),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )
        
        y_offset += 30
        
        # Draw each metric
        for key, value in metrics.items():
            # Format the key (convert snake_case to Title Case)
            display_key = key.replace('_', ' ').title()
            
            # Format the value
            if isinstance(value, float):
                display_value = f"{value:.2f}"
            else:
                display_value = str(value)
            
            metric_text = f"{display_key}: {display_value}"
            
            cv2.putText(
                annotated_image,
                metric_text,
                (width - metrics_width + 20, y_offset),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (200, 200, 200),
                1
            )
            
            y_offset += 25
            
            # Stop if we run out of space
            if y_offset > 10 + metrics_height - 20:
                break
        
        return Frame(
            image=annotated_image,
            frame_number=frame.frame_number,
            timestamp=frame.timestamp
        )
    
    def create_split_view(
        self,
        frames: List[Frame],
        layout: str = "grid"
    ) -> Frame:
        """
        Create split-view or multi-camera layout from multiple frames.
        
        Args:
            frames: List of Frame objects to combine
            layout: Layout type - "grid", "horizontal", "vertical", "pip" (picture-in-picture)
            
        Returns:
            Combined Frame with specified layout
        """
        if not frames:
            raise ValueError("At least one frame is required")
        
        if len(frames) == 1:
            return frames[0]
        
        # Get dimensions from first frame
        height, width = frames[0].image.shape[:2]
        
        if layout == "horizontal":
            combined = self._create_horizontal_layout(frames, width, height)
        elif layout == "vertical":
            combined = self._create_vertical_layout(frames, width, height)
        elif layout == "grid":
            combined = self._create_grid_layout(frames, width, height)
        elif layout == "pip":
            combined = self._create_pip_layout(frames, width, height)
        else:
            raise ValueError(f"Unknown layout: {layout}")
        
        return Frame(
            image=combined,
            frame_number=frames[0].frame_number,
            timestamp=frames[0].timestamp
        )
    
    def _create_horizontal_layout(
        self,
        frames: List[Frame],
        width: int,
        height: int
    ) -> np.ndarray:
        """Create horizontal split layout."""
        resized_frames = []
        new_width = width // len(frames)
        
        for frame in frames:
            resized = cv2.resize(frame.image, (new_width, height))
            resized_frames.append(resized)
        
        return np.hstack(resized_frames)
    
    def _create_vertical_layout(
        self,
        frames: List[Frame],
        width: int,
        height: int
    ) -> np.ndarray:
        """Create vertical split layout."""
        resized_frames = []
        new_height = height // len(frames)
        
        for frame in frames:
            resized = cv2.resize(frame.image, (width, new_height))
            resized_frames.append(resized)
        
        return np.vstack(resized_frames)
    
    def _create_grid_layout(
        self,
        frames: List[Frame],
        width: int,
        height: int
    ) -> np.ndarray:
        """Create grid layout (2x2, 3x3, etc.)."""
        num_frames = len(frames)
        
        # Calculate grid dimensions
        cols = int(np.ceil(np.sqrt(num_frames)))
        rows = int(np.ceil(num_frames / cols))
        
        cell_width = width // cols
        cell_height = height // rows
        
        # Create blank canvas
        canvas = np.zeros((rows * cell_height, cols * cell_width, 3), dtype=np.uint8)
        
        for idx, frame in enumerate(frames):
            row = idx // cols
            col = idx % cols
            
            resized = cv2.resize(frame.image, (cell_width, cell_height))
            
            y_start = row * cell_height
            y_end = y_start + cell_height
            x_start = col * cell_width
            x_end = x_start + cell_width
            
            canvas[y_start:y_end, x_start:x_end] = resized
        
        return canvas
    
    def _create_pip_layout(
        self,
        frames: List[Frame],
        width: int,
        height: int
    ) -> np.ndarray:
        """Create picture-in-picture layout (main + small overlays)."""
        # Main frame is the first one
        canvas = frames[0].image.copy()
        
        # Overlay other frames as small windows
        pip_width = width // 4
        pip_height = height // 4
        margin = 10
        
        for idx, frame in enumerate(frames[1:], start=1):
            resized = cv2.resize(frame.image, (pip_width, pip_height))
            
            # Position in bottom-right area, stacked vertically
            x_pos = width - pip_width - margin
            y_pos = height - (idx * (pip_height + margin))
            
            if y_pos < 0:
                break  # No more space
            
            canvas[y_pos:y_pos+pip_height, x_pos:x_pos+pip_width] = resized
            
            # Draw border around PIP
            cv2.rectangle(
                canvas,
                (x_pos, y_pos),
                (x_pos + pip_width, y_pos + pip_height),
                (255, 255, 255),
                2
            )
        
        return canvas
