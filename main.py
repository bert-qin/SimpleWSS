import os
import logging
import time
from drive import ui
from drive import tray
from drive import wsserver

LOG_FILE = 'log.txt'
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

args = {
    'level': eval('logging.{}'.format('INFO')),
    'format': LOG_FORMAT,
    'datefmt': DATE_FORMAT,
}

is_posix = os.name == 'posix'

if __name__ == '__main__':
    if os.path.exists(LOG_FILE):
        args['filename'] = LOG_FILE
    logging.basicConfig(**args)
    if is_posix:
        ui.start(wsserver.start(port=31531), port=31532, auto_open=False)
        while True:
            time.sleep(1)
    else:
        ui.start(wsserver.start(port=5787))
        tray.start()
