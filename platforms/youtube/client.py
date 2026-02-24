from typing import List, Optional, Dict, Any
from loguru import logger
from ..base import BasePlatformClient
from models.profile import Profile
from models.content import Content
from datetime import datetime

class YouTubeClient(BasePlatformClient):
    BASE_URL = "https://www.googleapis.com/youtube/v3"

    def __init__(self, http_client, api_key: str):
        super().__init__(http_client)
        self.api_key = api_key

    async def get_profile(self, username: str) -> Profile:
        """
        Fetch YouTube channel profile by username (handle).
        """
        # YouTube handles start with '@'. If not present, we might need search.
        # But usually, 'forHandle' or 'forUsername' is used.
        # Modern YouTube uses handles like @username.
        
        params = {
            "part": "snippet,statistics",
            "forHandle": username if username.startswith("@") else f"@{username}",
            "key": self.api_key
        }
        
        # If the handle lookup fails, we might try channelId or search
        response = await self.http_client.request("GET", f"{self.BASE_URL}/channels", params=params)
        data = response.json()
        
        if not data.get("items"):
            # Fallback to older username format if handle fails
            params.pop("forHandle", None)
            params["forUsername"] = username.lstrip("@")
            response = await self.http_client.request("GET", f"{self.BASE_URL}/channels", params=params)
            data = response.json()

        if not data.get("items"):
            raise ValueError(f"YouTube channel not found for: {username}")

        item = data["items"][0]
        snippet = item["snippet"]
        stats = item["statistics"]

        return Profile(
            id=item["id"],
            username=username,
            platform="youtube",
            display_name=snippet.get("title"),
            bio=snippet.get("description"),
            follower_count=int(stats.get("subscriberCount", 0)),
            post_count=int(stats.get("videoCount", 0)),
            avatar_url=snippet.get("thumbnails", {}).get("high", {}).get("url"),
            raw_data=item
        )

    async def get_all_content(self, username: str) -> List[Content]:
        """
        Fetch all videos for a channel using pagination.
        """
        profile = await self.get_profile(username)
        channel_id = profile.id
        
        all_videos = []
        next_page_token = None
        
        while True:
            params = {
                "part": "snippet",
                "channelId": channel_id,
                "maxResults": 50,
                "type": "video",
                "key": self.api_key,
            }
            if next_page_token:
                params["pageToken"] = next_page_token
            
            # Using search endpoint to get video IDs
            response = await self.http_client.request("GET", f"{self.BASE_URL}/search", params=params)
            data = response.json()
            
            items = data.get("items", [])
            if not items:
                break

            # Need to get detailed stats for each video because search endpoint is limited
            video_ids = [item["id"]["videoId"] for item in items]
            detailed_videos = await self._get_video_details(video_ids)
            all_videos.extend(detailed_videos)

            next_page_token = data.get("nextPageToken")
            logger.info(f"Fetched {len(items)} videos. Total: {len(all_videos)}. Next token: {next_page_token}")
            
            if not next_page_token:
                break
                
        return all_videos

    async def _get_video_details(self, video_ids: List[str]) -> List[Content]:
        params = {
            "part": "snippet,statistics",
            "id": ",".join(video_ids),
            "key": self.api_key
        }
        response = await self.http_client.request("GET", f"{self.BASE_URL}/videos", params=params)
        data = response.json()
        
        contents = []
        for item in data.get("items", []):
            snippet = item["snippet"]
            stats = item["statistics"]
            
            contents.append(Content(
                id=item["id"],
                platform="youtube",
                url=f"https://www.youtube.com/watch?v={item['id']}",
                text=snippet.get("title"),
                created_at=datetime.fromisoformat(snippet["publishedAt"].replace("Z", "+00:00")),
                author_username=snippet.get("channelTitle"),
                author_id=snippet.get("channelId"),
                view_count=int(stats.get("viewCount", 0)),
                like_count=int(stats.get("likeCount", 0)),
                comment_count=int(stats.get("commentCount", 0)),
                raw_data=item
            ))
        return contents
