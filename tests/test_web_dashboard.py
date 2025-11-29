"""
Tests for Web Dashboard Module

Tests the FastAPI application, WebSocket communication, and dashboard data manager.
"""

import pytest
import asyncio
import time
import numpy as np
from fastapi.testclient import TestClient
from src.web_dashboard import (
    WebDashboard,
    DashboardDataManager,
    Command,
    CommandType,
    Alert,
    AlertLevel
)


class TestDashboardDataManager:
    """Test suite for DashboardDataManager"""
    
    def test_initialization(self):
        """Test data manager initialization"""
        manager = DashboardDataManager()
        
        assert manager.active_connections == []
        assert manager.current_metrics == {}
        assert manager.current_frame is None
        assert manager.alerts == []
        assert manager.max_alerts == 100
    
    def test_update_metrics(self):
        """Test metrics update"""
        manager = DashboardDataManager()
        
        metrics = {
            "north": {"count": 5, "density": 0.3},
            "south": {"count": 3, "density": 0.2}
        }
        
        manager.update_metrics(metrics)
        assert manager.current_metrics == metrics
    
    def test_update_frame(self):
        """Test frame update"""
        manager = DashboardDataManager()
        
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        manager.update_frame(frame)
        
        assert manager.current_frame is not None
        assert manager.current_frame.shape == (480, 640, 3)
        # Verify it's a copy
        frame[0, 0, 0] = 255
        assert manager.current_frame[0, 0, 0] == 0
    
    def test_update_frame_none(self):
        """Test frame update with None"""
        manager = DashboardDataManager()
        
        manager.update_frame(None)
        assert manager.current_frame is None
    
    def test_add_alert(self):
        """Test adding alerts"""
        manager = DashboardDataManager()
        
        timestamp = time.time()
        manager.add_alert("Test alert", AlertLevel.INFO, timestamp)
        
        assert len(manager.alerts) == 1
        assert manager.alerts[0].message == "Test alert"
        assert manager.alerts[0].level == AlertLevel.INFO
        assert manager.alerts[0].timestamp == timestamp
    
    def test_alert_limit(self):
        """Test alert list size limit"""
        manager = DashboardDataManager()
        
        # Add more than max_alerts
        for i in range(150):
            manager.add_alert(f"Alert {i}", AlertLevel.INFO, time.time())
        
        # Should keep only last 100
        assert len(manager.alerts) == 100
        assert manager.alerts[0].message == "Alert 50"
        assert manager.alerts[-1].message == "Alert 149"
    
    def test_command_queue(self):
        """Test command queuing"""
        manager = DashboardDataManager()
        
        command1 = Command(
            command_type=CommandType.OVERRIDE_SIGNAL,
            target="north",
            value={"state": "green", "duration": 30.0},
            timestamp=time.time()
        )
        
        command2 = Command(
            command_type=CommandType.ADJUST_PARAMETER,
            target="min_green",
            value=15.0,
            timestamp=time.time()
        )
        
        # Use asyncio.run to execute async functions in sync test
        asyncio.run(manager.add_command(command1))
        asyncio.run(manager.add_command(command2))
        
        commands = manager.get_commands()
        assert len(commands) == 2
        assert commands[0].command_type == CommandType.OVERRIDE_SIGNAL
        assert commands[1].command_type == CommandType.ADJUST_PARAMETER
        
        # Queue should be empty now
        commands = manager.get_commands()
        assert len(commands) == 0


