from src.app import App
from src.utils import singleton


@singleton
class FlaskLite:
    app = App()
