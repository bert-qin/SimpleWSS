from enum import Enum
from dataclasses import dataclass


class Cmd(str, Enum):
    # non ocpp
    clear = "Clear"
    disconnect = "Disconnect"
    send = "Send"