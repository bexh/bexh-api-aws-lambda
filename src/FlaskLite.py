from src.App import App


class FlaskLite(object):
    """
    Singleton of FlaskLite which contains an App for the purpose of
    adding methods to the app
    """
    class __FlaskLite:
        def __init__(self):
            self.app = App()

        def __str__(self):
            return repr(self) + self.app
    instance = None

    def __new__(cls): # __new__ always a classmethod
        if not FlaskLite.instance:
            FlaskLite.instance = FlaskLite.__FlaskLite()
        return FlaskLite.instance

    def __getattr__(self, name):
        return getattr(self.instance, name)

    def __setattr__(self, name):
        return setattr(self.instance, name)
