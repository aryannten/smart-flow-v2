"""
Vehicle Detector module for SMART FLOW traffic signal simulation system.

Handles vehicle detection using YOLO and lane classification.
"""

from typing import List, Dict, Optional
from pathlib import Path
import numpy as np
from ultralytics import YOLO
from src.models import Detection, Region, Frame


class VehicleDetector:
    """
    Detects and counts vehicles using YOLO model.
    
    This class provides an interface for running YOLO inference on video frames,
    filtering detections by confidence, and classifying vehicles by lane.
    """
    
    # Vehicle classes from COCO dataset
    VEHICLE_CLASSES = {'car', 'truck', 'bus', 'motorcycle'}
    
    def __init__(self, model_path: str = "yolov8n.pt", confidence_threshold: float = 0.5):
        """
        Initialize VehicleDetector with YOLO model.
        
        Args:
            model_path: Path to YOLO model file (default: yolov8n.pt)
            confidence_threshold: Minimum confidence for detections (default: 0.5)
        """
        self.model_path = model_path
        self.confidence_threshold = confidence_threshold
        self.model: Optional[YOLO] = None
        self._load_model()
    
    def _load_model(self) -> None:
        """
        Load the YOLO model.
        
        Raises:
            Exception: If model loading fails
        """
        try:
            self.model = YOLO(self.model_path)
        except Exception as e:
            raise Exception(f"Failed to load YOLO model from {self.model_path}: {e}")
    
    def detect(self, frame: Frame) -> List[Detection]:
        """
        Detect vehicles in a frame using YOLO.
        
        Args:
            frame: Frame object containing the image to process
            
        Returns:
            List[Detection]: List of Detection objects for vehicles found
        """
        if self.model is None:
            raise RuntimeError("YOLO model not loaded")
        
        # Run YOLO inference
        results = self.model(frame.image, verbose=False)
        
        detections = []
        
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
                
                # Filter by vehicle classes
                if class_name not in self.VEHICLE_CLASSES:
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
                    class_name=class_name,
                    lane=None  # Will be assigned by count_by_lane
                )
                
                detections.append(detection)
        
        return detections
    
    def count_by_lane(
        self, 
        detections: List[Detection], 
        lane_regions: Dict[str, Region]
    ) -> Dict[str, int]:
        """
        Classify detections by lane and count vehicles per lane.
        
        Uses the center point of each detection's bounding box to determine
        which lane region it belongs to.
        
        Args:
            detections: List of Detection objects to classify
            lane_regions: Dictionary mapping lane names to Region objects
            
        Returns:
            Dict[str, int]: Dictionary mapping lane names to vehicle counts
        """
        # Initialize counts for all lanes
        lane_counts = {lane_name: 0 for lane_name in lane_regions.keys()}
        
        for detection in detections:
            # Calculate center point of bounding box
            x, y, width, height = detection.bbox
            center_x = x + width // 2
            center_y = y + height // 2
            
            # Find which lane region contains this center point
            for lane_name, region in lane_regions.items():
                if self._point_in_region(center_x, center_y, region):
                    detection.lane = lane_name
                    lane_counts[lane_name] += 1
                    break  # Each detection belongs to exactly one lane
        
        return lane_counts
    
    def _point_in_region(self, x: int, y: int, region: Region) -> bool:
        """
        Check if a point is inside a region.
        
        Args:
            x: X coordinate of the point
            y: Y coordinate of the point
            region: Region object to check against
            
        Returns:
            bool: True if point is inside region, False otherwise
        """
        return (
            region.x <= x < region.x + region.width and
            region.y <= y < region.y + region.height
        )
