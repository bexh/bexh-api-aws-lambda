import json
from src.core import Core


def handler(event, context):
    core = Core()
    return core.run(event, context).serialize()


if __name__ == "__main__":
    with open("event.json") as f:
        test_event = json.load(f)
    handler(test_event, None)
