"""TikTok API client implementation."""

from typing import Dict, Optional

from ..base import BaseAPIClient
from .endpoints import BASE_URL, ENDPOINTS
from .models import (
    HashtagInfo,
    HashtagPostsResponse,
    PaginatedResult,
    TikTokAPIResponse,
)


class TikTokClient(BaseAPIClient):
    """TikTok API client for scraping TikTok data."""

    def __init__(self, api_key: str, timeout: float = 30.0):
        """Initialize TikTok client with API key and timeout."""
        super().__init__(api_key=api_key, base_url=BASE_URL, timeout=timeout)

    def _get_default_headers(self) -> Dict[str, str]:
        """Get default headers for TikTok API requests."""
        return {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": "tiktok-scraper7.p.rapidapi.com",
        }

    async def get_hashtag_info(self, hashtag_name: str) -> Optional[HashtagInfo]:
        """Get information about a TikTok hashtag.

        Args:
            hashtag_name: The hashtag name (without #)

        Returns:
            HashtagInfo object if successful, None otherwise
        """
        # Clean hashtag name (remove # if present)
        clean_hashtag = hashtag_name.lstrip("#")

        response = await self._make_request(
            method="GET",
            endpoint=ENDPOINTS["CHALLENGE_INFO"],
            params={"challenge_name": clean_hashtag},
        )

        if not response.success or not response.data:
            return None

        try:
            # Parse the TikTok API response
            tiktok_response = TikTokAPIResponse(**response.data)

            if tiktok_response.code != 0 or not tiktok_response.data:
                return None

            # Create HashtagInfo from the data
            return HashtagInfo(**tiktok_response.data)

        except Exception:
            return None

    async def search_hashtags(self, query: str, limit: int = 10) -> Dict[str, any]:
        """Search for hashtags related to a query.

        Args:
            query: Search query
            limit: Maximum number of results

        Returns:
            Dictionary with search results
        """
        # This would be implemented when the search endpoint is available
        # For now, we'll return the single hashtag info if it matches
        hashtag_info = await self.get_hashtag_info(query)

        if hashtag_info:
            return {"query": query, "results": [hashtag_info.dict()], "total_count": 1}
        else:
            return {"query": query, "results": [], "total_count": 0}

    async def get_hashtag_posts_page(
        self, challenge_id: str, count: int = 20, cursor: int = 0
    ) -> Optional[PaginatedResult]:
        """Get a single page of posts/videos from a TikTok hashtag challenge.

        Args:
            challenge_id: The hashtag challenge ID
            count: Number of videos to fetch (max 20 per API call)
            cursor: Pagination cursor for fetching more results

        Returns:
            PaginatedResult with videos and pagination info, None if failed
        """
        # Limit count to max 20 as per API limit
        count = min(count, 20)

        response = await self._make_request(
            method="GET",
            endpoint=ENDPOINTS["CHALLENGE_POSTS"],
            params={"challenge_id": challenge_id, "count": count, "cursor": cursor},
        )

        if not response.success or not response.data:
            return None

        try:
            # Parse the TikTok API response
            posts_response = HashtagPostsResponse(**response.data)

            if posts_response.code != 0 or not posts_response.data:
                return None

            return PaginatedResult(
                videos=posts_response.data.videos,
                cursor=posts_response.data.cursor,
                has_more=posts_response.data.hasMore,
                total_fetched=len(posts_response.data.videos),
            )

        except Exception:
            return None

    async def get_hashtag_posts(
        self, challenge_id: str, target_count: int = 50, max_pages: int = 10
    ) -> Optional[PaginatedResult]:
        """Get posts/videos from a TikTok hashtag challenge with automatic pagination.

        Args:
            challenge_id: The hashtag challenge ID
            target_count: Target number of videos to fetch (will fetch at least this many)
            max_pages: Maximum number of API calls to prevent infinite loops

        Returns:
            PaginatedResult with all fetched videos, None if failed
        """
        all_videos = []
        cursor = 0
        pages_fetched = 0

        while len(all_videos) < target_count and pages_fetched < max_pages:
            # Calculate how many videos we still need
            remaining = target_count - len(all_videos)
            page_size = min(20, remaining)  # API max is 20

            page_result = await self.get_hashtag_posts_page(
                challenge_id=challenge_id, count=page_size, cursor=cursor
            )

            if not page_result or not page_result.videos:
                break

            all_videos.extend(page_result.videos)
            cursor = page_result.cursor
            pages_fetched += 1

            # If no more data available, break
            if not page_result.has_more:
                break

        if not all_videos:
            return None

        return PaginatedResult(
            videos=all_videos,
            cursor=cursor,
            has_more=pages_fetched < max_pages and len(all_videos) >= target_count,
            total_fetched=len(all_videos),
        )
