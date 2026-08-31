"""Pydantic models for the dotStatSuite Config API responses."""

from typing import Dict

from pydantic import BaseModel, ConfigDict, RootModel


class Space(BaseModel):
    """Model for spaces inside tenants

    Attributes:
        label: Space id
        url: Space url
    """

    label: str  # noqa VNE003
    url: str


class Oidc(BaseModel):
    """Model for the OIDC settings of a tenant scope

    Attributes:
        model_config: Configuration
        authority: URL of the OIDC (Keycloak) authority/realm to authenticate against
    """

    model_config = ConfigDict(extra="allow")
    authority: str


class Scope(BaseModel):
    """Model for a single scope (e.g. "dlm", "de") inside a tenant

    Attributes:
        model_config: Configuration
        oidc: OIDC settings for this scope
    """

    model_config = ConfigDict(extra="allow")
    oidc: Oidc


class Tenant(BaseModel):
    """Model for a single tenant entry in the tenants config

    Attributes:
        model_config: Configuration
        spaces: Dict of spaces inside the tenant, keyed by space name
        scopes: Dict of scopes inside the tenant, keyed by scope name
    """

    model_config = ConfigDict(extra="allow")
    spaces: Dict[str, Space]
    scopes: Dict[str, Scope] = {}


class Tenants(RootModel):
    """Collection of tenants, keyed by tenant name

    Attributes:
        root: Dict of tenants, keyed by tenant name
    """

    root: Dict[str, Tenant]
