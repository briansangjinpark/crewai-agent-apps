from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Optional, List
import asyncio


@dataclass
class TaskProgress:
    """Represents the progress of a research task"""
    task_id: str
    status: str  # "planning" | "searching" | "writing" | "completed" | "failed"
    current_step: str
    percent: int
    result: Optional[str] = None
    error: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)


class TaskManager:
    """Manages in-memory task tracking and real-time updates"""

    def __init__(self):
        self.tasks: Dict[str, TaskProgress] = {}
        self.subscribers: Dict[str, List[asyncio.Queue]] = {}

    def create_task(self, task_id: str) -> TaskProgress:
        """Create a new task with initial state"""
        task = TaskProgress(
            task_id=task_id,
            status="planning",
            current_step="Starting...",
            percent=0
        )
        self.tasks[task_id] = task
        self.subscribers[task_id] = []
        return task

    async def update_task(self, task_id: str, **kwargs):
        """Update task progress and notify all subscribers"""
        if task_id in self.tasks:
            for key, value in kwargs.items():
                setattr(self.tasks[task_id], key, value)

            # Notify all subscribers
            for queue in self.subscribers.get(task_id, []):
                try:
                    await queue.put(self.tasks[task_id])
                except Exception:
                    # Queue might be closed, ignore
                    pass

    async def subscribe(self, task_id: str) -> asyncio.Queue:
        """Subscribe to task updates"""
        queue = asyncio.Queue()
        if task_id not in self.subscribers:
            self.subscribers[task_id] = []
        self.subscribers[task_id].append(queue)
        return queue

    def get_task(self, task_id: str) -> Optional[TaskProgress]:
        """Get current task state"""
        return self.tasks.get(task_id)

    def cleanup_old_tasks(self, max_age_minutes: int = 60):
        """Remove tasks older than max_age_minutes"""
        now = datetime.now()
        to_remove = [
            task_id for task_id, task in self.tasks.items()
            if (now - task.created_at).total_seconds() > max_age_minutes * 60
        ]
        for task_id in to_remove:
            del self.tasks[task_id]
            if task_id in self.subscribers:
                del self.subscribers[task_id]

        return len(to_remove)


# Global task manager instance
task_manager = TaskManager()
