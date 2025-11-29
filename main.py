#!/usr/bin/env python3
"""
SMART FLOW v2: AI-Powered Adaptive Traffic Signal Management System

Main entry point for the enhanced traffic signal management application.
Supports live streams, pedestrian detection, emergency vehicles, turn lanes,
multi-intersection coordination, and real-time web dashboard.
"""

import argparse
import sys
import time
from pathlib import Path
from typing import Dict, Optional

# Enhanced v2 components
from src.stream_manager import StreamManager, Frame
from src.enhanced_detector import EnhancedDetector, DetectionResult, VehicleType
from src.enhanced_traffic_analyzer import EnhancedTrafficAnalyzer
from src.advanced_signal_controller import AdvancedSignalController, SignalConfig, LaneData
from src.enhanced_visualizer import EnhancedVisualizer
from src.video_writer import VideoWriter
from src.metrics_logger import MetricsLogger

# Manager components
from src.pedestrian_manager import PedestrianManager, CrosswalkRegion, WalkSignalState
from src.emergency_priority_handler import EmergencyPriorityHandler
from src.turn_lane_controller import TurnLaneController, TurnLaneConfig, TurnType
from src.queue_estimator import QueueEstimator
from src.multi_intersection_coordinator import MultiIntersectionCoordinator, NetworkConfig, NetworkMetrics

# Web Dashboard
from src.web_dashboard import WebDashboard, CommandType

# Error Handler
from src.error_handler import ErrorHandler, ErrorSeverity, SystemState

