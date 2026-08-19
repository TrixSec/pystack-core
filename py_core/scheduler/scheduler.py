"""
Scheduler implementation - Cron and natural language scheduling
"""

from typing import Callable, Awaitable, Optional, Dict
from py_core.scheduler.interfaces import Schedule, ScheduleType
import uuid


class Scheduler:
    """Scheduler for cron and interval-based tasks"""
    
    def __init__(self):
        self._schedules: Dict[str, Schedule] = {}
    
    async def schedule(self, 
                      name: str, 
                      expression: str, 
                      task: Callable[[], Awaitable[None]]) -> str:
        """Schedule a task, returns schedule ID"""
        schedule_id = str(uuid.uuid4())
        schedule = Schedule(
            schedule_id=schedule_id,
            name=name,
            type=ScheduleType.CRON,
            expression=expression,
            task=task
        )
        self._schedules[schedule_id] = schedule
        return schedule_id
    
    async def unschedule(self, schedule_id: str) -> None:
        """Unschedule a task"""
        if schedule_id in self._schedules:
            del self._schedules[schedule_id]
    
    async def get_schedule(self, schedule_id: str) -> Optional[Schedule]:
        """Get schedule by ID"""
        return self._schedules.get(schedule_id)
    
    async def list_schedules(self) -> list[Schedule]:
        """List all schedules"""
        return list(self._schedules.values())
    
    def cron(self, expression: str) -> Callable:
        """Decorator for cron-scheduled tasks"""
        def decorator(func):
            return func
        return decorator
    
    def interval(self, seconds: int) -> Callable:
        """Decorator for interval-scheduled tasks"""
        def decorator(func):
            return func
        return decorator
