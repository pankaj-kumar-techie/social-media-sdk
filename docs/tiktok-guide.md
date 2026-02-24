# TikTok Guide

Guide for using the session-based TikTok integration in the SDK.

---

## Important Notes

TikTok's web API is protected with anti-bot measures:

- Requests may require dynamically generated signatures.
- TikTok actively detects and blocks automated access.

This SDK provides the architecture for TikTok extraction. For production use, you may need to integrate a signature generator or use residential proxies.

---

## Authentication

### How to Get Your Session Cookie

1. Log into [tiktok.com](https://www.tiktok.com) in your browser.
2. Open Developer Tools (F12) > **Application** tab > **Cookies**.
3. Copy the `sessionid` value.
4. Add it to your `.env` file:
   ```env
   TIKTOK_SESSION_ID=your_session_id_here
   ```

---

## Usage

```python
from platforms.tiktok.client import TikTokClient

tt = TikTokClient(http_client, session_id="...")
profile = await tt.get_profile("@charlidamelio")
videos = await tt.get_all_content("@charlidamelio")
```

---

## Rate Limiting

- Recommended setting: `RateLimiter(requests_per_second=0.3)`.
- Use proxy rotation for any sustained volume.
- TikTok blocks IPs aggressively; residential proxies are recommended.
