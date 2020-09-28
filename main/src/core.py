from main.src.controllers import *
from main.src.utils import Request, Response
from main.src.logger import LoggerFactory
import os
from datetime import datetime, timezone


class Core:

    def __init__(self):
        self.flask = FlaskLite()
        self.app = self.flask.app
        log_level = os.environ.get("LOG_LEVEL", None)
        self.logger = LoggerFactory().get_logger(__name__, log_level)

    def run(self, event, context) -> Response:
        def run_route():
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
                response = controller(request)
                self.logger.info(f"Response: {response}")
                return response
            except Exception as e:
                self.logger.error(f"Failed API request: {e}")
                return Response(body={"error": "Internal Server Error"}, status_code=500)

        start_time = datetime.now(timezone.utc)
        to_return = run_route()
        end_time = datetime.now(timezone.utc)
        duration = (end_time - start_time).total_seconds()
        self.logger.info(f"Duration: {duration}")
        return to_return
