"""
Queue interfaces - Base interfaces for queue module
"""

from typing import Any, Dict, List, Optional
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
import uuid


class TaskStatus(Enum):
    """Task statuses"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILURE = "failure"
    RETRY = "retry"


class TaskBackend(Enum):
    """Queue backend types"""
    MEMORY = "memory"
    REDIS = "redis"
    CELERY = "celery"


@dataclass
class Task:
    """Background task"""
    task_id: str
    name: str
    args: List[Any]
    kwargs: Dict[str, Any]
    status: TaskStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Any] = None
    error: Optional[str] = None
    retry_count: int = 0
    
    def __post_init__(self):
        if not self.task_id:
            self.task_id = str(uuid.uuid4())
