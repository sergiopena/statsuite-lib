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
        self._log = logging.getLogger("AuthClient")

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
    ):
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

        # Add debugging to help identify the 400 Bad Request issue

        response = httpx.post(url=url, headers=headers, json=data)

        # Handle error responses
        self._handle_error_response(response)

        return response.json()

    def _handle_error_response(self, response: httpx.Response) -> None:
        """Handle error responses from the auth API.

        Args:
            response: The HTTP response to check for errors.
        """
        if response.status_code < 400:
            return

        resp = response.json()
        payload = resp.get("payload", {})
        errors = payload.get("errors", [])

        if errors and errors[0].startswith("Cannot insert duplicate key"):
            print("Permission already exists")
        else:
            response.raise_for_status()

    def _handle_delete_error_response(self, response: httpx.Response) -> None:
        """Handle error responses from delete operations.

        Args:
            response: The HTTP response to check for errors.
        """
        if response.status_code < 400:
            return

        resp = response.json()
        payload = resp.get("payload", {})
        errors = payload.get("errors", [])

        if errors and errors[0].startswith("Rule not found"):
            print("Rule not found")
        else:
            response.raise_for_status()

    def delete_rule(self, rule_id: str):
        """Delete an authorization rule by its ID.

        Args:
            rule_id (str): The unique identifier of the rule to delete.

        Returns:
            dict: The JSON response from the server confirming the deletion.


        """
        url = f"{self.AUTH_URL}/AuthorizationRules/{rule_id}"
        headers = self._keycloak_client.auth_header()

        # Add debugging to help identify any issues
        print(f"Deleting rule at: {url}")
        print(f"Headers: {headers}")

        response = httpx.delete(url=url, headers=headers)

        # Handle error responses
        self._handle_delete_error_response(response)

        return response.json()
