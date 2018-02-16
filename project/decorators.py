from functools import wraps
from django.http import JsonResponse
from utils.pyutil import api


# from django.views.decorators.http import require_http_methods
# /usr/lib/python3.6/site-packages/django/views/decorators/http.py
# @require_http_methods(["GET", "POST"])
def require_methods(methods):
    def decorator(f):
        @wraps(f)
        def wrapper(request, *args, **kwargs):
            if request.method not in methods:
                data, status = api(405)
                return JsonResponse(data, status=status)
            return f(request, *args, **kwargs)
        return wrapper
    return decorator

require_get = require_methods(['GET'])
require_post = require_methods(['POST'])


def require_fmts(fmts):
    def decorator(f):
        @wraps(f)
        def wrapper(request, *args, **kwargs):
            for k, v in kwargs.items():
                if k == 'fmt' and v not in fmts:
                    data, status = api(501)
                    return JsonResponse(data, status=status)
            return f(request, *args, **kwargs)
        return wrapper
    return decorator

require_html = require_fmts(['.html'])
require_json = require_fmts(['.json', ''])
