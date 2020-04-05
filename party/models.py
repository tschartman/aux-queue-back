from django.db import models
from auxqueue import settings

# Create your models here.
class Song(models.Model):
    title = models.CharField(max_length=30)
    artist = models.CharField(max_length=30)
    album = models.CharField(max_length=30)
    cover_uri = models.CharField(max_length=300)
    song_uri = models.CharField(max_length=300)
    requester = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='requester', on_delete=models.CASCADE)
    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)

class Party(models.Model):
    host = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='host', on_delete=models.CASCADE)
    guests = models.ManyToManyField(settings.AUTH_USER_MODEL)
    queue = models.ManyToManyField(Song)