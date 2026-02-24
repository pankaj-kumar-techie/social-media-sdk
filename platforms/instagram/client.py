import json
from typing import List, Optional, Dict, Any
from loguru import logger
from ..base import BasePlatformClient
from models.profile import Profile
from models.content import Content
from datetime import datetime

class InstagramClient(BasePlatformClient):
    BASE_URL = "https://www.instagram.com"
    API_URL = "https://www.instagram.com/api/v1"

    def __init__(self, http_client, session_id: str, csrf_token: Optional[str] = None):
        super().__init__(http_client)
        self.session_id = session_id
        self.csrf_token = csrf_token
        
        # Inject cookies into the client
        self.cookies = {
            "sessionid": session_id,
        }
        if csrf_token:
            self.cookies["csrftoken"] = csrf_token

    async def get_profile(self, username: str) -> Profile:
        """
        Fetch Instagram profile using the web API.
        """
        url = f"{self.API_URL}/users/web_profile_info/"
        params = {"username": username}
        
        headers = {
            "X-IG-App-ID": "936619743392459", # Standard IG Web App ID
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        response = await self.http_client.request(
            "GET", url, params=params, headers=headers, cookies=self.cookies
        )
        data = response.json()
        user = data["data"]["user"]

        return Profile(
            id=user["id"],
            username=user["username"],
            platform="instagram",
            display_name=user["full_name"],
            bio=user["biography"],
            follower_count=user["edge_followed_by"]["count"],
            following_count=user["edge_follow"]["count"],
            post_count=user["edge_owner_to_timeline_media"]["count"],
            avatar_url=user["profile_pic_url_hd"],
            is_verified=user["is_verified"],
            raw_data=user
        )

    async def get_all_content(self, username: str) -> List[Content]:
        """
        Fetch all posts for an Instagram user with cursor-based pagination.
        """
        profile = await self.get_profile(username)
        user_id = profile.id
        
        all_content = []
        has_next_page = True
        end_cursor = None
        
        headers = {
            "X-IG-App-ID": "936619743392459",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        while has_next_page:
            url = f"{self.API_URL}/feed/user/{user_id}/"
            params = {"count": 12}
            if end_cursor:
                params["max_id"] = end_cursor

            response = await self.http_client.request(
                "GET", url, params=params, headers=headers, cookies=self.cookies
            )
            data = response.json()
            
            items = data.get("items", [])
            for item in items:
                caption = item.get("caption", {})
                text = caption.get("text") if caption else None
                
                # Handling multi-media or single image/video
                media_urls = []
                if "carousel_media" in item:
                    media_urls = [m["image_versions2"]["candidates"][0]["url"] for m in item["carousel_media"]]
                elif "image_versions2" in item:
                    media_urls = [item["image_versions2"]["candidates"][0]["url"]]

                all_content.append(Content(
                    id=item["id"],
                    platform="instagram",
                    url=f"https://www.instagram.com/p/{item['code']}/",
                    text=text,
                    created_at=datetime.fromtimestamp(item["taken_at"]),
                    author_username=username,
                    author_id=user_id,
                    view_count=item.get("view_count", 0),
                    like_count=item.get("like_count", 0),
                    comment_count=item.get("comment_count", 0),
                    media_urls=media_urls,
                    raw_data=item
                ))

            end_cursor = data.get("next_max_id")
            has_next_page = bool(end_cursor)
            
            logger.info(f"Fetched {len(items)} Instagram posts. Total: {len(all_content)}")
            
            if not end_cursor:
                break
                
        return all_content
