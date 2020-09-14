import json
from main.src.core import Core


def handler(event, context):
    print("Starting...")
    core = Core()
    return core.run(event, context).serialize()


if __name__ == "__main__":
    with open("main/test/resources/event.json") as f:
        test_event = json.load(f)
    handler(test_event, None)
