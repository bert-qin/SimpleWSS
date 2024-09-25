from pywebio import *
from pywebio.output import *
from pywebio import pin
from pywebio import session
from drive.wsserver import WsServer
from drive.observable import Observer
from drive import event as e
from drive import station as s
from drive import cmd as c
from enum import Enum
import asyncio
import threading
import logging
import queue
import sys
import time

UI_TITLE = 'SimpleWSS'
UI_VER = 'v1.0.0'
UI_PORT = 9999
UI_LOCAL_URL = f'http://127.0.0.1:{UI_PORT}/'
UI_STYLE_FLEX = 'display:flex;gap:5px;flex-wrap: wrap;align-items:center'
UI_STYLE_FLEX_COLUMN = 'display:flex;flex-direction:column;gap:5px'


class Scop(str, Enum):
    log = 'log'
    control = 'control'
    label = 'label'


class Pins(str, Enum):
    request_textarea = 'request'
    sn_select = 'sn_select'
    control_action = 'control_action'


class MainWindow(Observer):

    def __init__(self, ws_server: WsServer) -> None:
        self._queue: queue.Queue = queue.Queue()
        self._ws_server = ws_server
        self._ws_server.register_observer(self)

    def update_observer(self, *args):
        if len(args) != 0:
            self._queue.put(args[0])

    def show_tip(self, msg, color=e.Color.info, position: str = 'right'):
        toast(msg, color=color, position=position)

    @use_scope(Scop.log)
    def show_log(self, msg, _clear=False):
        if _clear:
            clear()
        else:
            put_code(msg, position=0, language='json')

    @use_scope(Scop.label)
    def show_labels(self, msg, color: e.Color = e.Color.info):
        if color == e.Color.success:
            put_success(msg)
        elif color == e.Color.warn:
            put_warning(msg)
        elif color == e.Color.error:
            put_error(msg)
        else:
            put_info(msg)

    @use_scope(Scop.control)
    def show_control(self):
        buttons = []
        for cmd in c.Cmd:
            button = {}
            button['label'] = cmd
            button['value'] = cmd
            if cmd == c.Cmd.send:
                button['color'] = e.Color.success
            elif cmd == c.Cmd.disconnect:
                button['color'] = e.Color.danger
            else:
                button['color'] = e.Color.info
            buttons.append(button)
        clear()
        pin.put_actions(Pins.control_action, buttons=buttons).style(
            UI_STYLE_FLEX_COLUMN)

    def refrash(self):
        self.show_control()

    def put_csms_url(self):
        return put_info(f'🌏Server URL: {self._ws_server.get_url()}', pin.put_select(
            Pins.sn_select, options=[key for key in self._ws_server.station_dic.keys()])).style(f'{UI_STYLE_FLEX};padding:10px 16px 0px 16px')

    def update_sn(self, val: e.Connect):
        if val.is_connect:
            self.show_tip(f'{val.id} is connected', color=e.Color.success)
        else:
            self.show_tip(f'{val.id} is disconnected', color=e.Color.error)
        sta = self.get_current_sta()
        pin.pin_update(Pins.sn_select,
                       options=[key for key in self._ws_server.station_dic.keys()], value=sta)
        self.refrash()

    def get_current_sta(self):
        try:
            return pin.pin[Pins.sn_select]
        except Exception as e:
            logging.exception(e)

    def on_control_action(self):
        val = pin.pin_wait_change(
            Pins.control_action, Pins.sn_select, timeout=1)
        if val:
            if val.get('name') == Pins.sn_select:
                self.refrash()
            else:
                cmd = val.get('value')
                if cmd == c.Cmd.clear:
                    self.show_log(None, _clear=True)
                else:
                    sta: s.Station = self._ws_server.station_dic.get(
                        self.get_current_sta())
                    if sta:
                        if cmd == c.Cmd.disconnect:
                            asyncio.run_coroutine_threadsafe(
                                sta._connection.close(), self._ws_server.loop)
                        if cmd == c.Cmd.send:
                            asyncio.run_coroutine_threadsafe(
                                sta.send(pin.pin[Pins.request_textarea]), self._ws_server.loop)
                        else:
                            pass
                    else:
                        self.show_tip('No valid station', e.Color.error)

    def show_event(self, event, only_log: bool = False):
        try:
            sta = self.get_current_sta()
            owner = sta and event.id == sta
            if isinstance(event, e.Log) and owner:
                self.show_log(event.msg)
            else:
                if not only_log:
                    if isinstance(event, e.Connect):
                        self.update_sn(event)
                    else:
                        if owner:
                            if isinstance(event, e.Label):
                                self.show_labels(event.msg, color=event.color)
                            elif isinstance(event, e.Tip):
                                self.show_tip(event.msg, color=event.color,
                                              position=event.position)
                            else:
                                self.show_log(event)
        except exceptions.SessionNotFoundException:
            pass
        except exceptions.SessionClosedException:
            pass
        except Exception as ex:
            logging.exception(ex)

    # @config(theme='dark')
    def main_win(self):
        @session.defer_call
        def clearup():
            self._ws_server.unregister_observer(observer=self)

        # session.register_thread(self._ws_server.thread)
        session.set_env(title=UI_TITLE, output_max_width='100%')
        put_column([put_markdown(f'## {UI_TITLE}',),
                    self.put_csms_url(),
                    put_row([pin.put_textarea(Pins.request_textarea),
                             None,
                             put_scope(Scop.control)], size='89% 1% 10%'),
                    put_scope(Scop.log)
                    ]).style(UI_STYLE_FLEX_COLUMN),
        self.refrash()
        while not session.get_current_session().closed():
            if self._queue.empty():
                self.on_control_action()
            else:
                self.show_event(self._queue.get())


def start(ws_server: WsServer, port=UI_PORT, auto_open=True):
    threading.Thread(target=lambda: start_server(lambda: MainWindow(ws_server).main_win(),
                                                 port, auto_open_webbrowser=auto_open), daemon=True, name='web-server').start()


if __name__ == '__main__':
    pass
