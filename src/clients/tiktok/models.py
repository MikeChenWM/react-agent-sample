"""Pydantic models for TikTok API responses."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from .utils import format_count, format_tiktok_url


class PaginatedResult(BaseModel):
    """Result with pagination info."""
    
    videos: List['VideoInfo'] = []
    cursor: int = 0
    has_more: bool = False
    total_fetched: int = 0


class TikTokAPIResponse(BaseModel):
    """Base TikTok API response model."""
    
    code: int
    msg: str
    processed_time: float
    data: Optional[Dict[str, Any]] = None


class HashtagInfo(BaseModel):
    """TikTok hashtag information model."""
    
    id: str
    cha_name: str = Field(alias="cha_name")
    desc: str = ""
    user_count: int = 0
    view_count: int = 0
    is_pgcshow: bool = False
    is_commerce: bool = False
    is_challenge: bool = False
    is_strong_music: bool = False
    type: int = 0
    cover: str = ""
    
    class Config:
        populate_by_name = True
        
    @property
    def hashtag_name(self) -> str:
        """Get clean hashtag name."""
        return self.cha_name
    
    @property
    def formatted_user_count(self) -> str:
        """Get formatted user count."""
        return format_count(self.user_count, "users")
    
    @property
    def formatted_view_count(self) -> str:
        """Get formatted view count."""
        return format_count(self.view_count, "views")


class UserInfo(BaseModel):
    """TikTok user information model."""
    
    id: str
    unique_id: str
    nickname: str
    avatar: str = ""
    signature: str = ""
    follower_count: int = 0
    following_count: int = 0
    heart_count: int = 0
    video_count: int = 0
    verified: bool = False


class MusicInfo(BaseModel):
    """TikTok music information model."""
    
    id: str
    title: str
    play: str = ""
    cover: str = ""
    author: str = ""
    original: bool = False
    duration: int = 0
    album: str = ""


class VideoAuthor(BaseModel):
    """TikTok video author model."""
    
    id: str
    unique_id: str
    nickname: str
    avatar: str = ""


class VideoInfo(BaseModel):
    """TikTok video information model."""
    
    aweme_id: str
    video_id: str
    region: str = ""
    title: str = ""
    cover: str = ""
    duration: int = 0
    play: str = ""
    size: int = 0
    play_count: int = 0
    digg_count: int = 0
    comment_count: int = 0
    share_count: int = 0
    download_count: int = 0
    collect_count: int = 0
    create_time: int = 0
    music_info: Optional[MusicInfo] = None
    author: Optional[VideoAuthor] = None
    is_top: int = 0
    
    @property
    def formatted_play_count(self) -> str:
        """Get formatted play count."""
        return format_count(self.play_count, "plays")
    
    @property
    def formatted_digg_count(self) -> str:
        """Get formatted like count."""
        return format_count(self.digg_count, "likes")
    
    @property
    def formatted_comment_count(self) -> str:
        """Get formatted comment count."""
        return format_count(self.comment_count, "comments")
    
    @property
    def formatted_share_count(self) -> str:
        """Get formatted share count."""
        return format_count(self.share_count, "shares")
    
    @property
    def tiktok_url(self) -> str:
        """Get TikTok video URL."""
        if self.author and self.author.unique_id:
            return format_tiktok_url(self.author.unique_id, self.video_id)
        return ""


class HashtagPostsData(BaseModel):
    """TikTok hashtag posts data model."""
    
    videos: List[VideoInfo] = []
    cursor: int = 0
    hasMore: bool = False
    
    class Config:
        populate_by_name = True


class HashtagPostsResponse(BaseModel):
    """TikTok hashtag posts response model."""
    
    code: int
    msg: str
    processed_time: float
    data: Optional[HashtagPostsData] = None