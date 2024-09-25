import pystray
import webbrowser
from PIL import Image
from drive.ui import UI_TITLE, UI_LOCAL_URL
from myico.icon import Icon
import base64
from io import BytesIO


def on_exit(icon, item):
    icon.stop()


def on_open_monitor(icon, item):
    webbrowser.open(UI_LOCAL_URL)


def start():
    image = Image.open(BytesIO(base64.b64decode(Icon().img)))
    menu = (
        pystray.MenuItem("Exit", on_exit),
        pystray.MenuItem("Open Monitor", on_open_monitor),
    )
    icon = pystray.Icon(UI_TITLE, image, UI_TITLE, menu)
    icon.run()


if __name__ == '__main__':
    start()
