# Core Components Deep Dive

This document covers the shared infrastructure layer (`core/`) in detail.

---

## HTTP Client (`core/http_client.py`)

The `AsyncHttpClient` is the single point of contact for all external HTTP requests. All platform clients route through this class.

### Architecture

```text
Platform Client
     │
     ▼
AsyncHttpClient.request()
     │
     ├── 1. RateLimiter.wait()    ← Block until token available
     ├── 2. Logging               ← Log the request
     ├── 3. httpx.request()       ← Actual HTTP call
     ├── 4. Handle 429            ← Raise for retry
     ├── 5. Handle 5xx            ← Raise for retry
     └── 6. Return response       ← Success

     Wrapped by: @async_retry     ← Exponential backoff handler
```

### Constructor Parameters

| Parameter      | Type         | Default | Description                |
| :------------- | :----------- | :------ | :------------------------- | --------------------- |
| `proxy_url`    | `str         | None`   | `None`                     | HTTP proxy URL        |
| `timeout`      | `float`      | `30.0`  | Request timeout in seconds |
| `headers`      | `dict        | None`   | User-Agent                 | Default headers       |
| `rate_limiter` | `RateLimiter | None`   | `None`                     | Token bucket instance |

---

## Rate Limiter (`core/rate_limiter.py`)

### Token Bucket Algorithm

The Token Bucket is a classic rate-limiting algorithm used to control the rate of outgoing requests.

**How it works:**

1. A bucket holds up to `capacity` tokens.
2. Tokens refill at a specific `rate` per second.
3. Each request consumes 1 token.
4. If empty, the caller waits until a token is refilled.

```text
                    Capacity = 5
                    Rate = 2/sec

              ┌───────────────┐
              │ ● ● ● ● ●    │  ← Full bucket
              │               │
              │  Refill: +2/s │  ← Incremental refill
              │               │
              │  Consume: -1  │  ← Per-request cost
              └───────────────┘
```

### Constructor Parameters

| Parameter             | Type    | Default | Description              |
| :-------------------- | :------ | :------ | :----------------------- |
| `requests_per_second` | `float` | —       | Token refill rate        |
| `burst`               | `int`   | `1`     | Maximum tokens in bucket |

---

## Retry Logic (`core/retry.py`)

### Exponential Backoff with Jitter

The `@async_retry` decorator retries failed requests with increasing delays to prevent overwhelming the target server.

```text
Delay = base_delay × 2^(attempt - 1) + random(0, 1)

Attempt 1: ~2.5s
Attempt 2: ~4.7s
Attempt 3: ~8.3s
```

**Jitter**: Spreading retries over time prevents many clients from hitting the server exactly at once after a rate limit clears.

### What Gets Retried

| HTTP Status             | Retried? | Reason             |
| :---------------------- | :------- | :----------------- |
| `200 OK`                | No       | Success            |
| `400 Bad Request`       | No       | Client error       |
| `401 Unauthorized`      | No       | Auth issue         |
| `429 Too Many Requests` | Yes      | Temporary limit    |
| `5xx Server Error`      | Yes      | Server instability |
| Network timeout         | Yes      | Transient issue    |

---

## Proxy Helper (`core/proxy.py`)

Utility to format proxy URLs for `httpx`:

```python
from core.proxy import get_proxy_dict

# Returns {"all://": "http://user:pass@host:port"}
proxy = get_proxy_dict("http://user:pass@host:port")
```

---

## Configuration (`core/config.py`)

Uses **Pydantic Settings** to load environment variables from `.env`:

```python
from core.config import settings

settings.YOUTUBE_API_KEY
settings.INSTAGRAM_SESSION_ID
settings.PROXY_URL
```

The `Settings` class automatically locates the `.env` file relative to the project root.
