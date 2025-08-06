"""Task management tools for the video researcher agent."""

from typing import Any, Dict, List, Optional

from common.task_management import TaskManager


def task_manager(
    state: Dict[str, Any], tasks: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """Comprehensive task management tool for organizing and tracking work.

    This tool allows complete management of a task list in a single operation, similar to
    how Claude Code handles todos. You can create, update, complete, and reorganize tasks
    all in one call. The tasks are stored in the agent's state.

    Usage modes:
    1. GET tasks: Call with tasks=None or empty list to retrieve current tasks
    2. MANAGE tasks: Call with tasks list to update the entire task list

    Each task item should have:
    - content: The task description (required)
    - status: "pending", "in_progress", or "completed" (optional, defaults to "pending")
    - priority: "low", "medium", or "high" (optional, defaults to "medium")
    - id: Unique identifier (optional, auto-generated if not provided)

    The tool will:
    - Return current tasks if no tasks parameter provided
    - Create new tasks for items without IDs
    - Update existing tasks that have matching IDs
    - Replace the entire task list in the agent state
    - Maintain task history and timestamps

    Args:
        state: Current agent state
        tasks: Complete list of task items to set as current task list (optional)
    """
    # If no tasks provided, return current tasks (GET mode)
    if tasks is None or (isinstance(tasks, list) and len(tasks) == 0):
        result = TaskManager.get_tasks_summary(state)
        return result

    if not isinstance(tasks, list):
        return {
            "success": False,
            "error": "tasks parameter must be a list of task items",
        }

    # Validate task items
    for i, task in enumerate(tasks):
        if not isinstance(task, dict):
            return {"success": False, "error": f"Task item {i} must be a dictionary"}

        if not task.get("content"):
            return {
                "success": False,
                "error": f"Task item {i} missing required 'content' field",
            }

        # Validate status if provided
        if "status" in task and task["status"] not in [
            "pending",
            "in_progress",
            "completed",
        ]:
            return {
                "success": False,
                "error": f"Task item {i} has invalid status. Must be: pending, in_progress, or completed",
            }

        # Validate priority if provided
        if "priority" in task and task["priority"] not in ["low", "medium", "high"]:
            return {
                "success": False,
                "error": f"Task item {i} has invalid priority. Must be: low, medium, or high",
            }

    # Use TaskManager to update tasks in state
    result = TaskManager.update_tasks_in_state(state, tasks)

    if result["success"]:
        # Add helpful message
        stats = result["stats"]
        summary = result["summary"]

        message_parts = []
        if stats["added"] > 0:
            message_parts.append(f"Added {stats['added']} new tasks")
        if stats["updated"] > 0:
            message_parts.append(f"Updated {stats['updated']} tasks")
        if stats["unchanged"] > 0:
            message_parts.append(f"{stats['unchanged']} tasks unchanged")

        status_summary = f"Status: {summary['pending']} pending, {summary['in_progress']} in progress, {summary['completed']} completed"
        completion = f"({summary['completion_percentage']:.1f}% complete)"

        result["message"] = (
            f"Task list updated successfully. {', '.join(message_parts)}. {status_summary} {completion}"
        )

    return result
