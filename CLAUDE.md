# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Testing
- `make test` - Run unit tests
- `make test TEST_FILE=tests/unit_tests/test_specific.py` - Run specific test file
- `make test_watch` - Run tests in watch mode with auto-reload
- `make extended_tests` - Run extended/integration tests
- `pytest tests/integration_tests/` - Run integration tests directly

### Linting and Formatting
- `make lint` - Run all linters (ruff, mypy)
- `make format` - Auto-format code with ruff
- `make lint_diff` - Lint only changed files vs main branch
- `make format_diff` - Format only changed files vs main branch

### LangGraph Development
- `langgraph dev` - Start LangGraph Studio for interactive development
- `langgraph up` - Deploy the graph locally

## Project Architecture

This is a specialized Video Researcher agent built on LangGraph and Python. The architecture follows a clean, modular design optimized for video platform research and content analysis.

### Core Architecture

**Graph Definition (`src/video_researcher/graph.py`)**
- ReAct pattern: reasoning → action (tools) → observation → repeat
- State flows: start → call_model → (tools if needed) → call_model → end
- Specialized for video research queries and multi-platform data aggregation

**State Management (`src/video_researcher/state.py`)**
- `InputState`: External interface with message history
- `State`: Internal state extending InputState with `is_last_step` flag and `tasks` list
- Optimized for video research workflows, tool chaining, and task management

**Configuration (`src/video_researcher/configuration.py`)**
- Model selection (default: anthropic/claude-3-5-sonnet-20240620)
- Video researcher system prompt
- Configurable search result limits

**Tool Architecture (`src/video_researcher/tools/`)**
- Modular tool organization by platform and functionality
- `tiktok_tools.py` - TikTok hashtag analysis and video fetching
- `tavily_tools.py` - Web search for video-related research
- `task_tools.py` - Task management for complex multi-step research
- `__init__.py` - Central TOOLS registry

**API Client Layer (`src/clients/`)**
- `base.py` - Shared BaseAPIClient with async HTTP handling
- `tiktok/` - Complete TikTok API integration with models, endpoints, utilities
- Designed for easy extension to YouTube, Instagram, etc.

**Common Shared Layer (`src/common/`)**
- `task_management/` - Reusable task management functionality
  - `models.py` - Task, TaskStatus, TaskPriority models
  - `manager.py` - TaskManager core logic for state operations
  - Follows same pattern as `clients/` for consistency

### Key Files
- `langgraph.json` - LangGraph configuration (graph name: `video_researcher`)  
- `pyproject.toml` - Dependencies including httpx, pydantic for API clients
- `Makefile` - Development commands and workflows

### Environment Setup
Required API keys in `.env`:
- `ANTHROPIC_API_KEY` - For Claude model
- `TAVILY_API_KEY` - For web search
- `RAPIDAPI_KEY` - For TikTok API access

### Adding New Video Platform Tools

**1. Create API Client**
```python
# src/clients/youtube/client.py
from ..base import BaseAPIClient
from .models import VideoInfo

class YouTubeClient(BaseAPIClient):
    def _get_default_headers(self):
        return {"Authorization": f"Bearer {self.api_key}"}
```

**2. Add Tool Functions**
```python  
# src/video_researcher/tools/youtube_tools.py
async def youtube_search(query: str) -> Dict[str, Any]:
    """Search YouTube videos with comprehensive metadata."""
    # Implementation following tool design patterns
```

**3. Register in Tools**
```python
# src/video_researcher/tools/__init__.py
from .youtube_tools import youtube_search

TOOLS = [tavily_search, tiktok_hashtag_search, tiktok_hashtag_posts, task_manager, youtube_search]
```

### Tool Design Patterns

**Consistent Return Format:**
- Always return `Dict[str, Any]` with `success: bool` field
- Include both raw data and formatted/human-readable versions
- Provide actionable URLs and metadata

**Error Handling:**
- Graceful API failure handling with descriptive error messages
- API key validation with clear setup instructions

**Data Formatting:**
- Shared utility functions for consistent number formatting (K/M/B)
- URL generation following platform conventions
- Structured data with stats, metadata, and content

**Pagination Support:**
- Automatic cursor-based pagination for large datasets
- Configurable limits with reasonable defaults
- Progress tracking and hasMore indicators

### Current Tool Capabilities

**TikTok Integration:**
- `tiktok_hashtag_search(hashtag)` - Get hashtag analytics, challenge IDs
- `tiktok_hashtag_posts(challenge_id, count)` - Fetch videos with pagination

**Web Research:**
- `tavily_search(query)` - General web search for video topics

**Task Management:**
- `task_manager(state, tasks)` - Comprehensive task list management
  - GET mode: Call with `tasks=None` to view current tasks
  - MANAGE mode: Call with task list to update entire task list
  - State-based persistence across conversation turns
  - Support for pending/in_progress/completed status and low/medium/high priority

**Data Quality:**
- Formatted metrics (e.g., "75.8M users", "909.6B views")
- Direct platform URLs (e.g., "https://www.tiktok.com/@user/video/123")
- Comprehensive video metadata (author, music, engagement stats)

### Adding Common Tools

**1. Create Core Functionality**
```python
# src/common/your_tool/models.py
from pydantic import BaseModel

class YourModel(BaseModel):
    # Define your data models
```

**2. Create Manager Class**
```python
# src/common/your_tool/manager.py
class YourManager:
    @staticmethod
    def operation(state: Dict[str, Any]) -> Dict[str, Any]:
        # Core logic here
```

**3. Create Agent Tool Wrapper**
```python
# src/video_researcher/tools/your_tools.py
from common.your_tool import YourManager

def your_tool(state: Dict[str, Any], params) -> Dict[str, Any]:
    return YourManager.operation(state, params)
```