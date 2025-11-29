"""
Data models for SMART FLOW traffic signal simulation system.
"""
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional, Tuple
import numpy as np
import json


class SignalState(Enum):
    """Traffic signal states."""
    RED = "red"
    YELLOW = "yellow"
    GREEN = "green"


class PhaseType(Enum):
    """Signal phase types."""
    THROUGH = "through"
    PROTECTED_LEFT = "protected_left"
    PROTECTED_RIGHT = "protected_right"
    PERMISSIVE_TURN = "permissive_turn"
    PEDESTRIAN = "pedestrian"
    EMERGENCY = "emergency"


@dataclass
class Frame:
    """Represents a single video frame with metadata."""
    image: np.ndarray  # OpenCV image array
    frame_number: int
    timestamp: float


@dataclass
class FrameMetadata:
    """Metadata about a video frame."""
    frame_number: int
    timestamp: float
    width: int
    height: int
    fps: float


@dataclass
class Detection:
    """Represents a detected vehicle in a frame."""
    bbox: Tuple[int, int, int, int]  # x, y, width, height
    confidence: float
    class_name: str
    lane: Optional[str] = None


@dataclass
class Region:
    """Represents a spatial region for lane classification."""
    x: int
    y: int
    width: int
    height: int
    lane_name: str
    
    def contains_point(self, point: tuple) -> bool:
        """
        Check if a point (x, y) is within this region.
        
        Args:
            point: Tuple of (x, y) coordinates
            
        Returns:
            True if point is within region bounds
        """
        px, py = point
        return (self.x <= px < self.x + self.width and 
                self.y <= py < self.y + self.height)


@dataclass
class SignalPhase:
    """Represents a signal phase in a cycle."""
    phase_type: 'PhaseType'
    lanes: list  # List of lane names
    duration: float
    state: SignalState


@dataclass
class LaneConfiguration:
    """Configuration for lane regions at an intersection."""
    lanes: Dict[str, Region]  # Maps lane name to spatial region
    
    @staticmethod
    def create_four_way(frame_width: int, frame_height: int) -> 'LaneConfiguration':
        """
        Creates default 4-way intersection configuration.
        Divides frame into quadrants for North, South, East, West lanes.
        
        Args:
            frame_width: Width of the video frame
            frame_height: Height of the video frame
            
        Returns:
            LaneConfiguration with four quadrant regions
        """
        half_width = frame_width // 2
        half_height = frame_height // 2
        
        lanes = {
            "north": Region(
                x=0,
                y=0,
                width=half_width,
                height=half_height,
                lane_name="north"
            ),
            "south": Region(
                x=half_width,
                y=half_height,
                width=half_width,
                height=half_height,
                lane_name="south"
            ),
            "east": Region(
                x=half_width,
                y=0,
                width=half_width,
                height=half_height,
                lane_name="east"
            ),
            "west": Region(
                x=0,
                y=half_height,
                width=half_width,
                height=half_height,
                lane_name="west"
            )
        }
        
        return LaneConfiguration(lanes=lanes)
    
    @staticmethod
    def from_json(json_path: str) -> 'LaneConfiguration':
        """
        Load lane configuration from a JSON file.
        
        Args:
            json_path: Path to JSON configuration file
            
        Returns:
            LaneConfiguration loaded from file
            
        Raises:
            FileNotFoundError: If JSON file doesn't exist
            ValueError: If JSON format is invalid
        """
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
            
            lanes = {}
            for lane_name, region_data in data.get('lanes', {}).items():
                lanes[lane_name] = Region(
                    x=region_data['x'],
                    y=region_data['y'],
                    width=region_data['width'],
                    height=region_data['height'],
                    lane_name=lane_name
                )
            
            return LaneConfiguration(lanes=lanes)
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {json_path}")
        except (KeyError, TypeError) as e:
            raise ValueError(f"Invalid JSON format in {json_path}: {e}")
    
    def to_json(self, json_path: str) -> None:
        """
        Save lane configuration to a JSON file.
        
        Args:
            json_path: Path where JSON file will be saved
        """
        data = {
            'lanes': {
                lane_name: {
                    'x': region.x,
                    'y': region.y,
                    'width': region.width,
                    'height': region.height
                }
                for lane_name, region in self.lanes.items()
            }
        }
        
        with open(json_path, 'w') as f:
            json.dump(data, f, indent=2)
