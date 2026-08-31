"""statsuite-lib: a client library for the dotStatSuite family of APIs.

Each API is exposed through its own client class (:class:`AuthClient`,
:class:`ConfigClient`, :class:`KeycloakClient`, :class:`NSIClient`,
:class:`SFSClient`, :class:`TransferClient`). Most clients require a
:class:`KeycloakClient` instance to obtain and refresh authentication
tokens.
"""

from .auth import AuthClient
from .config import ConfigClient
from .keycloak import KeycloakClient
from .nsi import NSIClient
from .sfs import SFSClient
from .transfer import TransferClient

__all__ = [
    "AuthClient",
    "ConfigClient",
    "KeycloakClient",
    "NSIClient",
    "SFSClient",
    "TransferClient",
]
