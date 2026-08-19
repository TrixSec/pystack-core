"""
Events interfaces - Base interfaces for events module
"""

from typing import Callable, Any, Dict
from dataclasses import dataclass
from datetime import datetime
import uuid


@dataclass
class Event:
    """Base event class"""
    name: str
    data: Dict[str, Any]
    timestamp: datetime
    event_id: str = ""
    
    def __post_init__(self):
        if not self.event_id:
            self.event_id = str(uuid.uuid4())
