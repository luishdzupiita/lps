from django.http import JsonResponse
from django.shortcuts import redirect
from utils.pyutil import api

# 400 (Bad Request)
# from django.core.exceptions import SuspiciousOperation
# raise SuspiciousOperation
def handler400(request):
    data, status = api(400)
    return JsonResponse(data, status=status)


# 403 (Forbidden)
# from django.core.exceptions import PermissionDenied
# raise PermissionDenied
def handler403(request):
    data, status = api(403)
    return JsonResponse(data, status=status)


# 404 (Not Found)
# from django.http import Http404
# raise Http404
def handler404(request):
    data, status = api(404)
    return JsonResponse(data, status=status)


# 500 (Internal Server Error)
# raise Exception
def handler500(request):
    data, status = api(500)
    return JsonResponse(data, status=status)
