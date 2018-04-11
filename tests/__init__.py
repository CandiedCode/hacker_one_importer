import json
import os

_BASE_PATH = os.path.dirname(os.path.realpath(__file__))
_RESOURCES_PATH = os.path.join(_BASE_PATH, "resources")


def load_resource_blob(resource_type):
    resource_path = os.path.join(_RESOURCES_PATH, "%s.json" % resource_type)
    with open(resource_path, "r") as f:
        return json.load(f)