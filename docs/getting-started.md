# Getting Started

This guide walks you through installing, configuring, and running your first data extraction with the Social Media SDK.

---

## Prerequisites

- **Python 3.10+**
- **YouTube Data API Key** ([Get one here](https://console.cloud.google.com/apis/library/youtube.googleapis.com))
- (Optional) Instagram session cookies
- (Optional) TikTok session cookies

---

## Step 1: Installation

```bash
git clone https://github.com/yourusername/social-media-sdk.git
cd social-media-sdk
pip install -e .
```

This installs the following dependencies:

- `httpx`: Async HTTP client
- `pydantic`: Data validation
- `pydantic-settings`: Configuration management
- `loguru`: Logging
- `python-dotenv`: Environment support

---

## Step 2: Configure Credentials

```bash
cp .env.example .env
```

Open `.env` and add your credentials:

```env
YOUTUBE_API_KEY=AIzaSy...your_key_here
# INSTAGRAM_SESSION_ID=...
# TIKTOK_SESSION_ID=...
```

---

## Step 3: Run the Example

```bash
python examples/example_usage.py
```

---

## Step 4: Use in Your Own Code

```python
import asyncio
from core.http_client import AsyncHttpClient
from core.rate_limiter import RateLimiter
from core.config import settings
from platforms.youtube.client import YouTubeClient

async def extract_channel_data(handle: str):
    limiter = RateLimiter(requests_per_second=2.0)
    client = AsyncHttpClient(rate_limiter=limiter)

    try:
        yt = YouTubeClient(client, api_key=settings.YOUTUBE_API_KEY)
        profile = await yt.get_profile(handle)
        print(f"Channel: {profile.display_name}")

        videos = await yt.get_all_content(handle)
        print(f"Fetched {len(videos)} videos.")
    finally:
        await client.close()

asyncio.run(extract_channel_data("@ndtvindia"))
```

---

## Troubleshooting

### "API Key not found"

Ensure your `.env` file is in the project root and the key is correctly defined.

### "400 Bad Request"

Verify your API key is valid and has YouTube Data API v3 enabled in your Google Cloud Console.

### "429 Too Many Requests"

The SDK automatically retries with backoff. You can also reduce `requests_per_second` in the `RateLimiter`.
