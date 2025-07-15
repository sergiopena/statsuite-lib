import datetime
import logging

import httpx

class KeycloakClient:
    def __init__(self, openid_url: str, username: str, password: str) -> None:
        self._client = httpx.Client()
        self.OPENID_URL = openid_url
        print(self.OPENID_URL)
        self.log = logging.getLogger("KeycloakClient")
        self._auth_endpoint = None
        self._token_endpoint = None
        self.access_token = None
        self.access_token_expires = None
        self.refresh_token = None
        self._get_openid_configuration()
        self._authenticate(username=username, password=password)

    def _get_openid_configuration(self) -> None:
        """Retrieves oidc config from keycloak"""
        self.log.info(f'Getting openid configuration from {self.OPENID_URL}')
        try:

            response = self._client.get(self.OPENID_URL)
            self._auth_endpoint = response.json()['authorization_endpoint']
            self._token_endpoint = response.json()['token_endpoint']

        except httpx.ConnectError as e:
            self.log.error(f'Failed to get openid configuration: {e}')
            raise e

    def _authenticate(self, username: str, password: str) -> None:
        self.log.info(f'Authenticating with {self._auth_endpoint}')
        try:
            r = self._client.post(self._token_endpoint, data={
                'grant_type': 'password',
                'client_id': 'stat-suite',
                'username': username,
                'password': password,
            })

            self.refresh_token = r.json()['refresh_token']
            self.access_token = r.json()['access_token']
            self.access_token_expires = datetime.datetime.now() + datetime.timedelta(seconds=r.json()['expires_in'])
        except httpx.ConnectError as e:
            self.log.error(f'Failed to authenticate: {e}')
            raise e

    def trigger_refresh_token(self) -> None:
        self.log.info("Triggering refresh token")
        try:
            r = self._client.post(self._token_endpoint, data={
                'grant_type': 'refresh_token',
                'client_id': 'stat-suite',
                'refresh_token': self.refresh_token,
            })
            self.access_token = r.json()['access_token']
            self.access_token_expires = datetime.datetime.now() + datetime.timedelta(seconds=r.json()['expires_in'])
            self.refresh_token = r.json()['refresh_token']
        except httpx.ConnectError as e:
            self.log.error(f'Failed to refresh token: {e}')
            raise e

    def get_access_token(self) -> str:
        self.log.info("Getting access token")
        if self.access_token_expires is None or self.access_token_expires < datetime.datetime.now():
            self.trigger_refresh_token()

        return self.access_token

    def auth_header(self) -> dict:
        return {'Authorization': f'Bearer {self.get_access_token()}'}
