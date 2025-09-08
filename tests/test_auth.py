import httpx
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


def test_add_rule_with_default_parameters(auth_client, httpx_mock):
    """Test add_rule with default parameters."""
    expected_response = {"status": "success", "rule_id": 456}
    httpx_mock.add_response(
        method="POST",
        url="http://test-auth/1.1/AuthorizationRules",
        json=expected_response,
        status_code=200,
    )

    result = auth_client.add_rule(
        user_mask="test_user",
        is_group=True,
        permission=2,
    )

    assert result == expected_response


def test_add_rule_duplicate_key_error(auth_client, httpx_mock, capsys):
    """Test add_rule when duplicate key error occurs."""
    error_response = {
        "payload": {
            "errors": ["Cannot insert duplicate key in object 'AuthorizationRules'"]
        }
    }
    httpx_mock.add_response(
        method="POST",
        url="http://test-auth/1.1/AuthorizationRules",
        json=error_response,
        status_code=400,
    )

    result = auth_client.add_rule(
        user_mask="test_user",
        is_group=False,
        permission=1,
    )

    # Should return the error response without raising an exception
    assert result == error_response

    # Check that the duplicate key message was printed
    captured = capsys.readouterr()
    assert "Permission already exists" in captured.out


def test_add_rule_other_error(auth_client, httpx_mock):
    """Test add_rule when other error occurs (should raise exception)."""
    error_response = {"payload": {"errors": ["Some other error occurred"]}}
    httpx_mock.add_response(
        method="POST",
        url="http://test-auth/1.1/AuthorizationRules",
        json=error_response,
        status_code=400,
    )

    with pytest.raises(httpx.HTTPStatusError):
        auth_client.add_rule(
            user_mask="test_user",
            is_group=False,
            permission=1,
        )


def test_add_rule_no_errors_in_response(auth_client, httpx_mock):
    """Test add_rule when error response has no errors field."""
    error_response = {"payload": {}}
    httpx_mock.add_response(
        method="POST",
        url="http://test-auth/1.1/AuthorizationRules",
        json=error_response,
        status_code=400,
    )

    with pytest.raises(httpx.HTTPStatusError):
        auth_client.add_rule(
            user_mask="test_user",
            is_group=False,
            permission=1,
        )


def test_delete_rule_success(auth_client, httpx_mock, capsys):
    """Test successful rule deletion."""
    expected_response = {"status": "success", "message": "Rule deleted"}
    httpx_mock.add_response(
        method="DELETE",
        url="http://test-auth/1.1/AuthorizationRules/rule123",
        json=expected_response,
        status_code=200,
    )

    result = auth_client.delete_rule("rule123")

    assert result == expected_response

    # Check that debug messages were printed
    captured = capsys.readouterr()
    assert (
        "Deleting rule at: http://test-auth/1.1/AuthorizationRules/rule123"
        in captured.out
    )
    assert "Headers: {'Authorization': 'Bearer fake-token'}" in captured.out


def test_delete_rule_not_found(auth_client, httpx_mock, capsys):
    """Test delete_rule when rule is not found."""
    error_response = {"payload": {"errors": ["Rule not found with id: rule123"]}}
    httpx_mock.add_response(
        method="DELETE",
        url="http://test-auth/1.1/AuthorizationRules/rule123",
        json=error_response,
        status_code=404,
    )

    result = auth_client.delete_rule("rule123")

    # Should return the error response without raising an exception
    assert result == error_response

    # Check that the not found message was printed
    captured = capsys.readouterr()
    assert "Rule not found" in captured.out


def test_delete_rule_other_error(auth_client, httpx_mock):
    """Test delete_rule when other error occurs (should raise exception)."""
    error_response = {"payload": {"errors": ["Some other error occurred"]}}
    httpx_mock.add_response(
        method="DELETE",
        url="http://test-auth/1.1/AuthorizationRules/rule123",
        json=error_response,
        status_code=500,
    )

    with pytest.raises(httpx.HTTPStatusError):
        auth_client.delete_rule("rule123")


def test_delete_rule_no_errors_in_response(auth_client, httpx_mock):
    """Test delete_rule when error response has no errors field."""
    error_response = {"payload": {}}
    httpx_mock.add_response(
        method="DELETE",
        url="http://test-auth/1.1/AuthorizationRules/rule123",
        json=error_response,
        status_code=400,
    )

    with pytest.raises(httpx.HTTPStatusError):
        auth_client.delete_rule("rule123")
