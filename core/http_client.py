import asyncio
import httpx
from typing import Optional, Dict, Any, Union
from loguru import logger
from .retry import async_retry
from .rate_limiter import RateLimiter

class AsyncHttpClient:
    def __init__(
        self,
        proxy_url: Optional[str] = None,
        timeout: float = 30.0,
        headers: Optional[Dict[str, str]] = None,
        rate_limiter: Optional[RateLimiter] = None
    ):
        self.proxy_url = proxy_url
        self.timeout = timeout
        self.headers = headers or {
            "User-Agent": "SocialMediaSDK/0.1.0 (Python; +https://github.com/user/social_media_sdk)"
        }
        self.rate_limiter = rate_limiter
        self.client = httpx.AsyncClient(
            proxy=proxy_url if proxy_url else None,
            timeout=timeout,
            headers=self.headers,
            follow_redirects=True
        )

    @async_retry(max_retries=3, base_delay=2.0)
    async def request(
        self,
        method: str,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        cookies: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> httpx.Response:
        """
        Execute an async HTTP request with rate limiting, retries, and logging.
        """
        if self.rate_limiter:
            await self.rate_limiter.wait()

        logger.info(f"Requesting {method} {url}")
        
        try:
            response = await self.client.request(
                method,
                url,
                params=params,
                json=json_data,
                data=data,
                headers=headers,
                cookies=cookies,
                **kwargs
            )

            # Handle 429 Too Many Requests
            if response.status_code == 429:
                retry_after = response.headers.get("Retry-After")
                logger.warning(f"Rate limited (429) on {url}. Retry-After: {retry_after}")
                raise httpx.HTTPStatusError(
                    "Rate limited", request=response.request, response=response
                )

            # Handle 5xx Server Errors
            if 500 <= response.status_code < 600:
                logger.error(f"Server error {response.status_code} on {url}")
                response.raise_for_status()

            response.raise_for_status()
            return response

        except httpx.HTTPError as e:
            logger.error(f"HTTP error occurred: {str(e)}")
            raise

    async def close(self):
        await self.client.aclose()
        logger.info("HTTP client closed")
