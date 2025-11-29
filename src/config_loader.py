"""
Configuration loader and validator for SMART FLOW v2.

This module provides comprehensive configuration loading and validation
for single intersections, multi-intersection networks, and dashboard settings.
"""

import json
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum


class TurnType(Enum):
    """Turn lane types."""
    LEFT = "left"
    RIGHT = "right"
    U_TURN = "u_turn"


class LaneType(Enum):
    """Lane types."""
    THROUGH = "through"
    TURN = "turn"
    MIXED = "mixed"


@dataclass
class Region:
    """Bounding box region [x1, y1, x2, y2]."""
    x1: int
    y1: int
    x2: int
    y2: int
    
    @classmethod
    def from_list(cls, coords: List[int]) -> 'Region':
        """Create Region from list of coordinates."""
        if len(coords) != 4:
            raise ValueError(f"Region must have 4 coordinates, got {len(coords)}")
        return cls(coords[0], coords[1], coords[2], coords[3])
    
    def to_list(self) -> List[int]:
        """Convert Region to list of coordinates."""
        return [self.x1, self.y1, self.x2, self.y2]


@dataclass
class LaneConfig:
    """Configuration for a single lane."""
    region: Region
    direction: str
    lane_type: str = "through"
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LaneConfig':
        """Create LaneConfig from dictionary."""
        return cls(
            region=Region.from_list(data['region']),
            direction=data['direction'],
            lane_type=data.get('type', 'through')
        )


@dataclass
class TurnLaneConfig:
    """Configuration for a turn lane."""
    region: Region
    turn_type: str
    parent_lane: Optional[str] = None
    conflicting_movements: List[str] = field(default_factory=list)
    minimum_green: int = 5
    maximum_green: int = 30
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TurnLaneConfig':
        """Create TurnLaneConfig from dictionary."""
        return cls(
            region=Region.from_list(data['region']),
            turn_type=data['turn_type'],
            parent_lane=data.get('parent_lane'),
            conflicting_movements=data.get('conflicting_movements', []),
            minimum_green=data.get('minimum_green', 5),
            maximum_green=data.get('maximum_green', 30)
        )


@dataclass
class CrosswalkConfig:
    """Configuration for a crosswalk."""
    region: Region
    crossing_distance: float
    conflicting_lanes: List[str] = field(default_factory=list)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CrosswalkConfig':
        """Create CrosswalkConfig from dictionary."""
        return cls(
            region=Region.from_list(data['region']),
            crossing_distance=data['crossing_distance'],
            conflicting_lanes=data.get('conflicting_lanes', [])
        )


@dataclass
class SignalTimingConfig:
    """Signal timing parameters."""
    minimum_green: int = 10
    maximum_green: int = 60
    yellow_duration: int = 3
    all_red_duration: int = 2
    pedestrian_walk_speed: float = 1.2
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SignalTimingConfig':
        """Create SignalTimingConfig from dictionary."""
        return cls(
            minimum_green=data.get('minimum_green', 10),
            maximum_green=data.get('maximum_green', 60),
            yellow_duration=data.get('yellow_duration', 3),
            all_red_duration=data.get('all_red_duration', 2),
            pedestrian_walk_speed=data.get('pedestrian_walk_speed', 1.2)
        )


@dataclass
class DetectionConfig:
    """Detection and tracking configuration."""
    model_path: str = "yolov8n.pt"
    confidence_threshold: float = 0.5
    tracking_enabled: bool = True
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DetectionConfig':
        """Create DetectionConfig from dictionary."""
        return cls(
            model_path=data.get('model_path', 'yolov8n.pt'),
            confidence_threshold=data.get('confidence_threshold', 0.5),
            tracking_enabled=data.get('tracking_enabled', True)
        )


