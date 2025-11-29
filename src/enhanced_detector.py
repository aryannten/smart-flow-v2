"""
Enhanced Object Detector Module for SMART FLOW v2

Extends vehicle detection to include:
- Pedestrian detection
- Emergency vehicle classification
- Vehicle type classification
- Object tracking across frames
"""

from typing import List, Optional, Dict, Tuple
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
from ultralytics import YOLO
import time
import logging

from src.error_handler import ErrorHandler, ErrorSeverity

logger = logging.getLogger(__name__)


class VehicleType(Enum):
    """Vehicle type classifications"""
    CAR = "car"
    TRUCK = "truck"
    BUS = "bus"
    MOTORCYCLE = "motorcycle"
    BICYCLE = "bicycle"
    EMERGENCY_AMBULANCE = "ambulance"
    EMERGENCY_FIRE = "fire_truck"
    EMERGENCY_POLICE = "police"


@dataclass
class Detection:
    """Single object detection"""
    bbox: Tuple[int, int, int, int]  # (x, y, width, height)
    confidence: float
    class_id: int
    class_name: str
    center: Tuple[int, int] = field(init=False)
    
    def __post_init__(self):
        """Calculate center point after initialization"""
        x, y, w, h = self.bbox
        self.center = (x + w // 2, y + h // 2)


@dataclass
class DetectionResult:
    """Complete detection result for a frame"""
    vehicles: List[Detection]
    pedestrians: List[Detection]
    emergency_vehicles: List[Detection]
    timestamp: float


@dataclass
class TrackedObject:
    """Object tracked across frames"""
    object_id: int
    detection: Detection
    trajectory: List[Tuple[int, int]]  # List of (x, y) positions
    velocity: Tuple[float, float]  # (vx, vy) pixels per second
    age: int  # frames since first detection


class SimpleTracker:
    """
    Simple object tracker using IoU and centroid distance.
    Implements a lightweight tracking algorithm suitable for traffic scenarios.
    """
    
    def __init__(self, max_age: int = 30, min_hits: int = 3, iou_threshold: float = 0.3):
        """
        Initialize tracker.
        
        Args:
            max_age: Maximum frames to keep track without detection
            min_hits: Minimum detections before track is confirmed
            iou_threshold: Minimum IoU for matching detections to tracks
        """
        self.max_age = max_age
        self.min_hits = min_hits
        self.iou_threshold = iou_threshold
        self.tracks: Dict[int, Dict] = {}
        self.next_id = 0
        self.frame_count = 0
    
    def update(self, detections: List[Detection], fps: float = 30.0) -> List[TrackedObject]:
        """
        Update tracks with new detections.
        
        Args:
            detections: List of detections in current frame
            fps: Frame rate for velocity calculation
            
        Returns:
            List of tracked objects
        """
        self.frame_count += 1
        
        # Match detections to existing tracks
        matched_tracks, unmatched_detections = self._match_detections(detections)
        
        # Update matched tracks
        for track_id, detection in matched_tracks.items():
            track = self.tracks[track_id]
            track['detections'].append(detection)
            track['age'] = 0
            track['hits'] += 1
            
            # Update trajectory
            track['trajectory'].append(detection.center)
            
            # Calculate velocity (pixels per second)
            if len(track['trajectory']) >= 2:
                dt = 1.0 / fps
                dx = track['trajectory'][-1][0] - track['trajectory'][-2][0]
                dy = track['trajectory'][-1][1] - track['trajectory'][-2][1]
                track['velocity'] = (dx / dt, dy / dt)
        
        # Create new tracks for unmatched detections
        for detection in unmatched_detections:
            self.tracks[self.next_id] = {
                'detections': [detection],
                'trajectory': [detection.center],
                'velocity': (0.0, 0.0),
                'age': 0,
                'hits': 1
            }
            self.next_id += 1
        
        # Age unmatched tracks
        tracks_to_remove = []
        for track_id in self.tracks:
            if track_id not in matched_tracks:
                self.tracks[track_id]['age'] += 1
                if self.tracks[track_id]['age'] > self.max_age:
                    tracks_to_remove.append(track_id)
        
        # Remove old tracks
        for track_id in tracks_to_remove:
            del self.tracks[track_id]
        
        # Build tracked objects list
        tracked_objects = []
        for track_id, track in self.tracks.items():
            if track['hits'] >= self.min_hits:
                tracked_objects.append(TrackedObject(
                    object_id=track_id,
                    detection=track['detections'][-1],
                    trajectory=track['trajectory'].copy(),
                    velocity=track['velocity'],
                    age=self.frame_count - len(track['detections']) + 1
                ))
        
        return tracked_objects
    
    def _match_detections(self, detections: List[Detection]) -> Tuple[Dict[int, Detection], List[Detection]]:
        """
        Match detections to existing tracks using IoU and distance.
        
        Args:
            detections: List of detections to match
            
        Returns:
            Tuple of (matched_tracks dict, unmatched_detections list)
        """
        if not self.tracks or not detections:
            return {}, detections
        
        # Calculate cost matrix (negative IoU + distance penalty)
        track_ids = list(self.tracks.keys())
        cost_matrix = np.zeros((len(track_ids), len(detections)))
        
        for i, track_id in enumerate(track_ids):
            last_detection = self.tracks[track_id]['detections'][-1]
            for j, detection in enumerate(detections):
                iou = self._calculate_iou(last_detection.bbox, detection.bbox)
                distance = self._calculate_distance(last_detection.center, detection.center)
                # Cost is negative IoU plus normalized distance
                cost_matrix[i, j] = -iou + distance / 1000.0
        
        # Simple greedy matching
        matched_tracks = {}
        matched_detection_indices = set()
        
        # Sort by cost and match greedily
        matches = []
        for i in range(len(track_ids)):
            for j in range(len(detections)):
                if j not in matched_detection_indices:
                    matches.append((cost_matrix[i, j], i, j))
        
        matches.sort()
        
        for cost, i, j in matches:
            if i < len(track_ids) and j < len(detections):
                track_id = track_ids[i]
                if track_id not in matched_tracks and j not in matched_detection_indices:
                    # Check if match is good enough
                    last_detection = self.tracks[track_id]['detections'][-1]
                    iou = self._calculate_iou(last_detection.bbox, detections[j].bbox)
                    if iou >= self.iou_threshold or cost < 0.5:
                        matched_tracks[track_id] = detections[j]
                        matched_detection_indices.add(j)
        
        # Unmatched detections
        unmatched_detections = [d for i, d in enumerate(detections) if i not in matched_detection_indices]
        
        return matched_tracks, unmatched_detections
    
    def _calculate_iou(self, bbox1: Tuple[int, int, int, int], bbox2: Tuple[int, int, int, int]) -> float:
        """Calculate Intersection over Union between two bounding boxes."""
        x1, y1, w1, h1 = bbox1
        x2, y2, w2, h2 = bbox2
        
        # Calculate intersection
        x_left = max(x1, x2)
        y_top = max(y1, y2)
        x_right = min(x1 + w1, x2 + w2)
        y_bottom = min(y1 + h1, y2 + h2)
        
        if x_right < x_left or y_bottom < y_top:
            return 0.0
        
        intersection = (x_right - x_left) * (y_bottom - y_top)
        area1 = w1 * h1
        area2 = w2 * h2
        union = area1 + area2 - intersection
        
        return intersection / union if union > 0 else 0.0
    
    def _calculate_distance(self, point1: Tuple[int, int], point2: Tuple[int, int]) -> float:
        """Calculate Euclidean distance between two points."""
        return np.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)


