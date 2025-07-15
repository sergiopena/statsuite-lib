import logging
import pprint
import time

#from statsuite_lib import SFSClient

#client = SFSClient(
#    sfs_url="https://sfs-statsuite.dev.aws.fao.org",
#    sfs_api_key="a_YRHvna3l1jfvl7crUdIw",
#)
#
logging.basicConfig(level=logging.INFO)
# loadingId = client.index()


#time.sleep(2)
#loadingId = 1734959833223  # no
# loadingId=1723556258625 # yes
# client.wait_for_reindex(tenant='default', loading_id=loadingId, backoff=5)

#pprint.pp(client.get_log(tenant="default", loading_id=loadingId).logs)

from statsuite_lib import ConfigClient

client = ConfigClient(config_url='https://config-statsuite.dev.aws.fao.org')

spaces = client.get_dataspaces()
print(list(spaces))

