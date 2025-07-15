import logging

import httpx

from ..keycloak.keycloak import KeycloakClient


class NSIClient:
    def __init__(self, nsi_url: str, keycloak_client: KeycloakClient) -> None:
        self._client = httpx.Client()
        self.NSI_URL = nsi_url
        self._keycloak_client = keycloak_client
        self.log = logging.getLogger("NSIClient")

    def put(self, file, path: str, timeout: int = None) -> int:
        try:
            headers = self._keycloak_client.auth_header() | {'Content-Type': 'application/x-www-form-urlencoded'}

            self.log.info(f'Uploading to NSI: {self.NSI_URL + path}')

            r = httpx.post(self.NSI_URL + path,
                           content=file,
                           headers=headers,
                           timeout=timeout)
            if r.status_code != 207:
                self.log.info(f'NSI response: {r.text}')
            self.log.info(r.text)
            return r.status_code
        except Exception as e:
            self._error_collector.collect('NSIClient', f'Failed to upload to NSI {e}')
            raise e

    def get(self, path: str, headers: dict  = {}, timeout: int = None ) -> httpx.Response:
        try:
            headers |= self._keycloak_client.auth_header()
            self.log.info(f'Getting from NSI: {self.NSI_URL + path}')
            r = httpx.get(self.NSI_URL + path,
                          headers=headers,
                          timeout=timeout)
            return r
        except Exception as e:
            self._error_collector.collect('NSIClient', f'Failed to get from NSI {e}')
            raise e

    def delete(self, path: str, timeout: int = None) -> int:
        try:
            headers = self._keycloak_client.auth_header()
            self.log.info(f'Deleting from NSI: {self.NSI_URL + path}')
            r = httpx.delete(self.NSI_URL + path,
                             headers=headers,
                             timeout=timeout)
            return r.status_code
        except Exception as e:
            self._error_collector.collect('NSIClient', f'Failed to delete from NSI {e}')
            raise e
