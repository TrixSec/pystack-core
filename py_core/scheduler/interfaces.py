"""
Scheduler interfaces - Base interfaces for scheduler module
"""

from typing import Callable, Awaitable, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import uuid


class ScheduleType(Enum):
    """Schedule types"""
    CRON = "cron"
    INTERVAL = "interval"
    ONCE = "once"


@dataclass
class Schedule:
    """Schedule configuration"""
    schedule_id: str
    name: str
    type: ScheduleType
    expression: str
    task: Callable[[], Awaitable[None]]
    enabled: bool = True
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    
    def __post_init__(self):
        if not self.schedule_id:
            self.schedule_id = str(uuid.uuid4())
