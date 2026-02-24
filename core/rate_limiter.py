import asyncio
import time
from typing import Optional
from loguru import logger

class RateLimiter:
    """
    Token Bucket implementation of a rate limiter.
    """
    def __init__(self, requests_per_second: float, burst: int = 1):
        self.rate = requests_per_second
        self.capacity = burst
        self.tokens = float(burst)
        self.last_updated = time.monotonic()
        self.lock = asyncio.Lock()

    async def wait(self):
        """
        Wait until a token is available.
        """
        async with self.lock:
            while self.tokens < 1.0:
                now = time.monotonic()
                elapsed = now - self.last_updated
                self.tokens = min(float(self.capacity), self.tokens + elapsed * self.rate)
                self.last_updated = now

                if self.tokens < 1.0:
                    wait_time = (1.0 - self.tokens) / self.rate
                    await asyncio.sleep(wait_time)

            self.tokens -= 1.0
            
    def update_rate(self, new_rate: float):
        """Dynamically adjust the rate."""
        self.rate = new_rate
        logger.debug(f"Rate limited updated to {new_rate} req/s")
