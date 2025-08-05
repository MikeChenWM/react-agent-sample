"""Pydantic models for task management."""

import time
from enum import Enum
from uuid import uuid4

from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    """Task status enumeration."""
    
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class TaskPriority(str, Enum):
    """Task priority enumeration."""
    
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Task(BaseModel):
    """Individual task model for tracking work items."""
    
    id: str = Field(default_factory=lambda: str(uuid4())[:8])
    content: str
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.MEDIUM
    created_at: float = Field(default_factory=time.time)
    updated_at: float = Field(default_factory=time.time)
    
    def mark_completed(self) -> None:
        """Mark task as completed."""
        self.status = TaskStatus.COMPLETED
        self.updated_at = time.time()
    
    def mark_in_progress(self) -> None:
        """Mark task as in progress."""
        self.status = TaskStatus.IN_PROGRESS
        self.updated_at = time.time()
    
    def mark_pending(self) -> None:
        """Mark task as pending."""
        self.status = TaskStatus.PENDING
        self.updated_at = time.time()
    
    def update_content(self, content: str) -> None:
        """Update task content."""
        self.content = content
        self.updated_at = time.time()
    
    def update_priority(self, priority: TaskPriority) -> None:
        """Update task priority."""
        self.priority = priority
        self.updated_at = time.time()
    
    @property
    def formatted_created_at(self) -> str:
        """Get formatted creation time."""
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.created_at))
    
    @property
    def formatted_updated_at(self) -> str:
        """Get formatted update time."""
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.updated_at))
    
    @property
    def is_completed(self) -> bool:
        """Check if task is completed."""
        return self.status == TaskStatus.COMPLETED
    
    @property
    def is_in_progress(self) -> bool:
        """Check if task is in progress."""
        return self.status == TaskStatus.IN_PROGRESS
    
    @property
    def is_pending(self) -> bool:
        """Check if task is pending."""
        return self.status == TaskStatus.PENDING