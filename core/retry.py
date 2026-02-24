import asyncio
import functools
import random
from typing import Callable, Any, Type, Union, Tuple
from loguru import logger
import httpx

def async_retry(
    max_retries: int = 3,
    base_delay: float = 1.0,
    exponential: bool = True,
    exceptions: Union[Type[Exception], Tuple[Type[Exception], ...]] = (
        httpx.HTTPError,
        asyncio.TimeoutError,
    ),
):
    """
    Decorator for retrying async functions with exponential backoff and jitter.
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            retries = 0
            while True:
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    retries += 1
                    if retries > max_retries:
                        logger.error(f"Max retries ({max_retries}) exceeded for {func.__name__}: {str(e)}")
                        raise

                    # Calculate delay with exponential backoff and jitter
                    delay = base_delay * (2 ** (retries - 1)) if exponential else base_delay
                    delay += random.uniform(0, 1)  # Add jitter
                    
                    logger.warning(
                        f"Retry {retries}/{max_retries} for {func.__name__} after {delay:.2f}s due to error: {str(e)}"
                    )
                    await asyncio.sleep(delay)
        return wrapper
    return decorator
