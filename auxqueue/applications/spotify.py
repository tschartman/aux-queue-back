from django.http import HttpResponse, HttpRequest, HttpResponseForbidden, JsonResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django import forms
from django.shortcuts import redirect
import requests
import base64
import json
from urllib import parse
from django.conf import settings

@csrf_exempt
def auth(request):
    return HttpResponseRedirect('https://accounts.spotify.com/authorize?client_id=420e781f275641c39c09ee6ca9f94275&response_type=code&redirect_uri=' + settings.API_ENDPOINT +'/spotify/code/&scope=playlist-modify-private,playlist-modify-public,user-read-currently-playing')

def code(request):
    code = request.GET.get('code', '')
    headers = {'Authorization': "Basic ".encode("utf-8") + base64.b64encode((settings.SPOTIFY_CLIENT_ID + ":" + settings.SPOTIFY_CLIENT_SECRET).encode("utf-8"))}
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': settings.API_ENDPOINT + '/spotify/code/'
    }
    response = requests.post('https://accounts.spotify.com/api/token', headers=headers, data=data)
    token = json.loads(response.text).get('access_token', '')
    refresh = json.loads(response.text).get('refresh_token', '')
    return HttpResponseRedirect("auxqueue.com/link?token=" + token + "&refresh=" + refresh)

@csrf_exempt
def refresh(request):
    token = json.loads(request.body).get('token', '')
    headers = {'Authorization': "Basic ".encode("utf-8") + base64.b64encode((settings.SPOTIFY_CLIENT_ID + ":" + settings.SPOTIFY_CLIENT_SECRET).encode("utf-8"))}
    data = {
        'grant_type': 'refresh_token',
        'refresh_token': token
    }

    response = requests.post('https://accounts.spotify.com/api/token', headers=headers, data = data)
    return HttpResponse(response)