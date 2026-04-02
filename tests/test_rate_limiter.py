"""Tests for the RateLimiter token bucket implementation."""

import time
from unittest.mock import AsyncMock, call, patch

import pytest

from recruit_crm_mcp.api_client import RateLimiter


async def test_acquire_consumes_token():
    limiter = RateLimiter(requests_per_minute=60)
    assert limiter.tokens == 60
    await limiter.acquire()
    assert limiter.tokens == 59


async def test_refill_after_elapsed_time_does_not_sleep():
    """If enough time has elapsed to refill a token, acquire() must NOT sleep."""
    limiter = RateLimiter(requests_per_minute=60)
    limiter.tokens = 0
    limiter.last_refill = time.monotonic() - 1.0  # 1 second elapsed → 1 token refilled

    with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
        await limiter.acquire()

    mock_sleep.assert_not_called()
    # The refilled token was consumed — tokens should be near 0
    assert limiter.tokens < 0.1


async def test_refill_capped_at_max():
    limiter = RateLimiter(requests_per_minute=60)
    limiter.tokens = 0
    limiter.last_refill = time.monotonic() - 100.0  # Would refill 100 tokens

    with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
        await limiter.acquire()

    mock_sleep.assert_not_called()
    # min(60, 0+100) = 60 → consume 1 → 59
    assert abs(limiter.tokens - 59) < 0.01


async def test_acquire_sleeps_exact_duration_when_empty(monkeypatch):
    """Uses mocked time to verify the exact sleep duration formula: (1 - tokens) * (60/rpm)."""
    fixed_now = 1000.0
    monkeypatch.setattr("recruit_crm_mcp.api_client.time.monotonic", lambda: fixed_now)

    limiter = RateLimiter(requests_per_minute=60)
    # Constructor ran with mocked time → last_refill = 1000.0
    limiter.tokens = 0

    with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
        await limiter.acquire()

    # elapsed = 0 → refill = 0 → tokens stays 0 → wait_time = (1-0)*(60/60) = 1.0
    mock_sleep.assert_called_once_with(pytest.approx(1.0, abs=1e-9))
    assert limiter.tokens == 0


async def test_wait_time_scales_with_partial_token(monkeypatch):
    """tokens=0.5 → wait_time must be exactly 0.5 seconds."""
    fixed_now = 1000.0
    monkeypatch.setattr("recruit_crm_mcp.api_client.time.monotonic", lambda: fixed_now)

    limiter = RateLimiter(requests_per_minute=60)
    limiter.tokens = 0.5

    with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
        await limiter.acquire()

    # elapsed = 0 → tokens stays 0.5 → wait_time = (1-0.5)*(60/60) = 0.5
    mock_sleep.assert_called_once_with(pytest.approx(0.5, abs=1e-9))


async def test_sequential_acquires_drain_bucket():
    """10 sequential calls must reduce the bucket by exactly 10."""
    limiter = RateLimiter(requests_per_minute=60)
    for _ in range(10):
        await limiter.acquire()
    # Started at 60; each call consumes 1 (no real time passes between calls, so
    # refill per call is negligible — definitely < 0.1 per iteration)
    assert abs(limiter.tokens - 50) < 1.0
