import logging

import httpx


class ConfigClient:
    """Client for the SDMX Faceted search service"""

    def __init__(self, config_url: str) -> None:
        """Inits the client

        Args:
            config_url: Endpoint url for Config service.
        """

        self._client = httpx.Client()
        self.CONFIG_URL = config_url
        self.log = logging.getLogger("ConfigClient")
        self.log.level = logging.INFO

    def get_tenants(self) -> str:
        """Gets tenants config

        Returns:
            loadingId(str)
        """
        resp = httpx.get(
            f"{self.CONFIG_URL}/configs/tenants.json"
        )
        if resp.status_code == 200:
            from .models import Tenants

            loading = Tenants.model_validate(resp.json())
            return loading

    def get_dataspaces(self, tenant: str = 'default'):
        """Returns a list of dataspaces configured for a tenant

        Args:
            tenant: select which tenant
        """
        tenants = self.get_tenants()
        spaces = tenants.root.get(tenant).spaces
        for s in spaces:
            yield spaces.get(s)