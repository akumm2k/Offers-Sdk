from typing import Dict

import pytest
from pytest import MonkeyPatch

from config import ApiConfig


@pytest.fixture
def env_vars() -> Dict:
    return {
        "OFFERS_API_BASE_URL": "https://api.example.com",
        "AUTH_ENDPOINT": "https://auth.example.com",
        "REFRESH_TOKEN": "secret_token_123",
    }


def test_from_env_loads_config_successfully(
    monkeypatch: MonkeyPatch, env_vars: Dict
):
    # Set environment variables using monkeypatch
    for key, value in env_vars.items():
        monkeypatch.setenv(key, value)

    config = ApiConfig.from_env()

    assert config.base_url == "https://api.example.com"
    assert config.auth_endpoint == "https://auth.example.com"
    assert config.refresh_token == "secret_token_123"


@pytest.mark.parametrize(
    "missing_var",
    ["OFFERS_API_BASE_URL", "AUTH_ENDPOINT", "REFRESH_TOKEN"],
)
def test_from_env_raises_error_for_missing_variable(
    monkeypatch: MonkeyPatch, env_vars: Dict, missing_var: str
):
    for key, value in env_vars.items():
        monkeypatch.setenv(key, value)
    monkeypatch.delenv(missing_var)

    with pytest.raises(EnvironmentError) as exc_info:
        ApiConfig.from_env()

    assert missing_var in str(exc_info.value)
