import logging

import httpx


class SolrClient:
    """Client for Apache Solr search service"""

    def __init__(self, solr_url: str = "http://localhost:8983") -> None:
        """Initialize the Solr client.

        Args:
            solr_url: Base URL for the Solr service. Defaults to "http://localhost:8983".
        """
        self._client = httpx.Client()
        self.SOLR_URL = solr_url
        self.log = logging.getLogger("SolrClient")
        self.log.level = logging.INFO

    def create_collection(
        self,
        name: str,
        config_name: str = "_default",
        num_shards: int = 1,
        replication_factor: int = 1,
        router_name: str = "compositeId",
        wt: str = "json",
    ) -> dict:
        """Create a new Solr collection.

        Args:
            name: Name of the collection to create.
            config_name: Configuration name to use. Defaults to "_default".
            num_shards: Number of shards for the collection. Defaults to 1.
            replication_factor: Replication factor for the collection. Defaults to 1.
            router_name: Router name for the collection. Defaults to "compositeId".
            wt: Response format. Defaults to "json".

        Returns:
            dict: The JSON response from the Solr admin API.

        """
        url = f"{self.SOLR_URL}/solr/admin/collections"

        params = {
            "action": "CREATE",
            "name": name,
            "collection.configName": config_name,
            "numShards": num_shards,
            "replicationFactor": replication_factor,
            "router.name": router_name,
            "wt": wt,
        }

        self.log.info(f"Creating Solr collection: {name}")
        self.log.info(f"URL: {url}")
        self.log.info(f"Parameters: {params}")

        response = httpx.get(url=url, params=params)
        response.raise_for_status()

        result = response.json()
        self.log.info(f"Collection '{name}' created successfully")
        return result

    def delete_collection(
        self,
        name: str,
        wt: str = "json",
    ) -> dict:
        """Delete a Solr collection.

        Args:
            name: Name of the collection to delete.
            wt: Response format. Defaults to "json".

        Returns:
            dict: The JSON response from the Solr admin API.

        """
        url = f"{self.SOLR_URL}/solr/admin/collections"

        params = {
            "action": "DELETE",
            "name": name,
            "wt": wt,
        }

        self.log.info(f"Deleting Solr collection: {name}")
        self.log.info(f"URL: {url}")
        self.log.info(f"Parameters: {params}")

        response = httpx.get(url=url, params=params)
        response.raise_for_status()

        result = response.json()
        self.log.info(f"Collection '{name}' deleted successfully")
        return result
