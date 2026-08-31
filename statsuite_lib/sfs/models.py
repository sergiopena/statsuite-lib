"""Pydantic models for the SFS (SDMX Faceted Search) API responses."""

from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, RootModel


class Index(RootModel):
    """Model for return json from indexing request on SFS

    Attributes:
        root: The response JSON, in the format { "loadingId": ######### }
    """

    root: Dict[str, int]


class LoadingLog(BaseModel):
    """Minimal model for a Loading Log entity

    Attributes:
        model_config: Configuration
        executionStart: Timestamp start of the task
        executionStatus: Status of the task
        id: Loading id
    """

    model_config = ConfigDict(extra="allow")
    executionStart: str
    executionStatus: Optional[str] = None
    id: int  # noqa


class LoadingLogs(RootModel):
    """Collection of loading log entries

    Attributes:
        root: Collection of Loadings without key
    """

    root: List[LoadingLog]
