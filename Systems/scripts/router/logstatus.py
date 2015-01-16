
import sys
sys.path.append("/home/local/raf/python")

import logging
from logging.handlers import SysLogHandler
 
log = logging.getLogger("router/logstatus")
log.setLevel(logging.INFO)
 
handler = SysLogHandler(address='/dev/log', facility=SysLogHandler.LOG_USER)
 
formatter = logging.Formatter('%(name)s: %(message)s')
handler.setFormatter(formatter)
 
log.addHandler(handler)


# Instantiate a Router instance with the connection parameters,
# collect it's status, then ask it to generate a log message.

user = 'admin'
pwd = 'password'
host = '192.168.99.1'

import raf.router

router = raf.router.Router(host)
router.setStatusHelper(raf.router.netgear.NetgearStatusHelper)
router.updateStatus()

log.info(router.getStatusMessage())

