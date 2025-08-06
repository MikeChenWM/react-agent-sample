"""Video researcher tools for web scraping, search, and video platform analysis.

This module provides tools for researching video content across various platforms:
- General web search via Tavily
- TikTok hashtag analysis and search
- Video content analysis via Gemini Vision API
- Todo management for task tracking
- Additional video platform tools can be added here

These tools are designed for video research and content analysis workflows.
"""

from typing import Any, Callable, List

from .task_tools import task_manager
from .tavily_tools import tavily_search
from .tiktok_tools import tiktok_hashtag_posts, tiktok_hashtag_search
from .video_analyzer_tools import video_analyzer

TOOLS: List[Callable[..., Any]] = [
    tavily_search,
    tiktok_hashtag_search,
    tiktok_hashtag_posts,
    task_manager,
    video_analyzer,
]

__all__ = [
    "tiktok_hashtag_search",
    "tiktok_hashtag_posts",
    "tavily_search",
    "task_manager",
    "video_analyzer",
    "TOOLS",
]
