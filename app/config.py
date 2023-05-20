import os

BASE_DIR = os.path.dirname(os.path.realpath(__file__))

APP_NAME = 'FA to DFA'
APP_SHORTNAME = 'FA to DFA'

SECRET_KEY = os.environ.get("SECRET_KEY", "RXhhbWluYXRpb24gVGltZXRhYmxpbmc=")

TEMP_FOLDER = os.environ.get("TEMPLATE_FOLDER")

# Flask jsonify settings
JSON_SORT_KEYS = False
JSONIFY_PRETTYPRINT_REGULAR = False
JSONIFY_MIMETYPE = "application/json"