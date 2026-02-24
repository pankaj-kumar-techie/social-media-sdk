<div align="center">

# 📡 Social Media SDK

**A production-ready, async Python SDK for extracting creator data from YouTube, Instagram, and TikTok.**

[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-pep8-orange.svg)](https://pep8.org/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](./CONTRIBUTING.md)

</div>

---

## ✨ Features

- 🔁 **Auto-pagination** — Fetches all pages using cursor/token automatically
- ⚡ **Async-first** — Built on `httpx.AsyncClient` for high concurrency
- 🛡️ **Retry on failure** — Exponential backoff with jitter for 429 & 5xx
- 🪣 **Token Bucket Rate Limiter** — Per-platform request pacing
- 🔐 **Env-based auth** — Credentials isolated in `.env`, never hardcoded
- 🌐 **Proxy support** — Rotating proxy integration
- 📦 **Pydantic models** — Strongly-typed, validated output
- 📝 **Structured logging** — Full pipeline visibility with Loguru

---

## 🚀 Quick Start

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

## 📚 Documentation

| Document                                               | Description                                                             |
| ------------------------------------------------------ | ----------------------------------------------------------------------- |
| [Architecture & System Design](./docs/architecture.md) | How the SDK is designed internally — layers, data flow, design patterns |
| [Getting Started](./docs/getting-started.md)           | Installation, configuration, and your first API call                    |
| [YouTube Guide](./docs/youtube-guide.md)               | YouTube Data API v3 setup, usage, quota management                      |
| [Instagram Guide](./docs/instagram-guide.md)           | Session-based Instagram scraping guide                                  |
| [TikTok Guide](./docs/tiktok-guide.md)                 | TikTok web extraction guide                                             |
| [Core Components](./docs/core-components.md)           | HTTP Client, Rate Limiter, Retry, Proxy — deep dive                     |
| [Data Models](./docs/data-models.md)                   | Profile & Content schema reference                                      |
| [Extending the SDK](./docs/extending.md)               | How to add a new platform client                                        |
| [Contributing](./CONTRIBUTING.md)                      | Contributing guidelines                                                 |
| [Changelog](./CHANGELOG.md)                            | Version history                                                         |

---

## 📁 Project Structure

```text
social_media_sdk/
├── core/                   # Shared infrastructure layer
├── models/                 # Pydantic data contracts
├── platforms/              # Platform-specific business logic
├── examples/               # Runnable demos
├── docs/                   # Full documentation
└── .env.example            # Environment template
```

---

## 📜 License

MIT License — see [LICENSE](./LICENSE)

---

<div align="center">
Made with ❤️ for the open-source community
</div>
