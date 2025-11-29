# Implementation Plan

- [x] 1. Set up project structure and dependencies





  - Create directory structure: `src/`, `tests/`, `data/`, `logs/`
  - Create `requirements.txt` with opencv-python, ultralytics, numpy, pytest, hypothesis
  - Create main entry point `main.py`
  - Set up basic project configuration
  - _Requirements: 8.1, 8.2, 8.3, 8.4_

- [x] 2. Implement core data models






  - [x] 2.1 Create data model classes

    - Define `Frame`, `FrameMetadata`, `Detection`, `Region`, `LaneConfiguration` dataclasses
    - Define `SignalState` enum (RED, YELLOW, GREEN)
    - _Requirements: 2.2, 2.3_

  - [x] 2.2 Write property test for frame metadata preservation


    - **Property 2: Frame metadata preservation**
    - **Validates: Requirements 1.3**

- [x] 3. Implement Video Processor module





  - [x] 3.1 Create VideoProcessor class


    - Implement `__init__`, `load_video`, `get_next_frame`, `get_frame_metadata`, `release` methods
    - Add video format validation
    - Handle file I/O errors gracefully
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

  - [x] 3.2 Write property test for frame extraction order


    - **Property 1: Video frame extraction preserves order**
    - **Validates: Requirements 1.2**


  - [x] 3.3 Write property test for invalid video rejection

    - **Property 3: Invalid video rejection**
    - **Validates: Requirements 1.4**

  - [x] 3.4 Write unit tests for VideoProcessor


    - Test loading valid video files
    - Test error handling for missing files
    - Test frame extraction and metadata
    - _Requirements: 1.1, 1.2, 1.3, 1.4_

- [x] 4. Implement Vehicle Detector module





  - [x] 4.1 Create VehicleDetector class


    - Implement `__init__` with YOLO model loading
    - Implement `detect` method using ultralytics YOLO
    - Implement `count_by_lane` method with spatial classification
    - Add confidence threshold filtering
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6_

  - [x] 4.2 Write property test for detection bounding boxes


    - **Property 4: Detection produces bounding boxes**
    - **Validates: Requirements 2.2**

  - [x] 4.3 Write property test for lane classification


    - **Property 5: Lane classification is exhaustive and exclusive**
    - **Validates: Requirements 2.3**

  - [x] 4.4 Write property test for vehicle counting


    - **Property 6: Vehicle counting increments correctly**
    - **Validates: Requirements 2.4**

  - [x] 4.5 Write property test for confidence filtering


    - **Property 7: Low confidence detections are filtered**
    - **Validates: Requirements 2.5**

  - [x] 4.6 Write unit tests for VehicleDetector


    - Test YOLO model loading
    - Test detection on sample frames
    - Test lane classification logic
    - _Requirements: 2.1, 2.3, 2.5_

- [x] 5. Implement Traffic Analyzer module





  - [x] 5.1 Create TrafficAnalyzer class


    - Implement `calculate_density` method
    - Implement `identify_max_density_lane` method
    - Implement `get_density_ratios` method
    - Add tie-breaking logic for equal densities
    - _Requirements: 3.1, 3.2, 3.3, 3.4_

  - [x] 5.2 Write property test for density calculation


    - **Property 8: Density calculation completeness**
    - **Validates: Requirements 3.1**

  - [x] 5.3 Write property test for maximum density identification


    - **Property 9: Maximum density identification**
    - **Validates: Requirements 3.2**

  - [x] 5.4 Write property test for tie-breaking consistency


    - **Property 10: Tie-breaking consistency**
    - **Validates: Requirements 3.3**

  - [x] 5.5 Write unit tests for TrafficAnalyzer


    - Test density calculation with various counts
    - Test max identification with clear winner
    - Test tie-breaking with equal densities
    - _Requirements: 3.1, 3.2, 3.3_

