# Implementation Plan

- [x] 1. Set up enhanced project structure and dependencies





  - Extend existing directory structure with new modules
  - Update requirements.txt with streaming, web framework, and tracking libraries
  - Create configuration files for dashboard and multi-intersection setup
  - Set up development environment for web dashboard (Node.js, React)
  - _Requirements: 14.1, 14.2, 14.3, 14.4_

- [-] 2. Implement Stream Manager for multiple video sources


  - [x] 2.1 Create StreamManager class with unified interface


    - Implement connection logic for files, YouTube Live, RTSP, and webcams
    - Add auto-detection of source type from URL/path
    - Implement frame buffering for live streams
    - _Requirements: 1.1, 1.2, 1.3, 1.4_

  - [x] 2.2 Add reconnection and error handling

    - Implement exponential backoff retry logic
    - Handle network timeouts and connection failures
    - Add connection health monitoring
    - _Requirements: 1.5, 1.6, 15.2_

  - [x] 2.3 Write property test for stream resilience



    - **Property 1: Stream connection resilience**
    - **Validates: Requirements 1.5, 1.6**

  - [x] 2.4 Write property test for multi-source compatibility






    - **Property 2: Multi-source compatibility**
    - **Validates: Requirements 1.1, 1.2, 1.3, 1.4**



  - [x] 2.5 Write unit tests for StreamManager




    - Test file loading
    - Test webcam connection
    - Test RTSP stream connection (mocked)
    - Test YouTube URL parsing
    - Test reconnection logic
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [x] 3. Enhance Object Detector for pedestrians and emergency vehicles




  - [x] 3.1 Extend VehicleDetector to EnhancedDetector


    - Add pedestrian detection using YOLO person class
    - Implement vehicle type classification
    - Add emergency vehicle detection logic
    - Create DetectionResult dataclass
    - _Requirements: 2.1, 3.1, 6.1_

  - [x] 3.2 Implement object tracking


    - Integrate SORT or DeepSORT tracking algorithm
    - Track objects across frames with unique IDs
    - Calculate trajectories and velocities
    - _Requirements: 10.2_

  - [ ]* 3.3 Write property test for pedestrian detection
    - **Property 3: Pedestrian detection completeness**
    - **Validates: Requirements 2.1, 2.2**

  - [ ]* 3.4 Write property test for emergency vehicle detection
    - **Property 6: Emergency vehicle detection**
    - **Validates: Requirements 3.1**

  - [ ]* 3.5 Write property test for vehicle type classification
    - **Property 13: Vehicle type classification**
    - **Validates: Requirements 6.1**

  - [ ]* 3.6 Write unit tests for EnhancedDetector
    - Test pedestrian detection
    - Test emergency vehicle classification
    - Test vehicle type classification
    - Test object tracking
    - _Requirements: 2.1, 3.1, 6.1_

- [x] 4. Implement Queue Estimator




  - [x] 4.1 Create QueueEstimator class


    - Implement queue length calculation from vehicle positions
    - Calculate queue density and metrics
    - Detect queue spillback conditions
    - Predict clearance time
    - _Requirements: 5.1, 5.2, 5.4_

  - [ ]* 4.2 Write property test for queue length estimation
    - **Property 11: Queue length estimation accuracy**
    - **Validates: Requirements 5.1, 5.2**

  - [ ]* 4.3 Write property test for queue-based timing
    - **Property 12: Queue-based timing adjustment**
    - **Validates: Requirements 5.3**

  - [ ]* 4.4 Write unit tests for QueueEstimator
    - Test queue length calculation
    - Test spillback detection
    - Test clearance time prediction
    - _Requirements: 5.1, 5.2, 5.3_

- [x] 5. Implement Pedestrian Manager



  - [x] 5.1 Create PedestrianManager class


    - Implement pedestrian counting by crosswalk
    - Calculate crossing time based on pedestrian count
    - Manage walk signal states
    - Determine when crossing is needed
    - _Requirements: 2.2, 2.3, 2.4, 2.5, 2.6_

  - [ ]* 5.2 Write property test for pedestrian phase allocation
    - **Property 4: Pedestrian phase allocation**
    - **Validates: Requirements 2.3**

  - [ ]* 5.3 Write property test for pedestrian safety
    - **Property 5: Pedestrian safety guarantee**
    - **Validates: Requirements 2.4**

  - [ ]* 5.4 Write unit tests for PedestrianManager
    - Test pedestrian counting
    - Test crossing time calculation
    - Test walk signal state transitions
    - _Requirements: 2.2, 2.3, 2.4_

