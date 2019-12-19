from django.http import HttpResponse, HttpRequest, HttpResponseForbidden, JsonResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django import forms
from django.conf import settings
import requests
import json

@csrf_exempt
def auth(request):
    username = json.loads(request.body).get('email', '')
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

    response = requests.post('http://localhost:8000/o/token/', data=data)
    return HttpResponse(response)