from unittest.mock import patch

import httpx
import pytest

from statsuite_lib import KeycloakClient, TransferClient


@pytest.fixture
def keycloak_mock(mocker):
    mock_keycloak = mocker.Mock(spec=KeycloakClient)
    mock_keycloak.auth_header.return_value = {"Authorization": "Bearer fake-token"}
    return mock_keycloak


@pytest.fixture
def transfer_client(keycloak_mock):
    return TransferClient(
        transfer_url="https://transfer.example.com", keycloak_client=keycloak_mock
    )


def test_import_sdmx_file_success(transfer_client, httpx_mock):
    httpx_mock.add_response(
        method="POST",
        url="https://transfer.example.com/3/import/sdmxFile",
        json={"message": "File import completed for 12345"},
        status_code=200,
    )

    result = transfer_client.import_sdmx_file(
        file_object=b"test content",
        dataspace="test-space",
        target_version=1,
        restoration_option_required=True,
        validation_type=2,
        timeout=30,
    )

    assert result == "12345"


def test_import_sdmx_file_does_not_print(transfer_client, httpx_mock, capsys):
    """Regression test: import_sdmx_file used to print the raw response JSON
    to stdout on every call."""
    httpx_mock.add_response(
        method="POST",
        url="https://transfer.example.com/3/import/sdmxFile",
        json={"message": "File import completed for 12345"},
        status_code=200,
    )

    transfer_client.import_sdmx_file(
        file_object=b"test content", dataspace="test-space"
    )

    assert capsys.readouterr().out == ""


def test_import_sdmx_file_error_response(transfer_client, httpx_mock):
    httpx_mock.add_response(
        method="POST",
        url="https://transfer.example.com/3/import/sdmxFile",
        json={"error": "invalid dataspace"},
        status_code=400,
    )

    result = transfer_client.import_sdmx_file(
        file_object=b"test content", dataspace="test-space"
    )

    assert result is None


def test_check_request_status_success(transfer_client, httpx_mock):
    httpx_mock.add_response(
        method="POST",
        url="https://transfer.example.com/3/status/request",
        json={"executionStatus": "Completed"},
        status_code=200,
    )

    status = transfer_client.check_request_status(dataspace="test-space", id=12345)

    assert status == "Completed"


def test_check_request_status_error(transfer_client, httpx_mock):
    httpx_mock.add_exception(httpx.ConnectError("Connection failed"))

    with pytest.raises(Exception):
        transfer_client.check_request_status(dataspace="test-space", id=12345)


def test_wait_for_request_success(transfer_client):
    with patch.object(
        transfer_client, "check_request_status", return_value="Completed"
    ):
        result = transfer_client.wait_for_request(
            dataspace="test-space", id=12345, timeout=5, backoff=1
        )
        assert result is False


def test_wait_for_request_timeout(transfer_client):
    with patch.object(
        transfer_client, "check_request_status", return_value="InProgress"
    ):
        result = transfer_client.wait_for_request(
            dataspace="test-space", id=12345, timeout=1, backoff=0.1
        )
        assert result is True


def test_transfer_dataflow_success(transfer_client, httpx_mock):
    httpx_mock.add_response(
        method="POST",
        url="https://transfer.example.com/3/transfer/dataflow",
        json={"message": "Request ID: 12345"},
        status_code=200,
    )

    result = transfer_client.transfer_dataflow(
        source_dataspace="source-space",
        destination_dataspace="dest-space",
        dataflow="test-flow",
    )

    assert result == "12345"


def test_transfer_dataflow_error(transfer_client, httpx_mock):
    httpx_mock.add_exception(httpx.ConnectError("Connection failed"))

    with pytest.raises(Exception):
        transfer_client.transfer_dataflow(
            source_dataspace="source-space",
            destination_dataspace="dest-space",
            dataflow="test-flow",
        )


def test_get_tune_success(transfer_client, httpx_mock):
    expected_response = {"tune": "data"}
    httpx_mock.add_response(
        method="POST",
        url="https://transfer.example.com/3/tune/info",
        json=expected_response,
        status_code=200,
    )

    result = transfer_client.get_tune(dataspace="test-space", dsd_id="test-dsd")

    assert result == expected_response


def test_set_tune_success(transfer_client, httpx_mock):
    expected_response = {"status": "success"}
    httpx_mock.add_response(
        method="POST",
        url="https://transfer.example.com/3/tune/dsd",
        json=expected_response,
        status_code=200,
    )

    result = transfer_client.set_tune(
        dataspace="test-space", dsd_id="test-dsd", index_type=1
    )

    assert result == expected_response


def test_activate_dataflow_success(transfer_client, httpx_mock):
    expected_response = {"status": "success"}
    httpx_mock.add_response(
        method="POST",
        url="https://transfer.example.com/3/init/dataflow",
        json=expected_response,
        status_code=200,
    )

    result = transfer_client.activate_dataflow(
        dataspace="test-space", df_id="test-flow"
    )

    assert result == expected_response


def test_health_success(transfer_client, httpx_mock):
    expected_response = {"status": "UP"}
    httpx_mock.add_response(
        method="GET",
        url="https://transfer.example.com/health",
        json=expected_response,
        status_code=200,
    )

    result = transfer_client.health()

    assert result == expected_response


def test_health_error(transfer_client, httpx_mock):
    httpx_mock.add_response(
        method="GET",
        url="https://transfer.example.com/health",
        status_code=503,
    )

    with pytest.raises(httpx.HTTPStatusError):
        transfer_client.health()


def test_initialization(transfer_client):
    assert transfer_client.TRANSFER_URL == "https://transfer.example.com/3"
    assert isinstance(transfer_client._client, httpx.Client)


def test_no_circular_package_import():
    """Regression test: transfer.py previously did `from statsuite_lib import
    KeycloakClient`, importing from its own partially-initialized top-level
    package instead of a direct relative import. That only worked because of
    import order in statsuite_lib/__init__.py, and would break if that order
    ever changed. Guard against reintroducing it."""
    import inspect

    from statsuite_lib.transfer import transfer as transfer_module

    source = inspect.getsource(transfer_module)
    assert "from statsuite_lib import" not in source
    assert "from ..keycloak.keycloak import KeycloakClient" in source
