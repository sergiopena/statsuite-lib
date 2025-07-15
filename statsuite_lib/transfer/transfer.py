import time
import logging

import httpx

from ..keycloak.keycloak import KeycloakClient


class TransferClient:
    def __init__(self, transfer_url: str, keycloak_client: KeycloakClient) -> None:
        self._client = httpx.Client()
        self.TRANSFER_URL = transfer_url
        self._keycloak_client = keycloak_client
        self._log = logging.getLogger("TransferClient")


    def import_sdmx_file(self,
                         file,
                         dataspace: str,
                         target_version: int = 0,
                         restoration_option_required: bool = False,
                         validation_type: int = 1,
                         timeout: int = None) -> int:
        self._log.info(f'Importing sdmx file to dataspace {dataspace}')
        data = {'dataspace': dataspace,
                'targetVersion': target_version,
                'restorationOptionRequired': restoration_option_required,
                'validationType': validation_type}
        files = {'file': file}
        try:
            r = httpx.post(url=f'{self.TRANSFER_URL}/import/sdmxFile',
                           headers=self._keycloak_client.auth_header(),
                           data=data,
                           files=files,
                           timeout=timeout)
            print(r.json())
            return r.json().get('message').split(' ')[4]
        except Exception as e:
            self._log.error(f'Failed to import sdmx file {e}')
            raise e

    def check_request_status(self, dataspace: str, id: int) -> str:
        self._log.info(f'Checking request status for dataspace {dataspace} and id {id}')
        data = {'dataspace': dataspace,
                'id': id}
        try:
            r = httpx.post(url=f'{self.TRANSFER_URL}/1.2/status/request',
                           headers=self._keycloak_client.auth_header(),
                           data=data)
            return r.json().get('executionStatus')
        except Exception as e:
            self._log.error(f'Failed to check request status {e}')
            raise e

    def wait_for_request(self, dataspace: str, id: int, timeout: int = 300, backoff: int = 30) -> None:
        start = time.time()
        while True:
            status = self.check_request_status(dataspace=dataspace, id=id)
            if status == 'Completed':
                return False

            if time.time() - start > timeout:
                self.log.error(f'Timeout waiting for request to be completed {timeout} seconds passed')
                return True
            time.sleep(backoff)

    def transfer_dataflow(self, source_dataspace: str, destination_dataspace: str, dataflow: str):
        self._log.info(f'Transferring dataflow {dataflow} from {source_dataspace} to {destination_dataspace}')
        data = {'sourceDataspace': source_dataspace,
                'destinationDataspace': destination_dataspace,
                'sourceDataflow': dataflow,
                'destinationDataflow': dataflow,
                'transferContent': 0,
                'sourceVersion': 0,
                'targetVersion': 0,
                'restorationOptionRequired': False,
                'validationType': 0}

        try:
            r = httpx.post(url=f'{self.TRANSFER_URL}/transfer/dataflow',
                           headers=self._keycloak_client.auth_header(),
                           data=data)
            return r.json().get('message').split(' ')[4]
        except Exception as e:
            self._log.error(f'Failed to transfer dataflow {e}')
            raise e

    def get_tune(self, dataspace: str, dsd_id: str):
        self._log.info(f'Getting DSD {dsd_id} tune information in ds {dataspace}')
        data = {'dataspace': dataspace,
                'dsd': dsd_id }
        r = httpx.post(url=f'{self.TRANSFER_URL}/3/tune/info',
                       headers=self._keycloak_client.auth_header(),
                       data=data)
        return r.json()

    def set_tune(self, dataspace: str, dsd_id: str, index_type: int):
        self._log.info(f'Getting DSD {dsd_id} tune information in ds {dataspace}')
        data = {'dataspace': dataspace,
                'dsd': dsd_id,
                'indexType': index_type}
        r = httpx.post(url=f'{self.TRANSFER_URL}/3/tune/dsd',
                       headers=self._keycloak_client.auth_header(),
                       data=data)
        return r.json()

