# 🏗️ Architecture & System Design

> This document describes the internal design of the Social Media SDK — its layered architecture, data flow pipelines, design patterns, and the engineering rationale behind each decision.

---

## System Overview

```mermaid
graph TB
    subgraph "User Application"
        APP[Your Code / example_usage.py]
    end

    subgraph "Platform Layer"
        BASE[BasePlatformClient — Abstract Interface]
        YT[YouTubeClient]
        IG[InstagramClient]
        TT[TikTokClient]
    end

    subgraph "Core Infrastructure"
        HTTP[AsyncHttpClient]
        RL[RateLimiter — Token Bucket]
        RT[@async_retry — Exponential Backoff]
        CFG[Settings — Pydantic .env Loader]
    end

    subgraph "Data Layer"
        MP[Profile Model]
        MC[Content Model]
    end

    subgraph "External Services"
        YTAPI[YouTube Data API v3]
        IGAPI[Instagram Web API]
        TTAPI[TikTok Web API]
    end

    APP --> YT & IG & TT
    YT & IG & TT --> BASE
    YT & IG & TT --> HTTP
    HTTP --> RL
    HTTP --> RT
    HTTP --> YTAPI & IGAPI & TTAPI
    YT & IG & TT --> MP & MC
    CFG -.-> HTTP
    CFG -.-> YT & IG & TT

    style APP fill:#1a1a2e,stroke:#e94560,color:#fff
    style BASE fill:#16213e,stroke:#0f3460,color:#fff
    style YT fill:#0f3460,stroke:#533483,color:#fff
    style IG fill:#0f3460,stroke:#533483,color:#fff
    style TT fill:#0f3460,stroke:#533483,color:#fff
    style HTTP fill:#533483,stroke:#e94560,color:#fff
    style RL fill:#533483,stroke:#e94560,color:#fff
    style RT fill:#533483,stroke:#e94560,color:#fff
    style CFG fill:#533483,stroke:#e94560,color:#fff
    style MP fill:#2b2d42,stroke:#8d99ae,color:#fff
    style MC fill:#2b2d42,stroke:#8d99ae,color:#fff
    style YTAPI fill:#e94560,stroke:#1a1a2e,color:#fff
    style IGAPI fill:#e94560,stroke:#1a1a2e,color:#fff
    style TTAPI fill:#e94560,stroke:#1a1a2e,color:#fff
```

---

## Design Principles

### 1. Clean Architecture — Layered Separation

The SDK follows **Clean Architecture** (Robert C. Martin). Dependencies always flow **inward** — outer layers know about inner layers, never the reverse.

```mermaid
graph LR
    subgraph "Layer 1 — External"
        EXT["YouTube API / Instagram API / TikTok API"]
    end
    subgraph "Layer 2 — Infrastructure"
        INFRA["AsyncHttpClient / RateLimiter / Retry"]
    end
    subgraph "Layer 3 — Business Logic"
        BIZ["YouTubeClient / InstagramClient / TikTokClient"]
    end
    subgraph "Layer 4 — Application"
        APP["Your Application Code"]
    end

    EXT --> INFRA --> BIZ --> APP

    style EXT fill:#e94560,color:#fff,stroke:#333
    style INFRA fill:#533483,color:#fff,stroke:#333
    style BIZ fill:#0f3460,color:#fff,stroke:#333
    style APP fill:#1a1a2e,color:#fff,stroke:#333
```

**What this enables:**

- Add a new platform **without touching** Core
- Replace the HTTP library **without touching** any platform client
- Test each layer **independently** with mock injection

### 2. Dependency Injection

Platform clients don't create their own HTTP clients — they **receive** one via constructor:

```python
# One HTTP client shared across all platforms
http_client = AsyncHttpClient(rate_limiter=limiter, proxy_url="...")

yt = YouTubeClient(http_client, api_key="...")      # injected
ig = InstagramClient(http_client, session_id="...")  # same client reused
```

