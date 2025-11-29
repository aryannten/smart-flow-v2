# Requirements Document

## Introduction

SMART FLOW is an AI-powered adaptive traffic signal simulation system that optimizes traffic movement at intersections. The system uses computer vision and deep learning to analyze pre-recorded traffic video, detect vehicles, calculate lane-wise density, and simulate dynamic signal timing decisions. This MVP demonstrates the core intelligence of adaptive traffic management without requiring physical traffic light hardware.

## Glossary

- **System**: The SMART FLOW traffic signal simulation application
- **Lane**: A single directional traffic path at an intersection (North, South, East, West)
- **Vehicle Density**: The count of vehicles detected in a specific lane during an analysis window
- **Signal Cycle**: A complete sequence of signal states (green, yellow, red) across all lanes
- **Green Time**: The duration a lane receives a green signal, measured in seconds
- **Detection Frame**: A single video frame processed for vehicle detection
- **YOLO Model**: The You Only Look Once deep learning model used for vehicle detection
- **Bounding Box**: A rectangular region drawn around a detected vehicle
- **Intersection**: The four-way junction where lanes meet and traffic signals control flow

## Requirements

### Requirement 1

**User Story:** As a traffic engineer, I want the system to process pre-recorded intersection video, so that I can analyze traffic patterns and validate the adaptive signal logic.

#### Acceptance Criteria

1. WHEN a user provides a video file path THEN the System SHALL load and validate the video file format
2. WHEN the video is loaded THEN the System SHALL extract frames sequentially for processing
3. WHEN a frame is extracted THEN the System SHALL maintain the original video resolution and frame rate metadata
4. IF the video file is corrupted or unsupported THEN the System SHALL report an error and terminate gracefully
5. WHILE processing video frames THEN the System SHALL track the current frame number and timestamp

### Requirement 2

**User Story:** As a traffic engineer, I want the system to detect and count vehicles in each lane, so that I can understand real-time traffic density.

#### Acceptance Criteria

1. WHEN a frame is processed THEN the System SHALL apply the YOLO Model to detect all vehicles in the frame
2. WHEN vehicles are detected THEN the System SHALL draw Bounding Boxes around each detected vehicle
3. WHEN vehicles are detected THEN the System SHALL classify each detection by Lane based on spatial position
4. WHEN vehicles are classified by Lane THEN the System SHALL increment the vehicle count for that Lane
5. WHEN detection confidence is below a threshold THEN the System SHALL exclude that detection from the count
6. WHILE processing frames THEN the System SHALL maintain separate vehicle counts for each of the four Lanes

### Requirement 3

**User Story:** As a traffic engineer, I want the system to calculate traffic density for each lane, so that I can identify which lanes are most congested.

#### Acceptance Criteria

1. WHEN vehicle counts are updated THEN the System SHALL calculate Vehicle Density for each Lane
2. WHEN calculating density THEN the System SHALL compare all four Lane densities to identify the maximum
3. WHEN densities are equal THEN the System SHALL apply a consistent tie-breaking rule
4. WHEN density calculation completes THEN the System SHALL store the results with timestamp metadata

### Requirement 4

**User Story:** As a traffic engineer, I want the system to dynamically allocate signal timing based on traffic density, so that congested lanes receive more green time.

#### Acceptance Criteria

1. WHEN a Signal Cycle begins THEN the System SHALL determine Green Time allocation for each Lane based on Vehicle Density
2. WHEN allocating Green Time THEN the System SHALL assign longer duration to Lanes with higher Vehicle Density
3. WHEN allocating Green Time THEN the System SHALL ensure minimum Green Time of 10 seconds for any Lane
4. WHEN allocating Green Time THEN the System SHALL ensure maximum Green Time of 60 seconds for any Lane
5. WHEN Green Time is allocated THEN the System SHALL calculate yellow and red signal durations according to traffic engineering standards

### Requirement 5

**User Story:** As a traffic engineer, I want the system to simulate traffic signal state changes, so that I can visualize how the adaptive logic controls the intersection.

#### Acceptance Criteria

1. WHEN the simulation starts THEN the System SHALL initialize all Lanes to red signal state
2. WHEN a Lane receives Green Time allocation THEN the System SHALL transition that Lane to green state
3. WHEN Green Time expires THEN the System SHALL transition the Lane to yellow state for 3 seconds
4. WHEN yellow time expires THEN the System SHALL transition the Lane to red state
5. WHEN a Lane is in green or yellow state THEN the System SHALL keep all other Lanes in red state
6. WHEN signal states change THEN the System SHALL log the transition with timestamp and Lane identifier

### Requirement 6

**User Story:** As a traffic engineer, I want the system to display real-time visualization of detections and signal states, so that I can monitor system behavior during simulation.

#### Acceptance Criteria

1. WHEN processing each Detection Frame THEN the System SHALL render Bounding Boxes on the video output
2. WHEN rendering output THEN the System SHALL display current vehicle count for each Lane
3. WHEN rendering output THEN the System SHALL display current signal state (red, yellow, green) for each Lane
4. WHEN rendering output THEN the System SHALL display remaining time for the current signal state
5. WHEN rendering output THEN the System SHALL update the display at the video frame rate
6. WHEN the user closes the display window THEN the System SHALL terminate the simulation gracefully

### Requirement 7

**User Story:** As a traffic engineer, I want the system to log simulation metrics, so that I can analyze performance and validate the adaptive algorithm.

#### Acceptance Criteria

1. WHEN the simulation runs THEN the System SHALL log Vehicle Density measurements for each Lane at each Signal Cycle
2. WHEN signal timing decisions are made THEN the System SHALL log the allocated Green Time for each Lane
3. WHEN the simulation completes THEN the System SHALL calculate and log average waiting time per Lane
4. WHEN the simulation completes THEN the System SHALL calculate and log total Signal Cycles executed
5. WHEN logging data THEN the System SHALL write logs to a structured file format (JSON or CSV)

### Requirement 8

**User Story:** As a developer, I want the system to have a modular architecture, so that components can be tested and extended independently.

#### Acceptance Criteria

1. WHEN the System is designed THEN the video processing module SHALL be independent of the detection module
2. WHEN the System is designed THEN the detection module SHALL be independent of the signal timing module
3. WHEN the System is designed THEN the signal timing module SHALL be independent of the visualization module
4. WHEN modules interact THEN the System SHALL use well-defined interfaces with clear input and output contracts
