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


class Tenant(BaseModel):
    """Model for a single tenant entry in the tenants config

    Attributes:
        model_config: Configuration
        spaces: Dict of spaces inside the tenant, keyed by space name
    """

    model_config = ConfigDict(extra="allow")
    spaces: Dict[str, Space]


class Tenants(RootModel):
    """Collection of tenants, keyed by tenant name

    Attributes:
        root: Dict of tenants, keyed by tenant name
    """

    root: Dict[str, Tenant]
