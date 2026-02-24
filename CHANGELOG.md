# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.1.0] - 2026-02-24

### Added

- **Core Infrastructure**
  - `AsyncHttpClient` — Shared async HTTP client with proxy, timeout, and cookie support
  - `RateLimiter` — Token Bucket algorithm for per-platform request pacing
  - `@async_retry` — Exponential backoff decorator with jitter for 429/5xx handling
  - `Settings` — Pydantic-based configuration loaded from `.env`

- **Data Models**
  - `Profile` — Unified creator/channel model across all platforms
  - `Content` — Unified video/post model with engagement metrics

- **Platform Clients**
  - `YouTubeClient` — Full YouTube Data API v3 integration (profiles + paginated videos)
  - `InstagramClient` — Session-based Instagram Web API integration (profiles + posts)
  - `TikTokClient` — Session-based TikTok Web API structure (profiles + videos)

- **Documentation**
  - Architecture & system design with Mermaid diagrams
  - Getting started guide
  - Per-platform guides (YouTube, Instagram, TikTok)
  - Core components deep dive
  - Data model reference
  - Extending the SDK guide
  - Contributing guidelines
