from unittest.mock import Mock

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


def test_add_rule_duplicate_key_error(auth_client, httpx_mock):
    """Test add_rule handling duplicate key error."""
    # Setup mock response for duplicate key error
    error_response = {
        "payload": {
            "errors": ["Cannot insert duplicate key row in object 'auth_rules'"]
        }
    }
    httpx_mock.add_response(
        method="POST",
        url="http://test-auth/1.1/AuthorizationRules",
        json=error_response,
        status_code=400,
    )

    # Test that duplicate key error is handled gracefully (prints message, doesn't raise)
    result = auth_client.add_rule(
        user_mask="test_user",
        is_group=False,
        permission=1,
    )

    # Should return the error response without raising an exception
    assert result == error_response


def test_add_rule_general_error(auth_client, httpx_mock):
    """Test add_rule handling general HTTP error."""
    # Setup mock response for general error
    error_response = {"payload": {"errors": ["Some other error"]}}
    httpx_mock.add_response(
        method="POST",
        url="http://test-auth/1.1/AuthorizationRules",
        json=error_response,
        status_code=500,
    )

    # Test that general errors raise HTTPStatusError
    with pytest.raises(Exception):  # httpx.HTTPStatusError
        auth_client.add_rule(
            user_mask="test_user",
            is_group=False,
            permission=1,
        )


def test_delete_rule_success(auth_client, httpx_mock):
    """Test successful rule deletion."""
    expected_response = {"status": "success", "message": "Rule deleted"}
    httpx_mock.add_response(
        method="DELETE",
        url="http://test-auth/1.1/AuthorizationRules/123",
        json=expected_response,
        status_code=200,
    )

    result = auth_client.delete_rule("123")
    assert result == expected_response


def test_delete_rule_not_found_error(auth_client, httpx_mock):
    """Test delete_rule handling rule not found error."""
    error_response = {"payload": {"errors": ["Rule not found with ID: 123"]}}
    httpx_mock.add_response(
        method="DELETE",
        url="http://test-auth/1.1/AuthorizationRules/123",
        json=error_response,
        status_code=404,
    )

    # Test that rule not found error is handled gracefully (prints message, doesn't raise)
    result = auth_client.delete_rule("123")
    assert result == error_response


def test_delete_rule_general_error(auth_client, httpx_mock):
    """Test delete_rule handling general HTTP error."""
    error_response = {"payload": {"errors": ["Some other delete error"]}}
    httpx_mock.add_response(
        method="DELETE",
        url="http://test-auth/1.1/AuthorizationRules/123",
        json=error_response,
        status_code=500,
    )

    # Test that general errors raise HTTPStatusError
    with pytest.raises(Exception):  # httpx.HTTPStatusError
        auth_client.delete_rule("123")


def test_handle_error_response_success_status(auth_client):
    """Test _handle_error_response with successful status codes."""
    # Create a mock response with status code < 400
    mock_response = Mock()
    mock_response.status_code = 200

    # Should return without doing anything
    result = auth_client._handle_error_response(mock_response)
    assert result is None


def test_handle_delete_error_response_success_status(auth_client):
    """Test _handle_delete_error_response with successful status codes."""
    # Create a mock response with status code < 400
    mock_response = Mock()
    mock_response.status_code = 200

    # Should return without doing anything
    result = auth_client._handle_delete_error_response(mock_response)
    assert result is None
