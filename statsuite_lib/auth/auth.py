"""Client for the dotStatSuite Auth API (authorization rule management)."""

import logging

import httpx

from ..keycloak.keycloak import KeycloakClient


class AuthClient:
    """A client for managing authorization rules through the Auth API.

    This client handles the communication with the authorization service,
    allowing for the management of access rules and permissions.

    Attributes:
        AUTH_URL (str): The complete URL for the Auth API including version.

    Args:
        auth_url (str): Base URL of the authorization service.
        keycloak_client (KeycloakClient): Client for handling Keycloak authentication.
        api_version (str, optional): API version to use. Defaults to "1.1".
    """

    def __init__(
        self, auth_url: str, keycloak_client: KeycloakClient, api_version: str = "1.1"
    ) -> None:
        """Initialize the AuthClient.

        Creates a new instance of the AuthClient with the specified configuration.
        Sets up an HTTP client and configures logging.

        Args:
            auth_url (str): Base URL of the authorization service endpoint.
                Should not include the version number.
            keycloak_client (KeycloakClient): An initialized Keycloak client instance
                used for authentication headers.
            api_version (str, optional): API version string to use in URL construction.
                Defaults to "1.1".

        Example:
            keycloak_client = KeycloakClient(...)
            auth_client = AuthClient(
                auth_url="https://auth.example.com",
                keycloak_client=keycloak_client
            )
        """

        self._client = httpx.Client()
        self.AUTH_URL = f"{auth_url}/{api_version}"
        self._keycloak_client = keycloak_client
        self.log = logging.getLogger("AuthClient")

    def add_rule(
        self,
        user_mask: str,
        is_group: bool,
        permission: int,
        dataspace: str = "*",
        artifact_type: int = 0,
        artefact_agency_id: str = "*",
        artefact_id: str = "*",
        artefact_version: str = "*",
    ) -> dict:
        """Add a new authorization rule to the system.

        Args:
            user_mask (str): The user or group identifier pattern.
            is_group (bool): Whether the rule applies to a group (True) or user (False).
            permission (int): The permission level to grant.
            dataspace (str, optional): Target dataspace. Defaults to "*" (all dataspaces).
            artifact_type (int, optional): Type of artifact. Defaults to 0.
            artefact_agency_id (str, optional): Agency ID of the artifact. Defaults to "*".
            artefact_id (str, optional): ID of the artifact. Defaults to "*".
            artefact_version (str, optional): Version of the artifact. Defaults to "*".

        A duplicate-key error (the rule already exists) is treated as a no-op
        rather than an error; any other failure response raises
        ``httpx.HTTPStatusError``.

        Returns:
            dict: The JSON response from the server containing the created rule.
        """

        data = {
            "userMask": user_mask,
            "isGroup": is_group,
            "dataSpace": dataspace,
            "artefactType": artifact_type,
            "artefactAgencyId": artefact_agency_id,
            "artefactId": artefact_id,
            "artefactVersion": artefact_version,
            "permission": permission,
        }

        url = f"{self.AUTH_URL}/AuthorizationRules"
        headers = self._keycloak_client.auth_header()
        headers["Content-Type"] = "application/json"

        response = self._client.post(url=url, headers=headers, json=data)
        self._handle_error_response(
            response, ignorable_prefix="Cannot insert duplicate key"
        )

        return response.json()

    def _handle_error_response(
        self, response: httpx.Response, ignorable_prefix: str
    ) -> None:
        """Raise for error responses, except for a known, ignorable error.

        Any error response is re-raised as ``httpx.HTTPStatusError`` unless its
        first reported error matches ``ignorable_prefix``, in which case it is
        logged and swallowed instead.

        Args:
            response: The HTTP response to check for errors.
            ignorable_prefix: If the first reported error starts with this
                prefix, the error is logged and swallowed instead of raised
                (e.g. "the rule already exists" is not treated as a failure).
        """
        if response.status_code < 400:
            return

        resp = response.json()
        payload = resp.get("payload", {})
        errors = payload.get("errors", [])

        if errors and errors[0].startswith(ignorable_prefix):
            self.log.info(errors[0])
        else:
            response.raise_for_status()

    def delete_rule(self, rule_id: str) -> dict:
        """Delete an authorization rule by its ID.

        Args:
            rule_id (str): The unique identifier of the rule to delete.

        A rule-not-found error is treated as a no-op rather than an error; any
        other failure response raises ``httpx.HTTPStatusError``.

        Returns:
            dict: The JSON response from the server confirming the deletion.
        """
        url = f"{self.AUTH_URL}/AuthorizationRules/{rule_id}"
        headers = self._keycloak_client.auth_header()

        self.log.info(f"Deleting rule at: {url}")

        response = self._client.delete(url=url, headers=headers)
        self._handle_error_response(response, ignorable_prefix="Rule not found")

        return response.json()
