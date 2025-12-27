"""Async retry utilities.

Implements an exponential backoff retry decorator for transient failures.
"""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from contextlib import suppress
from functools import wraps
import logging
import random
from typing import Any, ParamSpec, TypeVar

logger = logging.getLogger(__name__)

P = ParamSpec("P")
R = TypeVar("R")


def async_retry(
    *,
    max_retries: int = 3,
    backoff_base_seconds: float = 1.0,
    retriable_exceptions: tuple[type[Exception], ...],
    jitter_ratio: float = 0.1,
    log_context_provider: Callable[[P.args, P.kwargs], dict[str, Any]] | None = None,
) -> Callable[[Callable[P, Awaitable[R]]], Callable[P, Awaitable[R]]]:
    """Retry an async function on specified exception types.

    Backoff schedule (without jitter):
        attempt 1 -> 1s
        attempt 2 -> 2s
        attempt 3 -> 4s

    Retries are performed for *transient* exceptions only.
    """

    if max_retries < 0:
        raise ValueError("max_retries must be >= 0")

    if backoff_base_seconds <= 0:
        raise ValueError("backoff_base_seconds must be > 0")

    if jitter_ratio < 0:
        raise ValueError("jitter_ratio must be >= 0")

    def decorator(func: Callable[P, Awaitable[R]]) -> Callable[P, Awaitable[R]]:
        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            last_exc: Exception | None = None

            for attempt in range(0, max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except retriable_exceptions as exc:
                    last_exc = exc
                    if attempt >= max_retries:
                        break

                    delay = backoff_base_seconds * (2**attempt)
                    jitter = random.uniform(0.0, jitter_ratio * delay)
                    wait_seconds = delay + jitter

                    extra: dict[str, Any] = {
                        "retry_attempt": attempt + 1,
                        "retry_max": max_retries,
                        "retry_wait_seconds": wait_seconds,
                        "function": getattr(func, "__name__", str(func)),
                        "error_type": type(exc).__name__,
                    }
                    if log_context_provider is not None:
                        with suppress(Exception):
                            extra.update(log_context_provider(args, kwargs))

                    logger.warning("retrying transient error", extra=extra)
                    await asyncio.sleep(wait_seconds)

            assert last_exc is not None
            extra = {
                "retry_max": max_retries,
                "function": getattr(func, "__name__", str(func)),
                "error_type": type(last_exc).__name__,
            }
            logger.error("retries exhausted", extra=extra)
            raise last_exc

        return wrapper

    return decorator
