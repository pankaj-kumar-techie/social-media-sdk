# ⚙️ Core Components — Deep Dive

This document covers the shared infrastructure layer (`core/`) in detail.

---

## HTTP Client (`core/http_client.py`)

The `AsyncHttpClient` is the **single point of contact** for all external HTTP requests. No platform client makes raw `httpx` calls — they all route through this class.

### Architecture

```text
Platform Client
     │
     ▼
AsyncHttpClient.request()
     │
     ├── 1. RateLimiter.wait()    ← Block until token available
     ├── 2. logger.info()          ← Log the request
     ├── 3. httpx.request()        ← Fire actual HTTP
     ├── 4. Handle 429             ← Raise for retry
     ├── 5. Handle 5xx             ← Raise for retry
     └── 6. Return response        ← Success

     Wrapped by: @async_retry      ← Catches errors, retries with backoff
```

### Constructor Parameters

| Parameter      | Type                  | Default    | Description                      |
| -------------- | --------------------- | ---------- | -------------------------------- |
| `proxy_url`    | `str \| None`         | `None`     | HTTP proxy URL                   |
| `timeout`      | `float`               | `30.0`     | Request timeout in seconds       |
| `headers`      | `dict \| None`        | User-Agent | Default headers for all requests |
| `rate_limiter` | `RateLimiter \| None` | `None`     | Token bucket instance            |

### Request Method

```python
await client.request(
    method="GET",                    # HTTP method
    url="https://api.example.com",   # Full URL
    params={"key": "value"},         # Query parameters
    json_data={"field": "value"},    # JSON body
    headers={"X-Custom": "..."},     # Per-request headers
    cookies={"sessionid": "..."},    # Per-request cookies
)
```

---

## Rate Limiter (`core/rate_limiter.py`)

### Token Bucket Algorithm

The Token Bucket is a classic rate-limiting algorithm used by AWS, Google Cloud, and most API gateways.

**How it works:**

1. A bucket holds up to `capacity` tokens
2. Tokens refill at `rate` tokens per second
3. Each request consumes 1 token
4. If the bucket is empty, the caller **waits** until a token refills

```text
                    Capacity = 5
                    Rate = 2/sec

              ┌───────────────┐
              │ ● ● ● ● ●    │  ← Full bucket (5 tokens)
              │               │
              │  refill: +2/s │  ← Tokens refill over time
              │               │
              │  consume: -1  │  ← Each request takes 1 token
              └───────────────┘
```

### Constructor Parameters

| Parameter             | Type    | Default | Description              |
| --------------------- | ------- | ------- | ------------------------ |
| `requests_per_second` | `float` | —       | Token refill rate        |
| `burst`               | `int`   | `1`     | Maximum tokens in bucket |

### Platform-Specific Recommendations

| Platform  | `requests_per_second` | `burst` | Reasoning                     |
| --------- | --------------------- | ------- | ----------------------------- |
| YouTube   | `2.0`                 | `5`     | Official API, generous limits |
| Instagram | `0.5`                 | `2`     | Aggressive rate limiting      |
| TikTok    | `0.3`                 | `1`     | Heavy anti-bot protection     |

---

## Retry Logic (`core/retry.py`)

### Exponential Backoff with Jitter

The `@async_retry` decorator retries failed requests with increasing delays:

```text
Delay = base_delay × 2^(attempt - 1) + random(0, 1)

Attempt 1: 2 × 2^0 + jitter = ~2.5s
Attempt 2: 2 × 2^1 + jitter = ~4.7s
Attempt 3: 2 × 2^2 + jitter = ~8.3s
```

**Why jitter?** Without jitter, if many clients hit a rate limit simultaneously, they'd all retry at the exact same time, causing a "thundering herd" problem. Random jitter spreads retries over time.

### Decorator Parameters

| Parameter     | Type    | Default                   | Description               |
| ------------- | ------- | ------------------------- | ------------------------- |
| `max_retries` | `int`   | `3`                       | Maximum retry attempts    |
| `base_delay`  | `float` | `1.0`                     | Initial delay in seconds  |
| `exponential` | `bool`  | `True`                    | Use exponential backoff   |
| `exceptions`  | `tuple` | `HTTPError, TimeoutError` | Which exceptions to retry |

### What Gets Retried

| HTTP Status                 | Retried? | Reason                            |
| --------------------------- | -------- | --------------------------------- |
| `200 OK`                    | ❌       | Success                           |
| `400 Bad Request`           | ❌       | Client error, won't fix itself    |
| `401 Unauthorized`          | ❌       | Auth issue, needs new credentials |
| `403 Forbidden`             | ❌       | Permission issue                  |
| `404 Not Found`             | ❌       | Resource doesn't exist            |
| `429 Too Many Requests`     | ✅       | Temporary, will clear after wait  |
| `500 Internal Server Error` | ✅       | Server hiccup, may recover        |
| `502 Bad Gateway`           | ✅       | Proxy/server issue                |
| `503 Service Unavailable`   | ✅       | Temporary overload                |
| Network timeout             | ✅       | Transient network issue           |

---

## Proxy Helper (`core/proxy.py`)

Simple utility to format proxy URLs for `httpx`:

```python
from core.proxy import get_proxy_dict

# Returns {"all://": "http://user:pass@host:port"}
proxy = get_proxy_dict("http://user:pass@host:port")

# Returns None if no proxy
proxy = get_proxy_dict(None)
```

---

## Configuration (`core/config.py`)

Uses **Pydantic Settings** to load environment variables from `.env`:

```python
from core.config import settings

settings.YOUTUBE_API_KEY        # str | None
settings.INSTAGRAM_SESSION_ID   # str | None
settings.INSTAGRAM_CSRF_TOKEN   # str | None
settings.TIKTOK_SESSION_ID      # str | None
settings.PROXY_URL              # str | None
settings.LOG_LEVEL              # str (default: "INFO")
```

The `Settings` class automatically locates the `.env` file relative to the project root, so it works regardless of your working directory.
