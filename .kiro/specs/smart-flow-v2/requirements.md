# Requirements Document

## Introduction

SMART FLOW v2 is an advanced AI-powered adaptive traffic signal management system that builds upon the original SMART FLOW with comprehensive enhancements. The system supports live video streams, pedestrian detection, emergency vehicle priority, multi-intersection coordination, turn lane management, real-time web dashboard, and advanced analytics. This version transforms the simulation into a production-ready intelligent traffic management platform.

## Glossary

- **System**: The SMART FLOW v2 traffic signal management application
- **Lane**: A directional traffic path including straight-through and turn lanes
- **Turn Lane**: A dedicated lane for left or right turns at an intersection
- **Vehicle Density**: The count of vehicles detected in a specific lane during an analysis window
- **Signal Cycle**: A complete sequence of signal states across all lanes including turn phases
- **Green Time**: The duration a lane receives a green signal, measured in seconds
- **Protected Turn**: A turn phase where turning vehicles have exclusive right-of-way
- **Detection Frame**: A single video frame processed for object detection
- **YOLO Model**: The You Only Look Once deep learning model used for object detection
- **Pedestrian**: A person detected waiting to cross or crossing the intersection
- **Crosswalk**: A designated pedestrian crossing area at the intersection
- **Emergency Vehicle**: An ambulance, fire truck, or police vehicle requiring priority
- **Live Stream**: Real-time video feed from YouTube Live, webcam, or RTSP source
- **RTSP**: Real-Time Streaming Protocol for network video streams
- **Queue Length**: The spatial extent of vehicles waiting at a red signal
- **Intersection**: The junction where lanes meet and traffic signals control flow
- **Dashboard**: A web-based interface displaying real-time traffic metrics and controls
- **Heatmap**: A visual representation of traffic density using color gradients
- **Trajectory**: The path a vehicle follows through the intersection
- **Throughput**: The number of vehicles passing through the intersection per unit time
- **Vehicle Type**: Classification of vehicles (car, truck, bus, motorcycle, bicycle)
- **Multi-Intersection Network**: A coordinated group of connected intersections
- **Green Wave**: Synchronized signal timing allowing continuous flow across multiple intersections

## Requirements

### Requirement 1

**User Story:** As a traffic engineer, I want the system to support multiple video input sources, so that I can analyze both recorded footage and live traffic streams.

#### Acceptance Criteria

1. WHEN a user provides a local video file path THEN the System SHALL load and process the video file
2. WHEN a user provides a YouTube Live URL THEN the System SHALL connect to the live stream and process frames in real-time
3. WHEN a user provides an RTSP stream URL THEN the System SHALL connect to the network camera and process the live feed
4. WHEN a user provides a webcam device ID THEN the System SHALL capture from the local webcam device
5. IF the video source is unavailable or connection fails THEN the System SHALL report an error and retry or terminate gracefully
6. WHEN processing live streams THEN the System SHALL handle network interruptions and attempt reconnection

### Requirement 2

**User Story:** As a traffic engineer, I want the system to detect pedestrians and manage crosswalk signals, so that pedestrian safety is integrated into traffic management.

#### Acceptance Criteria

1. WHEN a frame is processed THEN the System SHALL detect pedestrians in addition to vehicles
2. WHEN pedestrians are detected near crosswalks THEN the System SHALL classify them by crosswalk location
3. WHEN pedestrians are waiting to cross THEN the System SHALL allocate pedestrian crossing time in the signal cycle
4. WHEN a pedestrian phase is active THEN the System SHALL display a walk signal and ensure conflicting vehicle movements are stopped
5. WHEN no pedestrians are detected THEN the System SHALL skip the pedestrian phase to optimize vehicle flow
6. WHEN the pedestrian crossing time expires THEN the System SHALL transition to a don't-walk signal

### Requirement 3

**User Story:** As a traffic engineer, I want the system to detect emergency vehicles and give them immediate priority, so that emergency response times are minimized.

#### Acceptance Criteria

1. WHEN an emergency vehicle is detected THEN the System SHALL classify it as ambulance, fire truck, or police vehicle
2. WHEN an emergency vehicle approaches the intersection THEN the System SHALL immediately transition the relevant lane to green
3. WHEN an emergency vehicle is given priority THEN the System SHALL hold the green signal until the vehicle clears the intersection
4. WHEN multiple emergency vehicles approach THEN the System SHALL prioritize based on detection order
5. WHEN an emergency vehicle clears the intersection THEN the System SHALL resume normal signal operation
6. WHEN emergency priority is activated THEN the System SHALL log the event with timestamp and vehicle type

