from src.FlaskLite import FlaskLite
from src.utils import Response

flask = FlaskLite()
app = flask.app


@app.route("/test2", methods=["PUT"])
def test_2():
    print("test 2 path!!")
    return Response(body={"foo": "bar"}, status_code=204)


@app.route("/bexh", methods=["POST"])
def bexh():
    print("bexh path!!")
    return Response(body={"this": "that"}, status_code=204)