- [-] 6. Implement Emergency Priority Handler


  - [x] 6.1 Create EmergencyPriorityHandler class




    - Detect emergency vehicles from detections
    - Calculate priority lane for emergency vehicle
    - Create emergency signal plan
    - Track emergency event lifecycle
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6_

  - [ ]* 6.2 Write property test for emergency priority activation
    - **Property 7: Emergency priority activation**
    - **Validates: Requirements 3.2**

  - [ ]* 6.3 Write property test for emergency priority persistence
    - **Property 8: Emergency priority persistence**
    - **Validates: Requirements 3.3**

  - [ ]* 6.4 Write unit tests for EmergencyPriorityHandler
    - Test emergency detection
    - Test priority lane calculation
    - Test emergency plan creation
    - Test event lifecycle
    - _Requirements: 3.1, 3.2, 3.3, 3.4_

- [x] 7. Implement Turn Lane Controller




  - [x] 7.1 Create TurnLaneController class


    - Calculate turn demand from detections
    - Determine when to activate protected phases
    - Create turn signal phases
    - Identify conflicting movements
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6_

  - [ ]* 7.2 Write property test for turn lane detection
    - **Property 9: Turn lane detection**
    - **Validates: Requirements 4.1**

  - [ ]* 7.3 Write property test for protected turn safety
    - **Property 10: Protected turn phase safety**
    - **Validates: Requirements 4.3, 4.4**

  - [ ]* 7.4 Write unit tests for TurnLaneController
    - Test turn demand calculation
    - Test protected phase activation logic
    - Test conflict detection
    - _Requirements: 4.1, 4.2, 4.3_

- [x] 8. Enhance Traffic Analyzer




  - [x] 8.1 Extend TrafficAnalyzer to EnhancedTrafficAnalyzer


    - Integrate queue length into density calculation
    - Implement weighted priority calculation
    - Add congestion trend detection
    - Calculate throughput metrics
    - _Requirements: 5.2, 6.2, 12.2_

  - [ ]* 8.2 Write property test for vehicle type weighting
    - **Property 14: Vehicle type weighting**
    - **Validates: Requirements 6.2, 6.3**

  - [ ]* 8.3 Write property test for throughput calculation
    - **Property 25: Throughput calculation accuracy**
    - **Validates: Requirements 12.2**

  - [ ]* 8.4 Write unit tests for EnhancedTrafficAnalyzer
    - Test weighted priority calculation
    - Test congestion trend detection
    - Test throughput calculation
    - _Requirements: 5.2, 6.2, 12.2_

- [x] 9. Implement Advanced Signal Controller




  - [x] 9.1 Extend SignalController to AdvancedSignalController


    - Implement complex phase management (through, turn, pedestrian)
    - Add emergency override c  apability
    - Implement multi-factor allocation algorithm
    - Add manual override support
    - _Requirements: 4.2, 13.1, 13.2, 13.3, 13.4, 13.5, 13.6_

  - [ ]* 9.2 Write property test for multi-factor allocation
    - **Property 27: Multi-factor allocation**
    - **Validates: Requirements 13.1**

  - [ ]* 9.3 Write property test for starvation prevention
    - **Property 28: Starvation prevention**
    - **Validates: Requirements 13.2**

  - [ ]* 9.4 Write unit tests for AdvancedSignalController
    - Test complex phase sequences
    - Test emergency override
    - Test multi-factor allocation
    - Test manual override
    - _Requirements: 4.2, 13.1, 13.2_

- [x] 10. Checkpoint - Ensure core enhancements work



  - Ensure all tests pass, ask the user if questions arise.

- [-] 11. Implement Multi-Intersection Coordinator


  - [x] 11.1 Create MultiIntersectionCoordinator class



    - Implement intersection registration
    - Calculate signal offsets for coordination
    - Synchronize signals across network
    - Create green wave plans
    - Calculate network-wide metrics
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6_

  - [ ]* 11.2 Write property test for multi-intersection synchronization
    - **Property 15: Multi-intersection synchronization**
    - **Validates: Requirements 7.2, 7.3**

  - [ ]* 11.3 Write property test for green wave effectiveness
    - **Property 16: Green wave effectiveness**
    - **Validates: Requirements 7.3**

  - [ ]* 11.4 Write unit tests for MultiIntersectionCoordinator
    - Test offset calculation
    - Test synchronization logic
    - Test green wave creation
    - Test network metrics
    - _Requirements: 7.1, 7.2, 7.3_

