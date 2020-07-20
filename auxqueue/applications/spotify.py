from django.http import HttpResponse, HttpRequest, HttpResponseForbidden, JsonResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django import forms
from django.shortcuts import redirect
import requests
import base64
from party.models import Party, Song
import json
from urllib import parse
from django.conf import settings
import time
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

@csrf_exempt
def auth(request):
    return HttpResponseRedirect('https://accounts.spotify.com/authorize?client_id=' + settings.SPOTIFY_CLIENT_ID + '&response_type=code&redirect_uri=' + settings.API_ENDPOINT +'/spotify/code/&scope=playlist-modify-private,playlist-modify-public,user-read-currently-playing,user-read-recently-played,user-read-playback-state,user-top-read')

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
    return HttpResponseRedirect("https://auxqueue.com/link?token=" + token + "&refresh=" + refresh)

# @csrf_exempt
# def refresh(request):
#     token = json.loads(request.body).get('token', '')
#     headers = {'Authorization': "Basic ".encode("utf-8") + base64.b64encode((settings.SPOTIFY_CLIENT_ID + ":" + settings.SPOTIFY_CLIENT_SECRET).encode("utf-8"))}
#     data = {
#         'grant_type': 'refresh_token',
#         'refresh_token': token
#     }

#     response = requests.post('https://accounts.spotify.com/api/token', headers=headers, data = data)
#     return HttpResponse(response)

def refresh(user):
    headers = {'Authorization': "Basic ".encode("utf-8") + base64.b64encode((settings.SPOTIFY_CLIENT_ID + ":" + settings.SPOTIFY_CLIENT_SECRET).encode("utf-8"))}
    data = {
        'grant_type': 'refresh_token',
        'refresh_token': user.refresh_token
    }

    response = requests.post('https://accounts.spotify.com/api/token', headers=headers, data = data)
    token = json.loads(response.text).get('access_token')
    user.access_token = token
    user.save()
    return user

def getCurrentSong(user):
    headers = {'Authorization': "Bearer " + user.access_token}
    response =  requests.get('https://api.spotify.com/v1/me/player/currently-playing', headers=headers)
    if response.status_code == 401:
        updatedUser = refresh(user)
        getCurrentSong(updatedUser)
    elif response.status_code == 200:
        return response.json()
    else:
        return None

def updateSong(user):
    i = 3
    while Party.objects.filter(host=user).count() > 0:
        time.sleep(i)
        logging.info(f"polling spotify {user.user_name}'s party every {i} sec")
        try:
            party = Party.objects.get(host=user)
            playing = getCurrentSong(party.host)
            if(playing != None and playing.get('item') != None):
                playing = playing.get('item')
                try:
                    current_song = Song.objects.get(song_uri = playing.get('uri'))
                    party.currently_playing = current_song
                    party.save()
                except Song.DoesNotExist:
                    current_song = Song(
                        title = playing.get('name'),
                        artist = playing['artists'][0].get('name'),
                        album = playing['album'].get('name'),
                        cover_uri = playing['album']['images'][0].get('url'),
                        song_uri = playing.get('uri'),
                    )
                    current_song.save()
                    party.currently_playing = current_song
                    party.save()
        except Party.DoesNotExist:
            break
