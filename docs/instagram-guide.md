# 📸 Instagram Guide

Guide for using the session-based Instagram integration in the SDK.

---

## Authentication

Instagram does **not** offer a free public API for profile/post data. This SDK uses Instagram's **internal Web API** authenticated with browser session cookies.

### How to Get Your Cookies

1. Open **Chrome** and log into [instagram.com](https://www.instagram.com)
2. Press `F12` to open Developer Tools
3. Go to the **Application** tab
4. In the left sidebar, expand **Cookies** → click `https://www.instagram.com`
5. Find and copy these values:

| Cookie Name | Example Value         |
| ----------- | --------------------- |
| `sessionid` | `58234892%3AbR7xT...` |
| `csrftoken` | `a1b2c3d4e5f6g7h8...` |

6. Paste them into your `.env`:

```env
INSTAGRAM_SESSION_ID=58234892%3AbR7xT...
INSTAGRAM_CSRF_TOKEN=a1b2c3d4e5f6g7h8...
```

> ⚠️ **Session cookies expire** after a few days/weeks. You'll need to re-extract them when they expire (you'll see `401 Unauthorized` errors).

---

## Usage

### Fetch a Profile

```python
from platforms.instagram.client import InstagramClient

ig = InstagramClient(
    http_client,
    session_id="your_session_id",
    csrf_token="your_csrf_token"
)

profile = await ig.get_profile("nasa")
print(f"Name: {profile.display_name}")        # "NASA"
print(f"Bio: {profile.bio}")                   # "🚀 Exploring the universe..."
print(f"Followers: {profile.follower_count}")   # 97_000_000
print(f"Posts: {profile.post_count}")           # 4500
print(f"Verified: {profile.is_verified}")       # True
```

### Fetch All Posts

```python
posts = await ig.get_all_content("nasa")

for post in posts:
    print(f"Caption: {post.text[:80]}...")
    print(f"URL: {post.url}")
    print(f"Likes: {post.like_count:,}")
    print(f"Comments: {post.comment_count:,}")
    print(f"Media: {post.media_urls}")
    print()
```

---

## How It Works Internally

```text
Profile:
  GET /api/v1/users/web_profile_info/?username=nasa
  Headers: X-IG-App-ID: 936619743392459

Posts (paginated):
  GET /api/v1/feed/user/{user_id}/?count=12
  GET /api/v1/feed/user/{user_id}/?count=12&max_id={cursor}
  ...until max_id is empty
```

The SDK:

1. Fetches the profile to get the `user_id` (numeric)
2. Uses the `user_id` to paginate through the feed endpoint
3. Handles single images, videos, and carousel (multi-image) posts
4. Extracts the highest-resolution image URL from `image_versions2`

---

## Rate Limiting Notes

- Instagram is **aggressive** about rate limiting
- Recommended: `RateLimiter(requests_per_second=0.5)` (1 request every 2 seconds)
- If you get `429` errors, increase the delay or rotate proxies
- Using a proxy is **strongly recommended** for Instagram scraping

---

## Common Errors

| Error                   | Cause                     | Fix                             |
| ----------------------- | ------------------------- | ------------------------------- |
| `401 Unauthorized`      | Session cookie expired    | Re-extract cookies from browser |
| `429 Too Many Requests` | Rate limited by Instagram | Reduce `requests_per_second`    |
| `400 Bad Request`       | Invalid username          | Check username spelling         |
| `login_required`        | Session invalidated       | Log in again, get new cookies   |
