import pytest


@pytest.fixture
def api_token(monkeypatch):
    monkeypatch.setenv("RECRUIT_CRM_API_TOKEN", "test-token-abc123")
    return "test-token-abc123"
