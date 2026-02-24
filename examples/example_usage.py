import asyncio
import os
import sys
from pathlib import Path

# Add project root to sys.path
root_path = Path(__file__).parent.parent
sys.path.append(str(root_path))

from dotenv import load_dotenv
from loguru import logger

from core.http_client import AsyncHttpClient
from core.rate_limiter import RateLimiter
from core.config import settings
from platforms.youtube.client import YouTubeClient
from platforms.instagram.client import InstagramClient

async def main():
    # Initialize shared components
    rate_limiter = RateLimiter(requests_per_second=2.0)
    http_client = AsyncHttpClient(
        proxy_url=settings.PROXY_URL,
        rate_limiter=rate_limiter
    )

    try:
        # --- YouTube Example ---
        if settings.YOUTUBE_API_KEY:
            logger.info("Initializing YouTube Client...")
            yt_client = YouTubeClient(http_client, settings.YOUTUBE_API_KEY)
            
            # Fetch profile
            profile = await yt_client.get_profile("@ndtvindia")
            logger.info(f"YouTube Profile: {profile.display_name} - {profile.follower_count} subscribers")
            logger.info(f"Bio: {profile.bio[:50]}...")

            # Fetch all content (demonstrates cursor pagination and detailed video stats)
            logger.info(f"Fetching videos for {profile.display_name}...")
            # Note: For large channels like ndtvindia, this will fetch many pages.
            # In a real scenario, you might add a limit or stop condition.
            videos = await yt_client.get_all_content("@ndtvindia")
            
            logger.info(f"Successfully fetched {len(videos)} videos.")
            if videos:
                logger.info("Latest 5 videos:")
                for vid in videos[:5]:
                    logger.info(f"- [{vid.created_at.date()}] {vid.text} ({vid.url}) | Views: {vid.view_count:,}")
        else:
            logger.warning("YOUTUBE_API_KEY not found in .env")

        # --- Instagram Example ---
        # if settings.INSTAGRAM_SESSION_ID:
        #     logger.info("Initializing Instagram Client...")
        #     ig_client = InstagramClient(
        #         http_client, 
        #         session_id=settings.INSTAGRAM_SESSION_ID,
        #         csrf_token=settings.INSTAGRAM_CSRF_TOKEN
        #     )
            
        #     # Fetch profile
        #     ig_profile = await ig_client.get_profile("nasa")
        #     logger.info(f"Instagram Profile: {ig_profile.display_name} - {ig_profile.follower_count} followers")
        # else:
        #     logger.warning("INSTAGRAM_SESSION_ID not found in .env")

    except Exception as e:
        logger.error(f"An error occurred: {e}")
    finally:
        await http_client.close()

if __name__ == "__main__":
    asyncio.run(main())
