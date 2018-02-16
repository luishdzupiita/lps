# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from liveperson_stressor import *
from conversation_stressor import *
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import os

def landing_page(request):
    c = {}
    return render(request, 'index.html', c)

@csrf_exempt
def lps(request):
    if request.method == 'POST':
        if request.POST['instruction'] == 'init':
            ti = abs(int(request.POST['instances']))
            if ti == 0:
                ti = 1
            if request.POST['endpoint'].replace(' ','') != '':
                res = execute_lps(total_instances=ti, base_name=request.POST['base_name'], endpoint=request.POST['endpoint'])
            else:
                res = execute_lps(total_instances=ti, base_name=request.POST['base_name'])
            return JsonResponse(res, safe=False)

@csrf_exempt
def cs(request):
    if request.method == 'POST':
        if request.POST['instruction'] == 'init':
            ti = abs(int(request.POST['instances']))
            if ti == 0:
                ti = 1
            if request.POST['endpoint'].replace(' ','') != '':
                res = execute_cs(total_instances=ti, base_name=request.POST['base_name'], endpoint=request.POST['endpoint'])
            else:
                res = execute_cs(total_instances=ti, base_name=request.POST['base_name'])
            return JsonResponse(res, safe=False)
