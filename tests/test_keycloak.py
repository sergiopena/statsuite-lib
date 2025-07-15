import datetime

import httpx
import pytest
from freezegun import freeze_time

from statsuite_lib import KeycloakClient


@pytest.fixture
def openid_config_response():
    return {
        "authorization_endpoint": "https://auth.example.com/auth",
        "token_endpoint": "https://auth.example.com/token",
    }


@pytest.fixture
def token_response():
    return {
        "access_token": "fake-access-token",
        "refresh_token": "fake-refresh-token",
        "expires_in": 300,
    }


@pytest.fixture
def keycloak_client(httpx_mock, openid_config_response, token_response):
    # Mock openid configuration request
    httpx_mock.add_response(
        method="GET",
        url="https://keycloak.example.com/.well-known/openid-configuration",
        json=openid_config_response,
    )

    # Mock initial authentication request
    httpx_mock.add_response(
        method="POST", url="https://auth.example.com/token", json=token_response
    )

    return KeycloakClient(  # noqa S106
        openid_url="https://keycloak.example.com/.well-known/openid-configuration",
        username="test-user",
        password="test-password",
    )


def test_initialization(keycloak_client):
    openid_url = "https://keycloak.example.com/.well-known/openid-configuration"
    assert keycloak_client.OPENID_URL == openid_url
    assert (
        keycloak_client._auth_endpoint == "https://auth.example.com/auth"
    )  # noqa S105
    assert (
        keycloak_client._token_endpoint == "https://auth.example.com/token"  # noqa S105
    )
    assert keycloak_client.access_token == "fake-access-token"  # noqa S105
    assert keycloak_client.refresh_token == "fake-refresh-token"  # noqa S105
    assert isinstance(keycloak_client.access_token_expires, datetime.datetime)


def test_get_openid_configuration_error(httpx_mock):
    httpx_mock.add_exception(httpx.ConnectError("Connection failed"))

    with pytest.raises(httpx.ConnectError):
        KeycloakClient(  # noqa S105
            openid_url="https://keycloak.example.com/.well-known/openid-configuration",
            username="test-user",
            password="test-password",
        )


def test_trigger_refresh_token(keycloak_client, httpx_mock, token_response):
    # Mock refresh token request
    httpx_mock.add_response(
        method="POST", url="https://auth.example.com/token", json=token_response
    )

    keycloak_client.trigger_refresh_token()
    assert keycloak_client.access_token == "fake-access-token"  # noqa S105
    assert keycloak_client.refresh_token == "fake-refresh-token"  # noqa S105
    assert isinstance(keycloak_client.access_token_expires, datetime.datetime)


@freeze_time("2025-01-01 00:00:00")
def test_get_access_token_valid(keycloak_client):
    # Set a future expiration time
    keycloak_client.access_token_expires = datetime.datetime.now() + datetime.timedelta(
        minutes=5
    )
    assert keycloak_client.get_access_token() == "fake-access-token"


@freeze_time("2025-01-01 00:00:00")
def test_get_access_token_expired(keycloak_client, httpx_mock, token_response):
    # Set an expired token
    keycloak_client.access_token_expires = datetime.datetime.now() - datetime.timedelta(
        minutes=5
    )

    # Mock refresh token request
    httpx_mock.add_response(
        method="POST", url="https://auth.example.com/token", json=token_response
    )

    assert keycloak_client.get_access_token() == "fake-access-token"


def test_get_access_token_no_expiration(keycloak_client, httpx_mock, token_response):
    # Set no expiration time
    keycloak_client.access_token_expires = None

    # Mock refresh token request
    httpx_mock.add_response(
        method="POST", url="https://auth.example.com/token", json=token_response
    )

    assert keycloak_client.get_access_token() == "fake-access-token"


def test_auth_header(keycloak_client):
    assert keycloak_client.auth_header() == {
        "Authorization": "Bearer fake-access-token"
    }