class EnhancedDetector:
    """
    Enhanced object detector supporting vehicles, pedestrians, and emergency vehicles.
    Uses YOLO for detection and includes simple tracking.
    """
    
    # YOLO COCO class mappings
    VEHICLE_CLASSES = {'car', 'truck', 'bus', 'motorcycle', 'bicycle'}
    PEDESTRIAN_CLASS = 'person'
    
    # Emergency vehicle detection heuristics
    # In a real system, this would use more sophisticated methods
    # (e.g., color detection, siren detection, specialized models)
    EMERGENCY_KEYWORDS = ['ambulance', 'fire', 'police', 'emergency']
    
    def __init__(self, model_path: str, confidence_threshold: float = 0.5, error_handler: Optional[ErrorHandler] = None, enhance_night: bool = False):
        """
        Initialize enhanced detector.
        
        Args:
            model_path: Path to YOLO model
            confidence_threshold: Minimum confidence for detections
            error_handler: Optional error handler for comprehensive error management
            enhance_night: Enable night/low-light enhancement preprocessing
        """
        self.model_path = model_path
        self.confidence_threshold = confidence_threshold
        self.model: Optional[YOLO] = None
        self.tracker = SimpleTracker()
        self.error_handler = error_handler
        self.inference_failures = 0
        self.max_inference_failures = 5
        self.enhance_night = enhance_night
        self._load_model()
    
    def _load_model(self) -> None:
        """Load the YOLO model."""
        try:
            self.model = YOLO(self.model_path)
            logger.info(f"YOLO model loaded successfully from {self.model_path}")
        except Exception as e:
            error_msg = f"Failed to load YOLO model from {self.model_path}: {e}"
            logger.error(error_msg)
            if self.error_handler:
                self.error_handler.handle_exception(
                    component="EnhancedDetector",
                    operation="load_model",
                    exception=e,
                    severity=ErrorSeverity.CRITICAL
                )
            raise Exception(error_msg)
    
    def _preprocess_frame(self, frame: np.ndarray) -> np.ndarray:
        """
        Preprocess frame to improve detection in challenging conditions.
        Handles:
        - Low light / night conditions
        - Headlight glare
        - Contrast enhancement
        
        Args:
            frame: Input frame
            
        Returns:
            Preprocessed frame
        """
        import cv2
        
        # Gentle contrast enhancement using CLAHE
        # Less aggressive to avoid breaking normal detection
        lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        
        # Apply CLAHE with gentle settings
        clahe = cv2.createCLAHE(clipLimit=1.5, tileGridSize=(8, 8))
        l_enhanced = clahe.apply(l)
        
        # Merge channels back
        enhanced_lab = cv2.merge([l_enhanced, a, b])
        enhanced_frame = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)
        
        return enhanced_frame
    
    def detect_all(self, frame: np.ndarray, timestamp: Optional[float] = None) -> DetectionResult:
        """
        Detect all objects in frame.
        
        Args:
            frame: Input frame (numpy array)
            timestamp: Frame timestamp (defaults to current time)
            
        Returns:
            DetectionResult with vehicles, pedestrians, and emergency vehicles
        """
        if self.model is None:
            error_msg = "YOLO model not loaded"
            logger.error(error_msg)
            if self.error_handler:
                self.error_handler.handle_exception(
                    component="EnhancedDetector",
                    operation="detect_all",
                    exception=RuntimeError(error_msg),
                    severity=ErrorSeverity.CRITICAL
                )
            raise RuntimeError(error_msg)
        
        if timestamp is None:
            timestamp = time.time()
        
        try:
            # Optionally preprocess frame for better night detection
            if self.enhance_night:
                processed_frame = self._preprocess_frame(frame)
            else:
                processed_frame = frame
            
            # Run YOLO inference
            results = self.model(processed_frame, verbose=False)
            
            # Reset failure counter on successful inference
            self.inference_failures = 0
            
            vehicles = []
            pedestrians = []
            emergency_vehicles = []
            
            # Process results
            for result in results:
                boxes = result.boxes
                
                for i in range(len(boxes)):
                    # Get detection data
                    box = boxes.xyxy[i].cpu().numpy()  # [x1, y1, x2, y2]
                    confidence = float(boxes.conf[i].cpu().numpy())
                    class_id = int(boxes.cls[i].cpu().numpy())
                    class_name = result.names[class_id]
                    
                    # Filter by confidence threshold
                    if confidence < self.confidence_threshold:
                        continue
                    
                    # Convert to [x, y, width, height] format
                    x1, y1, x2, y2 = box
                    x = int(x1)
                    y = int(y1)
                    width = int(x2 - x1)
                    height = int(y2 - y1)
                    
                    # Create Detection object
                    detection = Detection(
                        bbox=(x, y, width, height),
                        confidence=confidence,
                        class_id=class_id,
                        class_name=class_name
                    )
                    
                    # Classify detection
                    if class_name == self.PEDESTRIAN_CLASS:
                        pedestrians.append(detection)
                    elif class_name in self.VEHICLE_CLASSES:
                        vehicles.append(detection)
                        
                        # Check if it's an emergency vehicle
                        if self.is_emergency_vehicle(detection):
                            emergency_vehicles.append(detection)
            
            return DetectionResult(
                vehicles=vehicles,
                pedestrians=pedestrians,
                emergency_vehicles=emergency_vehicles,
                timestamp=timestamp
            )
            
        except Exception as e:
            self.inference_failures += 1
            logger.error(f"Error during inference: {e}")
            
            if self.error_handler:
                severity = ErrorSeverity.CRITICAL if self.inference_failures >= self.max_inference_failures else ErrorSeverity.ERROR
                self.error_handler.handle_exception(
                    component="EnhancedDetector",
                    operation="detect_all",
                    exception=e,
                    severity=severity
                )
            
            # Return empty result on failure to allow graceful degradation
            return DetectionResult(
                vehicles=[],
                pedestrians=[],
                emergency_vehicles=[],
                timestamp=timestamp
            )
    
    def classify_vehicle_type(self, detection: Detection) -> VehicleType:
        """
        Classify vehicle type from detection.
        
        Args:
            detection: Vehicle detection
            
        Returns:
            VehicleType classification
        """
        class_name = detection.class_name.lower()
        
        # Check if emergency vehicle first
        if self.is_emergency_vehicle(detection):
            # For now, default to ambulance
            # In a real system, we'd use more sophisticated classification
            return VehicleType.EMERGENCY_AMBULANCE
        
        # Map YOLO class to VehicleType
        type_mapping = {
            'car': VehicleType.CAR,
            'truck': VehicleType.TRUCK,
            'bus': VehicleType.BUS,
            'motorcycle': VehicleType.MOTORCYCLE,
            'bicycle': VehicleType.BICYCLE
        }
        
        return type_mapping.get(class_name, VehicleType.CAR)
    
    def is_emergency_vehicle(self, detection: Detection) -> bool:
        """
        Check if detection is an emergency vehicle.
        
        This is a simplified heuristic-based approach. In a production system,
        this would use:
        - Specialized emergency vehicle detection models
        - Color detection (red/white for ambulance, red for fire truck)
        - Light bar detection
        - Siren audio detection
        - Vehicle marking recognition
        
        Args:
            detection: Vehicle detection
            
        Returns:
            True if emergency vehicle, False otherwise
        """
        # For now, use a simple heuristic based on vehicle size and type
        # Large vehicles (trucks, buses) have a small chance of being emergency vehicles
        # This is a placeholder for more sophisticated detection
        
        class_name = detection.class_name.lower()
        
        # Check class name for emergency keywords
        for keyword in self.EMERGENCY_KEYWORDS:
            if keyword in class_name:
                return True
        
        # In a real system, we would analyze:
        # 1. Vehicle color (red, white, yellow)
        # 2. Presence of light bars on top
        # 3. Vehicle markings/text
        # 4. Audio signals (sirens)
        
        # For simulation purposes, we'll use a size-based heuristic
        # Emergency vehicles tend to be larger than regular cars
        x, y, w, h = detection.bbox
        area = w * h
        
        # Trucks and buses could be emergency vehicles
        if class_name in ['truck', 'bus']:
            # Use a probabilistic approach based on size
            # Larger vehicles have higher chance
            # This is a placeholder - real detection would be deterministic
            return area > 50000  # Arbitrary threshold for demo
        
        return False
    
    def track_objects(self, detections: List[Detection], fps: float = 30.0) -> List[TrackedObject]:
        """
        Track objects across frames.
        
        Args:
            detections: List of detections in current frame
            fps: Frame rate for velocity calculation
            
        Returns:
            List of tracked objects with IDs and trajectories
        """
        return self.tracker.update(detections, fps)
