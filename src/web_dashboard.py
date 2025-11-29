"""
Web Dashboard Module for SMART FLOW v2

Real-time monitoring and control interface using FastAPI and WebSockets.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import asyncio
import threading
import json
import base64
import cv2
import numpy as np
import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
import uvicorn

from src.error_handler import ErrorHandler, ErrorSeverity

logger = logging.getLogger(__name__)


class CommandType(Enum):
    """Types of commands from dashboard"""
    OVERRIDE_SIGNAL = "override_signal"
    ADJUST_PARAMETER = "adjust_parameter"
    RESET_SYSTEM = "reset_system"
    EMERGENCY_STOP = "emergency_stop"


@dataclass
class Command:
    """User command from dashboard"""
    command_type: CommandType
    target: str  # Lane name or parameter name
    value: Any  # Signal state, parameter value, etc.
    timestamp: float


class SignalOverrideRequest(BaseModel):
    """Request model for signal override"""
    lane: str
    state: str  # 'red', 'yellow', 'green'
    duration: float


class ParameterAdjustmentRequest(BaseModel):
    """Request model for parameter adjustment"""
    parameter: str
    value: float


class AlertLevel(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class Alert:
    """Alert notification"""
    message: str
    level: AlertLevel
    timestamp: float


class DashboardDataManager:
    """
    Manages data aggregation and distribution for the dashboard.
    Handles WebSocket connections, command queuing, and alert notifications.
    """
    
    def __init__(self):
        """Initialize dashboard data manager"""
        self.active_connections: List[WebSocket] = []
        self.command_queue: asyncio.Queue = asyncio.Queue()
        self.current_metrics: Dict[str, Any] = {}
        self.current_frame: Optional[np.ndarray] = None
        self.alerts: List[Alert] = []
        self.max_alerts = 100  # Keep last 100 alerts
        
    async def connect(self, websocket: WebSocket):
        """
        Connect a new WebSocket client.
        
        Args:
            websocket: WebSocket connection
        """
        await websocket.accept()
        self.active_connections.append(websocket)
        
    def disconnect(self, websocket: WebSocket):
        """
        Disconnect a WebSocket client.
        
        Args:
            websocket: WebSocket connection
        """
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
    
    async def broadcast_json(self, message: Dict[str, Any]):
        """
        Broadcast JSON message to all connected clients.
        
        Args:
            message: Dictionary to broadcast
        """
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.append(connection)
        
        # Clean up disconnected clients
        for conn in disconnected:
            self.disconnect(conn)
    
    async def add_command(self, command: Command):
        """
        Add a command to the queue.
        
        Args:
            command: Command to queue
        """
        await self.command_queue.put(command)
    
    def get_commands(self) -> List[Command]:
        """
        Get all pending commands from queue (non-blocking).
        
        Returns:
            List of commands
        """
        commands = []
        while not self.command_queue.empty():
            try:
                commands.append(self.command_queue.get_nowait())
            except asyncio.QueueEmpty:
                break
        return commands
    
    def update_metrics(self, metrics: Dict[str, Any]):
        """
        Update current metrics.
        
        Args:
            metrics: Dictionary of metrics
        """
        self.current_metrics = metrics
    
    def update_frame(self, frame: np.ndarray):
        """
        Update current video frame.
        
        Args:
            frame: Video frame
        """
        self.current_frame = frame.copy() if frame is not None else None
    
    def add_alert(self, message: str, level: AlertLevel, timestamp: float):
        """
        Add an alert notification.
        
        Args:
            message: Alert message
            level: Alert severity level
            timestamp: Alert timestamp
        """
        alert = Alert(message=message, level=level, timestamp=timestamp)
        self.alerts.append(alert)
        
        # Keep only recent alerts
        if len(self.alerts) > self.max_alerts:
            self.alerts = self.alerts[-self.max_alerts:]


class WebDashboard:
    """
    Web-based dashboard for real-time monitoring and control.
    Provides REST API endpoints, WebSocket for live updates, and video streaming.
    """
    
    def __init__(self, port: int = 8080, error_handler: Optional[ErrorHandler] = None):
        """
        Initialize web dashboard.
        
        Args:
            port: Port number for web server
            error_handler: Optional error handler for comprehensive error management
        """
        self.port = port
        self.error_handler = error_handler
        self.app = FastAPI(title="SMART FLOW v2 Dashboard", version="2.0.0")
        self.data_manager = DashboardDataManager()
        self.server_thread: Optional[threading.Thread] = None
        self.server: Optional[uvicorn.Server] = None
        self._setup_routes()
        self._setup_cors()
        
    def _setup_cors(self):
        """Configure CORS middleware"""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # In production, specify exact origins
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    def _setup_routes(self):
        """Set up API routes"""
        
        @self.app.get("/api/status")
        async def get_status():
            """Get system status"""
            return JSONResponse({
                "status": "running",
                "connected_clients": len(self.data_manager.active_connections),
                "pending_commands": self.data_manager.command_queue.qsize()
            })
        
        @self.app.get("/api/metrics")
        async def get_metrics():
            """Get current metrics"""
            return JSONResponse(self.data_manager.current_metrics)
        
        @self.app.get("/api/history/{metric}")
        async def get_history(metric: str):
            """Get historical data for a specific metric"""
            # Placeholder - would integrate with metrics logger
            return JSONResponse({
                "metric": metric,
                "data": [],
                "message": "Historical data integration pending"
            })
        
        @self.app.post("/api/override")
        async def override_signal(request: SignalOverrideRequest):
            """Manual signal override"""
            import time
            command = Command(
                command_type=CommandType.OVERRIDE_SIGNAL,
                target=request.lane,
                value={"state": request.state, "duration": request.duration},
                timestamp=time.time()
            )
            await self.data_manager.add_command(command)
            return JSONResponse({
                "success": True,
                "message": f"Override command queued for lane {request.lane}"
            })
        
        @self.app.post("/api/adjust")
        async def adjust_parameter(request: ParameterAdjustmentRequest):
            """Adjust system parameter"""
            import time
            command = Command(
                command_type=CommandType.ADJUST_PARAMETER,
                target=request.parameter,
                value=request.value,
                timestamp=time.time()
            )
            await self.data_manager.add_command(command)
            return JSONResponse({
                "success": True,
                "message": f"Parameter adjustment queued for {request.parameter}"
            })
        
        @self.app.get("/api/intersections")
        async def get_intersections():
            """Get list of intersections"""
            # Placeholder - would integrate with multi-intersection coordinator
            return JSONResponse({
                "intersections": [],
                "message": "Multi-intersection integration pending"
            })
        
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            """WebSocket endpoint for live updates"""
            await self.data_manager.connect(websocket)
            try:
                while True:
                    # Keep connection alive and receive messages
                    data = await websocket.receive_text()
                    # Echo back for testing
                    await websocket.send_json({"echo": data})
            except WebSocketDisconnect:
                self.data_manager.disconnect(websocket)
        
        @self.app.get("/stream")
        async def video_stream():
            """Video streaming endpoint"""
            async def generate():
                while True:
                    if self.data_manager.current_frame is not None:
                        # Encode frame as JPEG
                        _, buffer = cv2.imencode('.jpg', self.data_manager.current_frame)
                        frame_bytes = buffer.tobytes()
                        
                        # Yield frame in multipart format
                        yield (b'--frame\r\n'
                               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                    await asyncio.sleep(0.033)  # ~30 FPS
            
            return StreamingResponse(
                generate(),
                media_type="multipart/x-mixed-replace; boundary=frame"
            )
    
    def start(self) -> None:
        """Start web server in a separate thread"""
        if self.server_thread is not None and self.server_thread.is_alive():
            return  # Already running
        
        try:
            config = uvicorn.Config(
                app=self.app,
                host="0.0.0.0",
                port=self.port,
                log_level="info"
            )
            self.server = uvicorn.Server(config)
            
            def run_server():
                try:
                    asyncio.run(self.server.serve())
                except Exception as e:
                    logger.error(f"Error running dashboard server: {e}")
                    if self.error_handler:
                        self.error_handler.handle_exception(
                            component="WebDashboard",
                            operation="run_server",
                            exception=e,
                            severity=ErrorSeverity.ERROR
                        )
            
            self.server_thread = threading.Thread(target=run_server, daemon=True)
            self.server_thread.start()
            logger.info(f"Dashboard server started on port {self.port}")
            
        except Exception as e:
            logger.error(f"Failed to start dashboard server: {e}")
            if self.error_handler:
                self.error_handler.handle_exception(
                    component="WebDashboard",
                    operation="start",
                    exception=e,
                    severity=ErrorSeverity.ERROR
                )
    
    def update_video_feed(self, frame: np.ndarray) -> None:
        """
        Update video feed.
        
        Args:
            frame: Current frame
        """
        self.data_manager.update_frame(frame)
    
    def update_metrics(self, metrics: Dict[str, Any]) -> None:
        """
        Update metrics display and broadcast to connected clients.
        
        Args:
            metrics: Dictionary of metrics
        """
        try:
            self.data_manager.update_metrics(metrics)
            
            # Broadcast to WebSocket clients (non-blocking)
            if self.data_manager.active_connections:
                try:
                    asyncio.run_coroutine_threadsafe(
                        self.data_manager.broadcast_json({
                            "type": "metrics_update",
                            "data": metrics
                        }),
                        asyncio.get_event_loop()
                    )
                except RuntimeError:
                    # Event loop not running, skip broadcast
                    pass
        except Exception as e:
            logger.error(f"Error updating metrics: {e}")
            if self.error_handler:
                self.error_handler.handle_exception(
                    component="WebDashboard",
                    operation="update_metrics",
                    exception=e,
                    severity=ErrorSeverity.WARNING
                )
    
    def get_user_commands(self) -> List[Command]:
        """
        Get user commands from dashboard.
        
        Returns:
            List of commands
        """
        return self.data_manager.get_commands()
    
    def broadcast_alert(self, message: str, level: str) -> None:
        """
        Broadcast alert to dashboard.
        
        Args:
            message: Alert message
            level: Alert level ('info', 'warning', 'error')
        """
        import time
        
        try:
            alert_level = AlertLevel(level.lower())
        except ValueError:
            alert_level = AlertLevel.INFO
        
        timestamp = time.time()
        self.data_manager.add_alert(message, alert_level, timestamp)
        
        # Broadcast to WebSocket clients
        if self.data_manager.active_connections:
            asyncio.run_coroutine_threadsafe(
                self.data_manager.broadcast_json({
                    "type": "alert",
                    "data": {
                        "message": message,
                        "level": alert_level.value,
                        "timestamp": timestamp
                    }
                }),
                asyncio.get_event_loop()
            )
    
    def stop(self) -> None:
        """Stop web server"""
        if self.server is not None:
            self.server.should_exit = True
        
        if self.server_thread is not None:
            self.server_thread.join(timeout=5.0)
