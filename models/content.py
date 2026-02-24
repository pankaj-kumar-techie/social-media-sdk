from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class Content(BaseModel):
    id: str
    platform: str
    url: str
    text: Optional[str] = None
    created_at: Optional[datetime] = None
    author_username: str
    author_id: str
    view_count: Optional[int] = 0
    like_count: Optional[int] = 0
    comment_count: Optional[int] = 0
    share_count: Optional[int] = 0
    media_urls: List[str] = Field(default_factory=list)
    raw_data: Optional[Dict[str, Any]] = Field(default=None, exclude=True)

    class Config:
        from_attributes = True