### 3. Strategy Pattern — Platform Abstraction

All platform clients implement `BasePlatformClient`:

```mermaid
classDiagram
    class BasePlatformClient {
        <<abstract>>
        +http_client: AsyncHttpClient
        +get_profile(username: str) Profile
        +get_all_content(username: str) List~Content~
    }

    class YouTubeClient {
        +api_key: str
        +get_profile(username) Profile
        +get_all_content(username) List~Content~
        -_get_video_details(ids) List~Content~
    }

    class InstagramClient {
        +session_id: str
        +csrf_token: str
        +get_profile(username) Profile
        +get_all_content(username) List~Content~
    }

    class TikTokClient {
        +session_id: str
        +get_profile(username) Profile
        +get_all_content(username) List~Content~
        -_parse_item(item) Content
    }

    BasePlatformClient <|-- YouTubeClient
    BasePlatformClient <|-- InstagramClient
    BasePlatformClient <|-- TikTokClient
```

### 4. Decorator Pattern — Retry Logic

The `@async_retry` transparently wraps `AsyncHttpClient.request()`, keeping retry logic completely separate from business logic:

```python
class AsyncHttpClient:
    @async_retry(max_retries=3, base_delay=2.0)   # ← transparent wrapper
    async def request(self, method, url, ...):
        ...  # clean request logic, no retry code here
```

---

## Request Lifecycle

Every API call flows through the same pipeline:

```mermaid
sequenceDiagram
    participant App as Your App
    participant PC as Platform Client
    participant HTTP as AsyncHttpClient
    participant RL as RateLimiter
    participant RT as @async_retry
    participant API as External API

    App->>PC: get_profile("@ndtvindia")
    PC->>HTTP: request("GET", url, params)

    Note over RT: @async_retry wraps this call

    HTTP->>RL: wait()
    RL-->>HTTP: Token granted ✓

    HTTP->>API: GET /youtube/v3/channels?...

    alt 200 OK
        API-->>HTTP: Response JSON
        HTTP-->>PC: httpx.Response
        PC-->>App: Profile(...)
    end

    alt 429 Rate Limited
        API-->>HTTP: 429 Too Many Requests
        HTTP->>RT: Raise HTTPStatusError
        RT->>RT: Sleep 2^n + jitter
        RT->>HTTP: Retry request
        HTTP->>RL: wait()
        HTTP->>API: GET (retry)
        API-->>HTTP: 200 OK
        HTTP-->>PC: httpx.Response
        PC-->>App: Profile(...)
    end

    alt 5xx Server Error
        API-->>HTTP: 500/502/503
        HTTP->>RT: Raise for retry
        RT->>RT: Sleep 2^n + jitter
        RT->>HTTP: Retry request
    end
```

---

## Pagination Engine

All platforms implement the same **cursor-based pagination** pattern:

```mermaid
flowchart TD
    START([Start]) --> INIT[Initialize cursor = None]
    INIT --> FETCH[Fetch page with cursor]
    FETCH --> PARSE[Parse items from response]
    PARSE --> APPEND[Append items to results]
    APPEND --> CHECK{Next cursor exists?}
    CHECK -->|Yes| UPDATE[Update cursor] --> FETCH
    CHECK -->|No| DONE([Return all results])

    FETCH -.->|On Error| RETRY{Retry available?}
    RETRY -->|Yes| WAIT[Backoff + Jitter] --> FETCH
    RETRY -->|No| FAIL([Raise Error])

    style START fill:#0f3460,color:#fff
    style DONE fill:#0f3460,color:#fff
    style FAIL fill:#e94560,color:#fff
    style CHECK fill:#533483,color:#fff
    style RETRY fill:#533483,color:#fff
```

**Platform cursor mapping:**