- [x] 6. Implement Signal Controller module





  - [x] 6.1 Create SignalController class


    - Implement `__init__` with timing parameters
    - Implement `allocate_green_time` method with proportional algorithm
    - Implement signal state machine in `update_state` method
    - Implement `get_current_states` method
    - Implement `start_cycle` method
    - Add min/max green time constraints (10-60 seconds)
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 5.1, 5.2, 5.3, 5.4, 5.5, 5.6_

  - [x] 6.2 Write property test for green time proportionality


    - **Property 11: Green time proportional to density**
    - **Validates: Requirements 4.2**

  - [x] 6.3 Write property test for green time bounds


    - **Property 12: Green time bounds enforcement**
    - **Validates: Requirements 4.3, 4.4**

  - [x] 6.4 Write property test for yellow duration


    - **Property 13: Yellow duration is constant**
    - **Validates: Requirements 4.5**

  - [x] 6.5 Write property test for state machine correctness


    - **Property 14: Signal state machine correctness**
    - **Validates: Requirements 5.3, 5.4**

  - [x] 6.6 Write property test for mutual exclusion


    - **Property 15: Mutual exclusion of green signals**
    - **Validates: Requirements 5.5**

  - [x] 6.7 Write unit tests for SignalController


    - Test green time allocation algorithm
    - Test state transitions
    - Test timing constraints
    - Test initial state (all red)
    - _Requirements: 4.1, 4.2, 5.1, 5.2_

- [x] 7. Checkpoint - Ensure all tests pass





  - Ensure all tests pass, ask the user if questions arise.

- [x] 8. Implement Visualizer module





  - [x] 8.1 Create Visualizer class


    - Implement `draw_detections` method with bounding boxes
    - Implement `draw_signal_states` method with colored indicators
    - Implement `draw_vehicle_counts` method with text overlay
    - Implement `display` method with OpenCV window
    - Add color coding: GREEN=#00FF00, YELLOW=#FFFF00, RED=#FF0000
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6_



  - [x] 8.2 Write property test for visualization completeness

    - **Property 17: Visualization completeness**
    - **Validates: Requirements 6.1, 6.2, 6.3, 6.4**

  - [x] 8.3 Write unit tests for Visualizer


    - Test bounding box rendering
    - Test signal state display
    - Test vehicle count overlay
    - _Requirements: 6.1, 6.2, 6.3_

- [x] 9. Implement Metrics Logger module




  - [x] 9.1 Create MetricsLogger class


    - Implement `__init__` with output file path
    - Implement `log_density` method
    - Implement `log_signal_allocation` method
    - Implement `log_state_transition` method
    - Implement `finalize` method with summary statistics
    - Support JSON output format
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 5.6_

  - [x] 9.2 Write property test for state transition logging


    - **Property 16: State transitions are logged**
    - **Validates: Requirements 5.6**

  - [x] 9.3 Write property test for cycle metrics logging


    - **Property 18: Cycle metrics are logged**
    - **Validates: Requirements 7.1, 7.2**

  - [x] 9.4 Write property test for summary statistics


    - **Property 19: Summary statistics completeness**
    - **Validates: Requirements 7.3, 7.4**

  - [x] 9.5 Write property test for log format validity


    - **Property 20: Log format validity**
    - **Validates: Requirements 7.5**

  - [x] 9.6 Write unit tests for MetricsLogger


    - Test log file creation
    - Test JSON format validation
    - Test summary statistics calculation
    - _Requirements: 7.1, 7.2, 7.5_

- [x] 10. Implement main simulation loop





  - [x] 10.1 Create main simulation orchestrator


    - Initialize all modules (VideoProcessor, VehicleDetector, TrafficAnalyzer, SignalController, Visualizer, MetricsLogger)
    - Implement main loop: read frame → detect → analyze → control → visualize → log
    - Add command-line argument parsing for video file path
    - Handle graceful shutdown on window close
    - Add error handling and recovery
    - _Requirements: 1.1, 6.6, 8.1, 8.2, 8.3, 8.4_

  - [x] 10.2 Write integration test for complete pipeline


    - Test end-to-end flow with sample video
    - Verify all modules work together
    - Validate output logs are created
    - _Requirements: All requirements_

- [x] 11. Create sample configuration and test data




  - [x] 11.1 Add lane configuration support


    - Create `LaneConfiguration.create_four_way()` method
    - Define default lane regions (quadrants)
    - Support loading custom configurations from JSON
    - _Requirements: 2.3_

  - [x] 11.2 Add sample video and documentation


    - Create README.md with usage instructions
    - Document command-line arguments
    - Add example video file or download instructions
    - Document expected output format
    - _Requirements: 1.1_

- [x] 12. Final checkpoint - Ensure all tests pass




  - Ensure all tests pass, ask the user if questions arise.
