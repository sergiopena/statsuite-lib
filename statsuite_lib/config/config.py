"""Client for the dotStatSuite Config API (tenants and dataspaces)."""

import logging
from typing import Iterator

import httpx

from .models import Space, Tenant, Tenants


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

    def get_tenants(self) -> Tenants:
        """Gets tenants config

        Returns:
            Tenants: The parsed tenants configuration.
        """
        resp = self._client.get(f"{self.CONFIG_URL}/configs/tenants.json")
        resp.raise_for_status()
        return Tenants.model_validate(resp.json())

    def _get_tenant(self, tenant: str) -> Tenant:
        """Look up a tenant by name, raising a clear error if unknown.

        Args:
            tenant: select which tenant

        Returns:
            Tenant: The tenant configuration.

        Raises:
            KeyError: If ``tenant`` is not present in the tenants config.
        """
        tenants = self.get_tenants()
        if tenant not in tenants.root:
            raise KeyError(
                f"Unknown tenant {tenant!r}, available tenants: "
                f"{sorted(tenants.root)}"
            )
        return tenants.root[tenant]

    def get_dataspaces(self, tenant: str = "default") -> Iterator[Space]:
        """Returns a list of dataspaces configured for a tenant

        Args:
            tenant: select which tenant

        Yields:
            Space: A dataspace configuration object for each space in the tenant.
        """
        spaces = self._get_tenant(tenant).spaces
        for space in spaces:
            yield spaces.get(space)

    def get_dataspace(self, dataspace: str, tenant: str = "default") -> Space:
        """Returns a dataspace configuration object for a given tenant and space

        Args:
            dataspace: select which dataspace
            tenant: select which tenant

        Returns:
            Space: A dataspace configuration object for the given tenant and space.
        """
        return self._get_tenant(tenant).spaces.get(dataspace)

    def get_oidc_authority(self, tenant: str = "default") -> str:
        """Returns the OIDC authority URL configured for a tenant

        A tenant's scopes (e.g. "dlm", "de") each carry their own OIDC
        settings, but in practice they all point at the same authority for a
        given tenant, so the authority of any one of the tenant's scopes is
        returned.

        Args:
            tenant: select which tenant

        Returns:
            str: The OIDC authority URL for the tenant.

        Raises:
            LookupError: If the tenant has no scopes configured.
        """
        scopes = self._get_tenant(tenant).scopes
        if not scopes:
            raise LookupError(f"No scopes configured for tenant {tenant!r}")
        return next(iter(scopes.values())).oidc.authority
