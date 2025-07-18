import pytest

from statsuite_lib import SFSClient


@pytest.fixture
def loadings():
    return """[{
    "userEmail": null,
    "submissionTime": "2024-08-13T13:37:38.633Z",
    "executionStart": "2024-08-13T13:37:38.633Z",
    "executionStatus": "completed",
    "tenant": "defadddult",
    "action": "deleteAll",
    "logs": [
        {
            "executionStart": "2024-08-13T13:37:38.684Z",
            "message": "All dataflows deleted for organisation default",
            "status": "success",
            "server": "sfs"
        }
    ],
    "executionEnd": "2024-08-13T13:37:38.689Z",
    "outcome": "success",
    "id": 1723556258625
    }]"""


@pytest.fixture
def loading():
    return """{
    "submissionTime": "2024-08-13T13:37:38.633Z",
    "executionStart": "2024-08-13T13:37:38.633Z",
    "executionStatus": "completed",
    "logs": [
        {
            "executionStart": "2024-08-13T13:37:38.684Z",
            "message": "All dataflows deleted for organisation default",
            "status": "success",
            "server": "sfs"
        }
    ],
    "executionEnd": "2024-08-13T13:37:38.689Z",
    "outcome": "success",
    "id": 1723556258625
    }"""


@pytest.fixture
def loading_inprogress():
    return """{
    "submissionTime": "2024-08-13T13:37:38.633Z",
    "executionStart": "2024-08-13T13:37:38.633Z",
    "executionStatus": "inProgress",
    "logs": [
        {
            "executionStart": "2024-08-13T13:37:38.684Z",
            "message": "All dataflows deleted for organisation default",
            "status": "success",
            "server": "sfs"
        }
    ],
    "executionEnd": "2024-08-13T13:37:38.689Z",
    "outcome": "success",
    "id": 1723556258625
    }"""


def test_get_log(httpx_mock, loading):
    httpx_mock.add_response(status_code=200, content=loading)

    client = SFSClient(sfs_url="https://foo", sfs_api_key="bar")
    log = client.get_log(tenant="foo", loading_id="bar")
    assert log.id == 1723556258625


def test_get_log_502_error(httpx_mock, loadings):
    httpx_mock.add_response(status_code=502, content="{}")
    httpx_mock.add_response(status_code=200, content=loadings)
    client = SFSClient(sfs_url="https://foo", sfs_api_key="bar")
    log = client.get_log(tenant="foo", loading_id="1723556258625")
    assert log.id == 1723556258625


def test_get_log_return_none_if_not_found(httpx_mock, loadings):
    httpx_mock.add_response(status_code=502, content="{}")
    httpx_mock.add_response(status_code=200, content=loadings)
    client = SFSClient(sfs_url="https://foo", sfs_api_key="bar")
    log = client.get_log(tenant="foo", loading_id="172355625862")
    assert log is None


def test_check_status_loading(httpx_mock, loading):
    httpx_mock.add_response(status_code=200, content=loading)
    client = SFSClient(sfs_url="https://foo", sfs_api_key="bar")
    status = client.check_status_loading(tenant="foo", loading_id="bar")
    assert status == SFSClient.LoadingStatus.COMPLETED


def test_check_status_loading_inprogress(httpx_mock, loading_inprogress):
    httpx_mock.add_response(status_code=200, content=loading_inprogress)
    client = SFSClient(sfs_url="https://foo", sfs_api_key="bar")
    status = client.check_status_loading(tenant="foo", loading_id="bar")
    assert status == SFSClient.LoadingStatus.RETRY


def test_index(httpx_mock):
    httpx_mock.add_response(
        method="POST", status_code=200, content='{"loadingId": 1734967844099}'
    )
    client = SFSClient(sfs_url="https://foo", sfs_api_key="bar")
    loading_id = client.index()
    assert loading_id == 1734967844099


def test_wait_for_reindex(httpx_mock, loading):
    httpx_mock.add_response(status_code=200, content=loading)
    client = SFSClient(sfs_url="https://foo", sfs_api_key="bar")
    finished = client.check_if_reindex_finished(
        tenant="default", loading_id="172355625862"
    )
    assert finished is True


def test_wait_for_reindex_expire(httpx_mock, loading_inprogress, mocker):
    mocker.patch(
        "statsuite_lib.SFSClient.check_status_loading",
        return_value=SFSClient.LoadingStatus.RETRY,
    )
    client = SFSClient(sfs_url="https://foo", sfs_api_key="bar")
    finished = client.check_if_reindex_finished(
        tenant="default", loading_id="172355625862", backoff=0.1, timeout=0.2
    )
    assert finished is False
