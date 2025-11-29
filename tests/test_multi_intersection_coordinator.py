"""
Unit tests for MultiIntersectionCoordinator
"""

import pytest
from src.multi_intersection_coordinator import (
    MultiIntersectionCoordinator,
    NetworkConfig,
    NetworkMetrics,
    CoordinationPlan
)


class MockController:
    """Mock signal controller for testing"""
    def __init__(self, cycle_time=60.0):
        self.config = type('Config', (), {'max_cycle_time': cycle_time})()
        self._phase_start_time = 0.0
        self.offset = 0.0
    
    def set_offset(self, offset: float):
        self.offset = offset


def test_coordinator_initialization():
    """Test coordinator initialization"""
    config = NetworkConfig(
        intersections={'A': {}, 'B': {}},
        connections=[('A', 'B')],
        travel_times={('A', 'B'): 30.0},
        coordination_enabled=True
    )
    
    coordinator = MultiIntersectionCoordinator(config)
    
    assert coordinator.network_config == config
    assert len(coordinator._controllers) == 0
    assert len(coordinator._offsets) == 0


def test_register_intersection():
    """Test intersection registration"""
    config = NetworkConfig(
        intersections={'A': {}, 'B': {}},
        connections=[('A', 'B')],
        travel_times={('A', 'B'): 30.0},
        coordination_enabled=True
    )
    
    coordinator = MultiIntersectionCoordinator(config)
    controller_a = MockController()
    controller_b = MockController()
    
    coordinator.register_intersection('A', controller_a)
    coordinator.register_intersection('B', controller_b)
    
    assert 'A' in coordinator._controllers
    assert 'B' in coordinator._controllers
    assert coordinator._controllers['A'] == controller_a
    assert coordinator._controllers['B'] == controller_b
    assert coordinator._offsets['A'] == 0.0
    assert coordinator._offsets['B'] == 0.0


def test_register_invalid_intersection():
    """Test registering intersection not in config"""
    config = NetworkConfig(
        intersections={'A': {}},
        connections=[],
        travel_times={},
        coordination_enabled=True
    )
    
    coordinator = MultiIntersectionCoordinator(config)
    controller = MockController()
    
    with pytest.raises(ValueError, match="not in network configuration"):
        coordinator.register_intersection('B', controller)


def test_calculate_offsets_simple():
    """Test offset calculation for simple two-intersection network"""
    config = NetworkConfig(
        intersections={'A': {}, 'B': {}},
        connections=[('A', 'B')],
        travel_times={('A', 'B'): 30.0},
        coordination_enabled=True
    )
    
    coordinator = MultiIntersectionCoordinator(config)
    
    # Register controllers
    coordinator.register_intersection('A', MockController(60.0))
    coordinator.register_intersection('B', MockController(60.0))
    
    # Calculate offsets
    travel_times = {('A', 'B'): 30.0}
    offsets = coordinator.calculate_offsets(travel_times)
    
    # First intersection should have offset 0
    assert offsets['A'] == 0.0
    
    # Second intersection should have offset equal to travel time
    assert offsets['B'] == 30.0


def test_calculate_offsets_three_intersections():
    """Test offset calculation for three intersections in a line"""
    config = NetworkConfig(
        intersections={'A': {}, 'B': {}, 'C': {}},
        connections=[('A', 'B'), ('B', 'C')],
        travel_times={('A', 'B'): 20.0, ('B', 'C'): 25.0},
        coordination_enabled=True
    )
    
    coordinator = MultiIntersectionCoordinator(config)
    
    # Register controllers
    coordinator.register_intersection('A', MockController(60.0))
    coordinator.register_intersection('B', MockController(60.0))
    coordinator.register_intersection('C', MockController(60.0))
    
    # Calculate offsets
    travel_times = {('A', 'B'): 20.0, ('B', 'C'): 25.0}
    offsets = coordinator.calculate_offsets(travel_times)
    
    assert offsets['A'] == 0.0
    assert offsets['B'] == 20.0
    assert offsets['C'] == 45.0  # 20 + 25


