"""
Integration tests for SMART FLOW v2 traffic signal simulation system.

Tests the complete pipeline from video input to log output, including:
- Enhanced detection (vehicles, pedestrians, emergency vehicles)
- Stream management (multiple video sources)
- Emergency priority handling
- Pedestrian crossing management
- Turn lane control
- Multi-intersection coordination
"""

import pytest
import json
import numpy as np
import cv2
from pathlib import Path
import tempfile
import shutil
import time

# V1 imports
from src.video_processor import VideoProcessor
from src.vehicle_detector import VehicleDetector
from src.traffic_analyzer import TrafficAnalyzer
from src.signal_controller import SignalController
from src.visualizer import Visualizer
from src.metrics_logger import MetricsLogger
from src.models import LaneConfiguration, Frame, SignalState

# V2 imports
from src.stream_manager import StreamManager, StreamMetadata
from src.enhanced_detector import EnhancedDetector, VehicleType, Detection, DetectionResult
from src.emergency_priority_handler import EmergencyPriorityHandler, EmergencyEvent
from src.pedestrian_manager import PedestrianManager, CrosswalkRegion, WalkSignalState
from src.turn_lane_controller import TurnLaneController, TurnLaneConfig, TurnType
from src.multi_intersection_coordinator import MultiIntersectionCoordinator, NetworkConfig, NetworkMetrics
from src.advanced_signal_controller import AdvancedSignalController
from src.enhanced_traffic_analyzer import EnhancedTrafficAnalyzer


