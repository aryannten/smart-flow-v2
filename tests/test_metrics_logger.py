"""
Unit tests for MetricsLogger module.
"""
import json
import tempfile
from pathlib import Path
import pytest
from src.metrics_logger import MetricsLogger
from src.models import SignalState


class TestMetricsLogger:
    """Unit tests for MetricsLogger class."""
    
    def test_log_file_creation(self):
        """Test that log file is created when finalize is called."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
            output_path = tmp_file.name
        
        try:
            # Create logger and finalize without logging anything
            logger = MetricsLogger(output_path)
            logger.finalize()
            
            # Verify file exists
            assert Path(output_path).exists(), "Log file should be created"
            
            # Verify file is valid JSON
            with open(output_path, 'r') as f:
                data = json.load(f)
            
            assert isinstance(data, dict), "Log file should contain a JSON object"
            assert 'summary' in data, "Log file should have summary section"
            assert 'density_logs' in data, "Log file should have density_logs section"
            assert 'allocation_logs' in data, "Log file should have allocation_logs section"
            assert 'transition_logs' in data, "Log file should have transition_logs section"
        
        finally:
            Path(output_path).unlink(missing_ok=True)
    
    def test_json_format_validation(self):
        """Test that output is valid JSON format."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
            output_path = tmp_file.name
        
        try:
            logger = MetricsLogger(output_path)
            
            # Log some data
            logger.log_density(0.0, {'north': 10.0, 'south': 5.0, 'east': 8.0, 'west': 3.0})
            logger.log_signal_allocation(1.0, {'north': 20, 'south': 15, 'east': 18, 'west': 12})
            logger.log_state_transition(2.0, 'north', SignalState.RED, SignalState.GREEN)
            
            logger.finalize()
            
            # Verify JSON is valid
            with open(output_path, 'r') as f:
                data = json.load(f)
            
            # Verify structure
            assert isinstance(data['summary'], dict)
            assert isinstance(data['density_logs'], list)
            assert isinstance(data['allocation_logs'], list)
            assert isinstance(data['transition_logs'], list)
            
            # Verify data was logged
            assert len(data['density_logs']) == 1
            assert len(data['allocation_logs']) == 1
            assert len(data['transition_logs']) == 1
        
        finally:
            Path(output_path).unlink(missing_ok=True)
    
    def test_summary_statistics_calculation(self):
        """Test that summary statistics are calculated correctly."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
            output_path = tmp_file.name
        
        try:
            logger = MetricsLogger(output_path)
            
            # Log 3 cycles
            for i in range(3):
                logger.log_signal_allocation(float(i * 100), {
                    'north': 15,
                    'south': 20,
                    'east': 25,
                    'west': 10
                })
            
            # Log some transitions
            logger.log_state_transition(0.0, 'north', SignalState.RED, SignalState.GREEN)
            logger.log_state_transition(15.0, 'north', SignalState.GREEN, SignalState.YELLOW)
            logger.log_state_transition(18.0, 'north', SignalState.YELLOW, SignalState.RED)
            
            logger.finalize()
            
            # Read and verify summary
            with open(output_path, 'r') as f:
                data = json.load(f)
            
            summary = data['summary']
            
            # Verify cycle count
            assert summary['total_cycles'] == 3, "Should have 3 cycles"
            
            # Verify average waiting times exist
            assert 'average_waiting_time_per_lane' in summary
            assert isinstance(summary['average_waiting_time_per_lane'], dict)
            
            # Verify counts
            assert summary['total_allocations'] == 3
            assert summary['total_transitions'] == 3
            assert summary['total_density_measurements'] == 0  # We didn't log any densities
        
        finally:
            Path(output_path).unlink(missing_ok=True)
    
    def test_density_logging(self):
        """Test that density measurements are logged correctly."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
            output_path = tmp_file.name
        
        try:
            logger = MetricsLogger(output_path)
            
            # Log densities
            densities1 = {'north': 10.0, 'south': 5.0, 'east': 8.0, 'west': 3.0}
            densities2 = {'north': 12.0, 'south': 7.0, 'east': 9.0, 'west': 4.0}
            
            logger.log_density(0.0, densities1)
            logger.log_density(10.0, densities2)
            
            logger.finalize()
            
            # Verify logged data
            with open(output_path, 'r') as f:
                data = json.load(f)
            
            density_logs = data['density_logs']
            assert len(density_logs) == 2
            
            # Verify first log
            assert density_logs[0]['timestamp'] == 0.0
            assert density_logs[0]['densities'] == densities1
            
            # Verify second log
            assert density_logs[1]['timestamp'] == 10.0
            assert density_logs[1]['densities'] == densities2
        
        finally:
            Path(output_path).unlink(missing_ok=True)
    
    def test_allocation_logging(self):
        """Test that signal allocations are logged correctly."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
            output_path = tmp_file.name
        
        try:
            logger = MetricsLogger(output_path)
            
            # Log allocations
            green_times1 = {'north': 15, 'south': 20, 'east': 25, 'west': 10}
            green_times2 = {'north': 18, 'south': 22, 'east': 28, 'west': 12}
            
            logger.log_signal_allocation(0.0, green_times1)
            logger.log_signal_allocation(100.0, green_times2)
            
            logger.finalize()
            
            # Verify logged data
            with open(output_path, 'r') as f:
                data = json.load(f)
            
            allocation_logs = data['allocation_logs']
            assert len(allocation_logs) == 2
            
            # Verify first log
            assert allocation_logs[0]['timestamp'] == 0.0
            assert allocation_logs[0]['green_times'] == green_times1
            
            # Verify second log
            assert allocation_logs[1]['timestamp'] == 100.0
            assert allocation_logs[1]['green_times'] == green_times2
        
        finally:
            Path(output_path).unlink(missing_ok=True)
    
    def test_transition_logging(self):
        """Test that state transitions are logged correctly."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
            output_path = tmp_file.name
        
        try:
            logger = MetricsLogger(output_path)
            
            # Log transitions
            logger.log_state_transition(0.0, 'north', SignalState.RED, SignalState.GREEN)
            logger.log_state_transition(15.0, 'north', SignalState.GREEN, SignalState.YELLOW)
            logger.log_state_transition(18.0, 'north', SignalState.YELLOW, SignalState.RED)
            
            logger.finalize()
            
            # Verify logged data
            with open(output_path, 'r') as f:
                data = json.load(f)
            
            transition_logs = data['transition_logs']
            assert len(transition_logs) == 3
            
            # Verify first transition
            assert transition_logs[0]['timestamp'] == 0.0
            assert transition_logs[0]['lane'] == 'north'
            assert transition_logs[0]['old_state'] == 'red'
            assert transition_logs[0]['new_state'] == 'green'
            
            # Verify second transition
            assert transition_logs[1]['timestamp'] == 15.0
            assert transition_logs[1]['old_state'] == 'green'
            assert transition_logs[1]['new_state'] == 'yellow'
            
            # Verify third transition
            assert transition_logs[2]['timestamp'] == 18.0
            assert transition_logs[2]['old_state'] == 'yellow'
            assert transition_logs[2]['new_state'] == 'red'
        
        finally:
            Path(output_path).unlink(missing_ok=True)
    
    def test_waiting_time_calculation(self):
        """Test that waiting times are calculated correctly."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
            output_path = tmp_file.name
        
        try:
            logger = MetricsLogger(output_path)
            
            # Simulate a complete cycle for north lane
            # RED -> GREEN (waiting time = 10 seconds)
            logger.log_state_transition(0.0, 'north', SignalState.GREEN, SignalState.YELLOW)
            logger.log_state_transition(3.0, 'north', SignalState.YELLOW, SignalState.RED)
            logger.log_state_transition(10.0, 'north', SignalState.RED, SignalState.GREEN)
            
            # Another cycle (waiting time = 20 seconds)
            logger.log_state_transition(25.0, 'north', SignalState.GREEN, SignalState.YELLOW)
            logger.log_state_transition(28.0, 'north', SignalState.YELLOW, SignalState.RED)
            logger.log_state_transition(48.0, 'north', SignalState.RED, SignalState.GREEN)
            
            logger.finalize()
            
            # Verify waiting times
            with open(output_path, 'r') as f:
                data = json.load(f)
            
            waiting_times = data['summary']['average_waiting_time_per_lane']
            
            # North lane should have average waiting time of (7 + 20) / 2 = 13.5
            # First wait: 10.0 - 3.0 = 7.0
            # Second wait: 48.0 - 28.0 = 20.0
            assert 'north' in waiting_times
            expected_avg = (7.0 + 20.0) / 2
            assert abs(waiting_times['north'] - expected_avg) < 0.01
        
        finally:
            Path(output_path).unlink(missing_ok=True)
    
    def test_empty_logs(self):
        """Test that logger handles empty logs gracefully."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
            output_path = tmp_file.name
        
        try:
            logger = MetricsLogger(output_path)
            
            # Finalize without logging anything
            logger.finalize()
            
            # Verify file is created and valid
            with open(output_path, 'r') as f:
                data = json.load(f)
            
            # Verify empty logs
            assert len(data['density_logs']) == 0
            assert len(data['allocation_logs']) == 0
            assert len(data['transition_logs']) == 0
            
            # Verify summary with zero counts
            summary = data['summary']
            assert summary['total_cycles'] == 0
            assert summary['total_density_measurements'] == 0
            assert summary['total_allocations'] == 0
            assert summary['total_transitions'] == 0
        
        finally:
            Path(output_path).unlink(missing_ok=True)



