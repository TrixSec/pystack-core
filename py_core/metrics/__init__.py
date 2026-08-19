"""
Metrics module - Automatic metrics collection and export
"""

from py_core.metrics.metrics import Metrics
from py_core.metrics.interfaces import MetricType, Metric

__all__ = [
    "Metrics",
    "MetricType",
    "Metric",
]
