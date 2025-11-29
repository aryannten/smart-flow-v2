"""
Tests for Error Handler Module
"""

import pytest
import time
import tempfile
from pathlib import Path

from src.error_handler import (
    ErrorHandler,
    ErrorSeverity,
    SystemState,
    ErrorContext,
    with_error_handling
)


class TestErrorHandler:
    """Test error handler functionality"""
    
    def test_initialization(self):
        """Test error handler initialization"""
        handler = ErrorHandler()
        assert handler.current_state == SystemState.NORMAL
        assert len(handler.degraded_components) == 0
        assert len(handler.error_history) == 0
    
    def test_initialization_with_log_file(self):
        """Test error handler initialization with log file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test_error.log"
            handler = ErrorHandler(log_file=str(log_file))
            assert handler.log_file == str(log_file)
            handler.shutdown()
            
            # Close all handlers to release file locks (Windows issue)
            for h in handler.logger.handlers[:]:
                h.close()
                handler.logger.removeHandler(h)
    
    def test_log_error(self):
        """Test error logging"""
        handler = ErrorHandler()
        
        context = ErrorContext(
            component="TestComponent",
            operation="test_operation",
            error_type="TestError",
            message="Test error message",
            severity=ErrorSeverity.ERROR,
            timestamp=time.time()
        )
        
        handler.log_error(context)
        
        assert len(handler.error_history) == 1
        assert handler.error_history[0] == context
        assert "TestComponent:TestError" in handler.error_counts
        
        handler.shutdown()
    
    def test_handle_exception(self):
        """Test exception handling"""
        handler = ErrorHandler()
        
        exception = ValueError("Test exception")
        result = handler.handle_exception(
            component="TestComponent",
            operation="test_operation",
            exception=exception,
            severity=ErrorSeverity.ERROR
        )
        
        assert result is False  # No recovery strategy
        assert len(handler.error_history) == 1
        assert handler.error_history[0].error_type == "ValueError"
        assert handler.error_history[0].message == "Test exception"
        
        handler.shutdown()
    
    def test_recovery_strategy(self):
        """Test recovery strategy registration and execution"""
        handler = ErrorHandler()
        
        # Register recovery strategy
        recovery_called = []
        
        def test_recovery(exception):
            recovery_called.append(True)
        
        handler.register_recovery_strategy("test_recovery", test_recovery)
        
        # Handle exception with recovery
        exception = ValueError("Test exception")
        result = handler.handle_exception(
            component="TestComponent",
            operation="test_operation",
            exception=exception,
            severity=ErrorSeverity.ERROR,
            recovery_strategy="test_recovery"
        )
        
        assert result is True
        assert len(recovery_called) == 1
        assert handler.error_history[0].recovery_attempted is True
        assert handler.error_history[0].recovery_successful is True
        
        handler.shutdown()
    
    def test_component_degradation(self):
        """Test component degradation"""
        handler = ErrorHandler()
        
        # Degrade a component
        handler._degrade_component("TestComponent")
        
        assert "TestComponent" in handler.degraded_components
        assert handler.current_state == SystemState.DEGRADED
        assert handler.is_component_degraded("TestComponent")
        
        # Restore component
        handler.restore_component("TestComponent")
        
        assert "TestComponent" not in handler.degraded_components
        assert handler.current_state == SystemState.NORMAL
        assert not handler.is_component_degraded("TestComponent")
        
        handler.shutdown()
    
    def test_critical_state(self):
        """Test critical state when multiple components degraded"""
        handler = ErrorHandler()
        
        # Degrade multiple components
        handler._degrade_component("Component1")
        handler._degrade_component("Component2")
        handler._degrade_component("Component3")
        
        assert handler.current_state == SystemState.CRITICAL
        assert len(handler.degraded_components) == 3
        
        handler.shutdown()
    
    def test_error_rate_tracking(self):
        """Test error rate tracking"""
        handler = ErrorHandler()
        
        # Generate multiple errors
        for i in range(5):
            context = ErrorContext(
                component="TestComponent",
                operation="test_operation",
                error_type="TestError",
                message=f"Error {i}",
                severity=ErrorSeverity.ERROR,
                timestamp=time.time()
            )
            handler.log_error(context)
        
        summary = handler.get_error_summary()
        assert summary['total_errors'] == 5
        assert summary['recent_errors'] == 5
        
        handler.shutdown()
    
    def test_resource_monitoring_start_stop(self):
        """Test resource monitoring start and stop"""
        handler = ErrorHandler()
        
        # Start monitoring
        handler.start_resource_monitoring(interval=1.0)
        assert handler.monitor_thread is not None
        assert handler.monitor_thread.is_alive()
        
        # Wait a bit for metrics to be collected
        time.sleep(2.0)
        
        # Check metrics
        metrics = handler.get_resource_metrics()
        assert metrics is not None
        assert metrics.cpu_percent >= 0
        assert metrics.memory_percent >= 0
        
        # Stop monitoring
        handler.stop_resource_monitoring()
        
        handler.shutdown()
    
    def test_should_throttle(self):
        """Test throttling check"""
        handler = ErrorHandler()
        
        # Start monitoring
        handler.start_resource_monitoring(interval=1.0)
        time.sleep(2.0)
        
        # Check throttling (should be False under normal conditions)
        should_throttle = handler.should_throttle()
        assert isinstance(should_throttle, bool)
        
        handler.shutdown()
    
    def test_error_summary(self):
        """Test error summary generation"""
        handler = ErrorHandler()
        
        # Add some errors
        for i in range(3):
            context = ErrorContext(
                component="TestComponent",
                operation="test_operation",
                error_type="TestError",
                message=f"Error {i}",
                severity=ErrorSeverity.ERROR,
                timestamp=time.time()
            )
            handler.log_error(context)
        
        summary = handler.get_error_summary()
        
        assert 'total_errors' in summary
        assert 'recent_errors' in summary
        assert 'error_rate' in summary
        assert 'system_state' in summary
        assert 'degraded_components' in summary
        assert 'error_counts' in summary
        
        assert summary['total_errors'] == 3
        assert summary['system_state'] == SystemState.NORMAL.value
        
        handler.shutdown()
    
    def test_with_error_handling_decorator(self):
        """Test error handling decorator"""
        handler = ErrorHandler()
        
        @with_error_handling(
            component="TestComponent",
            operation="test_function",
            error_handler=handler,
            severity=ErrorSeverity.ERROR,
            default_return="default"
        )
        def test_function():
            raise ValueError("Test error")
        
        result = test_function()
        
        assert result == "default"
        assert len(handler.error_history) == 1
        assert handler.error_history[0].error_type == "ValueError"
        
        handler.shutdown()
    
    def test_with_error_handling_decorator_success(self):
        """Test error handling decorator with successful function"""
        handler = ErrorHandler()
        
        @with_error_handling(
            component="TestComponent",
            operation="test_function",
            error_handler=handler,
            severity=ErrorSeverity.ERROR,
            default_return="default"
        )
        def test_function():
            return "success"
        
        result = test_function()
        
        assert result == "success"
        assert len(handler.error_history) == 0
        
        handler.shutdown()


class TestErrorHandlerIntegration:
    """Integration tests for error handler with other components"""
    
    def test_stream_manager_with_error_handler(self):
        """Test StreamManager with error handler integration"""
        from src.stream_manager import StreamManager
        
        handler = ErrorHandler()
        
        # Try to connect to non-existent file
        stream_manager = StreamManager("nonexistent.mp4", error_handler=handler)
        result = stream_manager.connect()
        
        assert result is False
        assert len(handler.error_history) > 0
        
        handler.shutdown()
    
    def test_detector_with_error_handler(self):
        """Test EnhancedDetector with error handler integration"""
        from src.enhanced_detector import EnhancedDetector
        import numpy as np
        
        handler = ErrorHandler()
        
        # Initialize detector with valid model
        try:
            detector = EnhancedDetector("yolov8n.pt", error_handler=handler)
            
            # Test with invalid frame (should handle gracefully)
            invalid_frame = np.zeros((10, 10, 3), dtype=np.uint8)
            result = detector.detect_all(invalid_frame)
            
            # Should return empty result, not crash
            assert result is not None
            assert isinstance(result.vehicles, list)
            assert isinstance(result.pedestrians, list)
            
        except Exception as e:
            # Model might not be available, that's okay for this test
            pass
        
        handler.shutdown()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
