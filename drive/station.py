import logging
import asyncio
from typing import Dict
from drive.observable import Observable
from drive import event
from drive.util import time
from dataclasses import asdict
import json
import websockets
import traceback

class Station(Observable):
    def __init__(self, id, connection, ws_server, response_timeout=30):
        self.id = id
        self._connection = connection
        self._ws_server = ws_server
        super().__init__()

    def show_log(self, msg):
        self.notify_all(event.Log(self.id, f'{time.get_yyyy_mm_dd_hh_mm_ss()} {msg}'))

    def show_connect(self, is_connect: bool):
        self.notify_all(event.Connect(self.id, is_connect))

    def show_result_tip(self, result: bool = True, prefix: str = None):
        if result:
            msg = event.Result.OK
            color = event.Color.success
        else:
            msg = event.Result.NG
            color = event.Color.error
        if prefix:
            msg = f'{prefix}: {msg}'
        self.notify_all(event.Tip(self.id, msg, color=color))

    async def start(self):
        try:
            self.show_connect(True)
            while True:
                try:
                    message = await self._connection.recv()
                    info = f'{self.id} << {message}'
                    logging.info(info)
                    self.show_log(info)
                except websockets.exceptions.ConnectionClosed:
                    break
                except Exception as e:
                    logging.error(e)
                    self.show_log(f'{self.id} >> {traceback.format_exc()}')
            self._ws_server.station_dic.pop(self.id)
            self.show_connect(False)
            self.unregister_observer()
        except Exception as ex:
            logging.error(ex)

    async def send(self, message):
        info = f'{self.id} >> {message}'
        logging.info(info)
        self.show_log(info)
        await self._connection.send(message)

if __name__ == '__main__':
    pass
