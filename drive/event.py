from enum import Enum
from dataclasses import dataclass


class Color(str, Enum):
    info = 'info'
    success = 'success'
    warn = 'warn'
    error = 'error'
    primary = 'primary'
    secondary = 'secondary'
    danger = 'danger'
    warning = 'warning'
    light = 'light'
    dark = 'dark'


class Result(str, Enum):
    OK = 'Success!'
    NG = 'Failure!'


@dataclass
class Log:
    id: str
    msg: str


@dataclass
class Label:
    id: str
    msg: str
    color: Color = Color.info


@dataclass
class Tip:
    id: str
    msg: str
    color: Color = Color.info
    position: str = 'right'


@dataclass
class Connect:
    id: str
    is_connect: bool
