import os
from dotenv import load_dotenv

# Load environment variables from .env file
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path)

BASE_DIR = os.path.dirname(os.path.realpath(__file__))

APP_NAME = 'FA to DFA'
APP_SHORTNAME = 'FA to DFA'

SECRET_KEY = os.getenv("SECRET_KEY", "RXhhbWluYXRpb24gVGltZXRhYmxpbmc=")

TEMP_FOLDER = os.getenv("TEMPLATE_FOLDER")

# Flask jsonify settings
JSON_SORT_KEYS = False
JSONIFY_PRETTYPRINT_REGULAR = False
JSONIFY_MIMETYPE = "application/json"