### Requirement 4

**User Story:** As a traffic engineer, I want the system to support turn lanes with dedicated signals, so that turning movements are managed safely and efficiently.

#### Acceptance Criteria

1. WHEN lane configuration includes turn lanes THEN the System SHALL detect and count vehicles in turn lanes separately
2. WHEN calculating signal timing THEN the System SHALL allocate time for protected turn phases
3. WHEN a protected left turn phase is active THEN the System SHALL display a green arrow and ensure opposing traffic is stopped
4. WHEN a protected right turn phase is active THEN the System SHALL display a green arrow and ensure conflicting pedestrian crossings are stopped
5. WHEN turn lane demand is low THEN the System SHALL skip the protected phase and allow permissive turns
6. WHEN turn phases complete THEN the System SHALL transition to through-traffic phases

### Requirement 5

**User Story:** As a traffic engineer, I want the system to estimate queue lengths, so that signal timing accounts for spatial congestion in addition to vehicle counts.

#### Acceptance Criteria

1. WHEN vehicles are detected in a lane THEN the System SHALL estimate the spatial extent of the vehicle queue
2. WHEN calculating density THEN the System SHALL incorporate queue length in addition to vehicle count
3. WHEN a queue extends beyond a threshold THEN the System SHALL increase green time allocation for that lane
4. WHEN queue length is measured THEN the System SHALL express it in meters or vehicle-equivalents
5. WHEN queues are forming THEN the System SHALL detect the trend and adjust timing proactively

### Requirement 6

**User Story:** As a traffic engineer, I want the system to classify vehicle types and apply priority weighting, so that public transit and heavy vehicles receive appropriate service.

#### Acceptance Criteria

1. WHEN vehicles are detected THEN the System SHALL classify them as car, truck, bus, motorcycle, or bicycle
2. WHEN calculating lane priority THEN the System SHALL apply weighting factors based on vehicle types
3. WHEN a bus is detected THEN the System SHALL apply higher priority weight to support public transit
4. WHEN bicycles are detected THEN the System SHALL ensure adequate crossing time
5. WHEN heavy trucks are detected THEN the System SHALL account for slower acceleration in timing
6. WHEN vehicle type distribution is logged THEN the System SHALL record counts by type for each lane

### Requirement 7

**User Story:** As a traffic engineer, I want the system to coordinate multiple intersections, so that traffic flows smoothly across a network without stopping at every light.

#### Acceptance Criteria

1. WHEN multiple intersections are configured THEN the System SHALL establish communication between intersection controllers
2. WHEN coordinating intersections THEN the System SHALL calculate optimal offset timing to create green waves
3. WHEN a vehicle clears one intersection THEN the System SHALL ensure the next intersection is green when the vehicle arrives
4. WHEN coordination is active THEN the System SHALL maintain synchronization across the network
5. WHEN network conditions change THEN the System SHALL dynamically adjust coordination parameters
6. WHEN coordination is enabled THEN the System SHALL log network-wide metrics including average travel time

### Requirement 8

**User Story:** As a traffic engineer, I want the system to provide a real-time web dashboard, so that I can monitor traffic conditions and system performance remotely.

#### Acceptance Criteria

1. WHEN the System starts THEN the System SHALL launch a web server hosting the dashboard interface
2. WHEN a user accesses the dashboard THEN the System SHALL display live video feeds with annotations
3. WHEN displaying metrics THEN the System SHALL show real-time vehicle counts, densities, and signal states
4. WHEN displaying analytics THEN the System SHALL show throughput, average wait times, and queue lengths
5. WHEN displaying visualizations THEN the System SHALL render traffic heatmaps and flow diagrams
6. WHEN the user interacts with the dashboard THEN the System SHALL allow manual signal overrides and parameter adjustments
7. WHEN historical data is requested THEN the System SHALL display time-series charts and trend analysis

### Requirement 9

**User Story:** As a traffic engineer, I want the system to save annotated video output, so that I can review and share simulation results.

#### Acceptance Criteria

1. WHEN video output is enabled THEN the System SHALL record processed frames with all annotations
2. WHEN saving video THEN the System SHALL include bounding boxes, counts, signal states, and metrics overlays
3. WHEN video recording completes THEN the System SHALL save the output in a standard format (MP4, AVI)
4. WHEN saving video THEN the System SHALL maintain the original frame rate and resolution
5. WHEN disk space is limited THEN the System SHALL compress video efficiently without significant quality loss

