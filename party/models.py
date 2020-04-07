from django.db import models
from auxqueue import settings

class Rating(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='user', on_delete=models.CASCADE)
    like = models.BooleanField(blank=False, null=False)

class Song(models.Model):
    title = models.CharField(max_length=30)
    artist = models.CharField(max_length=30)
    album = models.CharField(max_length=30)
    cover_uri = models.CharField(max_length=300)
    song_uri = models.CharField(max_length=300)
    requester = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='requester', on_delete=models.CASCADE)
    rating = models.ManyToManyField(Rating)

class Party(models.Model):
    name = models.CharField(max_length=30, blank=True, null=True)
    cover_uri = models.CharField(max_length=300, blank=True, null=True)
    host = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='host', on_delete=models.CASCADE)
    guests = models.ManyToManyField(settings.AUTH_USER_MODEL)
    queue = models.ManyToManyField(Song)