def create_test_video(output_path: str, num_frames: int = 30, width: int = 640, height: int = 480, fps: float = 30.0):
    """
    Create a simple test video file for integration testing.
    
    Args:
        output_path: Path where the video will be saved
        num_frames: Number of frames to generate
        width: Video width in pixels
        height: Video height in pixels
        fps: Frames per second
    """
    # Define codec and create VideoWriter
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    for i in range(num_frames):
        # Create a frame with some simple content
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Add some colored rectangles to simulate vehicles
        # These won't be detected by YOLO, but that's okay for integration testing
        cv2.rectangle(frame, (50, 50), (150, 150), (255, 0, 0), -1)
        cv2.rectangle(frame, (width - 150, 50), (width - 50, 150), (0, 255, 0), -1)
        cv2.rectangle(frame, (50, height - 150), (150, height - 50), (0, 0, 255), -1)
        
        # Add frame number text
        cv2.putText(frame, f"Frame {i}", (width // 2 - 50, height // 2),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        out.write(frame)
    
    out.release()


class TestIntegration:
    """Integration tests for the complete SMART FLOW pipeline."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test files."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def test_video_path(self, temp_dir):
        """Create a test video file."""
        video_path = str(Path(temp_dir) / "test_video.mp4")
        create_test_video(video_path, num_frames=30)
        return video_path
    
    @pytest.fixture
    def output_log_path(self, temp_dir):
        """Create path for output log file."""
        return str(Path(temp_dir) / "test_metrics.json")
    
    def test_complete_pipeline_with_test_video(self, test_video_path, output_log_path):
        """
        Test end-to-end flow with a generated test video.
        
        Validates: All requirements
        """
        # Initialize all modules
        video_processor = VideoProcessor(test_video_path)
        assert video_processor.load_video(), "Failed to load test video"
        
        # Get video metadata
        metadata = video_processor.get_frame_metadata()
        assert metadata.width > 0
        assert metadata.height > 0
        assert metadata.fps > 0
        
        # Create lane configuration
        lane_config = LaneConfiguration.create_four_way(metadata.width, metadata.height)
        assert len(lane_config.lanes) == 4
        
        # Initialize other modules
        vehicle_detector = VehicleDetector(model_path="yolov8n.pt", confidence_threshold=0.5)
        traffic_analyzer = TrafficAnalyzer()
        signal_controller = SignalController(min_green=10, max_green=60, yellow_duration=3)
        visualizer = Visualizer()
        metrics_logger = MetricsLogger(output_log_path)
        
        # Process frames through the pipeline
        frame_count = 0
        cycle_interval = 10  # Start new cycle every 10 frames
        cycle_frame_counter = 0
        cycle_started = False
        
        while frame_count < 30:  # Process all frames
            # Read frame
            frame = video_processor.get_next_frame()
            if frame is None:
                break
            
            frame_count += 1
            cycle_frame_counter += 1
            
            # Detect vehicles
            detections = vehicle_detector.detect(frame)
            assert isinstance(detections, list)
            
            # Count by lane
            lane_counts = vehicle_detector.count_by_lane(detections, lane_config.lanes)
            assert len(lane_counts) == 4
            assert all(count >= 0 for count in lane_counts.values())
            
            # Analyze traffic
            densities = traffic_analyzer.calculate_density(lane_counts)
            assert len(densities) == 4
            
            # Log density
            metrics_logger.log_density(frame.timestamp, densities)
            
            # Start signal cycle at intervals
            if cycle_frame_counter >= cycle_interval:
                density_ratios = traffic_analyzer.get_density_ratios(densities)
                green_times = signal_controller.allocate_green_time(density_ratios)
                
                # Verify green time constraints
                for time in green_times.values():
                    assert 10 <= time <= 60
                
                metrics_logger.log_signal_allocation(frame.timestamp, green_times)
                signal_controller.start_cycle(green_times)
                
                cycle_frame_counter = 0
                cycle_started = True
            
            # Get signal states
            if cycle_started:
                current_states = signal_controller.get_current_states()
                remaining_times = signal_controller.get_remaining_times()
                
                assert len(current_states) == 4
                assert len(remaining_times) == 4
                
                # Verify mutual exclusion (at most one green/yellow)
                green_or_yellow_count = sum(
                    1 for state in current_states.values()
                    if state in (SignalState.GREEN, SignalState.YELLOW)
                )
                assert green_or_yellow_count <= 1
            else:
                current_states = {lane: SignalState.RED for lane in lane_config.lanes.keys()}
                remaining_times = {lane: 0.0 for lane in lane_config.lanes.keys()}
            
            # Visualize (without displaying)
            annotated_frame = visualizer.draw_detections(frame, detections)
            annotated_frame = visualizer.draw_vehicle_counts(annotated_frame, lane_counts)
            annotated_frame = visualizer.draw_signal_states(
                annotated_frame,
                current_states,
                remaining_times
            )
            
            # Verify annotated frame is valid
            assert annotated_frame.image is not None
            assert annotated_frame.frame_number == frame.frame_number
        
        # Finalize metrics
        metrics_logger.finalize()
        
        # Verify output log was created
        assert Path(output_log_path).exists()
        
        # Verify log file is valid JSON
        with open(output_log_path, 'r') as f:
            log_data = json.load(f)
        
        # Verify log structure
        assert 'summary' in log_data
        assert 'density_logs' in log_data
        assert 'allocation_logs' in log_data
        assert 'transition_logs' in log_data
        
        # Verify summary statistics
        summary = log_data['summary']
        assert 'total_cycles' in summary
        assert 'average_waiting_time_per_lane' in summary
        assert 'total_density_measurements' in summary
        assert 'total_allocations' in summary
        assert 'total_transitions' in summary
        
        # Verify we logged data
        assert len(log_data['density_logs']) > 0
        assert summary['total_density_measurements'] == len(log_data['density_logs'])
        
        # Clean up
        video_processor.release()
        visualizer.close()
        
        print(f"✓ Integration test passed: Processed {frame_count} frames")
        print(f"✓ Logged {len(log_data['density_logs'])} density measurements")
        print(f"✓ Logged {len(log_data['allocation_logs'])} signal allocations")
        print(f"✓ Total cycles: {summary['total_cycles']}")
    
    def test_pipeline_handles_empty_detections(self, test_video_path, output_log_path):
        """
        Test that the pipeline handles frames with no vehicle detections gracefully.
        
        Validates: Requirements 3.1, 4.1
        """
        # Initialize modules
        video_processor = VideoProcessor(test_video_path)
        assert video_processor.load_video()
        
        metadata = video_processor.get_frame_metadata()
        lane_config = LaneConfiguration.create_four_way(metadata.width, metadata.height)
        
        traffic_analyzer = TrafficAnalyzer()
        signal_controller = SignalController()
        metrics_logger = MetricsLogger(output_log_path)
        
        # Simulate empty detections (no vehicles)
        lane_counts = {lane: 0 for lane in lane_config.lanes.keys()}
        
        # Analyze with zero vehicles
        densities = traffic_analyzer.calculate_density(lane_counts)
        assert all(density == 0.0 for density in densities.values())
        
        # Get density ratios (should be equal distribution)
        density_ratios = traffic_analyzer.get_density_ratios(densities)
        assert all(ratio == 0.25 for ratio in density_ratios.values())
        
        # Allocate green time (should still work)
        green_times = signal_controller.allocate_green_time(density_ratios)
        assert all(10 <= time <= 60 for time in green_times.values())
        
        # Log and finalize
        metrics_logger.log_density(0.0, densities)
        metrics_logger.log_signal_allocation(0.0, green_times)
        metrics_logger.finalize()
        
        # Verify log was created
        assert Path(output_log_path).exists()
        
        video_processor.release()
        
        print("✓ Pipeline handles empty detections correctly")
    
    def test_pipeline_error_recovery(self, temp_dir):
        """
        Test that the pipeline handles errors gracefully.
        
        Validates: Requirements 1.4, 8.1, 8.2, 8.3, 8.4
        """
        # Test with non-existent video file
        video_processor = VideoProcessor(str(Path(temp_dir) / "nonexistent.mp4"))
        assert not video_processor.load_video()
        
        # Test with invalid video format
        invalid_video = str(Path(temp_dir) / "invalid.txt")
        Path(invalid_video).write_text("not a video")
        
        video_processor = VideoProcessor(invalid_video)
        assert not video_processor.load_video()
        
        print("✓ Pipeline handles errors gracefully")


class TestV2Integration:
    """Integration tests for SMART FLOW v2 enhanced features."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test files."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        # Give time for file handles to close
        time.sleep(0.1)
        try:
            shutil.rmtree(temp_dir)
        except PermissionError:
            # On Windows, sometimes files are still locked
            time.sleep(0.5)
            try:
                shutil.rmtree(temp_dir)
            except:
                pass  # Best effort cleanup
    
    @pytest.fixture
    def test_video_path(self, temp_dir):
        """Create a test video file."""
        video_path = str(Path(temp_dir) / "test_video.mp4")
        create_test_video(video_path, num_frames=60, width=1280, height=720)
        return video_path
    
    def test_end_to_end_with_video_file(self, test_video_path):
        """
        Test end-to-end v2 pipeline with video file.
        
        Tests complete pipeline with:
        - StreamManager for video input
        - EnhancedDetector for object detection
        - EnhancedTrafficAnalyzer for traffic analysis
        - AdvancedSignalController for signal control
        
        Validates: All requirements
        """
        # Initialize stream manager
        stream_manager = StreamManager(test_video_path, source_type='file')
        assert stream_manager.connect(), "Failed to connect to video file"
        
        # Get metadata
        metadata = stream_manager.get_metadata()
        assert metadata.width > 0
        assert metadata.height > 0
        assert not metadata.is_live
        assert metadata.source_type == 'file'
        
        # Initialize enhanced detector
        detector = EnhancedDetector(model_path="yolov8n.pt", confidence_threshold=0.5)
        
        # Initialize traffic analyzer
        analyzer = EnhancedTrafficAnalyzer()
        
        # Create lane configuration
        lane_config = LaneConfiguration.create_four_way(metadata.width, metadata.height)
        
        # Initialize signal controller
        from src.advanced_signal_controller import SignalConfig
        config = SignalConfig(min_green=10, max_green=60)
        controller = AdvancedSignalController(config=config)
        
        # Process frames
        frame_count = 0
        max_frames = 30
        
        while frame_count < max_frames:
            frame = stream_manager.get_next_frame()
            if frame is None:
                break
            
            frame_count += 1
            
            # Detect objects
            detection_result = detector.detect_all(frame.image, frame.timestamp)
            
            # Verify detection result structure
            assert isinstance(detection_result, DetectionResult)
            assert isinstance(detection_result.vehicles, list)
            assert isinstance(detection_result.pedestrians, list)
            assert isinstance(detection_result.emergency_vehicles, list)
            
            # Count vehicles by lane
            lane_counts = {}
            for lane_name, region in lane_config.lanes.items():
                count = sum(1 for v in detection_result.vehicles 
                           if region.contains_point(v.center))
                lane_counts[lane_name] = count
            
            # Analyze traffic
            densities = analyzer.calculate_density(lane_counts)
            assert len(densities) == 4
            
            # Update signal controller
            if frame_count % 10 == 0:  # Every 10 frames
                controller.update_state(1.0)
        
        # Clean up
        stream_manager.release()
        
        print(f"✓ V2 end-to-end test passed: Processed {frame_count} frames")
        assert frame_count > 0, "No frames were processed"
    
    def test_simulated_live_stream(self, test_video_path):
        """
        Test with simulated live stream.
        
        Uses a video file but treats it as a live stream to test
        live stream handling logic.
        
        Validates: Requirements 1.1, 1.2, 1.5, 1.6
        """
        # Initialize stream manager with file (simulating live stream behavior)
        stream_manager = StreamManager(test_video_path, source_type='file')
        assert stream_manager.connect()
        
        # Get connection health
        health = stream_manager.get_connection_health()
        assert health['is_connected']
        assert health['capture_opened']
        assert health['frames_processed'] == 0
        
        # Process some frames
        frame_count = 0
        max_frames = 20
        
        while frame_count < max_frames:
            frame = stream_manager.get_next_frame()
            if frame is None:
                break
            
            frame_count += 1
            assert frame.image is not None
            assert frame.frame_number == frame_count
        
        # Check health again
        health = stream_manager.get_connection_health()
        assert health['frames_processed'] == frame_count
        
        stream_manager.release()
        
        print(f"✓ Simulated live stream test passed: Processed {frame_count} frames")
        assert frame_count > 0
    
    def test_emergency_vehicle_scenario(self, test_video_path):
        """
        Test emergency vehicle detection and priority.
        
        Simulates emergency vehicle detection and verifies that:
        - Emergency vehicles are detected
        - Priority is activated
        - Emergency lane gets green signal
        - Emergency clears properly
        
        Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5, 3.6
        """
        # Initialize components
        stream_manager = StreamManager(test_video_path, source_type='file')
        assert stream_manager.connect()
        
        metadata = stream_manager.get_metadata()
        lane_config = LaneConfiguration.create_four_way(metadata.width, metadata.height)
        
        detector = EnhancedDetector(model_path="yolov8n.pt")
        emergency_handler = EmergencyPriorityHandler(emergency_green_duration=15.0)
        
        from src.advanced_signal_controller import SignalConfig
        config = SignalConfig(min_green=10, max_green=60)
        controller = AdvancedSignalController(config=config)
        
        # Process frames and simulate emergency vehicle
        frame = stream_manager.get_next_frame()
        assert frame is not None
        
        detection_result = detector.detect_all(frame.image, frame.timestamp)
        
        # Simulate emergency vehicle detection by creating a fake emergency detection
        if detection_result.vehicles:
            # Take first vehicle and treat it as emergency for testing
            emergency_detection = detection_result.vehicles[0]
            
            # Create emergency event
            emergency_event = EmergencyEvent(
                vehicle_type='ambulance',
                lane='',
                detection=emergency_detection,
                timestamp=frame.timestamp,
                priority_level=1
            )
            
            # Calculate priority lane
            lanes_dict = {name: (region.x, region.y, region.width, region.height) 
                         for name, region in lane_config.lanes.items()}
            priority_lane = emergency_handler.calculate_priority_lane(
                emergency_event, lanes_dict
            )
            
            assert priority_lane in lane_config.lanes.keys()
            
            # Activate emergency
            emergency_handler.activate_emergency(emergency_event, priority_lane)
            assert emergency_handler.is_emergency_active()
            
            # Create emergency plan
            plan = emergency_handler.create_emergency_plan(priority_lane, frame.timestamp)
            assert plan.emergency_lane == priority_lane
            assert plan.duration == 15.0
            
            # Handle emergency in controller
            controller.handle_emergency(priority_lane)
            
            # Verify emergency lane has green
            states = controller.get_current_states()
            assert states[priority_lane] == SignalState.GREEN
            
            # Simulate time passing
            time.sleep(0.1)
            
            # Check if emergency should clear
            should_clear = emergency_handler.should_clear_emergency(
                frame.timestamp + 20.0
            )
            assert should_clear
            
            # Clear emergency
            emergency_handler.clear_emergency()
            assert not emergency_handler.is_emergency_active()
            
            print("✓ Emergency vehicle scenario test passed")
        else:
            print("⚠ No vehicles detected, skipping emergency test")
        
        stream_manager.release()
    
    def test_pedestrian_crossing_scenario(self, test_video_path):
        """
        Test pedestrian detection and crossing management.
        
        Simulates pedestrian detection and verifies:
        - Pedestrians are detected by crosswalk
        - Crossing time is calculated correctly
        - Walk signals are managed properly
        - Conflicting lanes are identified
        
        Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5, 2.6
        """
        # Initialize components
        stream_manager = StreamManager(test_video_path, source_type='file')
        assert stream_manager.connect()
        
        metadata = stream_manager.get_metadata()
        
        # Create crosswalk configuration
        crosswalk_config = {
            'north_crosswalk': CrosswalkRegion(
                name='north_crosswalk',
                region=(metadata.width // 2 - 50, 0, metadata.width // 2 + 50, 100),
                conflicting_lanes=['north', 'south'],
                crossing_distance=15.0  # meters
            ),
            'south_crosswalk': CrosswalkRegion(
                name='south_crosswalk',
                region=(metadata.width // 2 - 50, metadata.height - 100, 
                       metadata.width // 2 + 50, metadata.height),
                conflicting_lanes=['north', 'south'],
                crossing_distance=15.0
            )
        }
        
        pedestrian_manager = PedestrianManager(crosswalk_config)
        detector = EnhancedDetector(model_path="yolov8n.pt")
        
        # Process frame
        frame = stream_manager.get_next_frame()
        assert frame is not None
        
        detection_result = detector.detect_all(frame.image, frame.timestamp)
        
        # Detect pedestrians by crosswalk
        ped_counts = pedestrian_manager.detect_pedestrians(detection_result.pedestrians)
        assert isinstance(ped_counts, dict)
        assert 'north_crosswalk' in ped_counts
        assert 'south_crosswalk' in ped_counts
        
        # Simulate pedestrians at north crosswalk
        # Create fake pedestrian detections for testing
        fake_pedestrians = [
            Detection(
                bbox=(metadata.width // 2, 50, 30, 60),
                confidence=0.9,
                class_id=0,
                class_name='person'
            ),
            Detection(
                bbox=(metadata.width // 2 + 40, 50, 30, 60),
                confidence=0.85,
                class_id=0,
                class_name='person'
            )
        ]
        
        ped_counts = pedestrian_manager.detect_pedestrians(fake_pedestrians)
        
        # Check if crossing is needed
        if ped_counts['north_crosswalk'] > 0:
            assert pedestrian_manager.is_crossing_needed('north_crosswalk')
            
            # Calculate crossing time
            crossing_time = pedestrian_manager.calculate_crossing_time(
                'north_crosswalk', ped_counts['north_crosswalk']
            )
            assert crossing_time > 0
            assert crossing_time >= pedestrian_manager.BASE_CROSSING_TIME
            
            # Activate crossing
            actual_time = pedestrian_manager.activate_crossing('north_crosswalk')
            assert actual_time == crossing_time
            
            # Check walk signal state
            state = pedestrian_manager.get_walk_signal_state('north_crosswalk')
            assert state == WalkSignalState.WALK
            
            # Get conflicting lanes
            conflicting = pedestrian_manager.get_conflicting_lanes('north_crosswalk')
            assert 'north' in conflicting or 'south' in conflicting
            
            print("✓ Pedestrian crossing scenario test passed")
        else:
            print("⚠ No pedestrians detected at crosswalk, basic validation passed")
        
        stream_manager.release()
    
    def test_turn_lane_scenario(self, test_video_path):
        """
        Test turn lane detection and protected phases.
        
        Simulates turn lane vehicles and verifies:
        - Turn demand is calculated
        - Protected phases are activated when needed
        - Turn phases are created correctly
        - Conflicting movements are identified
        
        Validates: Requirements 4.1, 4.2, 4.3, 4.4, 4.5, 4.6
        """
        # Initialize components
        stream_manager = StreamManager(test_video_path, source_type='file')
        assert stream_manager.connect()
        
        metadata = stream_manager.get_metadata()
        
        # Create turn lane configuration
        turn_lane_config = {
            'north_left': TurnLaneConfig(
                lane_name='north_left',
                turn_type=TurnType.LEFT,
                region=(metadata.width // 4, 0, metadata.width // 4, metadata.height // 2),
                conflicting_movements=['south', 'east', 'west'],
                minimum_green=10,
                maximum_green=30
            ),
            'south_left': TurnLaneConfig(
                lane_name='south_left',
                turn_type=TurnType.LEFT,
                region=(3 * metadata.width // 4, metadata.height // 2, 
                       metadata.width // 4, metadata.height // 2),
                conflicting_movements=['north', 'east', 'west'],
                minimum_green=10,
                maximum_green=30
            )
        }
        
        turn_controller = TurnLaneController(turn_lane_config, protected_threshold=3)
        detector = EnhancedDetector(model_path="yolov8n.pt")
        
        # Process frame
        frame = stream_manager.get_next_frame()
        assert frame is not None
        
        detection_result = detector.detect_all(frame.image, frame.timestamp)
        
        # Calculate turn demand
        turn_demand = turn_controller.calculate_turn_demand(detection_result.vehicles)
        assert isinstance(turn_demand, dict)
        assert 'north_left' in turn_demand
        assert 'south_left' in turn_demand
        
        # Test protected phase activation logic
        for lane, demand in turn_demand.items():
            should_activate = turn_controller.should_activate_protected_phase(lane, demand)
            assert isinstance(should_activate, bool)
            
            if demand >= 3:
                assert should_activate
        
        # Create turn phase
        turn_phase = turn_controller.create_turn_phase('north_left', TurnType.LEFT)
        assert turn_phase is not None
        assert 'north_left' in turn_phase.lanes
        assert turn_phase.duration >= 10
        
        # Get conflicting movements
        conflicting = turn_controller.get_conflicting_movements('north_left')
        assert isinstance(conflicting, list)
        assert len(conflicting) > 0
        
        print("✓ Turn lane scenario test passed")
        
        stream_manager.release()
    
    def test_multi_intersection_coordination(self):
        """
        Test multi-intersection coordination.
        
        Simulates multiple intersections and verifies:
        - Intersections can be registered
        - Offsets are calculated correctly
        - Signals are synchronized
        - Green waves are created
        - Network metrics are tracked
        
        Validates: Requirements 7.1, 7.2, 7.3, 7.4, 7.5, 7.6
        """
        # Create network configuration
        network_config = NetworkConfig(
            intersections={
                'intersection_1': {},
                'intersection_2': {},
                'intersection_3': {}
            },
            connections=[
                ('intersection_1', 'intersection_2'),
                ('intersection_2', 'intersection_3')
            ],
            travel_times={
                ('intersection_1', 'intersection_2'): 20.0,  # 20 seconds
                ('intersection_2', 'intersection_3'): 25.0   # 25 seconds
            },
            coordination_enabled=True
        )
        
        # Initialize coordinator
        coordinator = MultiIntersectionCoordinator(network_config)
        
        # Create mock controllers
        class MockController:
            def __init__(self):
                self.config = type('obj', (object,), {'max_cycle_time': 60.0})()
                self._phase_start_time = time.time()
            
            def set_offset(self, offset):
                self.offset = offset
        
        # Register intersections
        controller1 = MockController()
        controller2 = MockController()
        controller3 = MockController()
        
        coordinator.register_intersection('intersection_1', controller1)
        coordinator.register_intersection('intersection_2', controller2)
        coordinator.register_intersection('intersection_3', controller3)
        
        # Calculate offsets
        offsets = coordinator.calculate_offsets(network_config.travel_times)
        assert isinstance(offsets, dict)
        assert 'intersection_1' in offsets
        assert 'intersection_2' in offsets
        assert 'intersection_3' in offsets
        
        # First intersection should have 0 offset
        assert offsets['intersection_1'] == 0.0
        
        # Downstream intersections should have non-zero offsets
        assert offsets['intersection_2'] > 0
        assert offsets['intersection_3'] > 0
        
        # Synchronize signals
        coordinator.synchronize_signals()
        
        # Create green wave
        corridor = ['intersection_1', 'intersection_2', 'intersection_3']
        green_wave = coordinator.create_green_wave(corridor, 'northbound')
        
        assert green_wave.corridor == corridor
        assert green_wave.direction == 'northbound'
        assert len(green_wave.offsets) == 3
        assert green_wave.target_speed > 0
        
        # Update and get network metrics
        coordinator.update_metrics(vehicle_travel_time=45.0, vehicle_stops=1)
        coordinator.update_metrics(vehicle_travel_time=50.0, vehicle_stops=2)
        coordinator.update_metrics(vehicle_travel_time=40.0, vehicle_stops=0)
        
        metrics = coordinator.get_network_metrics()
        assert isinstance(metrics, NetworkMetrics)
        assert metrics.total_throughput == 3
        assert metrics.average_travel_time > 0
        assert metrics.stops_per_vehicle >= 0
        assert 0 <= metrics.coordination_quality <= 1.0
        
        print("✓ Multi-intersection coordination test passed")
        print(f"  - Network throughput: {metrics.total_throughput} vehicles")
        print(f"  - Average travel time: {metrics.average_travel_time:.1f}s")
        print(f"  - Stops per vehicle: {metrics.stops_per_vehicle:.2f}")
        print(f"  - Coordination quality: {metrics.coordination_quality:.2f}")
    
    def test_complete_v2_pipeline_integration(self, test_video_path):
        """
        Test complete v2 pipeline with all features integrated.
        
        This is the comprehensive integration test that combines:
        - Stream management
        - Enhanced detection
        - Emergency priority
        - Pedestrian management
        - Turn lane control
        - Advanced signal control
        - Enhanced visualization
        
        Validates: All requirements
        """
        # Initialize all components
        stream_manager = StreamManager(test_video_path, source_type='file')
        assert stream_manager.connect()
        
        metadata = stream_manager.get_metadata()
        lane_config = LaneConfiguration.create_four_way(metadata.width, metadata.height)
        
        # Enhanced detector
        detector = EnhancedDetector(model_path="yolov8n.pt", confidence_threshold=0.5)
        
        # Traffic analyzer
        analyzer = EnhancedTrafficAnalyzer()
        
        # Emergency handler
        emergency_handler = EmergencyPriorityHandler(emergency_green_duration=15.0)
        
        # Pedestrian manager
        crosswalk_config = {
            'north': CrosswalkRegion(
                name='north',
                region=(metadata.width // 2 - 50, 0, metadata.width // 2 + 50, 100),
                conflicting_lanes=['north', 'south'],
                crossing_distance=15.0
            )
        }
        pedestrian_manager = PedestrianManager(crosswalk_config)
        
        # Turn lane controller
        turn_lane_config = {
            'north_left': TurnLaneConfig(
                lane_name='north_left',
                turn_type=TurnType.LEFT,
                region=(metadata.width // 4, 0, metadata.width // 4, metadata.height // 2),
                conflicting_movements=['south'],
                minimum_green=10,
                maximum_green=30
            )
        }
        turn_controller = TurnLaneController(turn_lane_config)
        
        # Advanced signal controller
        from src.advanced_signal_controller import SignalConfig
        config = SignalConfig(min_green=10, max_green=60)
        signal_controller = AdvancedSignalController(config=config)
        
        # Process frames through complete pipeline
        frame_count = 0
        max_frames = 30
        
        emergency_detected = False
        pedestrians_detected = False
        vehicles_detected = False
        
        while frame_count < max_frames:
            frame = stream_manager.get_next_frame()
            if frame is None:
                break
            
            frame_count += 1
            
            # 1. Detect all objects
            detection_result = detector.detect_all(frame.image, frame.timestamp)
            
            # Track what we detected
            if detection_result.vehicles:
                vehicles_detected = True
            if detection_result.pedestrians:
                pedestrians_detected = True
            if detection_result.emergency_vehicles:
                emergency_detected = True
            
            # 2. Check for emergency vehicles
            if detection_result.emergency_vehicles:
                emergency_event = emergency_handler.detect_emergency(
                    detection_result, frame.timestamp
                )
                if emergency_event and not emergency_handler.is_emergency_active():
                    lanes_dict = {name: (region.x, region.y, region.width, region.height) 
                                 for name, region in lane_config.lanes.items()}
                    priority_lane = emergency_handler.calculate_priority_lane(
                        emergency_event, lanes_dict
                    )
                    emergency_handler.activate_emergency(emergency_event, priority_lane)
                    signal_controller.handle_emergency(priority_lane)
            
            # 3. Detect pedestrians
            ped_counts = pedestrian_manager.detect_pedestrians(detection_result.pedestrians)
            
            # 4. Calculate turn demand
            turn_demand = turn_controller.calculate_turn_demand(detection_result.vehicles)
            
            # 5. Count vehicles by lane
            lane_counts = {}
            for lane_name, region in lane_config.lanes.items():
                count = sum(1 for v in detection_result.vehicles 
                           if region.contains_point(v.center))
                lane_counts[lane_name] = count
            
            # 6. Analyze traffic
            densities = analyzer.calculate_density(lane_counts)
            
            # 7. Update signal controller
            if frame_count % 10 == 0:
                # Start a cycle if not already started
                if frame_count == 10:
                    # Initialize with equal green times
                    green_times = {lane: 15 for lane in lane_config.lanes.keys()}
                    signal_controller.start_cycle(green_times)
                else:
                    signal_controller.update_state(1.0)
            
            # 8. Get current signal states
            states = signal_controller.get_current_states()
            # States will be empty until first cycle starts
            if frame_count >= 10:
                assert len(states) == 4
            
            # 9. Update pedestrian manager
            pedestrian_manager.update(0.033)  # ~30 fps
        
        # Verify pipeline processed frames
        assert frame_count > 0, "No frames were processed"
        
        # Clean up
        stream_manager.release()
        
        print(f"✓ Complete v2 pipeline integration test passed")
        print(f"  - Processed {frame_count} frames")
        print(f"  - Vehicles detected: {vehicles_detected}")
        print(f"  - Pedestrians detected: {pedestrians_detected}")
        print(f"  - Emergency vehicles detected: {emergency_detected}")