### Requirement 10

**User Story:** As a traffic engineer, I want enhanced visualization features, so that I can better understand traffic patterns and system behavior.

#### Acceptance Criteria

1. WHEN rendering frames THEN the System SHALL display a traffic density heatmap overlay
2. WHEN vehicles are tracked THEN the System SHALL draw trajectory lines showing vehicle paths
3. WHEN displaying congestion THEN the System SHALL use color coding (green=light, yellow=moderate, red=heavy)
4. WHEN showing metrics THEN the System SHALL display throughput rates and average speeds
5. WHEN visualizing queues THEN the System SHALL highlight queue extents with visual indicators
6. WHEN rendering the dashboard THEN the System SHALL provide multiple view modes (split-screen, grid, focus)

### Requirement 11

**User Story:** As a traffic engineer, I want the system to adapt to time-of-day and weather conditions, so that signal timing reflects environmental factors.

#### Acceptance Criteria

1. WHEN the System starts THEN the System SHALL detect the current time of day
2. WHEN operating during peak hours THEN the System SHALL apply aggressive timing to maximize throughput
3. WHEN operating during off-peak hours THEN the System SHALL apply relaxed timing to minimize wait times
4. WHEN weather data is available THEN the System SHALL adjust timing for rain, snow, or fog conditions
5. WHEN visibility is reduced THEN the System SHALL increase yellow phase duration for safety
6. WHEN time or weather changes THEN the System SHALL log the adaptation and its effects

### Requirement 12

**User Story:** As a traffic engineer, I want comprehensive analytics and metrics, so that I can evaluate system performance and identify improvements.

#### Acceptance Criteria

1. WHEN the simulation runs THEN the System SHALL calculate average wait time per vehicle (not just per lane)
2. WHEN measuring throughput THEN the System SHALL record vehicles per hour for each lane and the intersection total
3. WHEN calculating efficiency THEN the System SHALL compute the ratio of green time to total cycle time
4. WHEN measuring fairness THEN the System SHALL track maximum wait time and wait time variance across lanes
5. WHEN estimating environmental impact THEN the System SHALL calculate fuel consumption and CO2 emissions based on idling time
6. WHEN generating reports THEN the System SHALL produce summary statistics, charts, and comparison metrics

### Requirement 13

**User Story:** As a traffic engineer, I want smarter signal allocation algorithms, so that timing decisions optimize multiple objectives simultaneously.

#### Acceptance Criteria

1. WHEN allocating green time THEN the System SHALL consider vehicle count, queue length, wait time, and vehicle type
2. WHEN a lane has been waiting excessively THEN the System SHALL apply a fairness boost to prevent starvation
3. WHEN multiple lanes have similar demand THEN the System SHALL use round-robin with weighted priorities
4. WHEN demand is very low THEN the System SHALL use minimum cycle times to reduce overall delay
5. WHEN demand is very high THEN the System SHALL extend cycle times up to a maximum threshold
6. WHEN allocation decisions are made THEN the System SHALL log the factors and weights used

### Requirement 14

**User Story:** As a developer, I want the system to maintain modular architecture, so that new features can be added without disrupting existing functionality.

#### Acceptance Criteria

1. WHEN new detection types are added THEN the System SHALL integrate them without modifying core detection logic
2. WHEN new video sources are added THEN the System SHALL support them through a common interface
3. WHEN new signal algorithms are added THEN the System SHALL allow selection via configuration
4. WHEN modules interact THEN the System SHALL use well-defined interfaces with clear contracts
5. WHEN the System is extended THEN the System SHALL maintain backward compatibility with existing configurations

### Requirement 15

**User Story:** As a system administrator, I want robust error handling and logging, so that issues can be diagnosed and resolved quickly.

#### Acceptance Criteria

1. WHEN errors occur THEN the System SHALL log detailed error messages with timestamps and context
2. WHEN network connections fail THEN the System SHALL attempt reconnection with exponential backoff
3. WHEN detection fails THEN the System SHALL continue operation with degraded functionality
4. WHEN resources are exhausted THEN the System SHALL gracefully reduce processing load
5. WHEN critical errors occur THEN the System SHALL save state and shut down safely
6. WHEN the System recovers from errors THEN the System SHALL log the recovery and resume normal operation
