"""
Monitoring and observability utilities for VolveRAG.

This module provides structured metrics, health checks, and observability
features for production monitoring.
"""
import time
import threading
from typing import Dict, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict

from .logging import get_logger

logger = get_logger(__name__)


@dataclass
class Metric:
    """Single metric value with timestamp."""
    name: str
    value: float
    timestamp: float = field(default_factory=time.time)
    tags: Dict[str, str] = field(default_factory=dict)


class MetricsCollector:
    """
    Thread-safe metrics collector.
    
    Collects and aggregates metrics for monitoring and observability.
    Supports counters, gauges, and histograms.
    """
    
    def __init__(self):
        """Initialize metrics collector."""
        self._counters: Dict[str, float] = defaultdict(float)
        self._gauges: Dict[str, float] = {}
        self._histograms: Dict[str, list] = defaultdict(list)
        self._lock = threading.Lock()
        self._start_time = time.time()
    
    def increment(self, name: str, value: float = 1.0, tags: Optional[Dict[str, str]] = None) -> None:
        """
        Increment a counter metric.
        
        Args:
            name: Metric name
            value: Value to increment by (default: 1.0)
            tags: Optional tags for the metric
        """
        with self._lock:
            self._counters[name] += value
            logger.debug(f"Metric incremented: {name} += {value}")
    
    def set_gauge(self, name: str, value: float, tags: Optional[Dict[str, str]] = None) -> None:
        """
        Set a gauge metric (current value).
        
        Args:
            name: Metric name
            value: Current value
            tags: Optional tags for the metric
        """
        with self._lock:
            self._gauges[name] = value
            logger.debug(f"Gauge set: {name} = {value}")
    
    def record_histogram(self, name: str, value: float, tags: Optional[Dict[str, str]] = None) -> None:
        """
        Record a histogram value.
        
        Args:
            name: Metric name
            value: Value to record
            tags: Optional tags for the metric
        """
        with self._lock:
            self._histograms[name].append(value)
            # Keep only last 1000 values to prevent memory growth
            if len(self._histograms[name]) > 1000:
                self._histograms[name] = self._histograms[name][-1000:]
            logger.debug(f"Histogram recorded: {name} = {value}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get all metrics as a dictionary.
        
        Returns:
            Dictionary containing counters, gauges, and histogram summaries
        """
        with self._lock:
            # Calculate histogram statistics
            histogram_stats = {}
            for name, values in self._histograms.items():
                if values:
                    histogram_stats[name] = {
                        "count": len(values),
                        "min": min(values),
                        "max": max(values),
                        "mean": sum(values) / len(values),
                        "p50": sorted(values)[len(values) // 2] if values else 0,
                        "p95": sorted(values)[int(len(values) * 0.95)] if values else 0,
                        "p99": sorted(values)[int(len(values) * 0.99)] if values else 0,
                    }
            
            return {
                "counters": dict(self._counters),
                "gauges": dict(self._gauges),
                "histograms": histogram_stats,
                "uptime_seconds": time.time() - self._start_time,
            }
    
    def reset(self) -> None:
        """Reset all metrics (thread-safe)."""
        with self._lock:
            self._counters.clear()
            self._gauges.clear()
            self._histograms.clear()
            self._start_time = time.time()


# Global metrics collector instance
_metrics_collector: Optional[MetricsCollector] = None
_metrics_lock = threading.Lock()


def get_metrics_collector() -> MetricsCollector:
    """Get or create global metrics collector."""
    global _metrics_collector
    if _metrics_collector is None:
        with _metrics_lock:
            if _metrics_collector is None:
                _metrics_collector = MetricsCollector()
    return _metrics_collector


def record_request_metric(endpoint: str, duration: float, status: str = "success") -> None:
    """
    Record a request metric.
    
    Args:
        endpoint: Endpoint name
        duration: Request duration in seconds
        status: Request status ("success" or "error")
    """
    collector = get_metrics_collector()
    collector.increment(f"requests.{endpoint}.{status}")
    collector.record_histogram(f"requests.{endpoint}.duration", duration)
    collector.increment("requests.total")


def record_llm_metric(model: str, duration: float, tokens: Optional[int] = None) -> None:
    """
    Record an LLM call metric.
    
    Args:
        model: Model name
        duration: Call duration in seconds
        tokens: Number of tokens (if available)
    """
    collector = get_metrics_collector()
    collector.increment(f"llm.{model}.calls")
    collector.record_histogram(f"llm.{model}.duration", duration)
    if tokens:
        collector.record_histogram(f"llm.{model}.tokens", float(tokens))


def record_cache_metric(operation: str, hit: bool) -> None:
    """
    Record a cache operation metric.
    
    Args:
        operation: Cache operation name
        hit: Whether it was a cache hit
    """
    collector = get_metrics_collector()
    collector.increment(f"cache.{operation}.{'hit' if hit else 'miss'}")
    collector.increment(f"cache.{operation}.total")


@dataclass
class HealthStatus:
    """Health check status."""
    healthy: bool
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


def check_health() -> HealthStatus:
    """
    Perform health check.
    
    Checks:
    - Configuration loaded
    - Cache operational
    - Rate limiter operational
    
    Returns:
        HealthStatus indicating system health
    """
    details = {}
    issues = []
    
    # Check configuration
    try:
        from .config import get_config
        config = get_config()
        details["config"] = "ok"
    except Exception as e:
        details["config"] = f"error: {str(e)}"
        issues.append("Configuration failed")
    
    # Check cache
    try:
        from .cache import get_llm_cache
        cache = get_llm_cache()
        cache.get("health_check")
        details["cache"] = "ok"
    except Exception as e:
        details["cache"] = f"error: {str(e)}"
        issues.append("Cache failed")
    
    # Check rate limiter
    try:
        from .security import get_rate_limiter
        limiter = get_rate_limiter()
        limiter.get_remaining("health_check")
        details["rate_limiter"] = "ok"
    except Exception as e:
        details["rate_limiter"] = f"error: {str(e)}"
        issues.append("Rate limiter failed")
    
    healthy = len(issues) == 0
    message = "All systems operational" if healthy else f"Issues: {', '.join(issues)}"
    
    return HealthStatus(
        healthy=healthy,
        message=message,
        details=details
    )

