"""Utility functions for TikTok data formatting."""


def format_count(count: int, suffix: str = "") -> str:
    """
    Format a number with appropriate units (K, M, B).
    
    Args:
        count: The number to format
        suffix: Optional suffix to add (e.g., "views", "likes")
        
    Returns:
        Formatted string with units
    """
    if count >= 1_000_000_000:
        formatted = f"{count / 1_000_000_000:.1f}B"
    elif count >= 1_000_000:
        formatted = f"{count / 1_000_000:.1f}M"
    elif count >= 1_000:
        formatted = f"{count / 1_000:.1f}K"
    else:
        formatted = str(count)
    
    return f"{formatted} {suffix}".strip()


def format_tiktok_url(username: str, video_id: str) -> str:
    """
    Format a TikTok video URL.
    
    Args:
        username: The author's username (unique_id)
        video_id: The video ID
        
    Returns:
        Complete TikTok video URL
    """
    return f"https://www.tiktok.com/@{username}/video/{video_id}"