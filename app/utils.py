import json
import logging
import base64
import decimal
from datetime import datetime, date

from flask import current_app, request

# extend the json.JSONEncoder class, custom JSONEncoder
class JSONEncoder(json.JSONEncoder):
    # overload method default
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        if isinstance(obj, set):
            return list(obj)
        # Call the default method for other types
        return super(JSONEncoder, self).default(obj)

def jsonify(*args, **kwargs):
    indent = None
    separators = (',', ':')

    if current_app.config['JSONIFY_PRETTYPRINT_REGULAR'] and not request.is_xhr:
        indent = 2
        separators = (', ', ': ')

    if args and kwargs:
        raise TypeError('jsonify() behavior undefined when passed both args and kwargs')
    elif len(args) == 1:  # single args are passed directly to dumps()
        data = args[0]
    else:
        data = args or kwargs

    return current_app.response_class(
        (json.dumps(data, indent=indent, separators=separators, cls=JSONEncoder), '\n'),
        mimetype=current_app.config['JSONIFY_MIMETYPE']
    )

def bad_request(message="Invalid request."):
    return jsonify(status=False, message=message)

def response(data=None, status=True):
    return jsonify(status=status, data=data)

def log_err(message="", *args):
    logging.error(f"{request.path}: {message}")
