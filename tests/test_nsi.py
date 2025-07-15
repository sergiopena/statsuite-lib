import pytest

from statsuite_lib import KeycloakClient, NSIClient


@pytest.fixture
def keycloak_mock(mocker):
    mock_keycloak = mocker.Mock(spec=KeycloakClient)
    mock_keycloak.auth_header.return_value = {"Authorization": "Bearer fake-token"}
    return mock_keycloak


@pytest.fixture
def nsi_client(keycloak_mock):
    return NSIClient(nsi_url="https://nsi.example.com", keycloak_client=keycloak_mock)


def test_put_success(nsi_client, httpx_mock):
    # Mock successful PUT request
    httpx_mock.add_response(
        method="POST",
        url="https://nsi.example.com/test/path",
        status_code=207,
        text="Success",
    )

    response = nsi_client.put(file_to_upload=b"test content", path="/test/path")
    assert response == 207


def test_put_different_status(nsi_client, httpx_mock):
    # Mock PUT request with non-207 status
    httpx_mock.add_response(
        method="POST",
        url="https://nsi.example.com/test/path",
        status_code=200,
        text="Different status response",
    )

    response = nsi_client.put(file_to_upload=b"test content", path="/test/path")
    assert response == 200


def test_put_with_timeout(nsi_client, httpx_mock):
    # Mock PUT request with timeout
    httpx_mock.add_response(
        method="POST", url="https://nsi.example.com/test/path", status_code=207
    )

    response = nsi_client.put(
        file_to_upload=b"test content", path="/test/path", timeout=30
    )
    assert response == 207


def test_get_success(nsi_client, httpx_mock):
    # Mock successful GET request
    httpx_mock.add_response(
        method="GET",
        url="https://nsi.example.com/test/path",
        status_code=200,
        text="Success",
    )

    response = nsi_client.get(path="/test/path")
    assert response.status_code == 200
    assert response.text == "Success"


def test_get_with_custom_headers(nsi_client, httpx_mock):
    # Mock GET request with custom headers
    custom_headers = {"Custom-Header": "value"}
    httpx_mock.add_response(
        method="GET", url="https://nsi.example.com/test/path", status_code=200
    )

    response = nsi_client.get(path="/test/path", headers=custom_headers)
    assert response.status_code == 200


def test_get_with_timeout(nsi_client, httpx_mock):
    # Mock GET request with timeout
    httpx_mock.add_response(
        method="GET", url="https://nsi.example.com/test/path", status_code=200
    )

    response = nsi_client.get(path="/test/path", timeout=30)
    assert response.status_code == 200


def test_delete_success(nsi_client, httpx_mock):
    # Mock successful DELETE request
    httpx_mock.add_response(
        method="DELETE", url="https://nsi.example.com/test/path", status_code=204
    )

    response = nsi_client.delete(path="/test/path")
    assert response == 204


def test_delete_with_timeout(nsi_client, httpx_mock):
    # Mock DELETE request with timeout
    httpx_mock.add_response(
        method="DELETE", url="https://nsi.example.com/test/path", status_code=204
    )

    response = nsi_client.delete(path="/test/path", timeout=30)
    assert response == 204
