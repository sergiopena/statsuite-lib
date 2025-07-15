import pytest

from statsuite_lib import KeycloakClient
from statsuite_lib.auth.auth import AuthClient


@pytest.fixture
def keycloak_mock(mocker):
    mock_keycloak = mocker.Mock(spec=KeycloakClient)
    mock_keycloak.auth_header.return_value = {"Authorization": "Bearer fake-token"}
    return mock_keycloak


@pytest.fixture
def auth_client(keycloak_mock):
    return AuthClient(auth_url="http://test-auth", keycloak_client=keycloak_mock)


def test_add_rule_success(auth_client, httpx_mock):
    # Setup mock response
    expected_response = {"status": "success", "rule_id": 123}
    httpx_mock.add_response(
        method="POST",
        url="http://test-auth/1.1/AuthorizationRules",
        json=expected_response,
        status_code=200,
    )

    # Test data
    result = auth_client.add_rule(
        user_mask="test_user",
        is_group=False,
        permission=1,
        dataspace="test_space",
        artifact_type=1,
        artefact_agency_id="AGENCY1",
        artefact_id="ID1",
        artefact_version="1.0",
    )

    # Verify response
    assert result == expected_response


def test_init_with_custom_api_version(keycloak_mock):
    client = AuthClient(
        auth_url="http://test-auth", keycloak_client=keycloak_mock, api_version="2.0"
    )
    assert client.AUTH_URL == "http://test-auth/2.0"
