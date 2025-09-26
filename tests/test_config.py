import logging

import pytest

from statsuite_lib import ConfigClient
from statsuite_lib.config.models import Space, Tenants


@pytest.fixture
def config_client():
    return ConfigClient(config_url="https://config.example.com")


@pytest.fixture
def tenants_response():
    return {
        "default": {
            "id": "default",
            "spaces": {
                "space1": {"label": "space1", "url": "https://space1.example.com"},
                "space2": {"label": "space2", "url": "https://space2.example.com"},
            },
        },
        "tenant2": {
            "id": "tenant2",
            "spaces": {
                "space3": {"label": "space3", "url": "https://space3.example.com"}
            },
        },
    }


def test_init_config_client():
    client = ConfigClient(config_url="https://config.example.com")
    assert client.CONFIG_URL == "https://config.example.com"
    assert client.log.level == logging.INFO


def test_get_tenants_success(config_client, httpx_mock, tenants_response):
    # Mock successful response
    httpx_mock.add_response(
        method="GET",
        url="https://config.example.com/configs/tenants.json",
        json=tenants_response,
        status_code=200,
    )

    result = config_client.get_tenants()
    assert isinstance(result, Tenants)
    assert "default" in result.root
    assert "tenant2" in result.root
    assert len(result.root["default"].spaces) == 2
    assert len(result.root["tenant2"].spaces) == 1


def test_get_dataspaces_default_tenant(config_client, httpx_mock, tenants_response):
    # Mock successful response
    httpx_mock.add_response(
        method="GET",
        url="https://config.example.com/configs/tenants.json",
        json=tenants_response,
        status_code=200,
    )

    spaces = list(config_client.get_dataspaces())
    assert len(spaces) == 2
    assert all(isinstance(space, Space) for space in spaces)
    assert spaces[0].label == "space1"
    assert spaces[0].url == "https://space1.example.com"
    assert spaces[1].label == "space2"
    assert spaces[1].url == "https://space2.example.com"


def test_get_dataspaces_specific_tenant(config_client, httpx_mock, tenants_response):
    # Mock successful response
    httpx_mock.add_response(
        method="GET",
        url="https://config.example.com/configs/tenants.json",
        json=tenants_response,
        status_code=200,
    )

    spaces = list(config_client.get_dataspaces(tenant="tenant2"))
    assert len(spaces) == 1
    assert isinstance(spaces[0], Space)
    assert spaces[0].label == "space3"
    assert spaces[0].url == "https://space3.example.com"


def test_get_tenants_error_response(config_client, httpx_mock):
    # Mock error response
    httpx_mock.add_response(
        method="GET",
        url="https://config.example.com/configs/tenants.json",
        status_code=404,
    )

    result = config_client.get_tenants()
    assert result is None


def test_get_dataspaces_with_error(config_client, httpx_mock):
    # Mock error response
    httpx_mock.add_response(
        method="GET",
        url="https://config.example.com/configs/tenants.json",
        status_code=404,
    )

    with pytest.raises(AttributeError):
        list(config_client.get_dataspaces())
