# Instagram Guide

Guide for using the session-based Instagram integration in the SDK.

---

## Authentication

Instagram does not offer a free public API for data extraction. This SDK uses Instagram's internal Web API authenticated with browser session cookies.

### How to Get Your Cookies

1. Log into [instagram.com](https://www.instagram.com) in your browser.
2. Open Developer Tools (F12).
3. Go to the **Application** tab (or **Storage** in Firefox).
4. Select **Cookies** for `https://www.instagram.com`.
5. Locate and copy the following values:

| Cookie Name | Description                      |
| :---------- | :------------------------------- |
| `sessionid` | Your unique session identifier   |
| `csrftoken` | Cross-site request forgery token |

6. Add them to your `.env` file:
   ```env
   INSTAGRAM_SESSION_ID=your_session_id
   INSTAGRAM_CSRF_TOKEN=your_csrf_token
   ```

Note: Session cookies typically expire after a few weeks. You will need to refresh them if you see `401 Unauthorized` errors.

---

## Usage

### Fetch a Profile

```python
from platforms.instagram.client import InstagramClient

ig = InstagramClient(http_client, session_id="...", csrf_token="...")
profile = await ig.get_profile("nasa")
```

### Fetch All Posts

```python
posts = await ig.get_all_content("nasa")

for post in posts[:5]:
    print(f"{post.text[:50]}... ({post.like_count} likes)")
```

---

## Rate Limiting

- Instagram is aggressive about rate limiting.
- Recommended setting: `RateLimiter(requests_per_second=0.5)`.
- Using a proxy is strongly recommended for sustained Instagram extraction.

---

## Common Errors

- **401 Unauthorized**: Session cookie expired.
- **429 Too Many Requests**: Rate limited.
- **login_required**: Session invalidated by Instagram.
