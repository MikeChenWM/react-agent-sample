"""TikTok search and analysis tools."""

import os
from typing import Any, Dict

from clients.tiktok import TikTokClient


async def tiktok_hashtag_search(hashtag: str) -> Dict[str, Any]:
    """Search for TikTok hashtag information.

    This tool retrieves detailed information about a TikTok hashtag including:
    - User count (how many users have used this hashtag)
    - View count (total views for videos with this hashtag)
    - Hashtag type and characteristics
    - Whether it's associated with challenges, commerce, etc.

    Args:
        hashtag: The hashtag name to search for (with or without #)
    """
    api_key = os.getenv("RAPIDAPI_KEY")
    if not api_key:
        return {"error": "RAPIDAPI_KEY environment variable not set", "success": False}

    try:
        async with TikTokClient(api_key=api_key) as client:
            hashtag_info = await client.get_hashtag_info(hashtag)

            if not hashtag_info:
                return {
                    "error": f"Hashtag '{hashtag}' not found or API request failed",
                    "success": False,
                    "hashtag": hashtag,
                }

            return {
                "success": True,
                "hashtag": hashtag_info.hashtag_name,
                "challenge_id": hashtag_info.id,
                "description": hashtag_info.desc or "No description available",
                "stats": {
                    "user_count": hashtag_info.user_count,
                    "formatted_user_count": hashtag_info.formatted_user_count,
                    "view_count": hashtag_info.view_count,
                    "formatted_view_count": hashtag_info.formatted_view_count,
                },
                "characteristics": {
                    "is_challenge": hashtag_info.is_challenge,
                    "is_commerce": hashtag_info.is_commerce,
                    "is_pgcshow": hashtag_info.is_pgcshow,
                    "is_strong_music": hashtag_info.is_strong_music,
                    "type": hashtag_info.type,
                },
                "cover": hashtag_info.cover,
                "raw_data": hashtag_info.dict(),
            }

    except Exception as e:
        return {
            "error": f"Failed to search TikTok hashtag: {str(e)}",
            "success": False,
            "hashtag": hashtag,
        }


async def tiktok_hashtag_posts(challenge_id: str, count: int = 50) -> Dict[str, Any]:
    """Get posts/videos from a TikTok hashtag challenge with automatic pagination.

    This tool retrieves videos from a specific TikTok hashtag challenge including:
    - Video titles and descriptions
    - Play counts, like counts, comment counts
    - Video authors and music information
    - Video covers and play URLs
    - Creation timestamps
    - Direct TikTok URLs and video play URLs

    The tool automatically handles pagination to fetch the requested number of videos
    by making multiple API calls (each call fetches max 20 videos).

    Args:
        challenge_id: The hashtag challenge ID (get this from tiktok_hashtag_search first)
        count: Number of videos to fetch (default 50, can be much higher than 20)
    """
    api_key = os.getenv("RAPIDAPI_KEY")
    if not api_key:
        return {"error": "RAPIDAPI_KEY environment variable not set", "success": False}

    try:
        # Ensure reasonable limits but allow much higher counts
        count = max(count, 1)  # At least 1 video
        max_pages = min(count // 20 + 1, 50)  # Reasonable page limit to prevent abuse

        async with TikTokClient(api_key=api_key) as client:
            result = await client.get_hashtag_posts(
                challenge_id=challenge_id, target_count=count, max_pages=max_pages
            )

            if not result or not result.videos:
                return {
                    "error": f"No videos found for challenge_id '{challenge_id}' or API request failed",
                    "success": False,
                    "challenge_id": challenge_id,
                }

            # Format video data for the agent
            formatted_videos = []
            for video in result.videos:
                formatted_video = {
                    "video_id": video.video_id,
                    "title": video.title,
                    "tiktok_url": video.tiktok_url,
                    "play_url": video.play,
                    "cover_url": video.cover,
                    "duration": video.duration,
                    "author": {
                        "username": video.author.unique_id
                        if video.author
                        else "unknown",
                        "nickname": video.author.nickname
                        if video.author
                        else "unknown",
                        "avatar": video.author.avatar if video.author else "",
                    },
                    "stats": {
                        "play_count": video.play_count,
                        "formatted_play_count": video.formatted_play_count,
                        "like_count": video.digg_count,
                        "formatted_like_count": video.formatted_digg_count,
                        "comment_count": video.comment_count,
                        "formatted_comment_count": video.formatted_comment_count,
                        "share_count": video.share_count,
                        "formatted_share_count": video.formatted_share_count,
                        "collect_count": video.collect_count,
                    },
                    "music": {
                        "title": video.music_info.title if video.music_info else "",
                        "author": video.music_info.author if video.music_info else "",
                        "duration": video.music_info.duration
                        if video.music_info
                        else 0,
                        "original": video.music_info.original
                        if video.music_info
                        else False,
                    },
                    "create_time": video.create_time,
                    "is_top": bool(video.is_top),
                }
                formatted_videos.append(formatted_video)

            return {
                "success": True,
                "challenge_id": challenge_id,
                "requested_count": count,
                "video_count": len(formatted_videos),
                "total_fetched": result.total_fetched,
                "has_more": result.has_more,
                "next_cursor": result.cursor,
                "videos": formatted_videos,
                "message": f"Successfully fetched {len(formatted_videos)} videos from hashtag challenge (requested: {count})",
            }

    except Exception as e:
        return {
            "error": f"Failed to get hashtag posts: {str(e)}",
            "success": False,
            "challenge_id": challenge_id,
        }
