"""
Metrics interfaces - Base interfaces for metrics module
"""

from typing import Any, Dict, Optional
from enum import Enum
from dataclasses import dataclass


class MetricType(Enum):
    """Metric types"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


@dataclass
class Metric:
    """Metric with metadata"""
    name: str
    type: MetricType
    value: float
    labels: Optional[Dict[str, str]] = None
    timestamp: Optional[float] = None
