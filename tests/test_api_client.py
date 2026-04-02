"""Tests for RecruitCRMClient HTTP error handling and retry logic."""

from unittest.mock import AsyncMock, patch

import httpx
import pytest

from recruit_crm_mcp.api_client import RecruitCRMClient, RecruitCRMError


# ---------------------------------------------------------------------------
# Initialisation
# ---------------------------------------------------------------------------

def test_missing_token_raises(monkeypatch):
    monkeypatch.delenv("RECRUIT_CRM_API_TOKEN", raising=False)
    with pytest.raises(RecruitCRMError) as exc:
        RecruitCRMClient()
    assert exc.value.status_code is None
    assert "RECRUIT_CRM_API_TOKEN" in exc.value.message


async def test_bearer_token_sent_in_header(httpx_mock, api_token):
    """The Authorization header must contain the exact token passed at construction."""
    httpx_mock.add_response(status_code=200, json={})
    client = RecruitCRMClient(api_token="my-secret-token")

    await client._request("GET", "/candidates")

    request = httpx_mock.get_requests()[0]
    assert request.headers["Authorization"] == "Bearer my-secret-token"
    await client.close()


# ---------------------------------------------------------------------------
# HTTP error mapping
# ---------------------------------------------------------------------------

async def test_401_raises_with_correct_status_and_message(httpx_mock, api_token):
    httpx_mock.add_response(status_code=401)
    client = RecruitCRMClient()

    with pytest.raises(RecruitCRMError) as exc:
        await client._request("GET", "/candidates")

    assert exc.value.status_code == 401
    assert "invalid" in exc.value.message.lower() or "expired" in exc.value.message.lower()
    await client.close()


async def test_401_is_not_retried(httpx_mock, api_token):
    """A 401 must abort immediately — no retry attempts."""
    httpx_mock.add_response(status_code=401)
    client = RecruitCRMClient()

    with pytest.raises(RecruitCRMError):
        await client._request("GET", "/candidates")

    assert len(httpx_mock.get_requests()) == 1
    await client.close()


async def test_404_raises_with_correct_status_and_message(httpx_mock, api_token):
    httpx_mock.add_response(status_code=404)
    client = RecruitCRMClient()

    with pytest.raises(RecruitCRMError) as exc:
        await client._request("GET", "/candidates/nonexistent")

    assert exc.value.status_code == 404
    assert "not found" in exc.value.message.lower()
    await client.close()


async def test_422_raises_with_details(httpx_mock, api_token):
    httpx_mock.add_response(
        status_code=422,
        json={"message": "Validation failed", "errors": {"name": ["required"]}},
    )
    client = RecruitCRMClient()

    with pytest.raises(RecruitCRMError) as exc:
        await client._request("POST", "/candidates", json_data={})

    assert exc.value.status_code == 422
    assert "validation" in exc.value.message.lower()
    assert exc.value.details.get("message") == "Validation failed"
    await client.close()


async def test_500_raises_generic(httpx_mock, api_token):
    httpx_mock.add_response(status_code=500, text="Internal Server Error")
    client = RecruitCRMClient()

    with pytest.raises(RecruitCRMError) as exc:
        await client._request("GET", "/candidates")

    assert exc.value.status_code == 500
    await client.close()


async def test_204_returns_success_dict(httpx_mock, api_token):
    httpx_mock.add_response(status_code=204)
    client = RecruitCRMClient()

    result = await client._request("DELETE", "/candidates/abc")

    assert result == {"success": True}
    await client.close()


async def test_200_returns_parsed_json(httpx_mock, api_token):
    httpx_mock.add_response(status_code=200, json={"data": [{"id": 1}], "total": 1})
    client = RecruitCRMClient()

    result = await client._request("GET", "/candidates")

    assert result == {"data": [{"id": 1}], "total": 1}
    await client.close()


# ---------------------------------------------------------------------------
# 429 retry logic
# ---------------------------------------------------------------------------

async def test_429_retries_twice_then_raises(httpx_mock, api_token):
    """With max_retries=3: two sleeps between attempts, raise on the third 429."""
    for _ in range(3):
        httpx_mock.add_response(status_code=429, headers={"Retry-After": "5"}, json={})
    client = RecruitCRMClient()

    with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
        with pytest.raises(RecruitCRMError) as exc:
            await client._request("GET", "/candidates")

    assert exc.value.status_code == 429
    # Slept once after attempt 0 and once after attempt 1 — not after attempt 2
    assert mock_sleep.call_count == 2
    await client.close()


async def test_429_respects_retry_after_header(httpx_mock, api_token):
    """The sleep duration must equal the Retry-After header value."""
    httpx_mock.add_response(status_code=429, headers={"Retry-After": "7"}, json={})
    httpx_mock.add_response(status_code=200, json={"data": []})
    client = RecruitCRMClient()

    with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
        result = await client._request("GET", "/candidates")

    assert result == {"data": []}
    mock_sleep.assert_called_once_with(7)  # Retry-After: 7
    await client.close()


# ---------------------------------------------------------------------------
# Network error retry with exponential backoff
# ---------------------------------------------------------------------------

async def test_network_error_retries_with_exponential_backoff(httpx_mock, api_token):
    """ConnectError must be retried with backoff values 1, 2 (2**0, 2**1)."""
    for _ in range(3):
        httpx_mock.add_exception(httpx.ConnectError("Connection refused"))
    client = RecruitCRMClient()

    with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
        with pytest.raises(RecruitCRMError) as exc:
            await client._request("GET", "/candidates")

    assert "Request failed" in exc.value.message
    assert mock_sleep.call_count == 2
    # Verify exponential backoff values: sleep(1) then sleep(2)
    sleep_values = [c.args[0] for c in mock_sleep.call_args_list]
    assert sleep_values == [1, 2]
    await client.close()


async def test_network_error_succeeds_on_retry(httpx_mock, api_token):
    """A transient network error followed by a 200 must return the JSON body."""
    httpx_mock.add_exception(httpx.ConnectError("Transient failure"))
    httpx_mock.add_response(status_code=200, json={"data": []})
    client = RecruitCRMClient()

    with patch("asyncio.sleep", new_callable=AsyncMock):
        result = await client._request("GET", "/candidates")

    assert result == {"data": []}
    await client.close()