class TestEnhancedMetricsLogger:
    """Unit tests for EnhancedMetricsLogger class."""
    
    def test_detection_result_logging(self):
        """Test that detection results are logged correctly."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
            output_path = tmp_file.name
        
        try:
            from src.metrics_logger import EnhancedMetricsLogger
            from src.enhanced_detector import DetectionResult, Detection
            
            logger = EnhancedMetricsLogger(output_path)
            
            # Create mock detection result
            vehicles = [
                Detection(bbox=(10, 10, 50, 50), confidence=0.9, class_id=2, class_name='car'),
                Detection(bbox=(100, 100, 60, 60), confidence=0.85, class_id=7, class_name='truck')
            ]
            pedestrians = [
                Detection(bbox=(200, 200, 30, 60), confidence=0.8, class_id=0, class_name='person')
            ]
            emergency_vehicles = []
            
            result = DetectionResult(
                vehicles=vehicles,
                pedestrians=pedestrians,
                emergency_vehicles=emergency_vehicles,
                timestamp=1.0
            )
            
            # Log detection result
            logger.log_detection_result(1.0, result)
            
            logger.finalize()
            
            # Verify logged data
            with open(output_path, 'r') as f:
                data = json.load(f)
            
            assert 'detection_logs' in data
            assert len(data['detection_logs']) == 1
            
            log = data['detection_logs'][0]
            assert log['timestamp'] == 1.0
            assert log['vehicle_count'] == 2
            assert log['pedestrian_count'] == 1
            assert log['emergency_vehicle_count'] == 0
            assert 'vehicle_types' in log
            assert log['vehicle_types']['car'] == 1
            assert log['vehicle_types']['truck'] == 1
        
        finally:
            Path(output_path).unlink(missing_ok=True)
    
    def test_queue_metrics_logging(self):
        """Test that queue metrics are logged correctly."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
            output_path = tmp_file.name
        
        try:
            from src.metrics_logger import EnhancedMetricsLogger
            from src.queue_estimator import QueueMetrics
            
            logger = EnhancedMetricsLogger(output_path)
            
            # Create mock queue metrics
            queue_metrics = {
                'north': QueueMetrics(
                    length_meters=25.5,
                    vehicle_count=5,
                    density=0.2,
                    head_position=(100, 100),
                    tail_position=(200, 200),
                    is_spillback=False
                ),
                'south': QueueMetrics(
                    length_meters=40.0,
                    vehicle_count=8,
                    density=0.2,
                    head_position=(300, 300),
                    tail_position=(400, 400),
                    is_spillback=True
                )
            }
            
            # Log queue metrics
            logger.log_queue_metrics(2.0, queue_metrics)
            
            logger.finalize()
            
            # Verify logged data
            with open(output_path, 'r') as f:
                data = json.load(f)
            
            assert 'queue_logs' in data
            assert len(data['queue_logs']) == 1
            
            log = data['queue_logs'][0]
            assert log['timestamp'] == 2.0
            assert 'queues' in log
            assert 'north' in log['queues']
            assert 'south' in log['queues']
            
            north_queue = log['queues']['north']
            assert north_queue['length_meters'] == 25.5
            assert north_queue['vehicle_count'] == 5
            assert north_queue['is_spillback'] is False
            
            south_queue = log['queues']['south']
            assert south_queue['length_meters'] == 40.0
            assert south_queue['vehicle_count'] == 8
            assert south_queue['is_spillback'] is True
        
        finally:
            Path(output_path).unlink(missing_ok=True)
    
    def test_emergency_event_logging(self):
        """Test that emergency events are logged correctly."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
            output_path = tmp_file.name
        
        try:
            from src.metrics_logger import EnhancedMetricsLogger
            from src.emergency_priority_handler import EmergencyEvent
            from src.enhanced_detector import Detection
            
            logger = EnhancedMetricsLogger(output_path)
            
            # Create mock emergency event
            detection = Detection(bbox=(50, 50, 80, 80), confidence=0.95, class_id=2, class_name='ambulance')
            event = EmergencyEvent(
                vehicle_type='ambulance',
                lane='north',
                detection=detection,
                timestamp=3.0,
                priority_level=1
            )
            
            # Log emergency event
            logger.log_emergency_event(event)
            
            logger.finalize()
            
            # Verify logged data
            with open(output_path, 'r') as f:
                data = json.load(f)
            
            assert 'emergency_logs' in data
            assert len(data['emergency_logs']) == 1
            
            log = data['emergency_logs'][0]
            assert log['vehicle_type'] == 'ambulance'
            assert log['lane'] == 'north'
            assert log['timestamp'] == 3.0
            assert log['priority_level'] == 1
        
        finally:
            Path(output_path).unlink(missing_ok=True)
    
    def test_pedestrian_activity_logging(self):
        """Test that pedestrian activity is logged correctly."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
            output_path = tmp_file.name
        
        try:
            from src.metrics_logger import EnhancedMetricsLogger
            
            logger = EnhancedMetricsLogger(output_path)
            
            # Log pedestrian activity
            crosswalk_data = {
                'north_crosswalk': 3,
                'south_crosswalk': 5,
                'east_crosswalk': 2,
                'west_crosswalk': 0
            }
            
            logger.log_pedestrian_activity(4.0, crosswalk_data)
            
            logger.finalize()
            
            # Verify logged data
            with open(output_path, 'r') as f:
                data = json.load(f)
            
            assert 'pedestrian_logs' in data
            assert len(data['pedestrian_logs']) == 1
            
            log = data['pedestrian_logs'][0]
            assert log['timestamp'] == 4.0
            assert log['crosswalks']['north_crosswalk'] == 3
            assert log['crosswalks']['south_crosswalk'] == 5
            assert log['crosswalks']['east_crosswalk'] == 2
            assert log['crosswalks']['west_crosswalk'] == 0
        
        finally:
            Path(output_path).unlink(missing_ok=True)
    
    def test_throughput_logging(self):
        """Test that throughput is logged correctly."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
            output_path = tmp_file.name
        
        try:
            from src.metrics_logger import EnhancedMetricsLogger
            
            logger = EnhancedMetricsLogger(output_path)
            
            # Log throughput for multiple lanes
            logger.log_throughput(5.0, 'north', 3)
            logger.log_throughput(5.0, 'south', 2)
            logger.log_throughput(10.0, 'north', 4)
            
            logger.finalize()
            
            # Verify logged data
            with open(output_path, 'r') as f:
                data = json.load(f)
            
            assert 'throughput_logs' in data
            assert len(data['throughput_logs']) == 3
            
            # Verify first log
            assert data['throughput_logs'][0]['timestamp'] == 5.0
            assert data['throughput_logs'][0]['lane'] == 'north'
            assert data['throughput_logs'][0]['count'] == 3
            
            # Verify throughput calculation in report
            assert 'performance' in data
            assert 'throughput_by_lane' in data['performance']
        
        finally:
            Path(output_path).unlink(missing_ok=True)
    
    def test_network_metrics_logging(self):
        """Test that network metrics are logged correctly."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
            output_path = tmp_file.name
        
        try:
            from src.metrics_logger import EnhancedMetricsLogger
            from src.multi_intersection_coordinator import NetworkMetrics
            
            logger = EnhancedMetricsLogger(output_path)
            
            # Create mock network metrics
            metrics = NetworkMetrics(
                average_travel_time=45.5,
                stops_per_vehicle=1.2,
                coordination_quality=0.85,
                total_throughput=150,
                network_delay=5.3
            )
            
            # Log network metrics
            logger.log_network_metrics(6.0, metrics)
            
            logger.finalize()
            
            # Verify logged data
            with open(output_path, 'r') as f:
                data = json.load(f)
            
            assert 'network_logs' in data
            assert len(data['network_logs']) == 1
            
            log = data['network_logs'][0]
            assert log['timestamp'] == 6.0
            assert log['average_travel_time'] == 45.5
            assert log['stops_per_vehicle'] == 1.2
            assert log['coordination_quality'] == 0.85
            assert log['total_throughput'] == 150
            assert log['network_delay'] == 5.3
        
        finally:
            Path(output_path).unlink(missing_ok=True)
    
    def test_environmental_impact_calculation(self):
        """Test that environmental impact is calculated correctly."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
            output_path = tmp_file.name
        
        try:
            from src.metrics_logger import EnhancedMetricsLogger
            from src.queue_estimator import QueueMetrics
            
            logger = EnhancedMetricsLogger(output_path)
            
            # Log queue metrics to accumulate idle time
            for i in range(10):
                queue_metrics = {
                    'north': QueueMetrics(
                        length_meters=20.0,
                        vehicle_count=4,
                        density=0.2,
                        head_position=(100, 100),
                        tail_position=(200, 200),
                        is_spillback=False
                    )
                }
                logger.log_queue_metrics(float(i), queue_metrics)
            
            # Calculate environmental impact
            impact = logger.calculate_environmental_impact()
            
            # Verify calculations
            assert 'total_idle_time' in impact
            assert 'estimated_fuel_consumption' in impact
            assert 'estimated_co2_emissions' in impact
            assert 'emissions_saved_vs_fixed_timing' in impact
            
            # Verify values are reasonable
            assert impact['total_idle_time'] > 0
            assert impact['estimated_fuel_consumption'] > 0
            assert impact['estimated_co2_emissions'] > 0
            assert impact['emissions_saved_vs_fixed_timing'] > 0
            
            # Verify relationship: CO2 = fuel * 2.3
            expected_co2 = impact['estimated_fuel_consumption'] * 2.3
            assert abs(impact['estimated_co2_emissions'] - expected_co2) < 0.01
        
        finally:
            Path(output_path).unlink(missing_ok=True)
    
    def test_comprehensive_report_generation(self):
        """Test that comprehensive report is generated correctly."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
            output_path = tmp_file.name
        
        try:
            from src.metrics_logger import EnhancedMetricsLogger
            from src.enhanced_detector import DetectionResult, Detection
            from src.queue_estimator import QueueMetrics
            
            logger = EnhancedMetricsLogger(output_path)
            
            # Log various metrics
            # Detection results
            vehicles = [Detection(bbox=(10, 10, 50, 50), confidence=0.9, class_id=2, class_name='car')]
            pedestrians = [Detection(bbox=(200, 200, 30, 60), confidence=0.8, class_id=0, class_name='person')]
            result = DetectionResult(vehicles=vehicles, pedestrians=pedestrians, emergency_vehicles=[], timestamp=1.0)
            logger.log_detection_result(1.0, result)
            
            # Queue metrics
            queue_metrics = {
                'north': QueueMetrics(
                    length_meters=25.5,
                    vehicle_count=5,
                    density=0.2,
                    head_position=(100, 100),
                    tail_position=(200, 200),
                    is_spillback=False
                )
            }
            logger.log_queue_metrics(2.0, queue_metrics)
            
            # Throughput
            logger.log_throughput(3.0, 'north', 2)
            
            # Pedestrian activity
            logger.log_pedestrian_activity(4.0, {'north_crosswalk': 3})
            
            # Generate report
            report = logger.generate_report()
            
            # Verify report structure
            assert 'summary' in report
            assert 'performance' in report
            assert 'queue_analysis' in report
            assert 'environmental_impact' in report
            assert 'detection_summary' in report
            assert 'pedestrian_summary' in report
            assert 'network_summary' in report
            
            # Verify summary data
            assert report['summary']['total_vehicles_detected'] == 1
            assert report['summary']['total_pedestrians_detected'] == 1
            
            # Verify queue analysis
            assert 'average_queue_length_by_lane' in report['queue_analysis']
            assert 'north' in report['queue_analysis']['average_queue_length_by_lane']
            
            # Verify environmental impact
            assert 'total_idle_time' in report['environmental_impact']
            assert 'estimated_fuel_consumption' in report['environmental_impact']
        
        finally:
            Path(output_path).unlink(missing_ok=True)
    
    def test_vehicle_tracking(self):
        """Test per-vehicle wait time tracking."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
            output_path = tmp_file.name
        
        try:
            from src.metrics_logger import EnhancedMetricsLogger
            
            logger = EnhancedMetricsLogger(output_path)
            
            # Track vehicles
            logger.track_vehicle(1, 0.0, 'north')
            logger.vehicle_stopped(1)
            logger.vehicle_departed(1, 10.0)
            
            logger.track_vehicle(2, 5.0, 'south')
            logger.vehicle_departed(2, 15.0)
            
            logger.finalize()
            
            # Verify tracked data
            with open(output_path, 'r') as f:
                data = json.load(f)
            
            assert 'vehicle_tracking' in data
            assert '1' in data['vehicle_tracking']
            assert '2' in data['vehicle_tracking']
            
            # Verify vehicle 1
            v1 = data['vehicle_tracking']['1']
            assert v1['entry_time'] == 0.0
            assert v1['exit_time'] == 10.0
            assert v1['wait_time'] == 10.0
            assert v1['stops'] == 1
            assert v1['lane'] == 'north'
            
            # Verify vehicle 2
            v2 = data['vehicle_tracking']['2']
            assert v2['entry_time'] == 5.0
            assert v2['exit_time'] == 15.0
            assert v2['wait_time'] == 10.0
            assert v2['stops'] == 0
            assert v2['lane'] == 'south'
            
            # Verify performance metrics
            assert 'performance' in data
            assert 'average_vehicle_wait_time' in data['performance']
            assert data['performance']['average_vehicle_wait_time'] == 10.0
        
        finally:
            Path(output_path).unlink(missing_ok=True)
    
    def test_finalize_with_all_enhanced_metrics(self):
        """Test that finalize includes all enhanced metrics in output."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
            output_path = tmp_file.name
        
        try:
            from src.metrics_logger import EnhancedMetricsLogger
            
            logger = EnhancedMetricsLogger(output_path)
            
            # Don't log anything, just finalize
            logger.finalize()
            
            # Verify file structure
            with open(output_path, 'r') as f:
                data = json.load(f)
            
            # Verify all sections exist
            assert 'summary' in data
            assert 'performance' in data
            assert 'queue_analysis' in data
            assert 'environmental_impact' in data
            assert 'detection_summary' in data
            assert 'pedestrian_summary' in data
            assert 'network_summary' in data
            
            # Verify all log sections exist
            assert 'density_logs' in data
            assert 'allocation_logs' in data
            assert 'transition_logs' in data
            assert 'detection_logs' in data
            assert 'queue_logs' in data
            assert 'emergency_logs' in data
            assert 'pedestrian_logs' in data
            assert 'throughput_logs' in data
            assert 'network_logs' in data
            assert 'vehicle_tracking' in data
        
        finally:
            Path(output_path).unlink(missing_ok=True)
