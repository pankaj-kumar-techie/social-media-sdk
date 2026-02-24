# 🎵 TikTok Guide

Guide for using the session-based TikTok integration in the SDK.

---

## ⚠️ Important Notes

TikTok's web API is **heavily protected** with anti-bot measures:

- Requests require dynamically generated signatures (`msToken`, `X-Bogus`, `_signature`)
- These signatures change with every request
- TikTok actively detects and blocks automated access

The current SDK implementation provides the **architecture and structure** for TikTok extraction. For production use, you may need to integrate a signature generator or use a headless browser approach.

---

## Authentication

### How to Get Your Session Cookie

1. Open **Chrome** and log into [tiktok.com](https://www.tiktok.com)
2. Press `F12` → **Application** tab → **Cookies** → `https://www.tiktok.com`
3. Copy the `sessionid` value
4. Paste into `.env`:

```env
TIKTOK_SESSION_ID=your_session_id_here
```

---

## Usage

```python
from platforms.tiktok.client import TikTokClient

tt = TikTokClient(http_client, session_id="your_session_id")

# Fetch profile
profile = await tt.get_profile("@charlidamelio")

# Fetch videos
videos = await tt.get_all_content("@charlidamelio")
```

---

## How It Works Internally

```text
Profile:
  GET https://www.tiktok.com/@username
  → Parse __UNIVERSAL_DATA_FOR_REHYDRATION__ JSON block from HTML
  → Extract user stats from embedded data

Videos (paginated):
  GET /api/post/item_list/?count=30&cursor=0
  GET /api/post/item_list/?count=30&cursor=30
  ...until hasMore=false
```

---

## Content Model Mapping

When fully implemented, TikTok videos map to the `Content` model as follows:

| TikTok Field              | Content Field     |
| ------------------------- | ----------------- |
| `item.id`                 | `id`              |
| `item.desc`               | `text`            |
| `item.createTime`         | `created_at`      |
| `item.author.uniqueId`    | `author_username` |
| `item.stats.playCount`    | `view_count`      |
| `item.stats.diggCount`    | `like_count`      |
| `item.stats.commentCount` | `comment_count`   |
| `item.stats.shareCount`   | `share_count`     |

---

## Extending the TikTok Client

To make TikTok extraction work in production, you'll need one of these approaches:

### Option 1: Signature Generator

Integrate a library that generates `X-Bogus` and `msToken` parameters:

```python
# In platforms/tiktok/client.py
params["X-Bogus"] = generate_x_bogus(url, params)
params["msToken"] = generate_ms_token()
```

### Option 2: Headless Browser

Use Playwright or Selenium to load pages and extract data from the rendered HTML.

### Option 3: Third-Party API

Use a service like RapidAPI's TikTok endpoints that handle the signing for you.

---

## Rate Limiting Notes

- Recommended: `RateLimiter(requests_per_second=0.3)` (very conservative)
- Use proxy rotation for any volume beyond a few requests
- TikTok blocks IPs aggressively — residential proxies recommended