- [-] 12. Enhance Visualizer with advanced features


  - [x] 12.1 Extend Visualizer to EnhancedVisualizer



    - Implement traffic density heatmap rendering
    - Add trajectory visualization for tracked objects
    - Implement queue visualization
    - Add enhanced signal panel with phase information
    - Add metrics overlay
    - Implement split-view and multi-camera layouts
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6_

  - [ ]* 12.2 Write property test for heatmap accuracy
    - **Property 20: Heatmap accuracy**
    - **Validates: Requirements 10.1, 10.3**

  - [ ]* 12.3 Write property test for trajectory continuity
    - **Property 21: Trajectory continuity**
    - **Validates: Requirements 10.2**

  - [ ]* 12.4 Write unit tests for EnhancedVisualizer
    - Test heatmap generation
    - Test trajectory rendering
    - Test queue visualization
    - Test split-view layouts
    - _Requirements: 10.1, 10.2, 10.3, 10.6_

- [ ] 13. Implement Video Writer


  - [x] 13.1 Create VideoWriter class



    - Implement frame writing with OpenCV
    - Handle codec selection and fallback
    - Implement efficient compression
    - Add finalization and cleanup
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_

  - [ ]* 13.2 Write property test for video output completeness
    - **Property 19: Video output completeness**
    - **Validates: Requirements 9.1, 9.2**

  - [ ]* 13.3 Write unit tests for VideoWriter
    - Test frame writing
    - Test codec handling
    - Test finalization
    - _Requirements: 9.1, 9.2, 9.3_

- [ ] 14. Implement time and weather adaptation


  - [x] 14.1 Create TimeWeatherAdapter class



    - Detect time of day and classify as peak/off-peak
    - Implement time-based timing adjustments
    - Add weather condition detection (optional API integration)
    - Implement weather-based timing adjustments
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5, 11.6_

  - [ ]* 14.2 Write property test for time-of-day adaptation
    - **Property 22: Time-of-day adaptation**
    - **Validates: Requirements 11.2, 11.3**

  - [ ]* 14.3 Write property test for weather adaptation
    - **Property 23: Weather adaptation**
    - **Validates: Requirements 11.5**

  - [ ]* 14.4 Write unit tests for TimeWeatherAdapter
    - Test time classification
    - Test time-based adjustments
    - Test weather-based adjustments
    - _Requirements: 11.1, 11.2, 11.3, 11.5_

- [x] 15. Enhance Metrics Logger with comprehensive analytics



  - [x] 15.1 Extend MetricsLogger to EnhancedMetricsLogger


    - Add detection result logging
    - Add queue metrics logging
    - Add emergency event logging
    - Add pedestrian activity logging
    - Add throughput logging
    - Add network metrics logging
    - Implement environmental impact calculation
    - Implement comprehensive report generation
    - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5, 12.6_

  - [ ]* 15.2 Write property test for per-vehicle wait time
    - **Property 24: Per-vehicle wait time tracking**
    - **Validates: Requirements 12.1**

  - [ ]* 15.3 Write property test for fairness metrics
    - **Property 26: Fairness metric calculation**
    - **Validates: Requirements 12.4**

  - [ ]* 15.4 Write unit tests for EnhancedMetricsLogger
    - Test comprehensive logging
    - Test environmental impact calculation
    - Test report generation
    - _Requirements: 12.1, 12.2, 12.3, 12.5_

- [x] 16. Checkpoint - Ensure all backend features work





  - Ensure all tests pass, ask the user if questions arise.

- [x] 17. Implement Web Dashboard backend


  - [x] 17.1 Create FastAPI application



    - Set up FastAPI app with CORS
    - Implement REST API endpoints for status and metrics
    - Implement WebSocket endpoint for live updates
    - Add video streaming endpoint
    - Implement command handling for manual overrides
    - _Requirements: 8.1, 8.2, 8.3, 8.6_

  - [x] 17.2 Create dashboard data manager


    - Implement data aggregation for dashboard
    - Create WebSocket broadcast system
    - Implement command queue for user actions
    - Add alert notification system
    - _Requirements: 8.2, 8.3, 8.4, 8.5_

  - [ ]* 17.3 Write property test for dashboard data freshness
    - **Property 17: Dashboard data freshness**
    - **Validates: Requirements 8.2, 8.3**

  - [ ]* 17.4 Write property test for dashboard control responsiveness
    - **Property 18: Dashboard control responsiveness**
    - **Validates: Requirements 8.6**

  - [x]* 17.5 Write unit tests for dashboard backend
    - Test API endpoints
    - Test WebSocket communication
    - Test command handling
    - _Requirements: 8.1, 8.2, 8.6_

