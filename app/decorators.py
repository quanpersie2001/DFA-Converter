from functools import wraps
from flask import request
from app.utils import bad_request, log_err


def json_required(f):
    @wraps(f)
    def deco_func(*args, **kwagrs):
        if not request.json:
            log_err("Request json required.", request.url)
            return bad_request()
        return f(*args, **kwagrs)
    return deco_func