@dataclass
class IntersectionConfig:
    """Configuration for a single intersection."""
    id: str
    name: str
    video_source: str
    lanes: Dict[str, LaneConfig]
    turn_lanes: Dict[str, TurnLaneConfig] = field(default_factory=dict)
    crosswalks: Dict[str, CrosswalkConfig] = field(default_factory=dict)
    signal_timing: SignalTimingConfig = field(default_factory=SignalTimingConfig)
    detection: DetectionConfig = field(default_factory=DetectionConfig)
    vehicle_weights: Dict[str, float] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'IntersectionConfig':
        """Create IntersectionConfig from dictionary."""
        # Parse intersection metadata
        intersection_data = data.get('intersection', {})
        
        # Parse lanes
        lanes = {}
        for lane_name, lane_data in data.get('lanes', {}).items():
            lanes[lane_name] = LaneConfig.from_dict(lane_data)
        
        # Parse turn lanes
        turn_lanes = {}
        for turn_name, turn_data in data.get('turn_lanes', {}).items():
            turn_lanes[turn_name] = TurnLaneConfig.from_dict(turn_data)
        
        # Parse crosswalks
        crosswalks = {}
        for crosswalk_name, crosswalk_data in data.get('crosswalks', {}).items():
            crosswalks[crosswalk_name] = CrosswalkConfig.from_dict(crosswalk_data)
        
        # Parse signal timing
        signal_timing = SignalTimingConfig.from_dict(data.get('signal_timing', {}))
        
        # Parse detection config
        detection = DetectionConfig.from_dict(data.get('detection', {}))
        
        # Parse vehicle weights
        vehicle_weights = data.get('vehicle_weights', {
            'car': 1.0,
            'truck': 1.5,
            'bus': 2.0,
            'motorcycle': 0.8,
            'bicycle': 0.5
        })
        
        return cls(
            id=intersection_data.get('id', 'default_intersection'),
            name=intersection_data.get('name', 'Unnamed Intersection'),
            video_source=intersection_data.get('video_source', ''),
            lanes=lanes,
            turn_lanes=turn_lanes,
            crosswalks=crosswalks,
            signal_timing=signal_timing,
            detection=detection,
            vehicle_weights=vehicle_weights
        )


@dataclass
class NetworkConnection:
    """Connection between two intersections."""
    from_intersection: str
    to_intersection: str
    distance_meters: float
    travel_time_seconds: float
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NetworkConnection':
        """Create NetworkConnection from dictionary."""
        return cls(
            from_intersection=data['from'],
            to_intersection=data['to'],
            distance_meters=data.get('distance_meters', data.get('distance', 0)),
            travel_time_seconds=data.get('travel_time_seconds', data.get('time', 0))
        )


@dataclass
class Corridor:
    """Traffic corridor configuration."""
    name: str
    intersections: List[str]
    direction: str
    priority: str = "normal"
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Corridor':
        """Create Corridor from dictionary."""
        return cls(
            name=data['name'],
            intersections=data['intersections'],
            direction=data['direction'],
            priority=data.get('priority', 'normal')
        )


@dataclass
class NetworkConfig:
    """Configuration for multi-intersection network."""
    name: str
    coordination_enabled: bool
    target_speed_mph: float
    update_interval: float
    intersections: Dict[str, IntersectionConfig]
    connections: List[NetworkConnection]
    corridors: List[Corridor] = field(default_factory=list)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NetworkConfig':
        """Create NetworkConfig from dictionary."""
        # Parse network metadata
        network_data = data.get('network', {})
        
        # Parse intersections
        intersections = {}
        for int_id, int_data in data.get('intersections', {}).items():
            # Create a full intersection config from the network data
            full_int_data = {
                'intersection': {
                    'id': int_data.get('id', int_id),
                    'name': int_data.get('name', int_id),
                    'video_source': int_data.get('video_source', '')
                },
                'lanes': int_data.get('lanes', {}),
                'turn_lanes': int_data.get('turn_lanes', {}),
                'crosswalks': int_data.get('crosswalks', {}),
                'signal_timing': int_data.get('signal_timing', {}),
                'detection': int_data.get('detection', {}),
                'vehicle_weights': int_data.get('vehicle_weights', {})
            }
            intersections[int_id] = IntersectionConfig.from_dict(full_int_data)
        
        # Parse connections
        connections = []
        for conn_data in data.get('connections', []):
            connections.append(NetworkConnection.from_dict(conn_data))
        
        # Parse corridors
        corridors = []
        for corridor_data in data.get('corridors', []):
            corridors.append(Corridor.from_dict(corridor_data))
        
        return cls(
            name=network_data.get('name', 'Unnamed Network'),
            coordination_enabled=network_data.get('coordination_enabled', True),
            target_speed_mph=network_data.get('target_speed_mph', 35),
            update_interval=network_data.get('update_interval', 5.0),
            intersections=intersections,
            connections=connections,
            corridors=corridors
        )


