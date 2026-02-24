# 📦 Getting Started

This guide walks you through installing, configuring, and running your first data extraction with the Social Media SDK.

---

## Prerequisites

- **Python 3.10+** installed on your system
- A **YouTube Data API Key** ([Get one here](https://console.cloud.google.com/apis/library/youtube.googleapis.com))
- _(Optional)_ Instagram session cookies for Instagram extraction
- _(Optional)_ TikTok session cookies for TikTok extraction

---

## Step 1: Clone & Install

```bash
# Clone the repository
git clone https://github.com/yourusername/social-media-sdk.git
cd social-media-sdk

# Install in editable mode (recommended for development)
pip install -e .
```

This installs all dependencies automatically:

- `httpx` — Async HTTP client
- `pydantic` — Data validation models
- `pydantic-settings` — Environment variable management
- `loguru` — Structured logging
- `python-dotenv` — .env file support

---

## Step 2: Configure Credentials

```bash
cp .env.example .env
```

Open `.env` and fill in your credentials:

```env
# YouTube (required for YouTube extraction)
YOUTUBE_API_KEY=AIzaSy...your_key_here

# Instagram (required for Instagram extraction)
# INSTAGRAM_SESSION_ID=your_session_id
# INSTAGRAM_CSRF_TOKEN=your_csrf_token

# TikTok (required for TikTok extraction)
# TIKTOK_SESSION_ID=your_session_id

# Optional proxy
# PROXY_URL=http://user:pass@host:port
```

> ⚠️ **Security:** The `.env` file is gitignored. Never commit your API keys or session cookies.

---

## Step 3: Run the Example

```bash
cd examples
python example_usage.py
```

**Expected output:**

```text
2026-02-24 13:37:41 | INFO | Initializing YouTube Client...
2026-02-24 13:37:41 | INFO | Requesting GET https://www.googleapis.com/youtube/v3/channels
2026-02-24 13:37:42 | INFO | YouTube Profile: NDTV India - 72,400,000 subscribers
2026-02-24 13:37:42 | INFO | Bio: NDTV India is the Hindi news ...
2026-02-24 13:37:42 | INFO | Fetching videos for NDTV India...
2026-02-24 13:37:45 | INFO | Fetched 50 videos. Total: 50. Next token: CDIQAA
...
2026-02-24 13:37:50 | INFO | Successfully fetched 200 videos.
2026-02-24 13:37:50 | INFO | Latest 5 videos:
```

---

## Step 4: Use in Your Own Code

```python
import asyncio
import sys
from pathlib import Path

# If running outside the project root, add it to path
sys.path.append(str(Path(__file__).parent.parent))

from core.http_client import AsyncHttpClient
from core.rate_limiter import RateLimiter
from core.config import settings
from platforms.youtube.client import YouTubeClient

async def extract_channel_data(handle: str):
    """Extract profile and videos for any YouTube channel."""
    limiter = RateLimiter(requests_per_second=2.0)
    client = AsyncHttpClient(rate_limiter=limiter)

    try:
        yt = YouTubeClient(client, api_key=settings.YOUTUBE_API_KEY)

        # Profile
        profile = await yt.get_profile(handle)
        print(f"Channel: {profile.display_name}")
        print(f"Subscribers: {profile.follower_count:,}")
        print(f"Total videos: {profile.post_count}")

        # Videos
        videos = await yt.get_all_content(handle)
        print(f"\nFetched {len(videos)} videos:")
        for v in videos[:10]:
            print(f"  [{v.created_at.date()}] {v.text}")
            print(f"    URL: {v.url}")
            print(f"    Views: {v.view_count:,} | Likes: {v.like_count:,}")
    finally:
        await client.close()

asyncio.run(extract_channel_data("@ndtvindia"))
```

---

## Troubleshooting

### "YOUTUBE_API_KEY not found in .env"

- Make sure your `.env` file is in the **project root** directory (not in `examples/`)
- Make sure the key is not commented out (no `#` before it)

### "400 Bad Request" on YouTube

- Ensure your API key is valid and has YouTube Data API v3 enabled
- Check your [Google Cloud Console](https://console.cloud.google.com) for quota usage

### "HTTP error 429"

- You're being rate-limited. The SDK automatically retries with backoff
- Consider reducing `requests_per_second` in the `RateLimiter`

### Import errors

- Run from the project root: `python examples/example_usage.py`
- Or install the package: `pip install -e .`
