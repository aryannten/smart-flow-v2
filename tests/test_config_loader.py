"""
Unit tests for configuration loader.
"""

import pytest
import json
import tempfile
from pathlib import Path
from src.config_loader import (
    ConfigLoader,
    IntersectionConfig,
    NetworkConfig,
    DashboardConfig,
    LaneConfig,
    TurnLaneConfig,
    CrosswalkConfig,
    Region,
    load_config
)


class TestRegion:
    """Test Region class."""
    
    def test_from_list(self):
        """Test creating Region from list."""
        region = Region.from_list([100, 200, 300, 400])
        assert region.x1 == 100
        assert region.y1 == 200
        assert region.x2 == 300
        assert region.y2 == 400
    
    def test_from_list_invalid_length(self):
        """Test Region creation with invalid length."""
        with pytest.raises(ValueError, match="must have 4 coordinates"):
            Region.from_list([100, 200, 300])
    
    def test_to_list(self):
        """Test converting Region to list."""
        region = Region(100, 200, 300, 400)
        assert region.to_list() == [100, 200, 300, 400]


class TestLaneConfig:
    """Test LaneConfig class."""
    
    def test_from_dict(self):
        """Test creating LaneConfig from dictionary."""
        data = {
            'region': [100, 200, 300, 400],
            'direction': 'north',
            'type': 'through'
        }
        lane = LaneConfig.from_dict(data)
        assert lane.direction == 'north'
        assert lane.lane_type == 'through'
        assert lane.region.x1 == 100
    
    def test_from_dict_default_type(self):
        """Test LaneConfig with default type."""
        data = {
            'region': [100, 200, 300, 400],
            'direction': 'south'
        }
        lane = LaneConfig.from_dict(data)
        assert lane.lane_type == 'through'


class TestTurnLaneConfig:
    """Test TurnLaneConfig class."""
    
    def test_from_dict_full(self):
        """Test creating TurnLaneConfig with all fields."""
        data = {
            'region': [100, 200, 300, 400],
            'turn_type': 'left',
            'parent_lane': 'north',
            'conflicting_movements': ['south', 'east'],
            'minimum_green': 10,
            'maximum_green': 40
        }
        turn = TurnLaneConfig.from_dict(data)
        assert turn.turn_type == 'left'
        assert turn.parent_lane == 'north'
        assert turn.conflicting_movements == ['south', 'east']
        assert turn.minimum_green == 10
        assert turn.maximum_green == 40
    
    def test_from_dict_defaults(self):
        """Test TurnLaneConfig with default values."""
        data = {
            'region': [100, 200, 300, 400],
            'turn_type': 'right'
        }
        turn = TurnLaneConfig.from_dict(data)
        assert turn.minimum_green == 5
        assert turn.maximum_green == 30
        assert turn.conflicting_movements == []


class TestCrosswalkConfig:
    """Test CrosswalkConfig class."""
    
    def test_from_dict(self):
        """Test creating CrosswalkConfig from dictionary."""
        data = {
            'region': [250, 380, 450, 420],
            'crossing_distance': 15.0,
            'conflicting_lanes': ['north', 'south']
        }
        crosswalk = CrosswalkConfig.from_dict(data)
        assert crosswalk.crossing_distance == 15.0
        assert crosswalk.conflicting_lanes == ['north', 'south']


