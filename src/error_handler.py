"""
Error Handler Module for SMART FLOW v2

Provides comprehensive error handling, logging, and recovery mechanisms.
Implements graceful degradation and resource monitoring.
"""

import logging
import sys
import traceback
import time
import psutil
from typing import Optional, Callable, Any, Dict
from dataclasses import dataclass
from enum import Enum
from functools import wraps
import threading


class ErrorSeverity(Enum):
    """Error severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class SystemState(Enum):
    """System operational states"""
    NORMAL = "normal"
    DEGRADED = "degraded"
    CRITICAL = "critical"
    SHUTDOWN = "shutdown"


@dataclass
class ErrorContext:
    """Context information for an error"""
    component: str
    operation: str
    error_type: str
    message: str
    severity: ErrorSeverity
    timestamp: float
    traceback_str: Optional[str] = None
    recovery_attempted: bool = False
    recovery_successful: bool = False


@dataclass
class ResourceMetrics:
    """System resource metrics"""
    cpu_percent: float
    memory_percent: float
    memory_available_mb: float
    timestamp: float


class ErrorHandler:
    """
    Centralized error handling and recovery system.
    
    Features:
    - Structured error logging
    - Automatic recovery attempts
    - Graceful degradation
    - Resource monitoring
    - Error rate tracking
    """
    
    # Resource thresholds
    CPU_WARNING_THRESHOLD = 80.0  # percent
    CPU_CRITICAL_THRESHOLD = 95.0  # percent
    MEMORY_WARNING_THRESHOLD = 80.0  # percent
    MEMORY_CRITICAL_THRESHOLD = 90.0  # percent
    
    # Error rate thresholds
    ERROR_RATE_WINDOW = 60.0  # seconds
    ERROR_RATE_WARNING = 10  # errors per minute
    ERROR_RATE_CRITICAL = 30  # errors per minute
    
    def __init__(self, log_file: Optional[str] = None):
        """
        Initialize error handler.
        
        Args:
            log_file: Path to log file (None for console only)
        """
        self.log_file = log_file
        self.logger = self._setup_logging()
        
        # Error tracking
        self.error_history: list[ErrorContext] = []
        self.error_counts: Dict[str, int] = {}
        self.max_history = 1000
        
        # System state
        self.current_state = SystemState.NORMAL
        self.degraded_components: set[str] = set()
        
        # Resource monitoring
        self.resource_metrics: list[ResourceMetrics] = []
        self.max_metrics = 100
        self.monitoring_enabled = True
        self.monitor_thread: Optional[threading.Thread] = None
        self._stop_monitoring = threading.Event()
        
        # Recovery strategies
        self.recovery_strategies: Dict[str, Callable] = {}
        
        self.logger.info("Error handler initialized")
    
    def _setup_logging(self) -> logging.Logger:
        """
        Set up logging configuration.
        
        Returns:
            Configured logger
        """
        logger = logging.getLogger('smart_flow_v2')
        logger.setLevel(logging.DEBUG)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
        
        # File handler (if specified)
        if self.log_file:
            file_handler = logging.FileHandler(self.log_file)
            file_handler.setLevel(logging.DEBUG)
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
        
        return logger
    
    def log_error(self, context: ErrorContext) -> None:
        """
        Log an error with context.
        
        Args:
            context: Error context information
        """
        # Add to history
        self.error_history.append(context)
        if len(self.error_history) > self.max_history:
            self.error_history = self.error_history[-self.max_history:]
        
        # Update error counts
        key = f"{context.component}:{context.error_type}"
        self.error_counts[key] = self.error_counts.get(key, 0) + 1
        
        # Log based on severity
        extra = {'component': context.component}
        message = f"[{context.component}] {context.operation}: {context.message}"
        
        if context.severity == ErrorSeverity.INFO:
            self.logger.info(message, extra=extra)
        elif context.severity == ErrorSeverity.WARNING:
            self.logger.warning(message, extra=extra)
        elif context.severity == ErrorSeverity.ERROR:
            self.logger.error(message, extra=extra)
            if context.traceback_str:
                self.logger.debug(f"Traceback:\n{context.traceback_str}", extra=extra)
        elif context.severity == ErrorSeverity.CRITICAL:
            self.logger.critical(message, extra=extra)
            if context.traceback_str:
                self.logger.debug(f"Traceback:\n{context.traceback_str}", extra=extra)
        
        # Check error rate
        self._check_error_rate()
    
    def handle_exception(
        self,
        component: str,
        operation: str,
        exception: Exception,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        recovery_strategy: Optional[str] = None
    ) -> bool:
        """
        Handle an exception with optional recovery.
        
        Args:
            component: Component where error occurred
            operation: Operation being performed
            exception: The exception that occurred
            severity: Error severity level
            recovery_strategy: Name of recovery strategy to attempt
            
        Returns:
            True if recovered successfully, False otherwise
        """
        # Create error context
        context = ErrorContext(
            component=component,
            operation=operation,
            error_type=type(exception).__name__,
            message=str(exception),
            severity=severity,
            timestamp=time.time(),
            traceback_str=traceback.format_exc()
        )
        
        # Log the error
        self.log_error(context)
        
        # Attempt recovery if strategy provided
        if recovery_strategy and recovery_strategy in self.recovery_strategies:
            context.recovery_attempted = True
            try:
                self.logger.info(f"Attempting recovery: {recovery_strategy}")
                recovery_func = self.recovery_strategies[recovery_strategy]
                recovery_func(exception)
                context.recovery_successful = True
                self.logger.info(f"Recovery successful: {recovery_strategy}")
                return True
            except Exception as recovery_error:
                self.logger.error(f"Recovery failed: {recovery_error}")
                context.recovery_successful = False
        
        # Update system state based on severity
        if severity == ErrorSeverity.CRITICAL:
            self._degrade_component(component)
        
        return False
    
    def register_recovery_strategy(self, name: str, strategy: Callable) -> None:
        """
        Register a recovery strategy.
        
        Args:
            name: Strategy name
            strategy: Recovery function
        """
        self.recovery_strategies[name] = strategy
        self.logger.debug(f"Registered recovery strategy: {name}")
    
    def _degrade_component(self, component: str) -> None:
        """
        Mark a component as degraded.
        
        Args:
            component: Component name
        """
        self.degraded_components.add(component)
        self.logger.warning(f"Component degraded: {component}")
        
        # Update system state
        if len(self.degraded_components) >= 3:
            self.current_state = SystemState.CRITICAL
            self.logger.critical("System in CRITICAL state")
        elif len(self.degraded_components) >= 1:
            self.current_state = SystemState.DEGRADED
            self.logger.warning("System in DEGRADED state")
    
    def restore_component(self, component: str) -> None:
        """
        Mark a component as restored.
        
        Args:
            component: Component name
        """
        if component in self.degraded_components:
            self.degraded_components.remove(component)
            self.logger.info(f"Component restored: {component}")
            
            # Update system state
            if len(self.degraded_components) == 0:
                self.current_state = SystemState.NORMAL
                self.logger.info("System restored to NORMAL state")
            elif len(self.degraded_components) < 3:
                self.current_state = SystemState.DEGRADED
    
    def is_component_degraded(self, component: str) -> bool:
        """
        Check if a component is degraded.
        
        Args:
            component: Component name
            
        Returns:
            True if degraded, False otherwise
        """
        return component in self.degraded_components
    
    def get_system_state(self) -> SystemState:
        """
        Get current system state.
        
        Returns:
            Current SystemState
        """
        return self.current_state
    
    def _check_error_rate(self) -> None:
        """Check if error rate exceeds thresholds."""
        current_time = time.time()
        cutoff_time = current_time - self.ERROR_RATE_WINDOW
        
        # Count recent errors
        recent_errors = [e for e in self.error_history if e.timestamp >= cutoff_time]
        error_rate = len(recent_errors)
        
        if error_rate >= self.ERROR_RATE_CRITICAL:
            self.logger.critical(f"Critical error rate: {error_rate} errors in last minute")
            self.current_state = SystemState.CRITICAL
        elif error_rate >= self.ERROR_RATE_WARNING:
            self.logger.warning(f"High error rate: {error_rate} errors in last minute")
    
    def start_resource_monitoring(self, interval: float = 5.0) -> None:
        """
        Start background resource monitoring.
        
        Args:
            interval: Monitoring interval in seconds
        """
        if self.monitor_thread and self.monitor_thread.is_alive():
            return  # Already monitoring
        
        self._stop_monitoring.clear()
        self.monitor_thread = threading.Thread(
            target=self._monitor_resources,
            args=(interval,),
            daemon=True
        )
        self.monitor_thread.start()
        self.logger.info(f"Resource monitoring started (interval: {interval}s)")
    
    def stop_resource_monitoring(self) -> None:
        """Stop background resource monitoring."""
        if self.monitor_thread and self.monitor_thread.is_alive():
            self._stop_monitoring.set()
            self.monitor_thread.join(timeout=5.0)
            self.logger.info("Resource monitoring stopped")
    
    def _monitor_resources(self, interval: float) -> None:
        """
        Background resource monitoring loop.
        
        Args:
            interval: Monitoring interval in seconds
        """
        while not self._stop_monitoring.is_set():
            try:
                # Get resource metrics
                cpu_percent = psutil.cpu_percent(interval=1.0)
                memory = psutil.virtual_memory()
                memory_percent = memory.percent
                memory_available_mb = memory.available / (1024 * 1024)
                
                metrics = ResourceMetrics(
                    cpu_percent=cpu_percent,
                    memory_percent=memory_percent,
                    memory_available_mb=memory_available_mb,
                    timestamp=time.time()
                )
                
                # Store metrics
                self.resource_metrics.append(metrics)
                if len(self.resource_metrics) > self.max_metrics:
                    self.resource_metrics = self.resource_metrics[-self.max_metrics:]
                
                # Check thresholds
                if cpu_percent >= self.CPU_CRITICAL_THRESHOLD:
                    self.logger.critical(f"Critical CPU usage: {cpu_percent:.1f}%")
                    self.current_state = SystemState.CRITICAL
                elif cpu_percent >= self.CPU_WARNING_THRESHOLD:
                    self.logger.warning(f"High CPU usage: {cpu_percent:.1f}%")
                
                if memory_percent >= self.MEMORY_CRITICAL_THRESHOLD:
                    self.logger.critical(f"Critical memory usage: {memory_percent:.1f}%")
                    self.current_state = SystemState.CRITICAL
                elif memory_percent >= self.MEMORY_WARNING_THRESHOLD:
                    self.logger.warning(f"High memory usage: {memory_percent:.1f}%")
                
                # Sleep until next check
                time.sleep(interval)
                
            except Exception as e:
                self.logger.error(f"Error in resource monitoring: {e}")
                time.sleep(interval)
    
    def get_resource_metrics(self) -> Optional[ResourceMetrics]:
        """
        Get latest resource metrics.
        
        Returns:
            Latest ResourceMetrics or None if not available
        """
        if self.resource_metrics:
            return self.resource_metrics[-1]
        return None
    
    def should_throttle(self) -> bool:
        """
        Check if system should throttle processing.
        
        Returns:
            True if should throttle, False otherwise
        """
        metrics = self.get_resource_metrics()
        if metrics:
            return (metrics.cpu_percent >= self.CPU_WARNING_THRESHOLD or
                    metrics.memory_percent >= self.MEMORY_WARNING_THRESHOLD)
        return False
    
    def get_error_summary(self) -> Dict[str, Any]:
        """
        Get summary of errors.
        
        Returns:
            Dictionary with error statistics
        """
        current_time = time.time()
        cutoff_time = current_time - self.ERROR_RATE_WINDOW
        recent_errors = [e for e in self.error_history if e.timestamp >= cutoff_time]
        
        return {
            'total_errors': len(self.error_history),
            'recent_errors': len(recent_errors),
            'error_rate': len(recent_errors) / (self.ERROR_RATE_WINDOW / 60.0),
            'system_state': self.current_state.value,
            'degraded_components': list(self.degraded_components),
            'error_counts': self.error_counts.copy()
        }
    
    def shutdown(self) -> None:
        """Shutdown error handler and cleanup resources."""
        self.logger.info("Shutting down error handler")
        self.stop_resource_monitoring()
        self.current_state = SystemState.SHUTDOWN


def with_error_handling(
    component: str,
    operation: str,
    error_handler: ErrorHandler,
    severity: ErrorSeverity = ErrorSeverity.ERROR,
    recovery_strategy: Optional[str] = None,
    default_return: Any = None
):
    """
    Decorator for automatic error handling.
    
    Args:
        component: Component name
        operation: Operation name
        error_handler: ErrorHandler instance
        severity: Error severity level
        recovery_strategy: Recovery strategy name
        default_return: Default return value on error
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                recovered = error_handler.handle_exception(
                    component=component,
                    operation=operation,
                    exception=e,
                    severity=severity,
                    recovery_strategy=recovery_strategy
                )
                if not recovered:
                    return default_return
                # If recovered, try again
                try:
                    return func(*args, **kwargs)
                except Exception:
                    return default_return
        return wrapper
    return decorator
