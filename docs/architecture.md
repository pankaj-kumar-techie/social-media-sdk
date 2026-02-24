# Architecture and System Design

This document describes the internal design of the Social Media SDK — its layered architecture, data flow pipelines, design patterns, and the engineering rationale behind each decision.

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
        RT["@async_retry — Exponential Backoff"]
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

### 1. Layered Separation

The SDK follows a layered architecture where dependencies always flow inward. This ensures that outer layers know about inner layers, but not the reverse.

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

**Benefits:**

- Add a new platform without modifying core infrastructure.
- Replace the HTTP library without touching platform clients.
- Test each layer independently with mock injection.

### 2. Dependency Injection

Platform clients receive their dependencies (like the HTTP client) via constructor, promoting reusability and testability:

```python
# One HTTP client shared across all platforms
http_client = AsyncHttpClient(rate_limiter=limiter)

yt = YouTubeClient(http_client, api_key="...")
ig = InstagramClient(http_client, session_id="...")
```

### 3. Strategy Pattern

All platform clients implement the `BasePlatformClient` interface, ensuring consistent behavior across different social media providers.

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

### 4. Retry Logic

The `@async_retry` decorator wraps `AsyncHttpClient.request()`, keeping retry logic isolated from business logic.

---

## Request Lifecycle

Every API call flows through a standardized pipeline:

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
    RL-->>HTTP: Token granted
    HTTP->>API: GET request

    alt 200 OK
        API-->>HTTP: Response JSON
        HTTP-->>PC: httpx.Response
        PC-->>App: Profile(...)
    end

    alt 429 Rate Limited
        API-->>HTTP: 429 Too Many Requests
        HTTP->>RT: Raise HTTPStatusError
        RT->>RT: Sleep with backoff
        RT->>HTTP: Retry request
        HTTP->>RL: wait()
        HTTP->>API: GET (retry)
        API-->>HTTP: 200 OK
        HTTP-->>PC: httpx.Response
        PC-->>App: Profile(...)
    end
```

---

## Pagination Engine

All platforms implement cursor-based pagination:

```mermaid
flowchart TD
    START([Start]) --> INIT[Initialize cursor = None]
    INIT --> FETCH[Fetch page with cursor]
    FETCH --> PARSE[Parse items]
    PARSE --> APPEND[Append to results]
    APPEND --> CHECK{Next cursor?}
    CHECK -->|Yes| UPDATE[Update cursor] --> FETCH
    CHECK -->|No| DONE([Return results])

    style START fill:#0f3460,color:#fff
    style DONE fill:#0f3460,color:#fff
```

| Platform  | Cursor Field (Response) | Cursor Param (Request) | Stop Condition    |
| --------- | ----------------------- | ---------------------- | ----------------- |
| YouTube   | `nextPageToken`         | `pageToken`            | Token is `null`   |
| Instagram | `next_max_id`           | `max_id`               | Field is absent   |
| TikTok    | `cursor` + `hasMore`    | `cursor`               | `hasMore = false` |

---

## Rate Limiting

The SDK uses a **Token Bucket** algorithm for request pacing.

```mermaid
stateDiagram-v2
    [*] --> Full: Init (capacity tokens)
    Full --> Consuming: Request arrives
    Consuming --> Available: tokens > 0
    Available --> Consuming: Next request
    Consuming --> Empty: tokens = 0
    Empty --> Refilling: Wait (1/rate)
    Refilling --> Available: Token refilled
```

- **Efficiency**: Allows bursts while maintaining a consistent throughput over time compared to fixed-delay limiting.

---

## Error Handling

```mermaid
flowchart TD
    REQ[HTTP Request] --> STATUS{Status Code}
    STATUS -->|2xx| OK[Success]
    STATUS -->|429/5xx| RETRYABLE{Retries left?}
    STATUS -->|4xx| RAISE[Client Error]

    RETRYABLE -->|Yes| BACKOFF[Wait with Jitter]
    BACKOFF --> REQ
    RETRYABLE -->|No| RAISE[Final Error]

    style OK fill:#2d6a4f,color:#fff
    style RAISE fill:#e94560,color:#fff
```

---

## Security Model

1. **Credentials**: Stored only in `.env` (gitignored).
2. **Log Masking**: Credentials are never exposed in logs.
3. **Session Management**: SDK raises clear errors on auth failure.

---

## Extension Points

- **New Platforms**: Inherit `BasePlatformClient` and implement core methods.
- **Caching**: Wrap `AsyncHttpClient` with a caching decorator.
- **Persistence**: Serialize Pydantic models to a database.
