"""Tavily search tools for web scraping and search functionality."""

from typing import Any, Optional, cast

from langchain_tavily import TavilySearch  # type: ignore[import-not-found]

from video_researcher.configuration import Configuration


async def tavily_search(query: str) -> Optional[dict[str, Any]]:
    """Search for general web results.

    This function performs a search using the Tavily search engine, which is designed
    to provide comprehensive, accurate, and trusted results. It's particularly useful
    for answering questions about current events.
    
    Args:
        query: The search query string
    """
    configuration = Configuration.from_context()
    wrapped = TavilySearch(max_results=configuration.max_search_results)
    return cast(dict[str, Any], await wrapped.ainvoke({"query": query}))