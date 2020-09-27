from main.src.app import App
from main.src.utils import singleton


@singleton
class FlaskLite:
    app = App()
