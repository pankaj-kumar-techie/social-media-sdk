# Social Media Data Extraction SDK

A professional, production-grade Python SDK designed for scalable and resilient data extraction from major social media platforms: **YouTube**, **Instagram**, and **TikTok**.

This SDK is built with **Clean Architecture** principles, ensuring modularity, testability, and ease of extension. It features built-in rate limiting, exponential backoff retries, and proxy support to handle high-volume extraction tasks reliably.

---

## 🚀 Key Features

- **Unified Interface**: Standardized methods (`get_profile`, `get_all_content`) across all platforms.
- **Async/Await Infrastructure**: Optimized for high-concurrency fetching using `httpx`.
- **Intelligent Pagination**: Automatic cursor-based and token-based pagination logic.
- **Resilience Layer**:
  - **Token Bucket Rate Limiter**: Precisely controls request pacing.
  - **Exponential Backoff**: Handles network flakiness and temporary rate limits with jitter.
- **Strong Typing**: Full Pydantic v2 integration for data validation and serialization.
- **Production-Ready**: Structured logging, proxy support, and environment-based configuration.

---

## 🛠️ Project Architecture

```text
social_media_sdk/
├── core/                   # Shared Infrastructure
│   ├── http_client.py      # Resilient Async HTTP Wrapper
│   ├── rate_limiter.py     # Token Bucket implementation
│   ├── retry.py            # Exponential Backoff logic
│   ├── proxy.py            # Proxy configuration helpers
│   └── config.py           # Pydantic Settings management
├── models/                 # Data Schemas
│   ├── profile.py          # Unified Profile model
│   └── content.py          # Unified Content (Video/Post) model
├── platforms/              # Platform Specific Clients
│   ├── base.py             # Abstract Base Client interface
│   ├── youtube/            # YouTube Data API v3 integration
│   ├── instagram/          # Session-based Web API scraping
│   └── tiktok/             # Web-based content extraction
├── examples/               # Usage Demonstations
└── .env                    # Hidden credentials (not in git)
```

---

## ⚙️ Configuration & Setup

### 1. Prerequisites

- Python 3.10+
- [YouTube Data API Key](https://console.cloud.google.com/apis/library/youtube.googleapis.com)
- Instagram Session ID (extracted from browser cookies)
- TikTok Session ID (extracted from browser cookies)

### 2. Installation

```bash
git clone https://github.com/yourusername/social_media_sdk.git
cd social_media_sdk
pip install -e .
```

### 3. Environment Variables

Create a `.env` file in the root directory:

```env
# YouTube
YOUTUBE_API_KEY=your_key_here

# Instagram (Required for authenticated scraping)
INSTAGRAM_SESSION_ID=your_sessionid_cookie
INSTAGRAM_CSRF_TOKEN=your_csrftoken_cookie

# TikTok
TIKTOK_SESSION_ID=your_sessionid_cookie

# Infrastructure
PROXY_URL=http://user:pass@host:port  # Optional
LOG_LEVEL=INFO
```

---

## 📖 Usage Example

### YouTube Data Extraction

```python
import asyncio
from core.http_client import AsyncHttpClient
from platforms.youtube.client import YouTubeClient

async def main():
    # Setup resilient client
    async with AsyncHttpClient() as http_client:
        yt = YouTubeClient(http_client, api_key="YOUR_API_KEY")

        # 1. Get Channel Profile
        profile = await yt.get_profile("@ndtvindia")
        print(f"Channel: {profile.display_name} | Subs: {profile.follower_count}")

        # 2. Get All Videos (Auto-paginated)
        videos = await yt.get_all_content("@ndtvindia")
        for video in videos[:10]:
            print(f"[{video.created_at}] {video.text} - {video.view_count} views")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🏗️ Technical Details

### Resilient HTTP Client

The `AsyncHttpClient` in `core/http_client.py` wraps every request with:

1. **Rate Limiter Check**: Checks the token bucket before firing.
2. **Retry Decorator**: Catches `429`, `5xx`, and timeouts, retrying with backoff.
3. **Structured Logging**: Provides clear visibility into the scraping pipeline.

### YouTube Strategy

The SDK uses a two-step approach for YouTube to maximize data quality:

1. `search` endpoint to discover video IDs for a channel.
2. `videos` endpoint to fetch detailed metadata (view count, like count) which isn't available in search results.

---

## 📝 License

MIT License.