class TestConfigLoader:
    """Test ConfigLoader class."""
    
    def test_load_json_file(self):
        """Test loading JSON configuration file."""
        config_data = {
            'intersection': {
                'id': 'test_intersection',
                'name': 'Test Intersection',
                'video_source': 'test.mp4'
            },
            'lanes': {
                'north': {
                    'region': [100, 0, 300, 400],
                    'direction': 'north'
                }
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            temp_path = f.name
        
        try:
            data = ConfigLoader.load_file(temp_path)
            assert data['intersection']['id'] == 'test_intersection'
        finally:
            Path(temp_path).unlink()
    
    def test_load_nonexistent_file(self):
        """Test loading non-existent file."""
        with pytest.raises(FileNotFoundError):
            ConfigLoader.load_file('nonexistent.json')
    
    def test_load_unsupported_format(self):
        """Test loading unsupported file format."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write('test')
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError, match="Unsupported file format"):
                ConfigLoader.load_file(temp_path)
        finally:
            Path(temp_path).unlink()
    
    def test_load_invalid_json(self):
        """Test loading invalid JSON."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('{invalid json}')
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError, match="Invalid JSON"):
                ConfigLoader.load_file(temp_path)
        finally:
            Path(temp_path).unlink()


class TestIntersectionConfig:
    """Test IntersectionConfig loading and validation."""
    
    def test_load_valid_intersection_config(self):
        """Test loading valid intersection configuration."""
        config_data = {
            'intersection': {
                'id': 'test_int',
                'name': 'Test Intersection',
                'video_source': 'test.mp4'
            },
            'lanes': {
                'north': {
                    'region': [100, 0, 300, 400],
                    'direction': 'north',
                    'type': 'through'
                },
                'south': {
                    'region': [400, 200, 600, 600],
                    'direction': 'south',
                    'type': 'through'
                }
            },
            'turn_lanes': {
                'north_left': {
                    'region': [100, 0, 200, 400],
                    'turn_type': 'left',
                    'parent_lane': 'north',
                    'conflicting_movements': ['south']
                }
            },
            'crosswalks': {
                'north_crosswalk': {
                    'region': [250, 380, 450, 420],
                    'crossing_distance': 15.0,
                    'conflicting_lanes': ['north', 'south']
                }
            },
            'signal_timing': {
                'minimum_green': 10,
                'maximum_green': 60,
                'yellow_duration': 3
            },
            'detection': {
                'model_path': 'yolov8n.pt',
                'confidence_threshold': 0.5
            },
            'vehicle_weights': {
                'car': 1.0,
                'bus': 2.0
            }
        }
        
        config = IntersectionConfig.from_dict(config_data)
        
        assert config.id == 'test_int'
        assert config.name == 'Test Intersection'
        assert config.video_source == 'test.mp4'
        assert len(config.lanes) == 2
        assert 'north' in config.lanes
        assert len(config.turn_lanes) == 1
        assert len(config.crosswalks) == 1
        assert config.signal_timing.minimum_green == 10
        assert config.detection.confidence_threshold == 0.5
        assert config.vehicle_weights['bus'] == 2.0
    
    def test_validate_valid_config(self):
        """Test validation of valid configuration."""
        config_data = {
            'intersection': {
                'id': 'test',
                'name': 'Test',
                'video_source': 'test.mp4'
            },
            'lanes': {
                'north': {
                    'region': [100, 0, 300, 400],
                    'direction': 'north'
                }
            }
        }
        
        config = IntersectionConfig.from_dict(config_data)
        errors = ConfigLoader.validate_intersection_config(config)
        assert len(errors) == 0
    
    def test_validate_missing_required_fields(self):
        """Test validation with missing required fields."""
        config = IntersectionConfig(
            id='',
            name='',
            video_source='',
            lanes={}
        )
        
        errors = ConfigLoader.validate_intersection_config(config)
        assert len(errors) > 0
        assert any('ID is required' in e for e in errors)
        assert any('name is required' in e for e in errors)
        assert any('Video source is required' in e for e in errors)
        assert any('At least one lane' in e for e in errors)
    
    def test_validate_invalid_turn_lane_reference(self):
        """Test validation with invalid turn lane reference."""
        config_data = {
            'intersection': {
                'id': 'test',
                'name': 'Test',
                'video_source': 'test.mp4'
            },
            'lanes': {
                'north': {
                    'region': [100, 0, 300, 400],
                    'direction': 'north'
                }
            },
            'turn_lanes': {
                'north_left': {
                    'region': [100, 0, 200, 400],
                    'turn_type': 'left',
                    'parent_lane': 'nonexistent',
                    'conflicting_movements': ['also_nonexistent']
                }
            }
        }
        
        config = IntersectionConfig.from_dict(config_data)
        errors = ConfigLoader.validate_intersection_config(config)
        assert len(errors) >= 2
        assert any('non-existent parent lane' in e for e in errors)
        assert any('also_nonexistent' in e for e in errors)
    
    def test_validate_invalid_signal_timing(self):
        """Test validation with invalid signal timing."""
        config_data = {
            'intersection': {
                'id': 'test',
                'name': 'Test',
                'video_source': 'test.mp4'
            },
            'lanes': {
                'north': {
                    'region': [100, 0, 300, 400],
                    'direction': 'north'
                }
            },
            'signal_timing': {
                'minimum_green': -5,
                'maximum_green': 5,
                'yellow_duration': 0
            }
        }
        
        config = IntersectionConfig.from_dict(config_data)
        errors = ConfigLoader.validate_intersection_config(config)
        assert any('Minimum green time must be positive' in e for e in errors)
        assert any('Yellow duration must be positive' in e for e in errors)


class TestNetworkConfig:
    """Test NetworkConfig loading and validation."""
    
    def test_load_valid_network_config(self):
        """Test loading valid network configuration."""
        config_data = {
            'network': {
                'name': 'Test Network',
                'coordination_enabled': True,
                'target_speed_mph': 35,
                'update_interval': 5.0
            },
            'intersections': {
                'int1': {
                    'id': 'int1',
                    'name': 'Intersection 1',
                    'video_source': 'test1.mp4',
                    'lanes': {
                        'north': {
                            'region': [100, 0, 300, 400],
                            'direction': 'north'
                        }
                    }
                },
                'int2': {
                    'id': 'int2',
                    'name': 'Intersection 2',
                    'video_source': 'test2.mp4',
                    'lanes': {
                        'south': {
                            'region': [400, 200, 600, 600],
                            'direction': 'south'
                        }
                    }
                }
            },
            'connections': [
                {
                    'from': 'int1',
                    'to': 'int2',
                    'distance_meters': 400,
                    'travel_time_seconds': 30
                }
            ],
            'corridors': [
                {
                    'name': 'Main Corridor',
                    'intersections': ['int1', 'int2'],
                    'direction': 'north',
                    'priority': 'high'
                }
            ]
        }
        
        config = NetworkConfig.from_dict(config_data)
        
        assert config.name == 'Test Network'
        assert config.coordination_enabled is True
        assert config.target_speed_mph == 35
        assert len(config.intersections) == 2
        assert len(config.connections) == 1
        assert len(config.corridors) == 1
        assert config.connections[0].from_intersection == 'int1'
        assert config.corridors[0].name == 'Main Corridor'
    
    def test_validate_valid_network_config(self):
        """Test validation of valid network configuration."""
        config_data = {
            'network': {
                'name': 'Test Network',
                'coordination_enabled': True,
                'target_speed_mph': 35,
                'update_interval': 5.0
            },
            'intersections': {
                'int1': {
                    'id': 'int1',
                    'name': 'Intersection 1',
                    'video_source': 'test1.mp4',
                    'lanes': {
                        'north': {
                            'region': [100, 0, 300, 400],
                            'direction': 'north'
                        }
                    }
                }
            },
            'connections': []
        }
        
        config = NetworkConfig.from_dict(config_data)
        errors = ConfigLoader.validate_network_config(config)
        assert len(errors) == 0
    
    def test_validate_invalid_connection_references(self):
        """Test validation with invalid connection references."""
        config_data = {
            'network': {
                'name': 'Test Network',
                'coordination_enabled': True,
                'target_speed_mph': 35,
                'update_interval': 5.0
            },
            'intersections': {
                'int1': {
                    'id': 'int1',
                    'name': 'Intersection 1',
                    'video_source': 'test1.mp4',
                    'lanes': {
                        'north': {
                            'region': [100, 0, 300, 400],
                            'direction': 'north'
                        }
                    }
                }
            },
            'connections': [
                {
                    'from': 'int1',
                    'to': 'nonexistent',
                    'distance_meters': 400,
                    'travel_time_seconds': 30
                }
            ]
        }
        
        config = NetworkConfig.from_dict(config_data)
        errors = ConfigLoader.validate_network_config(config)
        assert any('nonexistent' in e for e in errors)


class TestDashboardConfig:
    """Test DashboardConfig loading."""
    
    def test_load_dashboard_config(self):
        """Test loading dashboard configuration."""
        config_data = {
            'dashboard': {
                'port': 8080,
                'host': '0.0.0.0',
                'enable_cors': True,
                'allowed_origins': ['*'],
                'websocket_update_interval': 0.5,
                'video_stream_fps': 15,
                'video_stream_quality': 80
            }
        }
        
        config = DashboardConfig.from_dict(config_data)
        
        assert config.port == 8080
        assert config.host == '0.0.0.0'
        assert config.enable_cors is True
        assert config.websocket_update_interval == 0.5
    
    def test_dashboard_config_defaults(self):
        """Test dashboard configuration with defaults."""
        config_data = {'dashboard': {}}
        config = DashboardConfig.from_dict(config_data)
        
        assert config.port == 8080
        assert config.host == '0.0.0.0'
        assert config.enable_cors is True


class TestLoadConfig:
    """Test load_config convenience function."""
    
    def test_load_config_auto_detect_intersection(self):
        """Test auto-detecting intersection config."""
        config_data = {
            'intersection': {
                'id': 'test',
                'name': 'Test',
                'video_source': 'test.mp4'
            },
            'lanes': {
                'north': {
                    'region': [100, 0, 300, 400],
                    'direction': 'north'
                }
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            temp_path = f.name
        
        try:
            config = load_config(temp_path, config_type='auto')
            assert isinstance(config, IntersectionConfig)
            assert config.id == 'test'
        finally:
            Path(temp_path).unlink()
    
    def test_load_config_auto_detect_network(self):
        """Test auto-detecting network config."""
        config_data = {
            'network': {
                'name': 'Test Network',
                'coordination_enabled': True,
                'target_speed_mph': 35,
                'update_interval': 5.0
            },
            'intersections': {
                'int1': {
                    'id': 'int1',
                    'name': 'Intersection 1',
                    'video_source': 'test1.mp4',
                    'lanes': {
                        'north': {
                            'region': [100, 0, 300, 400],
                            'direction': 'north'
                        }
                    }
                }
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            temp_path = f.name
        
        try:
            config = load_config(temp_path, config_type='auto')
            assert isinstance(config, NetworkConfig)
            assert config.name == 'Test Network'
        finally:
            Path(temp_path).unlink()
    
    def test_load_config_invalid_raises_error(self):
        """Test that invalid config raises ValueError."""
        config_data = {
            'intersection': {
                'id': '',
                'name': '',
                'video_source': ''
            },
            'lanes': {}
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError, match="Invalid intersection configuration"):
                load_config(temp_path, config_type='intersection')
        finally:
            Path(temp_path).unlink()