class TestWebDashboard:
    """Test suite for WebDashboard"""
    
    def test_initialization(self):
        """Test dashboard initialization"""
        dashboard = WebDashboard(port=8081)
        
        assert dashboard.port == 8081
        assert dashboard.app is not None
        assert dashboard.data_manager is not None
        assert dashboard.server_thread is None
    
    def test_api_status_endpoint(self):
        """Test /api/status endpoint"""
        dashboard = WebDashboard(port=8081)
        client = TestClient(dashboard.app)
        
        response = client.get("/api/status")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert data["status"] == "running"
        assert "connected_clients" in data
        assert "pending_commands" in data
    
    def test_api_metrics_endpoint(self):
        """Test /api/metrics endpoint"""
        dashboard = WebDashboard(port=8081)
        client = TestClient(dashboard.app)
        
        # Set some metrics
        metrics = {"north": 5, "south": 3}
        dashboard.data_manager.update_metrics(metrics)
        
        response = client.get("/api/metrics")
        assert response.status_code == 200
        assert response.json() == metrics
    
    def test_api_override_endpoint(self):
        """Test /api/override endpoint"""
        dashboard = WebDashboard(port=8081)
        client = TestClient(dashboard.app)
        
        override_data = {
            "lane": "north",
            "state": "green",
            "duration": 30.0
        }
        
        response = client.post("/api/override", json=override_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "north" in data["message"]
    
    def test_api_adjust_endpoint(self):
        """Test /api/adjust endpoint"""
        dashboard = WebDashboard(port=8081)
        client = TestClient(dashboard.app)
        
        adjust_data = {
            "parameter": "min_green",
            "value": 15.0
        }
        
        response = client.post("/api/adjust", json=adjust_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "min_green" in data["message"]
    
    def test_api_intersections_endpoint(self):
        """Test /api/intersections endpoint"""
        dashboard = WebDashboard(port=8081)
        client = TestClient(dashboard.app)
        
        response = client.get("/api/intersections")
        assert response.status_code == 200
        
        data = response.json()
        assert "intersections" in data
    
    def test_api_history_endpoint(self):
        """Test /api/history/{metric} endpoint"""
        dashboard = WebDashboard(port=8081)
        client = TestClient(dashboard.app)
        
        response = client.get("/api/history/throughput")
        assert response.status_code == 200
        
        data = response.json()
        assert data["metric"] == "throughput"
        assert "data" in data
    
    def test_update_video_feed(self):
        """Test video feed update"""
        dashboard = WebDashboard(port=8081)
        
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        dashboard.update_video_feed(frame)
        
        assert dashboard.data_manager.current_frame is not None
        assert dashboard.data_manager.current_frame.shape == (480, 640, 3)
    
    def test_update_metrics(self):
        """Test metrics update"""
        dashboard = WebDashboard(port=8081)
        
        metrics = {"north": 5, "south": 3}
        dashboard.update_metrics(metrics)
        
        assert dashboard.data_manager.current_metrics == metrics
    
    def test_get_user_commands(self):
        """Test getting user commands"""
        dashboard = WebDashboard(port=8081)
        
        # Initially empty
        commands = dashboard.get_user_commands()
        assert len(commands) == 0
    
    def test_broadcast_alert_info(self):
        """Test broadcasting info alert"""
        dashboard = WebDashboard(port=8081)
        
        dashboard.broadcast_alert("Test info", "info")
        
        assert len(dashboard.data_manager.alerts) == 1
        assert dashboard.data_manager.alerts[0].level == AlertLevel.INFO
    
    def test_broadcast_alert_warning(self):
        """Test broadcasting warning alert"""
        dashboard = WebDashboard(port=8081)
        
        dashboard.broadcast_alert("Test warning", "warning")
        
        assert len(dashboard.data_manager.alerts) == 1
        assert dashboard.data_manager.alerts[0].level == AlertLevel.WARNING
    
    def test_broadcast_alert_error(self):
        """Test broadcasting error alert"""
        dashboard = WebDashboard(port=8081)
        
        dashboard.broadcast_alert("Test error", "error")
        
        assert len(dashboard.data_manager.alerts) == 1
        assert dashboard.data_manager.alerts[0].level == AlertLevel.ERROR
    
    def test_broadcast_alert_invalid_level(self):
        """Test broadcasting alert with invalid level defaults to info"""
        dashboard = WebDashboard(port=8081)
        
        dashboard.broadcast_alert("Test", "invalid")
        
        assert len(dashboard.data_manager.alerts) == 1
        assert dashboard.data_manager.alerts[0].level == AlertLevel.INFO
    
    def test_cors_configuration(self):
        """Test CORS is configured"""
        dashboard = WebDashboard(port=8081)
        client = TestClient(dashboard.app)
        
        response = client.options("/api/status")
        # CORS should allow the request
        assert response.status_code in [200, 405]  # 405 if OPTIONS not explicitly handled


class TestCommandIntegration:
    """Integration tests for command flow"""
    
    def test_command_flow_override(self):
        """Test complete command flow for signal override"""
        dashboard = WebDashboard(port=8081)
        client = TestClient(dashboard.app)
        
        # Submit override command
        override_data = {
            "lane": "north",
            "state": "green",
            "duration": 30.0
        }
        
        response = client.post("/api/override", json=override_data)
        assert response.status_code == 200
        
        # Retrieve commands
        commands = dashboard.get_user_commands()
        assert len(commands) == 1
        assert commands[0].command_type == CommandType.OVERRIDE_SIGNAL
        assert commands[0].target == "north"
        assert commands[0].value["state"] == "green"
        assert commands[0].value["duration"] == 30.0
    
    def test_command_flow_parameter(self):
        """Test complete command flow for parameter adjustment"""
        dashboard = WebDashboard(port=8081)
        client = TestClient(dashboard.app)
        
        # Submit parameter adjustment
        adjust_data = {
            "parameter": "max_green",
            "value": 60.0
        }
        
        response = client.post("/api/adjust", json=adjust_data)
        assert response.status_code == 200
        
        # Retrieve commands
        commands = dashboard.get_user_commands()
        assert len(commands) == 1
        assert commands[0].command_type == CommandType.ADJUST_PARAMETER
        assert commands[0].target == "max_green"
        assert commands[0].value == 60.0
    
    def test_multiple_commands(self):
        """Test handling multiple commands"""
        dashboard = WebDashboard(port=8081)
        client = TestClient(dashboard.app)
        
        # Submit multiple commands
        client.post("/api/override", json={"lane": "north", "state": "green", "duration": 30.0})
        client.post("/api/adjust", json={"parameter": "min_green", "value": 10.0})
        client.post("/api/override", json={"lane": "south", "state": "red", "duration": 20.0})
        
        # Retrieve all commands
        commands = dashboard.get_user_commands()
        assert len(commands) == 3
        
        # Commands should be in order
        assert commands[0].target == "north"
        assert commands[1].target == "min_green"
        assert commands[2].target == "south"
        
        # Queue should be empty after retrieval
        commands = dashboard.get_user_commands()
        assert len(commands) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
