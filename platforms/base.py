from abc import ABC, abstractmethod
from typing import List, Optional
from core.http_client import AsyncHttpClient
from models.profile import Profile
from models.content import Content

class BasePlatformClient(ABC):
    def __init__(self, http_client: AsyncHttpClient):
        self.http_client = http_client

    @abstractmethod
    async def get_profile(self, username: str) -> Profile:
        """Fetch profile information for a user."""
        pass

    @abstractmethod
    async def get_all_content(self, username: str) -> List[Content]:
        """Fetch all content for a user with cursor-based pagination."""
        pass
