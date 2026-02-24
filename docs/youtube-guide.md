# 📺 YouTube Guide

Complete guide for using the YouTube Data API v3 integration in this SDK.

---

## Setup

### 1. Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Click "Select a Project" → "New Project"
3. Name it (e.g., "Social Media SDK") → Create

### 2. Enable the YouTube Data API

1. Go to **APIs & Services** → **Library**
2. Search for "YouTube Data API v3"
3. Click **Enable**

### 3. Create an API Key

1. Go to **APIs & Services** → **Credentials**
2. Click **Create Credentials** → **API Key**
3. Copy the key and paste into `.env`:

```env
YOUTUBE_API_KEY=AIzaSy...your_key_here
```

> 💡 **Recommended:** Restrict the API key to only "YouTube Data API v3" in the credentials settings.

---

## API Quota

YouTube Data API has a **daily quota of 10,000 units** (free tier).

| Operation                       | Cost per call |
| ------------------------------- | ------------- |
| `channels.list` (profile)       | 1 unit        |
| `search.list` (video discovery) | 100 units     |
| `videos.list` (video details)   | 1 unit        |

**How `get_all_content()` uses quota:**

For a channel with 500 videos:

- 10 search pages × 100 units = **1,000 units**
- 10 video detail calls × 1 unit = **10 units**
- Total: ~**1,010 units** (10% of daily quota)

> ⚠️ For very large channels (10,000+ videos), consider using the YouTube Data API's `playlistItems` endpoint instead of `search`. This is a planned improvement for the SDK.

---

## Usage

### Fetch a Channel Profile

```python
from platforms.youtube.client import YouTubeClient

yt = YouTubeClient(http_client, api_key="your_key")

# By handle (recommended)
profile = await yt.get_profile("@ndtvindia")

# The SDK also supports legacy usernames as fallback
profile = await yt.get_profile("ndtvindia")
```

**Profile fields returned:**

```python
profile.id               # "UCttspZesZIDEwwpVIgoZtWQ"
profile.username          # "@ndtvindia"
profile.display_name      # "NDTV India"
profile.bio               # "NDTV India is the Hindi news channel..."
profile.follower_count    # 72400000
profile.post_count        # 548000
profile.avatar_url        # "https://yt3.ggpht.com/..."
```

### Fetch All Videos

```python
# Fetches ALL videos with automatic pagination
videos = await yt.get_all_content("@ndtvindia")

for v in videos:
    print(f"Title: {v.text}")
    print(f"URL: {v.url}")
    print(f"Published: {v.created_at}")
    print(f"Views: {v.view_count:,}")
    print(f"Likes: {v.like_count:,}")
    print(f"Comments: {v.comment_count:,}")
    print()
```

### Export to JSON

```python
import json

profile = await yt.get_profile("@ndtvindia")
print(profile.model_dump_json(indent=2))

videos = await yt.get_all_content("@ndtvindia")
data = [v.model_dump(mode="json") for v in videos]
with open("videos.json", "w") as f:
    json.dump(data, f, indent=2, default=str)
```

---

## How It Works Internally

The YouTube client uses a **two-step approach** for content fetching:

```text
Step 1: search.list API
  ├── Input: channelId
  ├── Returns: list of video IDs (50 per page)
  ├── Pagination: uses nextPageToken
  └── Cost: 100 units per page

Step 2: videos.list API (per batch of 50 IDs)
  ├── Input: comma-separated video IDs
  ├── Returns: full metadata (views, likes, comments, dates)
  └── Cost: 1 unit per call
```

**Why two steps?** The `search` endpoint only returns basic snippet data. To get statistics (view count, like count), you must call the `videos` endpoint separately. The SDK batches up to 50 video IDs per call for efficiency.

---

## Common Errors

| Error             | Cause                             | Fix                                |
| ----------------- | --------------------------------- | ---------------------------------- |
| `403 Forbidden`   | API key invalid or quota exceeded | Check key in Google Cloud Console  |
| `400 Bad Request` | Invalid parameter                 | Check that handle starts with `@`  |
| `quotaExceeded`   | Daily 10,000 unit limit reached   | Wait 24h or request quota increase |
