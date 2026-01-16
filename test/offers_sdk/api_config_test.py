from typing import Dict

import pytest
from pytest import MonkeyPatch

from offers_sdk.config import ApiConfig


@pytest.fixture
def env_vars() -> Dict:
    return {
        ApiConfig.BASE_URL_ENV_KEY: "https://api.example.com",
        ApiConfig.AUTH_ENDPOINT_ENV_KEY: "https://auth.example.com",
        ApiConfig.REFRESH_TOKEN_ENV_KEY: "secret_token_123",
        ApiConfig.PERSISTENT_AUTH_TOKEN_KEY: "test-auth-token-key",
    }


def test_from_env_loads_config_successfully(
    monkeypatch: MonkeyPatch, env_vars: Dict
):
    for key, value in env_vars.items():
        monkeypatch.setenv(key, value)

    config = ApiConfig.from_env()

    assert config.base_url == "https://api.example.com"
    assert config.auth_endpoint == "https://auth.example.com"
    assert config.refresh_token == "secret_token_123"
    assert config.persistent_auth_token_key == "test-auth-token-key"


@pytest.mark.parametrize(
    "missing_var",
    [
        ApiConfig.BASE_URL_ENV_KEY,
        ApiConfig.AUTH_ENDPOINT_ENV_KEY,
        ApiConfig.REFRESH_TOKEN_ENV_KEY,
        ApiConfig.PERSISTENT_AUTH_TOKEN_KEY,
    ],
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