| Platform  | Cursor Field (Response) | Cursor Param (Request) | Stop Condition    |
| --------- | ----------------------- | ---------------------- | ----------------- |
| YouTube   | `nextPageToken`         | `pageToken`            | Token is `null`   |
| Instagram | `next_max_id`           | `max_id`               | Field is absent   |
| TikTok    | `cursor` + `hasMore`    | `cursor`               | `hasMore = false` |

---

## Rate Limiting — Token Bucket

```mermaid
stateDiagram-v2
    [*] --> Full: Init (capacity tokens)

    Full --> Consuming: Request arrives
    Consuming --> Available: tokens > 0 → grant token
    Available --> Consuming: Next request

    Consuming --> Empty: tokens = 0
    Empty --> Refilling: Wait (1/rate seconds)
    Refilling --> Available: Token refilled

    note right of Full: Bucket starts with\n'burst' tokens
    note right of Empty: Caller blocks\nuntil refill
    note right of Refilling: Refill rate =\nrequests_per_second
```

**Why Token Bucket over fixed delay?**

- Fixed delay: 1 req every 500ms = always 2 req/s, even if API allows burst
- Token Bucket: Accumulate tokens during idle time, burst when needed, smooth over sustained load

---

## Error Handling Strategy

```mermaid
flowchart TD
    REQ[HTTP Request] --> STATUS{Status Code}

    STATUS -->|2xx| OK[Return Response ✓]
    STATUS -->|429| RATE[Rate Limited]
    STATUS -->|5xx| SERVER[Server Error]
    STATUS -->|4xx| CLIENT[Client Error]

    RATE --> RETRYABLE{Retries left?}
    SERVER --> RETRYABLE

    RETRYABLE -->|Yes| BACKOFF["Sleep: base × 2^attempt + jitter"]
    BACKOFF --> REQ

    RETRYABLE -->|No| RAISE[Raise Final Error ✗]
    CLIENT --> RAISE

    style OK fill:#2d6a4f,color:#fff
    style RAISE fill:#e94560,color:#fff
    style BACKOFF fill:#533483,color:#fff
    style RETRYABLE fill:#0f3460,color:#fff
```

---

## Security Model

```mermaid
flowchart LR
    ENV[".env file (gitignored)"] --> CFG["core/config.py\n(Pydantic Settings)"]
    CFG --> |API Key| YT[YouTube Client]
    CFG --> |Session Cookies| IG[Instagram Client]
    CFG --> |Session Cookies| TT[TikTok Client]
    CFG --> |Proxy URL| HTTP[HTTP Client]

    LOG["Loguru Logger"] -.-> |"Masks credentials\nin log output"| CONSOLE[Console / File]

    style ENV fill:#e94560,color:#fff
    style CFG fill:#533483,color:#fff
    style LOG fill:#0f3460,color:#fff
```

**Principles:**

1. Credentials live **only** in `.env` (gitignored)
2. Logger never exposes full API keys or session tokens
3. Session cookies have expiration — the SDK raises clear errors on auth failure
4. Proxy support enables IP rotation for anti-detection

---

## Extension Points

```mermaid
graph TD
    subgraph "Easy to Add"
        A[New Platform Client] --> B["Inherit BasePlatformClient\nImplement get_profile + get_all_content"]
        C[Caching Layer] --> D["Wrap AsyncHttpClient\nwith cache decorator"]
        E[New Auth Method] --> F["Add to config.py\nInject into client constructor"]
    end

    subgraph "Planned Improvements"
        G[Database Persistence] --> H["Serialize Pydantic models\nto SQLAlchemy / MongoDB"]
        I[Webhook Notifications] --> J["Add callbacks to\npagination loops"]
        K[Session Rotation] --> L["Pool of session IDs\nRotate on 401"]
    end

    style A fill:#0f3460,color:#fff
    style C fill:#0f3460,color:#fff
    style E fill:#0f3460,color:#fff
    style G fill:#533483,color:#fff
    style I fill:#533483,color:#fff
    style K fill:#533483,color:#fff
```
