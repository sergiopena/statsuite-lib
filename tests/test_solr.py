import pytest

from statsuite_lib import SolrClient


@pytest.fixture
def solr_client():
    """Create a SolrClient instance for testing."""
    return SolrClient(solr_url="http://test-solr:8983")


def test_init_with_default_url():
    """Test SolrClient initialization with default URL."""
    client = SolrClient()
    assert client.SOLR_URL == "http://localhost:8983"
    assert client.log.name == "SolrClient"


def test_init_with_custom_url():
    """Test SolrClient initialization with custom URL."""
    client = SolrClient(solr_url="https://solr.example.com:8983")
    assert client.SOLR_URL == "https://solr.example.com:8983"
    assert client.log.name == "SolrClient"


def test_create_collection_success(solr_client, httpx_mock):
    """Test successful collection creation with default parameters."""
    # Mock successful response
    mock_response = {
        "responseHeader": {"status": 0, "QTime": 123},
        "success": {"test-collection": {"responseHeader": {"status": 0, "QTime": 45}}},
    }

    httpx_mock.add_response(
        method="GET",
        url="http://test-solr:8983/solr/admin/collections?action=CREATE&name=test-collection&collection.configName=_default&numShards=1&replicationFactor=1&router.name=compositeId&wt=json",  # noqa E501
        json=mock_response,
        status_code=200,
    )

    result = solr_client.create_collection("test-collection")

    assert result == mock_response
    assert result["responseHeader"]["status"] == 0


def test_create_collection_with_custom_parameters(solr_client, httpx_mock):
    """Test collection creation with custom parameters."""
    mock_response = {
        "responseHeader": {"status": 0, "QTime": 100},
        "success": {"custom-collection": {"responseHeader": {"status": 0}}},
    }

    httpx_mock.add_response(
        method="GET",
        url="http://test-solr:8983/solr/admin/collections?action=CREATE&name=custom-collection&collection.configName=custom_config&numShards=2&replicationFactor=3&router.name=implicit&wt=xml",  # noqa E501
        json=mock_response,
        status_code=200,
    )

    result = solr_client.create_collection(
        name="custom-collection",
        config_name="custom_config",
        num_shards=2,
        replication_factor=3,
        router_name="implicit",
        wt="xml",
    )

    assert result == mock_response


def test_create_collection_http_error(solr_client, httpx_mock):
    """Test collection creation with HTTP error."""
    httpx_mock.add_response(
        method="GET",
        url="http://test-solr:8983/solr/admin/collections?action=CREATE&name=error-collection&collection.configName=_default&numShards=1&replicationFactor=1&router.name=compositeId&wt=json",  # noqa E501
        status_code=500,
        text="Internal Server Error",
    )

    with pytest.raises(Exception):
        solr_client.create_collection("error-collection")


def test_create_collection_solr_error(solr_client, httpx_mock):
    """Test collection creation with Solr API error response."""
    mock_response = {
        "responseHeader": {"status": 400, "QTime": 10},
        "error": {
            "msg": "Collection 'existing-collection' already exists.",
            "code": 400,
        },
    }

    httpx_mock.add_response(
        method="GET",
        url="http://test-solr:8983/solr/admin/collections?action=CREATE&name=existing-collection&collection.configName=_default&numShards=1&replicationFactor=1&router.name=compositeId&wt=json",  # noqa E501
        json=mock_response,
        status_code=200,
    )

    result = solr_client.create_collection("existing-collection")

    # Should still return the response even if Solr reports an error
    assert result == mock_response
    assert result["responseHeader"]["status"] == 400
    assert "already exists" in result["error"]["msg"]


