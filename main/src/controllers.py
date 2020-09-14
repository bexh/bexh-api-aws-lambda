from main.src.flask_lite import FlaskLite
from main.src.utils import Response, Request
from main.src.db import login_required, MySql
import logging

flask = FlaskLite()
app = flask.app


@app.route("/test2", methods=["PUT"])
def test_2(request: Request):
    logger = logging.getLogger()
    logger.info("another info message")
    return Response(body={"foo": "bar"}, status_code=204)


@app.route("/bexh", methods=["POST"])
@login_required
def bexh(request: Request):
    logger = logging.getLogger()
    logger.info("info message")
    logger.warning("warning message")
    logger.error("error message")

    db = MySql()
    try:
        foo = db.execute("""
            INSERT INTO BETS \
            (`BET_ID`, `TYPE`, `ODD1S`, `AMOUNT`, `EVENT`, `FRIEND`) \
            VALUES (%s, %s, %s, %s, %s, %s)
        """ % (4, "\"market\"", 1, 5, "\"pistons vs bulls\"", "\"eris\""))
        print(foo)
    except Exception as e:
        return Response(body={"error": "internal server error"}, status_code=500)

    try:
        results = db.fetch("SELECT * FROM BETS")
        print("results", results)
    except Exception as e:
        return Response(body={"error": "internal server error"}, status_code=500)

    return Response(body={"this": "that"}, status_code=204)