def test_calculate_offsets_with_cycle_wrap():
    """Test offset calculation with cycle time wrapping"""
    config = NetworkConfig(
        intersections={'A': {}, 'B': {}},
        connections=[('A', 'B')],
        travel_times={('A', 'B'): 70.0},
        coordination_enabled=True
    )
    
    coordinator = MultiIntersectionCoordinator(config)
    
    # Register controllers with 60s cycle time
    coordinator.register_intersection('A', MockController(60.0))
    coordinator.register_intersection('B', MockController(60.0))
    
    # Calculate offsets
    travel_times = {('A', 'B'): 70.0}
    offsets = coordinator.calculate_offsets(travel_times)
    
    assert offsets['A'] == 0.0
    # 70 % 60 = 10
    assert offsets['B'] == 10.0


def test_calculate_offsets_empty():
    """Test offset calculation with no travel times"""
    config = NetworkConfig(
        intersections={'A': {}, 'B': {}},
        connections=[],
        travel_times={},
        coordination_enabled=True
    )
    
    coordinator = MultiIntersectionCoordinator(config)
    
    offsets = coordinator.calculate_offsets({})
    
    # Should return zero offsets for all intersections
    assert offsets['A'] == 0.0
    assert offsets['B'] == 0.0


def test_synchronize_signals():
    """Test signal synchronization"""
    config = NetworkConfig(
        intersections={'A': {}, 'B': {}},
        connections=[('A', 'B')],
        travel_times={('A', 'B'): 30.0},
        coordination_enabled=True
    )
    
    coordinator = MultiIntersectionCoordinator(config)
    
    # Register controllers
    controller_a = MockController()
    controller_b = MockController()
    coordinator.register_intersection('A', controller_a)
    coordinator.register_intersection('B', controller_b)
    
    # Calculate offsets
    coordinator.calculate_offsets({('A', 'B'): 30.0})
    
    # Synchronize
    coordinator.synchronize_signals()
    
    # Check offsets were applied
    assert controller_a.offset == 0.0
    assert controller_b.offset == 30.0


def test_synchronize_signals_disabled():
    """Test that synchronization doesn't happen when disabled"""
    config = NetworkConfig(
        intersections={'A': {}, 'B': {}},
        connections=[('A', 'B')],
        travel_times={('A', 'B'): 30.0},
        coordination_enabled=False  # Disabled
    )
    
    coordinator = MultiIntersectionCoordinator(config)
    
    # Register controllers
    controller_a = MockController()
    controller_b = MockController()
    coordinator.register_intersection('A', controller_a)
    coordinator.register_intersection('B', controller_b)
    
    # Calculate offsets
    coordinator.calculate_offsets({('A', 'B'): 30.0})
    
    # Synchronize (should do nothing)
    coordinator.synchronize_signals()
    
    # Offsets should not be applied
    assert controller_a.offset == 0.0
    assert controller_b.offset == 0.0


def test_create_green_wave():
    """Test green wave creation"""
    config = NetworkConfig(
        intersections={'A': {}, 'B': {}, 'C': {}},
        connections=[('A', 'B'), ('B', 'C')],
        travel_times={('A', 'B'): 20.0, ('B', 'C'): 25.0},
        coordination_enabled=True
    )
    
    coordinator = MultiIntersectionCoordinator(config)
    
    # Register controllers
    coordinator.register_intersection('A', MockController(60.0))
    coordinator.register_intersection('B', MockController(60.0))
    coordinator.register_intersection('C', MockController(60.0))
    
    # Create green wave
    corridor = ['A', 'B', 'C']
    plan = coordinator.create_green_wave(corridor, 'northbound')
    
    assert isinstance(plan, CoordinationPlan)
    assert plan.corridor == corridor
    assert plan.direction == 'northbound'
    assert 'A' in plan.offsets
    assert 'B' in plan.offsets
    assert 'C' in plan.offsets
    assert plan.target_speed > 0
    assert plan.cycle_time == 60.0


