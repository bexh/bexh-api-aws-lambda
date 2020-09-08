from src.utils import Request, Method, Route
import logging


class App:

    logger = logging.Logger(name="bexh-api-aws-lambda")

    def __init__(self):
        self.routes = {}

    def route(self, url_pattern: str, methods: [Method] = None):
        """
        Decorator for route in controllers. Wraps route and adds to route dict
        :param url_pattern: path for method
        :param methods:
        :return: wrapped function
        """
        def wrap(f):
            self.routes[url_pattern] = Route(f, methods)
            return f
        return wrap

    def find_route(self, request: Request):
        """
        Returns function for route if the route exists given the method
        :param request:
        :return: controller function if it exists else None
        """
        if request.path in self.routes.keys():
            route = self.routes[request.path]
            if route.valid_method(request.http_method):
                return route.func
            else:
                self.logger.info("Method does not exist for route")
                return None
        else:
            self.logger.info("Route not found")
            return None
