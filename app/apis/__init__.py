from flask import Blueprint

api_blp = Blueprint("api", __name__, url_prefix="/api")

from . import (
    fa
)