from typing import Dict, List, Optional, Union

from pydantic import BaseModel, ConfigDict, RootModel


class Index(RootModel):
    """Model for return json from indexing request on SFS

    Attributes:
        root: returns a json in the format { "loadingId": ######### }
    """

    root: Dict[str, Union[str,Dict]]

class Space(BaseModel):
    id: str
    url: str

class Tenant(BaseModel):
    """Minimun model for Loading Log entity

    Attributes:
        model_config: Configuration
        executionStart: Timestamp start of the task
        executionStatus: Status of the task
        id: Loadingid
    """

    model_config = ConfigDict(extra="allow")
    id: str
    spaces: Dict[str, Space]


class Tenants(RootModel):
    """Collection of loading log entries

    Attributes:
        root: Collection of Loadings without key
    """

    root: Dict[str, Tenant]
