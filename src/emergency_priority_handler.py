"""
Emergency Priority Handler Module for SMART FLOW v2

Detects and prioritizes emergency vehicles.
"""

from typing import Optional, List, Dict, Tuple
from dataclasses import dataclass
import time


@dataclass
class EmergencyEvent:
    """Emergency vehicle event"""
    vehicle_type: str  # VehicleType from enhanced_detector
    lane: str
    detection: object  # Detection object
    timestamp: float
    priority_level: int


@dataclass
class SignalPlan:
    """Emergency signal plan"""
    emergency_lane: str
    duration: float  # Duration to hold green signal
    timestamp: float


class EmergencyPriorityHandler:
    """
    Handles emergency vehicle detection and priority.
    
    This class detects emergency vehicles, determines which lane they're in,
    creates emergency signal plans, and tracks the emergency event lifecycle.
    """
    
    def __init__(self, emergency_green_duration: float = 30.0):
        """
        Initialize emergency priority handler.
        
        Args:
            emergency_green_duration: Duration to hold green signal for emergency vehicle (seconds)
        """
        self.emergency_green_duration = emergency_green_duration
        self._active_emergency: Optional[EmergencyEvent] = None
        self._emergency_start_time: Optional[float] = None
        self._emergency_history: List[EmergencyEvent] = []
    
    def detect_emergency(self, detections: List, timestamp: Optional[float] = None) -> Optional[EmergencyEvent]:
        """
        Detect emergency vehicles from detection list.
        
        Args:
            detections: List of Detection objects (should include emergency_vehicles)
            timestamp: Current timestamp (defaults to current time)
            
        Returns:
            EmergencyEvent if emergency vehicle detected, None otherwise
        """
        if timestamp is None:
            timestamp = time.time()
        
        # Check if detections is a DetectionResult object with emergency_vehicles attribute
        if hasattr(detections, 'emergency_vehicles'):
            emergency_detections = detections.emergency_vehicles
        else:
            # Assume it's a list of detections, filter for emergency vehicles
            emergency_detections = [d for d in detections if self._is_emergency_detection(d)]
        
        if not emergency_detections:
            return None
        
        # Take the first emergency vehicle (highest priority)
        # In a more sophisticated system, we could prioritize by type or proximity
        emergency_detection = emergency_detections[0]
        
        # Determine vehicle type
        vehicle_type = self._get_vehicle_type(emergency_detection)
        
        # Priority levels: ambulance=1 (highest), fire=2, police=3
        priority_map = {
            'ambulance': 1,
            'fire_truck': 2,
            'police': 3
        }
        priority_level = priority_map.get(vehicle_type, 2)
        
        # Create emergency event (lane will be set by calculate_priority_lane)
        event = EmergencyEvent(
            vehicle_type=vehicle_type,
            lane="",  # Will be set by calculate_priority_lane
            detection=emergency_detection,
            timestamp=timestamp,
            priority_level=priority_level
        )
        
        return event
    
    def calculate_priority_lane(self, emergency_vehicle, lanes: Dict[str, tuple]) -> str:
        """
        Calculate which lane the emergency vehicle is in.
        
        Args:
            emergency_vehicle: Emergency vehicle detection (Detection object or EmergencyEvent)
            lanes: Dictionary of lane regions (lane_name -> Region or (x, y, width, height))
            
        Returns:
            Lane identifier (lane name)
        """
        # Get the detection object
        if isinstance(emergency_vehicle, EmergencyEvent):
            detection = emergency_vehicle.detection
        else:
            detection = emergency_vehicle
        
        # Get vehicle center point
        if hasattr(detection, 'center'):
            vehicle_center = detection.center
        else:
            # Calculate center from bbox
            x, y, w, h = detection.bbox
            vehicle_center = (x + w // 2, y + h // 2)
        
        # Find which lane contains the vehicle center
        for lane_name, region in lanes.items():
            # Handle Region object or tuple
            if hasattr(region, 'x'):
                # Region object
                if (region.x <= vehicle_center[0] < region.x + region.width and
                    region.y <= vehicle_center[1] < region.y + region.height):
                    return lane_name
            else:
                # Tuple (x, y, width, height)
                x, y, width, height = region
                if (x <= vehicle_center[0] < x + width and
                    y <= vehicle_center[1] < y + height):
                    return lane_name
        
        # If not in any lane, return the closest lane
        min_distance = float('inf')
        closest_lane = list(lanes.keys())[0] if lanes else "unknown"
        
        for lane_name, region in lanes.items():
            # Calculate distance to lane center
            if hasattr(region, 'x'):
                lane_center = (region.x + region.width // 2, region.y + region.height // 2)
            else:
                x, y, width, height = region
                lane_center = (x + width // 2, y + height // 2)
            
            distance = ((vehicle_center[0] - lane_center[0]) ** 2 + 
                       (vehicle_center[1] - lane_center[1]) ** 2) ** 0.5
            
            if distance < min_distance:
                min_distance = distance
                closest_lane = lane_name
        
        return closest_lane
    
    def create_emergency_plan(self, lane: str, timestamp: Optional[float] = None) -> SignalPlan:
        """
        Create emergency signal plan.
        
        Args:
            lane: Lane to prioritize
            timestamp: Current timestamp (defaults to current time)
            
        Returns:
            SignalPlan for emergency
        """
        if timestamp is None:
            timestamp = time.time()
        
        plan = SignalPlan(
            emergency_lane=lane,
            duration=self.emergency_green_duration,
            timestamp=timestamp
        )
        
        return plan
    
    def activate_emergency(self, event: EmergencyEvent, lane: str) -> None:
        """
        Activate emergency priority for a detected emergency vehicle.
        
        Args:
            event: EmergencyEvent to activate
            lane: Lane where emergency vehicle is located
        """
        event.lane = lane
        self._active_emergency = event
        self._emergency_start_time = event.timestamp
        self._emergency_history.append(event)
    
    def is_emergency_active(self) -> bool:
        """
        Check if emergency is active.
        
        Returns:
            True if emergency active, False otherwise
        """
        return self._active_emergency is not None
    
    def get_active_emergency(self) -> Optional[EmergencyEvent]:
        """
        Get the currently active emergency event.
        
        Returns:
            Active EmergencyEvent or None
        """
        return self._active_emergency
    
    def should_clear_emergency(self, current_time: Optional[float] = None) -> bool:
        """
        Check if emergency should be cleared based on elapsed time.
        
        Args:
            current_time: Current timestamp (defaults to current time)
            
        Returns:
            True if emergency should be cleared, False otherwise
        """
        if not self.is_emergency_active():
            return False
        
        if current_time is None:
            current_time = time.time()
        
        elapsed = current_time - self._emergency_start_time
        return elapsed >= self.emergency_green_duration
    
    def clear_emergency(self) -> None:
        """Clear emergency state"""
        self._active_emergency = None
        self._emergency_start_time = None
    
    def get_emergency_history(self) -> List[EmergencyEvent]:
        """
        Get history of all emergency events.
        
        Returns:
            List of EmergencyEvent objects
        """
        return self._emergency_history.copy()
    
    def _is_emergency_detection(self, detection) -> bool:
        """
        Check if a detection is an emergency vehicle.
        
        Args:
            detection: Detection object
            
        Returns:
            True if emergency vehicle, False otherwise
        """
        # Check if detection has emergency-related class name
        if hasattr(detection, 'class_name'):
            class_name = detection.class_name.lower()
            emergency_keywords = ['ambulance', 'fire', 'police', 'emergency']
            return any(keyword in class_name for keyword in emergency_keywords)
        
        return False
    
    def _get_vehicle_type(self, detection) -> str:
        """
        Get vehicle type from detection.
        
        Args:
            detection: Detection object
            
        Returns:
            Vehicle type string
        """
        if hasattr(detection, 'class_name'):
            class_name = detection.class_name.lower()
            
            if 'ambulance' in class_name:
                return 'ambulance'
            elif 'fire' in class_name:
                return 'fire_truck'
            elif 'police' in class_name:
                return 'police'
        
        # Default to ambulance for unknown emergency vehicles
        return 'ambulance'