def test_create_collection_url_construction(solr_client, httpx_mock):
    """Test that the correct URL and parameters are constructed."""
    mock_response = {"responseHeader": {"status": 0}}

    httpx_mock.add_response(
        method="GET",
        url="http://test-solr:8983/solr/admin/collections?action=CREATE&name=test&collection.configName=test_config&numShards=5&replicationFactor=2&router.name=test_router&wt=xml",  # noqa E501
        json=mock_response,
        status_code=200,
    )

    solr_client.create_collection(
        name="test",
        config_name="test_config",
        num_shards=5,
        replication_factor=2,
        router_name="test_router",
        wt="xml",
    )

    # Verify the request was made with correct parameters
    request = httpx_mock.get_request()
    assert request.url.scheme == "http"
    assert request.url.host == "test-solr"
    assert request.url.port == 8983
    assert request.url.path == "/solr/admin/collections"

    # Check query parameters
    params = dict(request.url.params)
    assert params["action"] == "CREATE"
    assert params["name"] == "test"
    assert params["collection.configName"] == "test_config"
    assert params["numShards"] == "5"
    assert params["replicationFactor"] == "2"
    assert params["router.name"] == "test_router"
    assert params["wt"] == "xml"


def test_delete_collection_success(solr_client, httpx_mock):
    """Test successful collection deletion with default parameters."""
    # Mock successful response
    mock_response = {
        "responseHeader": {"status": 0, "QTime": 45},
        "success": {"test-collection": {"responseHeader": {"status": 0, "QTime": 12}}},
    }

    httpx_mock.add_response(
        method="GET",
        url="http://test-solr:8983/solr/admin/collections?action=DELETE&name=test-collection&wt=json",  # noqa E501
        json=mock_response,
        status_code=200,
    )

    result = solr_client.delete_collection("test-collection")

    assert result == mock_response
    assert result["responseHeader"]["status"] == 0


def test_delete_collection_with_custom_wt(solr_client, httpx_mock):
    """Test collection deletion with custom response format."""
    mock_response = {
        "responseHeader": {"status": 0, "QTime": 30},
        "success": {"custom-collection": {"responseHeader": {"status": 0}}},
    }

    httpx_mock.add_response(
        method="GET",
        url="http://test-solr:8983/solr/admin/collections?action=DELETE&name=custom-collection&wt=xml",  # noqa E501
        json=mock_response,
        status_code=200,
    )

    result = solr_client.delete_collection(name="custom-collection", wt="xml")

    assert result == mock_response


def test_delete_collection_http_error(solr_client, httpx_mock):
    """Test collection deletion with HTTP error."""
    httpx_mock.add_response(
        method="GET",
        url="http://test-solr:8983/solr/admin/collections?action=DELETE&name=error-collection&wt=json",  # noqa E501
        status_code=500,
        text="Internal Server Error",
    )

    with pytest.raises(Exception):
        solr_client.delete_collection("error-collection")


def test_delete_collection_solr_error(solr_client, httpx_mock):
    """Test collection deletion with Solr API error response."""
    mock_response = {
        "responseHeader": {"status": 400, "QTime": 8},
        "error": {
            "msg": "Collection 'non-existent-collection' not found.",
            "code": 400,
        },
    }

    httpx_mock.add_response(
        method="GET",
        url="http://test-solr:8983/solr/admin/collections?action=DELETE&name=non-existent-collection&wt=json",  # noqa E501
        json=mock_response,
        status_code=200,
    )

    result = solr_client.delete_collection("non-existent-collection")

    # Should still return the response even if Solr reports an error
    assert result == mock_response
    assert result["responseHeader"]["status"] == 400
    assert "not found" in result["error"]["msg"]


def test_delete_collection_url_construction(solr_client, httpx_mock):
    """Test that the correct URL and parameters are constructed for deletion."""
    mock_response = {"responseHeader": {"status": 0}}

    httpx_mock.add_response(
        method="GET",
        url="http://test-solr:8983/solr/admin/collections?action=DELETE&name=test-delete&wt=xml",  # noqa E501
        json=mock_response,
        status_code=200,
    )

    solr_client.delete_collection(name="test-delete", wt="xml")

    # Verify the request was made with correct parameters
    request = httpx_mock.get_request()
    assert request.url.scheme == "http"
    assert request.url.host == "test-solr"
    assert request.url.port == 8983
    assert request.url.path == "/solr/admin/collections"

    # Check query parameters
    params = dict(request.url.params)
    assert params["action"] == "DELETE"
    assert params["name"] == "test-delete"
    assert params["wt"] == "xml"