def test_create_green_wave_empty_corridor():
    """Test green wave creation with empty corridor"""
    config = NetworkConfig(
        intersections={'A': {}},
        connections=[],
        travel_times={},
        coordination_enabled=True
    )
    
    coordinator = MultiIntersectionCoordinator(config)
    
    with pytest.raises(ValueError, match="must contain at least one intersection"):
        coordinator.create_green_wave([], 'northbound')


def test_create_green_wave_invalid_intersection():
    """Test green wave creation with invalid intersection"""
    config = NetworkConfig(
        intersections={'A': {}},
        connections=[],
        travel_times={},
        coordination_enabled=True
    )
    
    coordinator = MultiIntersectionCoordinator(config)
    
    with pytest.raises(ValueError, match="not in network configuration"):
        coordinator.create_green_wave(['A', 'B'], 'northbound')


def test_get_network_metrics_initial():
    """Test getting network metrics with no data"""
    config = NetworkConfig(
        intersections={'A': {}},
        connections=[],
        travel_times={},
        coordination_enabled=True
    )
    
    coordinator = MultiIntersectionCoordinator(config)
    metrics = coordinator.get_network_metrics()
    
    assert isinstance(metrics, NetworkMetrics)
    assert metrics.average_travel_time == 0.0
    assert metrics.stops_per_vehicle == 0.0
    assert metrics.coordination_quality == 0.0
    assert metrics.total_throughput == 0
    assert metrics.network_delay == 0.0


def test_update_metrics():
    """Test updating network metrics"""
    config = NetworkConfig(
        intersections={'A': {}},
        connections=[],
        travel_times={},
        coordination_enabled=True
    )
    
    coordinator = MultiIntersectionCoordinator(config)
    
    # Update with vehicle data
    coordinator.update_metrics(vehicle_travel_time=120.0, vehicle_stops=2)
    coordinator.update_metrics(vehicle_travel_time=100.0, vehicle_stops=1)
    
    metrics = coordinator.get_network_metrics()
    
    assert metrics.total_throughput == 2
    assert metrics.average_travel_time == 110.0  # (120 + 100) / 2
    assert metrics.stops_per_vehicle == 1.5  # (2 + 1) / 2


def test_coordination_quality_calculation():
    """Test coordination quality score calculation"""
    config = NetworkConfig(
        intersections={'A': {}},
        connections=[],
        travel_times={},
        coordination_enabled=True
    )
    
    coordinator = MultiIntersectionCoordinator(config)
    
    # Perfect coordination: 0 stops
    coordinator.update_metrics(vehicle_travel_time=100.0, vehicle_stops=0)
    metrics = coordinator.get_network_metrics()
    assert metrics.coordination_quality == 1.0
    
    # Good coordination: 1 stop
    coordinator.reset_metrics()
    coordinator.update_metrics(vehicle_travel_time=100.0, vehicle_stops=1)
    metrics = coordinator.get_network_metrics()
    assert 0.4 < metrics.coordination_quality < 0.6
    
    # Poor coordination: 3 stops
    coordinator.reset_metrics()
    coordinator.update_metrics(vehicle_travel_time=100.0, vehicle_stops=3)
    metrics = coordinator.get_network_metrics()
    assert metrics.coordination_quality < 0.5


def test_reset_metrics():
    """Test resetting metrics"""
    config = NetworkConfig(
        intersections={'A': {}},
        connections=[],
        travel_times={},
        coordination_enabled=True
    )
    
    coordinator = MultiIntersectionCoordinator(config)
    
    # Add some data
    coordinator.update_metrics(vehicle_travel_time=120.0, vehicle_stops=2)
    
    # Reset
    coordinator.reset_metrics()
    
    metrics = coordinator.get_network_metrics()
    assert metrics.total_throughput == 0
    assert metrics.average_travel_time == 0.0
    assert metrics.stops_per_vehicle == 0.0