# Models
from src.models import LaneConfiguration, SignalState, PhaseType
import json


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="SMART FLOW v2 - Enhanced Adaptive Traffic Signal Management System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Local video file
  python main.py --source data/traffic_video.mp4
  
  # YouTube Live stream
  python main.py --source "https://youtube.com/watch?v=..." --live
  
  # RTSP camera
  python main.py --source "rtsp://camera.ip/stream" --live
  
  # Webcam
  python main.py --source "webcam:0" --live
  
  # With video output
  python main.py --source data/video.mp4 --save-video output/annotated.mp4
  
  # With web dashboard
  python main.py --source data/video.mp4 --dashboard --dashboard-port 8080
        """
    )
    
    # Input source
    parser.add_argument(
        '--source',
        type=str,
        required=True,
        help='Video source: file path, YouTube URL, RTSP URL, or webcam:N'
    )
    
    parser.add_argument(
        '--live',
        action='store_true',
        help='Treat source as live stream (enables reconnection logic)'
    )
    
    parser.add_argument(
        '--skip-frames',
        type=int,
        default=0,
        help='Process every Nth frame (0=process all, 2=every other frame, etc.)'
    )
    
    # Output options
    parser.add_argument(
        '--output',
        type=str,
        default='logs/simulation_metrics.json',
        help='Path to metrics log file (default: logs/simulation_metrics.json)'
    )
    
    parser.add_argument(
        '--save-video',
        type=str,
        default=None,
        help='Save annotated video to file (e.g., output/result.mp4)'
    )
    
    # Detection options
    parser.add_argument(
        '--model',
        type=str,
        default='yolov8n.pt',
        help='Path to YOLO model file (default: yolov8n.pt)'
    )
    
    parser.add_argument(
        '--confidence',
        type=float,
        default=0.5,
        help='Detection confidence threshold (0.0-1.0, default: 0.5)'
    )
    
    parser.add_argument(
        '--enhance-night',
        action='store_true',
        help='Enable night/low-light detection enhancement (use for dark videos)'
    )
    
    # Signal control options
    parser.add_argument(
        '--min-green',
        type=int,
        default=10,
        help='Minimum green time in seconds (default: 10)'
    )
    
    parser.add_argument(
        '--max-green',
        type=int,
        default=60,
        help='Maximum green time in seconds (default: 60)'
    )
    
    parser.add_argument(
        '--cycle-interval',
        type=int,
        default=30,
        help='Interval between signal cycles in frames (default: 30)'
    )
    
    # Feature flags
    parser.add_argument(
        '--enable-pedestrians',
        action='store_true',
        help='Enable pedestrian detection and crosswalk management'
    )
    
    parser.add_argument(
        '--enable-emergency',
        action='store_true',
        help='Enable emergency vehicle priority'
    )
    
    parser.add_argument(
        '--enable-turn-lanes',
        action='store_true',
        help='Enable turn lane management'
    )
    
    parser.add_argument(
        '--enable-queue-estimation',
        action='store_true',
        help='Enable queue length estimation'
    )
    
    parser.add_argument(
        '--enable-tracking',
        action='store_true',
        help='Enable object tracking across frames'
    )
    
    # Visualization options
    parser.add_argument(
        '--enable-heatmap',
        action='store_true',
        help='Enable traffic density heatmap visualization'
    )
    
    parser.add_argument(
        '--enable-trajectories',
        action='store_true',
        help='Enable vehicle trajectory visualization'
    )
    
    parser.add_argument(
        '--display-width',
        type=int,
        default=1280,
        help='Maximum display window width (default: 1280)'
    )
    
    parser.add_argument(
        '--display-height',
        type=int,
        default=720,
        help='Maximum display window height (default: 720)'
    )
    
    parser.add_argument(
        '--no-display',
        action='store_true',
        help='Run without displaying video window (headless mode)'
    )
    
    # Dashboard options
    parser.add_argument(
        '--dashboard',
        action='store_true',
        help='Enable web dashboard for real-time monitoring'
    )
    
    parser.add_argument(
        '--dashboard-port',
        type=int,
        default=8080,
        help='Port for web dashboard (default: 8080)'
    )
    
    # Multi-intersection options
    parser.add_argument(
        '--multi-intersection',
        action='store_true',
        help='Enable multi-intersection coordination'
    )
    
    parser.add_argument(
        '--network-config',
        type=str,
        default=None,
        help='Path to network configuration JSON file for multi-intersection'
    )
    
    return parser.parse_args()


def main():
    """Main application loop with enhanced v2 features."""
    args = parse_arguments()
    
    # Create output directory if it doesn't exist
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    print("=" * 70)
    print("SMART FLOW v2 - Enhanced Adaptive Traffic Signal Management")
    print("=" * 70)
    print(f"Source: {args.source}")
    print(f"Output: {args.output}")
    print(f"Model: {args.model}")
    print(f"Confidence Threshold: {args.confidence}")
    print(f"Green Time Range: {args.min_green}-{args.max_green} seconds")
    print()
    print("Enabled Features:")
    print(f"  - Pedestrian Detection: {args.enable_pedestrians}")
    print(f"  - Emergency Priority: {args.enable_emergency}")
    print(f"  - Turn Lanes: {args.enable_turn_lanes}")
    print(f"  - Queue Estimation: {args.enable_queue_estimation}")
    print(f"  - Object Tracking: {args.enable_tracking}")
    print(f"  - Heatmap Visualization: {args.enable_heatmap}")
    print(f"  - Trajectory Visualization: {args.enable_trajectories}")
    print(f"  - Web Dashboard: {args.dashboard}")
    if args.save_video:
        print(f"  - Video Output: {args.save_video}")
    print("=" * 70)
    print()
    
    # Initialize modules
    print("Initializing modules...")
    
    # Initialize error handler
    error_log_path = output_path.parent / "error_log.txt"
    error_handler = ErrorHandler(log_file=str(error_log_path))
    error_handler.start_resource_monitoring(interval=10.0)
    print(f"✓ Error handler initialized")
    print(f"  Error log: {error_log_path}")
    
    try:
        # Initialize StreamManager
        stream_manager = StreamManager(args.source, error_handler=error_handler)
        if not stream_manager.connect():
            print("Error: Failed to connect to video source", file=sys.stderr)
            error_handler.shutdown()
            sys.exit(1)
        
        # Get stream metadata
        metadata = stream_manager.get_metadata()
        print(f"✓ Stream connected: {metadata.width}x{metadata.height} @ {metadata.fps:.1f} FPS")
        print(f"  Source type: {metadata.source_type}, Live: {metadata.is_live}")
        
        # Configure lane regions (simplified 4-way intersection)
        lane_config = LaneConfiguration.create_four_way(metadata.width, metadata.height)
        
        # Initialize EnhancedDetector
        detector = EnhancedDetector(
            model_path=args.model,
            confidence_threshold=args.confidence,
            error_handler=error_handler,
            enhance_night=args.enhance_night
        )
        night_mode = " (night enhancement ON)" if args.enhance_night else ""
        print(f"✓ Enhanced detector initialized{night_mode}")
        
        # Initialize QueueEstimator (if enabled)
        queue_estimator = None
        if args.enable_queue_estimation:
            queue_estimator = QueueEstimator()
            print(f"✓ Queue estimator initialized")
        
        # Initialize PedestrianManager (if enabled)
        pedestrian_manager = None
        if args.enable_pedestrians:
            # Create simple crosswalk configuration
            crosswalk_config = {
                'north': CrosswalkRegion(
                    name='north',
                    region=(metadata.width // 4, 0, metadata.width // 2, metadata.height // 4),
                    conflicting_lanes=['south'],
                    crossing_distance=15.0
                ),
                'south': CrosswalkRegion(
                    name='south',
                    region=(metadata.width // 4, 3 * metadata.height // 4, metadata.width // 2, metadata.height // 4),
                    conflicting_lanes=['north'],
                    crossing_distance=15.0
                )
            }
            pedestrian_manager = PedestrianManager(crosswalk_config)
            print(f"✓ Pedestrian manager initialized")
        
        # Initialize EmergencyPriorityHandler (if enabled)
        emergency_handler = None
        if args.enable_emergency:
            emergency_handler = EmergencyPriorityHandler()
            print(f"✓ Emergency priority handler initialized")
        
        # Initialize TurnLaneController (if enabled)
        turn_controller = None
        if args.enable_turn_lanes:
            # Create simple turn lane configuration
            turn_config = {
                'north_left': TurnLaneConfig(
                    lane_name='north_left',
                    turn_type=TurnType.LEFT,
                    region=(0, 0, metadata.width // 4, metadata.height // 2),
                    conflicting_movements=['south', 'east'],
                    minimum_green=10,
                    maximum_green=30
                )
            }
            turn_controller = TurnLaneController(turn_config)
            print(f"✓ Turn lane controller initialized")
        
        # Initialize EnhancedTrafficAnalyzer
        traffic_analyzer = EnhancedTrafficAnalyzer()
        print(f"✓ Enhanced traffic analyzer initialized")
        
        # Initialize AdvancedSignalController
        signal_config = SignalConfig(
            min_green=args.min_green,
            max_green=args.max_green,
            yellow_duration=3
        )
        signal_controller = AdvancedSignalController(signal_config)
        print(f"✓ Advanced signal controller initialized")
        
        # Initialize EnhancedVisualizer
        visualizer = EnhancedVisualizer(
            enable_heatmap=args.enable_heatmap,
            enable_trajectories=args.enable_trajectories
        )
        # Set display size limits
        visualizer.max_display_width = args.display_width
        visualizer.max_display_height = args.display_height
        print(f"✓ Enhanced visualizer initialized (display: {args.display_width}x{args.display_height})")
        
        # Initialize VideoWriter (if enabled)
        video_writer = None
        if args.save_video:
            video_writer = VideoWriter(
                output_path=args.save_video,
                fps=metadata.fps,
                resolution=(metadata.width, metadata.height)
            )
            print(f"✓ Video writer initialized: {args.save_video}")
        
        # Initialize MetricsLogger
        metrics_logger = MetricsLogger(str(output_path))
        print(f"✓ Metrics logger initialized")
        
        # Initialize MultiIntersectionCoordinator (if enabled)
        coordinator = None
        if args.multi_intersection:
            if args.network_config and Path(args.network_config).exists():
                # Load network configuration from file
                with open(args.network_config, 'r') as f:
                    config_data = json.load(f)
                
                network_config = NetworkConfig(
                    intersections=config_data.get('intersections', {}),
                    connections=[(c['from'], c['to']) for c in config_data.get('connections', [])],
                    travel_times={(c['from'], c['to']): c['time'] for c in config_data.get('connections', [])},
                    coordination_enabled=config_data.get('coordination_enabled', True)
                )
                
                coordinator = MultiIntersectionCoordinator(network_config)
                # Register this intersection as the main one
                coordinator.register_intersection('main', signal_controller)
                print(f"✓ Multi-intersection coordinator initialized")
                print(f"  Network config: {args.network_config}")
            else:
                # Create simple default network configuration
                network_config = NetworkConfig(
                    intersections={'main': {}},
                    connections=[],
                    travel_times={},
                    coordination_enabled=True
                )
                coordinator = MultiIntersectionCoordinator(network_config)
                coordinator.register_intersection('main', signal_controller)
                print(f"✓ Multi-intersection coordinator initialized (single intersection mode)")
        
        # Initialize WebDashboard (if enabled)
        dashboard = None
        if args.dashboard:
            dashboard = WebDashboard(port=args.dashboard_port, error_handler=error_handler)
            dashboard.start()
            print(f"✓ Web dashboard started on port {args.dashboard_port}")
            print(f"  Access at: http://localhost:{args.dashboard_port}")
        
        print()
        print("Starting simulation...")
        if not args.no_display:
            print("Press ESC or close the window to stop.")
        print()
        
        # Simulation state
        frame_count = 0
        cycle_frame_counter = 0
        last_update_time = time.time()
        cycle_started = False
        tracked_objects = []
        
        # Main simulation loop
        while True:
            # Check system state
            system_state = error_handler.get_system_state()
            if system_state == SystemState.SHUTDOWN:
                print("\nSystem shutdown requested")
                break
            elif system_state == SystemState.CRITICAL:
                print("\nWarning: System in CRITICAL state")
                error_summary = error_handler.get_error_summary()
                print(f"  Degraded components: {error_summary['degraded_components']}")
                print(f"  Recent error rate: {error_summary['error_rate']:.1f} errors/min")
            
            # Check if should throttle
            if error_handler.should_throttle():
                metrics = error_handler.get_resource_metrics()
                if metrics:
                    print(f"Throttling: CPU={metrics.cpu_percent:.1f}%, Memory={metrics.memory_percent:.1f}%")
                time.sleep(0.1)  # Throttle processing
            
            # Read next frame
            frame = stream_manager.get_next_frame()
            
            if frame is None:
                if stream_manager.is_live():
                    print("Warning: Stream interrupted, attempting reconnection...")
                    if stream_manager.reconnect():
                        continue
                    else:
                        print("Error: Failed to reconnect to stream")
                        error_handler.handle_exception(
                            component="Main",
                            operation="stream_reconnect",
                            exception=RuntimeError("Failed to reconnect to stream"),
                            severity=ErrorSeverity.CRITICAL
                        )
                        break
                else:
                    print("\nEnd of video reached.")
                    break
            
            frame_count += 1
            
            # Skip frames if configured (for performance)
            if args.skip_frames > 0 and frame_count % (args.skip_frames + 1) != 0:
                # Still display the frame but skip detection
                if not args.no_display:
                    should_continue = visualizer.display(frame)
                    if not should_continue:
                        print("\nSimulation stopped by user.")
                        break
                continue
            
            cycle_frame_counter += 1
            
            # Detect all objects (vehicles, pedestrians, emergency vehicles)
            detection_result = detector.detect_all(frame.image, frame.timestamp)
            
            # Track objects (if enabled)
            if args.enable_tracking:
                all_detections = detection_result.vehicles + detection_result.pedestrians
                tracked_objects = detector.track_objects(all_detections, metadata.fps)
            
            # Count vehicles by lane
            lane_counts = {}
            for lane_name, region in lane_config.lanes.items():
                count = 0
                for detection in detection_result.vehicles:
                    if region.contains_point(detection.center):
                        count += 1
                lane_counts[lane_name] = count
            
            # Estimate queue lengths (if enabled)
            queue_metrics = {}
            if queue_estimator:
                for lane_name, region in lane_config.lanes.items():
                    lane_detections = [d for d in detection_result.vehicles 
                                     if region.contains_point(d.center)]
                    queue_metrics[lane_name] = queue_estimator.estimate_queue(lane_detections, lane_name)
            
            # Detect pedestrians by crosswalk (if enabled)
            pedestrian_counts = {}
            if pedestrian_manager:
                pedestrian_counts = pedestrian_manager.detect_pedestrians(detection_result.pedestrians)
                pedestrian_manager.update(1.0 / metadata.fps)
            
            # Check for emergency vehicles (if enabled)
            emergency_event = None
            if emergency_handler and detection_result.emergency_vehicles:
                emergency_event = emergency_handler.detect_emergency(detection_result, frame.timestamp)
                if emergency_event:
                    emergency_lane = emergency_handler.calculate_priority_lane(
                        emergency_event,
                        {name: (region.x, region.y, region.width, region.height) 
                         for name, region in lane_config.lanes.items()}
                    )
                    emergency_handler.activate_emergency(emergency_event, emergency_lane)
                    print(f"⚠ EMERGENCY: {emergency_event.vehicle_type} detected in lane {emergency_lane}")
            
            # Calculate turn demand (if enabled)
            turn_demand = {}
            if turn_controller:
                turn_demand = turn_controller.calculate_turn_demand(detection_result.vehicles)
            
            # Analyze traffic
            densities = traffic_analyzer.calculate_density(lane_counts)
            
            # Log density measurements
            metrics_logger.log_density(frame.timestamp, densities)
            
            # Start new signal cycle at intervals
            if cycle_frame_counter >= args.cycle_interval:
                # Build lane data for advanced allocation
                lane_data = {}
                for lane_name in lane_config.lanes.keys():
                    # Classify vehicle types
                    vehicle_types = {}
                    for detection in detection_result.vehicles:
                        if lane_config.lanes[lane_name].contains_point(detection.center):
                            vtype = detector.classify_vehicle_type(detection)
                            type_name = vtype.value
                            vehicle_types[type_name] = vehicle_types.get(type_name, 0) + 1
                    
                    lane_data[lane_name] = LaneData(
                        vehicle_count=lane_counts.get(lane_name, 0),
                        queue_length=queue_metrics.get(lane_name, type('obj', (), {'length_meters': 0.0})).length_meters if queue_metrics else 0.0,
                        wait_time=0.0,  # Would be calculated from tracking data
                        vehicle_types=vehicle_types,
                        has_emergency=(emergency_handler and emergency_handler.is_emergency_active() and 
                                     emergency_handler.get_active_emergency().lane == lane_name) if emergency_handler else False,
                        pedestrian_count=pedestrian_counts.get(lane_name, 0)
                    )
                
                # Handle emergency priority
                if emergency_handler and emergency_handler.is_emergency_active():
                    active_emergency = emergency_handler.get_active_emergency()
                    signal_controller.handle_emergency(active_emergency.lane)
                else:
                    # Normal allocation
                    signal_plan = signal_controller.allocate_time(lane_data)
                    
                    # Add pedestrian phases if needed
                    if pedestrian_manager:
                        for crosswalk, count in pedestrian_counts.items():
                            if pedestrian_manager.is_crossing_needed(crosswalk):
                                signal_controller.add_pedestrian_phase(crosswalk, count)
                    
                    # Add turn phases if needed
                    if turn_controller:
                        for turn_lane, demand in turn_demand.items():
                            if turn_controller.should_activate_protected_phase(turn_lane, demand):
                                turn_phase = turn_controller.create_turn_phase(turn_lane, TurnType.LEFT)
                                signal_controller.add_turn_phase(turn_lane, turn_phase.phase_type, demand)
                
                # Reset cycle counter
                cycle_frame_counter = 0
                cycle_started = True
            
            # Update signal states
            if cycle_started:
                current_time = time.time()
                elapsed = current_time - last_update_time
                last_update_time = current_time
                
                transitions = signal_controller.update_state(elapsed)
                
                # Log state transitions
                for transition in transitions:
                    metrics_logger.log_state_transition(
                        frame.timestamp,
                        transition.lane,
                        transition.old_state,
                        transition.new_state
                    )
                
                # Synchronize signals across network (if coordinator enabled)
                if coordinator:
                    coordinator.synchronize_signals()
                
                # Check if emergency should be cleared
                if emergency_handler and emergency_handler.should_clear_emergency(current_time):
                    emergency_handler.clear_emergency()
                    signal_controller.clear_emergency()
                    print("✓ Emergency cleared, resuming normal operation")
            
            # Get current signal states
            current_states = signal_controller.get_current_states()
            remaining_times = signal_controller.get_remaining_times()
            
            # Visualize results
            annotated_frame = frame
            
            # Draw detections
            annotated_frame = visualizer.draw_detections_enhanced(annotated_frame, detection_result)
            
            # Draw heatmap (if enabled)
            if args.enable_heatmap:
                annotated_frame = visualizer.draw_heatmap(annotated_frame, densities)
            
            # Draw trajectories (if enabled)
            if args.enable_trajectories and tracked_objects:
                annotated_frame = visualizer.draw_trajectories(annotated_frame, tracked_objects)
            
            # Draw queue visualization (if enabled)
            if queue_metrics:
                annotated_frame = visualizer.draw_queue_visualization(annotated_frame, queue_metrics)
            
            # Draw signal panel
            current_plan = signal_controller.get_current_plan()
            phases = current_plan.phases if current_plan else []
            annotated_frame = visualizer.draw_signal_panel(
                annotated_frame,
                current_states,
                phases,
                remaining_times
            )
            
            # Draw metrics overlay
            metrics = {
                'frame': frame_count,
                'vehicles': len(detection_result.vehicles),
                'pedestrians': len(detection_result.pedestrians),
                'emergency': len(detection_result.emergency_vehicles),
                'tracked': len(tracked_objects) if tracked_objects else 0
            }
            annotated_frame = visualizer.draw_metrics_overlay(annotated_frame, metrics)
            
            # Update dashboard (if enabled)
            if dashboard:
                # Update video feed
                dashboard.update_video_feed(annotated_frame.image)
                
                # Update metrics
                dashboard_metrics = {
                    'timestamp': frame.timestamp,
                    'frame_count': frame_count,
                    'total_vehicles': len(detection_result.vehicles),
                    'total_pedestrians': len(detection_result.pedestrians),
                    'emergency_vehicles': len(detection_result.emergency_vehicles),
                    'tracked_objects': len(tracked_objects) if tracked_objects else 0,
                    'lane_counts': lane_counts,
                    'densities': densities,
                    'signal_states': {k: v.value for k, v in current_states.items()},
                }
                
                # Add queue metrics if available
                if queue_metrics:
                    dashboard_metrics['queue_lengths'] = {
                        k: v.length_meters for k, v in queue_metrics.items()
                    }
                
                # Add network metrics if coordinator enabled
                if coordinator:
                    network_metrics = coordinator.get_network_metrics()
                    dashboard_metrics['network'] = {
                        'average_travel_time': network_metrics.average_travel_time,
                        'stops_per_vehicle': network_metrics.stops_per_vehicle,
                        'coordination_quality': network_metrics.coordination_quality,
                        'total_throughput': network_metrics.total_throughput,
                        'network_delay': network_metrics.network_delay
                    }
                
                dashboard.update_metrics(dashboard_metrics)
                
                # Process user commands from dashboard
                commands = dashboard.get_user_commands()
                for command in commands:
                    if command.command_type == CommandType.OVERRIDE_SIGNAL:
                        # Handle signal override
                        lane = command.target
                        state_str = command.value.get('state', 'red')
                        duration = command.value.get('duration', 30.0)
                        
                        # Convert string to SignalState
                        state_map = {'red': SignalState.RED, 'yellow': SignalState.YELLOW, 'green': SignalState.GREEN}
                        state = state_map.get(state_str.lower(), SignalState.RED)
                        
                        signal_controller.override_signal(lane, state, duration)
                        dashboard.broadcast_alert(f"Signal override: {lane} set to {state_str} for {duration}s", "info")
                        print(f"Dashboard command: Override {lane} to {state_str} for {duration}s")
                    
                    elif command.command_type == CommandType.ADJUST_PARAMETER:
                        # Handle parameter adjustment
                        param = command.target
                        value = command.value
                        dashboard.broadcast_alert(f"Parameter adjustment: {param} = {value}", "info")
                        print(f"Dashboard command: Adjust {param} to {value}")
            
            # Save to video (if enabled)
            if video_writer:
                video_writer.write_frame(annotated_frame.image)
            
            # Display frame (unless in headless mode)
            if not args.no_display:
                should_continue = visualizer.display(annotated_frame)
                if not should_continue:
                    print("\nSimulation stopped by user.")
                    break
            
            # Print progress every 30 frames
            if frame_count % 30 == 0:
                total_vehicles = len(detection_result.vehicles)
                total_pedestrians = len(detection_result.pedestrians)
                print(f"Frame {frame_count}: Vehicles: {total_vehicles}, "
                      f"Pedestrians: {total_pedestrians}, "
                      f"Emergency: {len(detection_result.emergency_vehicles)}")
        
        # Finalize and save
        print("\nFinalizing...")
        
        if video_writer:
            video_writer.finalize()
            print(f"✓ Video saved to: {args.save_video}")
        
        metrics_logger.finalize()
        print(f"✓ Metrics saved to: {args.output}")
        
        # Stop dashboard
        if dashboard:
            dashboard.stop()
            print(f"✓ Dashboard stopped")
        
        # Clean up
        stream_manager.release()
        visualizer.close()
        
        # Print error summary
        error_summary = error_handler.get_error_summary()
        print(f"\nError Summary:")
        print(f"  Total errors: {error_summary['total_errors']}")
        print(f"  Recent errors: {error_summary['recent_errors']}")
        print(f"  Final system state: {error_summary['system_state']}")
        if error_summary['degraded_components']:
            print(f"  Degraded components: {error_summary['degraded_components']}")
        
        # Shutdown error handler
        error_handler.shutdown()
        
        print("\nSimulation complete!")
        return 0
        
    except KeyboardInterrupt:
        print("\n\nSimulation interrupted by user (Ctrl+C)")
        
        # Attempt to save
        try:
            if video_writer:
                video_writer.finalize()
            metrics_logger.finalize()
            if dashboard:
                dashboard.stop()
            print(f"✓ Data saved")
        except Exception as e:
            print(f"Warning: Failed to save data: {e}")
            if 'error_handler' in locals():
                error_handler.handle_exception(
                    component="Main",
                    operation="save_on_interrupt",
                    exception=e,
                    severity=ErrorSeverity.WARNING
                )
        
        # Clean up
        try:
            stream_manager.release()
            visualizer.close()
            if 'error_handler' in locals():
                error_handler.shutdown()
        except:
            pass
        
        return 0
        
    except Exception as e:
        print(f"\nError during simulation: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        
        # Log error
        if 'error_handler' in locals():
            error_handler.handle_exception(
                component="Main",
                operation="simulation",
                exception=e,
                severity=ErrorSeverity.CRITICAL
            )
        
        # Clean up
        try:
            if 'stream_manager' in locals():
                stream_manager.release()
            if 'visualizer' in locals():
                visualizer.close()
            if 'video_writer' in locals():
                video_writer.finalize()
            if 'dashboard' in locals():
                dashboard.stop()
            if 'error_handler' in locals():
                # Print error summary before shutdown
                error_summary = error_handler.get_error_summary()
                print(f"\nError Summary:")
                print(f"  Total errors: {error_summary['total_errors']}")
                print(f"  System state: {error_summary['system_state']}")
                error_handler.shutdown()
        except:
            pass
        
        return 1


if __name__ == "__main__":
    sys.exit(main())
