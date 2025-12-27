"""Tests for async retry decorator."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from app.core.exceptions import NetworkError
from app.utils.retry import async_retry


@pytest.mark.asyncio
async def test_async_retry_retries_then_succeeds():
    calls = {"n": 0}

    async def flaky():
        calls["n"] += 1
        if calls["n"] < 3:
            raise NetworkError("net", error_code="NETWORK_ERROR")
        return "ok"

    with patch("app.utils.retry.asyncio.sleep", new=AsyncMock()) as sleep_mock, patch(
        "app.utils.retry.random.uniform", return_value=0.0
    ):
        wrapped = async_retry(
            max_retries=3,
            backoff_base_seconds=1.0,
            retriable_exceptions=(NetworkError,),
        )(flaky)
        result = await wrapped()

    assert result == "ok"
    assert calls["n"] == 3

    # Two sleeps: 1s then 2s (third attempt succeeds)
    assert [c.args[0] for c in sleep_mock.call_args_list] == [1.0, 2.0]


@pytest.mark.asyncio
async def test_async_retry_raises_after_exhaustion():
    async def always_fail():
        raise NetworkError("net", error_code="NETWORK_ERROR")

    with patch("app.utils.retry.asyncio.sleep", new=AsyncMock()) as sleep_mock, patch(
        "app.utils.retry.random.uniform", return_value=0.0
    ):
        wrapped = async_retry(
            max_retries=3,
            backoff_base_seconds=1.0,
            retriable_exceptions=(NetworkError,),
        )(always_fail)

        with pytest.raises(NetworkError):
            await wrapped()

    # 3 retries => sleeps after attempts 1..3 (initial attempt is 0)
    assert [c.args[0] for c in sleep_mock.call_args_list] == [1.0, 2.0, 4.0]


@pytest.mark.asyncio
async def test_async_retry_does_not_retry_non_retriable_exception():
    class NonRetriableError(Exception):
        pass

    calls = {"n": 0}

    async def fail_fast():
        calls["n"] += 1
        raise NonRetriableError("no")

    wrapped = async_retry(
        max_retries=3, backoff_base_seconds=1.0, retriable_exceptions=(NetworkError,)
    )(fail_fast)

    with pytest.raises(NonRetriableError):
        await wrapped()

    assert calls["n"] == 1
