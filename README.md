# Social Media SDK

**A production-ready, async Python SDK for extracting creator data from YouTube, Instagram, and TikTok.**

[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-pep8-orange.svg)](https://pep8.org/)

---

## Features

- **Auto-pagination**: Fetches all pages using cursor/token automatically.
- **Async-first**: Built on `httpx.AsyncClient` for high concurrency.
- **Retry Logic**: Exponential backoff with jitter for 429 and 5xx errors.
- **Rate Limiting**: Token Bucket implementation for per-platform request pacing.
- **Security**: Credentials isolated in `.env`, never hardcoded.
- **Proxy Support**: Easy rotating proxy integration.
- **Strong Typing**: Pydantic models for validated data output.
- **Logging**: Structured pipeline visibility with Loguru.

---

## Quick Start

```bash
git clone https://github.com/yourusername/social-media-sdk.git
cd social-media-sdk
pip install -e .
cp .env.example .env   # Fill in your credentials
```

```python
import asyncio
from core.http_client import AsyncHttpClient
from core.config import settings
from platforms.youtube.client import YouTubeClient

async def main():
    http_client = AsyncHttpClient()
    yt = YouTubeClient(http_client, api_key=settings.YOUTUBE_API_KEY)

    profile = await yt.get_profile("@ndtvindia")
    print(f"{profile.display_name} — {profile.follower_count:,} subscribers")

    videos = await yt.get_all_content("@ndtvindia")
    for v in videos[:5]:
        print(f"  {v.text} — {v.view_count:,} views")

    await http_client.close()

asyncio.run(main())
```

---

## Documentation

| Document                                     | Description                                     |
| :------------------------------------------- | :---------------------------------------------- |
| [Architecture](./docs/architecture.md)       | Layered design, data flow, and design patterns. |
| [Getting Started](./docs/getting-started.md) | Installation and basic configuration.           |
| [YouTube Guide](./docs/youtube-guide.md)     | API v3 setup and usage details.                 |
| [Instagram Guide](./docs/instagram-guide.md) | Session-based scraping guide.                   |
| [TikTok Guide](./docs/tiktok-guide.md)       | Web extraction guide.                           |
| [Core Components](./docs/core-components.md) | HTTP Client, Rate Limiter, and Retry logic.     |
| [Data Models](./docs/data-models.md)         | Profile and Content schema reference.           |
| [Contributing](./CONTRIBUTING.md)            | Guidelines for contributing.                    |

---

## Project Structure

```text
social_media_sdk/
├── core/                   # Shared infrastructure
├── models/                 # Data contracts
├── platforms/              # Platform business logic
├── examples/               # Runnable demos
├── docs/                   # Documentation
└── .env.example            # Environment template
```

---

## License

MIT License — see [LICENSE](./LICENSE)