@dataclass
class DashboardConfig:
    """Web dashboard configuration."""
    port: int = 8080
    host: str = "0.0.0.0"
    enable_cors: bool = True
    allowed_origins: List[str] = field(default_factory=lambda: ["*"])
    websocket_update_interval: float = 0.5
    video_stream_fps: int = 15
    video_stream_quality: int = 80
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DashboardConfig':
        """Create DashboardConfig from dictionary."""
        dashboard_data = data.get('dashboard', {})
        return cls(
            port=dashboard_data.get('port', 8080),
            host=dashboard_data.get('host', '0.0.0.0'),
            enable_cors=dashboard_data.get('enable_cors', True),
            allowed_origins=dashboard_data.get('allowed_origins', ['*']),
            websocket_update_interval=dashboard_data.get('websocket_update_interval', 0.5),
            video_stream_fps=dashboard_data.get('video_stream_fps', 15),
            video_stream_quality=dashboard_data.get('video_stream_quality', 80)
        )


class ConfigLoader:
    """Load and validate configuration files."""
    
    @staticmethod
    def load_file(file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Load configuration file (JSON or YAML).
        
        Args:
            file_path: Path to configuration file
            
        Returns:
            Dictionary containing configuration data
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format is unsupported or invalid
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {file_path}")
        
        # Determine file type by extension
        suffix = file_path.suffix.lower()
        
        try:
            with open(file_path, 'r') as f:
                if suffix == '.json':
                    return json.load(f)
                elif suffix in ['.yaml', '.yml']:
                    return yaml.safe_load(f)
                else:
                    raise ValueError(f"Unsupported file format: {suffix}. Use .json, .yaml, or .yml")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in {file_path}: {e}")
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in {file_path}: {e}")
    
    @staticmethod
    def load_intersection_config(file_path: Union[str, Path]) -> IntersectionConfig:
        """
        Load single intersection configuration.
        
        Args:
            file_path: Path to intersection configuration file
            
        Returns:
            IntersectionConfig object
        """
        data = ConfigLoader.load_file(file_path)
        return IntersectionConfig.from_dict(data)
    
    @staticmethod
    def load_network_config(file_path: Union[str, Path]) -> NetworkConfig:
        """
        Load multi-intersection network configuration.
        
        Args:
            file_path: Path to network configuration file
            
        Returns:
            NetworkConfig object
        """
        data = ConfigLoader.load_file(file_path)
        return NetworkConfig.from_dict(data)
    
    @staticmethod
    def load_dashboard_config(file_path: Union[str, Path]) -> DashboardConfig:
        """
        Load dashboard configuration.
        
        Args:
            file_path: Path to dashboard configuration file
            
        Returns:
            DashboardConfig object
        """
        data = ConfigLoader.load_file(file_path)
        return DashboardConfig.from_dict(data)
    
    @staticmethod
    def validate_intersection_config(config: IntersectionConfig) -> List[str]:
        """
        Validate intersection configuration.
        
        Args:
            config: IntersectionConfig to validate
            
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        
        # Validate required fields
        if not config.id:
            errors.append("Intersection ID is required")
        if not config.name:
            errors.append("Intersection name is required")
        if not config.video_source:
            errors.append("Video source is required")
        
        # Validate lanes
        if not config.lanes:
            errors.append("At least one lane must be configured")
        
        # Validate turn lane references
        for turn_name, turn_config in config.turn_lanes.items():
            if turn_config.parent_lane and turn_config.parent_lane not in config.lanes:
                errors.append(f"Turn lane '{turn_name}' references non-existent parent lane '{turn_config.parent_lane}'")
            
            for conflicting in turn_config.conflicting_movements:
                if conflicting not in config.lanes and conflicting not in config.turn_lanes:
                    errors.append(f"Turn lane '{turn_name}' references non-existent conflicting movement '{conflicting}'")
        
        # Validate crosswalk references
        for crosswalk_name, crosswalk_config in config.crosswalks.items():
            for lane in crosswalk_config.conflicting_lanes:
                if lane not in config.lanes:
                    errors.append(f"Crosswalk '{crosswalk_name}' references non-existent lane '{lane}'")
        
        # Validate signal timing
        if config.signal_timing.minimum_green <= 0:
            errors.append("Minimum green time must be positive")
        if config.signal_timing.maximum_green < config.signal_timing.minimum_green:
            errors.append("Maximum green time must be >= minimum green time")
        if config.signal_timing.yellow_duration <= 0:
            errors.append("Yellow duration must be positive")
        
        # Validate detection config
        if config.detection.confidence_threshold < 0 or config.detection.confidence_threshold > 1:
            errors.append("Confidence threshold must be between 0 and 1")
        
        return errors
    
    @staticmethod
    def validate_network_config(config: NetworkConfig) -> List[str]:
        """
        Validate network configuration.
        
        Args:
            config: NetworkConfig to validate
            
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        
        # Validate network metadata
        if not config.name:
            errors.append("Network name is required")
        if config.target_speed_mph <= 0:
            errors.append("Target speed must be positive")
        if config.update_interval <= 0:
            errors.append("Update interval must be positive")
        
        # Validate intersections
        if not config.intersections:
            errors.append("At least one intersection must be configured")
        
        # Validate each intersection
        for int_id, int_config in config.intersections.items():
            int_errors = ConfigLoader.validate_intersection_config(int_config)
            for error in int_errors:
                errors.append(f"Intersection '{int_id}': {error}")
        
        # Validate connections
        for conn in config.connections:
            if conn.from_intersection not in config.intersections:
                errors.append(f"Connection references non-existent intersection '{conn.from_intersection}'")
            if conn.to_intersection not in config.intersections:
                errors.append(f"Connection references non-existent intersection '{conn.to_intersection}'")
            if conn.distance_meters <= 0:
                errors.append(f"Connection distance must be positive")
            if conn.travel_time_seconds <= 0:
                errors.append(f"Connection travel time must be positive")
        
        # Validate corridors
        for corridor in config.corridors:
            for int_id in corridor.intersections:
                if int_id not in config.intersections:
                    errors.append(f"Corridor '{corridor.name}' references non-existent intersection '{int_id}'")
        
        return errors


def load_config(file_path: Union[str, Path], config_type: str = 'auto') -> Union[IntersectionConfig, NetworkConfig, DashboardConfig]:
    """
    Load and validate configuration file.
    
    Args:
        file_path: Path to configuration file
        config_type: Type of configuration ('intersection', 'network', 'dashboard', or 'auto')
        
    Returns:
        Configuration object (IntersectionConfig, NetworkConfig, or DashboardConfig)
        
    Raises:
        ValueError: If configuration is invalid
    """
    loader = ConfigLoader()
    
    # Auto-detect config type if needed
    if config_type == 'auto':
        data = loader.load_file(file_path)
        if 'network' in data or 'connections' in data:
            config_type = 'network'
        elif 'dashboard' in data:
            config_type = 'dashboard'
        else:
            config_type = 'intersection'
    
    # Load appropriate config type
    if config_type == 'intersection':
        config = loader.load_intersection_config(file_path)
        errors = loader.validate_intersection_config(config)
        if errors:
            raise ValueError(f"Invalid intersection configuration:\n" + "\n".join(f"  - {e}" for e in errors))
        return config
    
    elif config_type == 'network':
        config = loader.load_network_config(file_path)
        errors = loader.validate_network_config(config)
        if errors:
            raise ValueError(f"Invalid network configuration:\n" + "\n".join(f"  - {e}" for e in errors))
        return config
    
    elif config_type == 'dashboard':
        config = loader.load_dashboard_config(file_path)
        return config
    
    else:
        raise ValueError(f"Unknown config type: {config_type}")
