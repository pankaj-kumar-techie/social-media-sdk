# YouTube Guide

Complete guide for using the YouTube Data API v3 integration in this SDK.

---

## Setup

### 1. Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com).
2. Create a new project named "Social Media SDK".

### 2. Enable the YouTube Data API

1. Go to **APIs & Services** > **Library**.
2. Search for "YouTube Data API v3" and click **Enable**.

### 3. Create an API Key

1. Go to **APIs & Services** > **Credentials**.
2. Create an **API Key**.
3. Add the key to your `.env` file:
   ```env
   YOUTUBE_API_KEY=AIzaSy...your_key_here
   ```

Note: It is recommended to restrict the API key to "YouTube Data API v3" for security.

---

## API Quota

The YouTube Data API has a daily quota of 10,000 units on the free tier.

| Operation                 | Cost per call |
| :------------------------ | :------------ |
| `channels.list` (profile) | 1 unit        |
| `search.list` (discovery) | 100 units     |
| `videos.list` (details)   | 1 unit        |

---

## Usage

### Fetch a Channel Profile

```python
from platforms.youtube.client import YouTubeClient

yt = YouTubeClient(http_client, api_key="your_key")
profile = await yt.get_profile("@ndtvindia")
```

### Fetch All Videos

```python
# Fetches all videos with automatic pagination
videos = await yt.get_all_content("@ndtvindia")

for v in videos[:5]:
    print(f"{v.text}: {v.view_count:,} views")
```

---

## How It Works Internally

The YouTube client uses a two-step process to fetch complete data:

1. **Discovery**: Uses `search.list` to get a list of video IDs (100 units per 50 videos).
2. **Metadata Enhancement**: Uses `videos.list` to fetch statistics like views and likes for those IDs (1 unit per 50 videos).

This approach ensures you get the most detailed statistics available for every video.

---

## Common Errors

- **403 Forbidden**: API key invalid or quota exceeded.
- **400 Bad Request**: Invalid parameter or incorrectly formatted handle.
- **quotaExceeded**: Daily unit limit reached.
