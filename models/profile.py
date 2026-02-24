from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class Profile(BaseModel):
    id: str
    username: str
    platform: str
    display_name: Optional[str] = None
    bio: Optional[str] = None
    follower_count: Optional[int] = 0
    following_count: Optional[int] = 0
    post_count: Optional[int] = 0
    avatar_url: Optional[str] = None
    is_verified: bool = False
    raw_data: Optional[Dict[str, Any]] = Field(default=None, exclude=True)

    class Config:
        from_attributes = True
