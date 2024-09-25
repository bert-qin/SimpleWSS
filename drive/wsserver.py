
import logging
import asyncio
import websockets
import threading
from drive.observable import Observable
from drive.util import ip
from drive.station import Station
import time

class WsServer(Observable):
    def __init__(self, port=8080) -> None:
        super().__init__()
        self.port = port
        self.thread = None
        self.loop = None
        self.station_dic = {}

    def register_observer(self, observer):
        super().register_observer(observer)
        for sta in self.station_dic.values():
            sta.register_observer(observer)

    def unregister_observer(self, observer=None):
        super().unregister_observer(observer=observer)
        for sta in self.station_dic.values():
            sta.unregister_observer(observer=observer)

    async def on_connect(self, websocket, path):
        """ For every new charge point that connects, create a ChargePoint
        instance and start listening for messages.
        """
        try:
            requested_protocols = websocket.request_headers[
                'Sec-WebSocket-Protocol']
        except KeyError:
            logging.info("Client hasn't requested any Subprotocol.")
            # return await websocket.close()
        if websocket.subprotocol:
            logging.info("Protocols Matched: %s", websocket.subprotocol)
        else:
            # In the websockets lib if no subprotocols are supported by the
            # client and the server, it proceeds without a subprotocol,
            # so we have to manually close the connection.
            pass
            # logging.warning('Protocols Mismatched | Expected Subprotocols: %s,'
            #                 ' but client supports  %s | Closing connection',
            #                 websocket.available_subprotocols,
            #                 requested_protocols)
            # return await websocket.close()
        client_id = path.strip('/')
        if len(client_id) == 0:
            client_id  = websocket.remote_address[0]
        # clear first
        client = self.station_dic.pop(client_id, None)
        if client:
            for item in self._observer_set:
                client.unregister_observer()
            client._connection.close()
        client = Station(client_id, websocket, self)

        for item in self._observer_set:
            client.register_observer(item)
        self.station_dic[client_id] = client
        await client.start()

    def start(self):
        self.thread = threading.Thread(
            target=self.run, daemon=True, name='ws-server')
        self.thread.start()

    def run(self):
        time.sleep(5)
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self._start())
        self.loop.close()

    async def _start(self):
        server = await websockets.serve(
            self.on_connect,
            '0.0.0.0',
            self.port,
            # subprotocols=[OCPP_2_0_1, OCPP_1_6]
        )
        logging.info("WebSocket Server Started")
        await server.wait_closed()

    def get_url(self):
        return f'ws[s]://[{", ".join(ip.get_host_and_ipv4())}]:{self.port}/'


def start(port: int = 8080):
    server = WsServer(port=port)
    server.start()
    return server


if __name__ == '__main__':
    WsServer().start()