- [x] 18. Implement Web Dashboard frontend




  - [x] 18.1 Set up React application


    - Initialize React project with TypeScript
    - Set up Material-UI or Tailwind CSS
    - Configure routing and state management
    - Set up WebSocket client
    - _Requirements: 8.1_

  - [x] 18.2 Create live video feed component


    - Implement video streaming display
    - Add video controls (play, pause, speed)
    - Implement multi-camera grid view
    - _Requirements: 8.2_

  - [x] 18.3 Create metrics dashboard components


    - Implement real-time metrics cards
    - Create traffic heatmap visualization
    - Add signal state indicators
    - Create throughput and wait time charts
    - _Requirements: 8.3, 8.4, 8.5_

  - [x] 18.4 Create control panel components


    - Implement manual signal override controls
    - Add parameter adjustment sliders
    - Create alert notification display
    - _Requirements: 8.6_

  - [x] 18.5 Create historical data visualization


    - Implement time-series charts
    - Add trend analysis graphs
    - Create comparison views
    - _Requirements: 8.7_

  - [ ]* 18.6 Write integration tests for dashboard
    - Test frontend-backend communication
    - Test WebSocket updates
    - Test user interactions
    - _Requirements: 8.1, 8.2, 8.3, 8.6_

- [x] 19. Integrate all components in enhanced main application




  - [x] 19.1 Update main.py with new components


    - Integrate StreamManager for video input
    - Integrate EnhancedDetector for object detection
    - Integrate all new managers (Pedestrian, Emergency, Turn Lane, Queue)
    - Integrate AdvancedSignalController
    - Integrate EnhancedVisualizer
    - Integrate VideoWriter for output
    - Integrate EnhancedMetricsLogger
    - Add command-line arguments for new features
    - _Requirements: All requirements_

  - [x] 19.2 Add dashboard integration


    - Launch FastAPI server in separate thread
    - Connect dashboard to main processing loop
    - Implement bidirectional communication
    - _Requirements: 8.1, 8.2, 8.6_

  - [x] 19.3 Add multi-intersection support


    - Implement multi-intersection configuration loading
    - Integrate MultiIntersectionCoordinator
    - Add network-wide visualization
    - _Requirements: 7.1, 7.2, 7.3_

  - [x] 19.4 Write integration test for complete pipeline






    - Test end-to-end with video file
    - Test with simulated live stream
    - Test emergency vehicle scenario
    - Test pedestrian crossing scenario
    - Test turn lane scenario
    - Test multi-intersection coordination
    - _Requirements: All requirements_

- [-] 20. Implement error handling and recovery


  - [x] 20.1 Add comprehensive error handling




    - Implement error logging throughout system
    - Add reconnection logic for streams
    - Implement graceful degradation
    - Add resource monitoring and throttling
    - _Requirements: 15.1, 15.2, 15.3, 15.4, 15.5, 15.6_

  - [ ]* 20.2 Write property test for error recovery
    - **Property 29: Error recovery**
    - **Validates: Requirements 15.1, 15.3**

  - [ ]* 20.3 Write property test for graceful degradation
    - **Property 30: Graceful degradation**
    - **Validates: Requirements 15.4**

  - [ ]* 20.4 Write unit tests for error handling
    - Test error logging
    - Test reconnection logic
    - Test degradation behavior
    - _Requirements: 15.1, 15.2, 15.3, 15.4_

- [x] 21. Create configuration system




  - [x] 21.1 Implement configuration file support


    - Create JSON/YAML configuration schema
    - Implement configuration loading and validation
    - Add support for lane configurations
    - Add support for turn lane configurations
    - Add support for crosswalk configurations
    - Add support for network configurations
    - _Requirements: 14.3_

  - [x] 21.2 Create example configurations


    - Create example single intersection config
    - Create example multi-intersection network config
    - Create example with turn lanes and crosswalks
    - Document configuration format
    - _Requirements: 14.3_

- [x] 22. Create comprehensive documentation






  - [x] 22.1 Update README with v2 features

    - Document all new features
    - Add usage examples for each feature 
    - Add configuration guide
    - Add troubleshooting section
    - _Requirements: All requirements_


  - [x] 22.2 Create API documentation

    - Document dashboard API endpoints
    - Document WebSocket protocol
    - Document configuration schema
    - _Requirements: 8.1, 8.2, 8.6_


  - [x] 22.3 Create deployment guide

    - Document installation steps
    - Document dashboard deployment
    - Document multi-intersection setup
    - Add performance tuning guide
    - _Requirements: All requirements_

- [x] 23. Final checkpoint - Ensure all tests pass





  - Ensure all tests pass, ask the user if questions arise.