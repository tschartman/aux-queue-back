from django.http import HttpResponse, HttpRequest, HttpResponseForbidden, JsonResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django import forms
from django.conf import settings
import requests
import base64
import json

@csrf_exempt
def auth(request):
    username = json.loads(request.body).get('username', '')
    password = json.loads(request.body).get('password', '')
    client_id = settings.APP_CLIENT_ID
    client_secret = settings.APP_CLIENT_SECRET

    data = {
        'grant_type': 'password',
        'username': username,
        'password': password,
        'client_id': client_id,
        'client_secret': client_secret
    }

    response = requests.post(settings.API_ENDPOINT + '/o/token/', data=data)
    if response.status_code == 400:
        return HttpResponse(response, status=401)
    elif response.status_code == 200:
        return HttpResponse(response, status=200)
    else:
        return HttpResponse(response)

@csrf_exempt
def refresh(request):
    token = json.loads(request.body).get('token', '')
    client_id = settings.APP_CLIENT_ID
    client_secret = settings.APP_CLIENT_SECRET

    data = {
        'grant_type': 'refresh_token',
        'refresh_token': token,
        'client_id': client_id,
        'client_secret': client_secret
    }

    response = requests.post(settings.API_ENDPOINT + '/o/token/', data=data)
    return HttpResponse(response)