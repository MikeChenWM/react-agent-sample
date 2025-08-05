"""Core task management functionality."""

from typing import Any, Dict, List

from .models import Task, TaskPriority, TaskStatus


class TaskManager:
    """Core task management operations for agent state."""
    
    @staticmethod
    def get_tasks_from_state(state: Dict[str, Any]) -> List[Task]:
        """Get current tasks from agent state."""
        tasks = state.get("tasks", [])
        
        # Ensure tasks are Task objects
        task_objects = []
        for task in tasks:
            if isinstance(task, Task):
                task_objects.append(task)
            elif isinstance(task, dict):
                task_objects.append(Task(**task))
        
        return task_objects
    
    @staticmethod
    def update_tasks_in_state(
        state: Dict[str, Any], 
        task_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Update entire task list in agent state.
        
        Args:
            state: Current agent state
            task_data: List of task dictionaries to set as current tasks
            
        Returns:
            Dictionary with success status and updated tasks info
        """
        try:
            # Get existing tasks from state
            existing_tasks = TaskManager.get_tasks_from_state(state)
            existing_ids = {task.id for task in existing_tasks}
            
            # Process new task data
            updated_tasks = []
            stats = {"added": 0, "updated": 0, "unchanged": 0}
            
            for data in task_data:
                # Parse status and priority
                status = TaskStatus(data.get("status", "pending"))
                priority = TaskPriority(data.get("priority", "medium"))
                
                if "id" in data and data["id"] in existing_ids:
                    # Find and update existing task
                    existing_task = None
                    for task in existing_tasks:
                        if task.id == data["id"]:
                            existing_task = task
                            break
                    
                    if existing_task:
                        old_data = (existing_task.content, existing_task.status, existing_task.priority)
                        existing_task.update_content(data["content"])
                        existing_task.status = status
                        existing_task.priority = priority
                        
                        new_data = (existing_task.content, existing_task.status, existing_task.priority)
                        if old_data != new_data:
                            stats["updated"] += 1
                        else:
                            stats["unchanged"] += 1
                        
                        updated_tasks.append(existing_task)
                else:
                    # Create new task
                    new_task = Task(
                        content=data["content"],
                        status=status,
                        priority=priority
                    )
                    if "id" in data:
                        new_task.id = data["id"]
                    
                    updated_tasks.append(new_task)
                    stats["added"] += 1
            
            # Update state with new tasks
            state["tasks"] = updated_tasks
            
            # Calculate summary
            pending_count = len([t for t in updated_tasks if t.is_pending])
            in_progress_count = len([t for t in updated_tasks if t.is_in_progress])
            completed_count = len([t for t in updated_tasks if t.is_completed])
            total_count = len(updated_tasks)
            completion_percentage = (completed_count / total_count * 100) if total_count > 0 else 0
            
            return {
                "success": True,
                "total_tasks": total_count,
                "stats": stats,
                "tasks": [
                    {
                        "id": task.id,
                        "content": task.content,
                        "status": task.status.value,
                        "priority": task.priority.value,
                        "created_at": task.formatted_created_at,
                        "updated_at": task.formatted_updated_at
                    }
                    for task in updated_tasks
                ],
                "summary": {
                    "pending": pending_count,
                    "in_progress": in_progress_count,
                    "completed": completed_count,
                    "completion_percentage": completion_percentage
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Task management failed: {str(e)}"
            }
    
    @staticmethod
    def get_tasks_summary(state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get current task summary from agent state.
        
        Args:
            state: Current agent state
            
        Returns:
            Dictionary with success status and task summary
        """
        try:
            tasks = TaskManager.get_tasks_from_state(state)
            
            if not tasks:
                return {
                    "success": True,
                    "total_tasks": 0,
                    "tasks": [],
                    "message": "No tasks found. Use task management to create your first task list.",
                    "summary": {
                        "pending": 0,
                        "in_progress": 0,
                        "completed": 0,
                        "completion_percentage": 0.0
                    }
                }
            
            # Calculate summary
            pending_count = len([t for t in tasks if t.is_pending])
            in_progress_count = len([t for t in tasks if t.is_in_progress])
            completed_count = len([t for t in tasks if t.is_completed])
            total_count = len(tasks)
            completion_percentage = (completed_count / total_count * 100) if total_count > 0 else 0
            
            message = (
                f"Found {total_count} tasks: "
                f"{pending_count} pending, {in_progress_count} in progress, "
                f"{completed_count} completed ({completion_percentage:.1f}% complete)"
            )
            
            return {
                "success": True,
                "total_tasks": total_count,
                "message": message,
                "tasks": [
                    {
                        "id": task.id,
                        "content": task.content,
                        "status": task.status.value,
                        "priority": task.priority.value,
                        "created_at": task.formatted_created_at,
                        "updated_at": task.formatted_updated_at
                    }
                    for task in tasks
                ],
                "summary": {
                    "pending": pending_count,
                    "in_progress": in_progress_count,
                    "completed": completed_count,
                    "completion_percentage": completion_percentage
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get tasks: {str(e)}"
            }