import logging
from src.controllers import *
from src.utils import Request, Response


class Core:
    flask = FlaskLite()

    def __init__(self):
        self.app = flask.app
        self.logger = logging.Logger(name="bexh-api-aws-lambda")

    def run(self, event, context) -> Response:
        try:
            self.logger.info("Begin handling API request")
            self.logger.info("Parsing event")
            request = Request(event)
            self.logger.info("Finding method for path")
            controller = self.app.find_route(request)
            if not controller:
                response = Response(body={"error": "Page not found"}, status_code=404)
                self.logger.info(f"Response: {response.serialize()}")
                return response
            response = controller()
            self.logger.info(f"Response: {response}")
            return response
        except Exception as e:
            self.logger.error("Failed API request", stack_info=True)
            return Response(body={"error": "Internal Server Error"}, status_code=500)
