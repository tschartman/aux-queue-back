from django.db import models
from auxqueue import settings

# Create your models here.

class Relationship(models.Model):
    following = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='following', on_delete=models.CASCADE)
    follower = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='follower', on_delete=models.CASCADE)
    status = models.SmallIntegerField(default=0)
    action_user_id = models.SmallIntegerField(default=0)
    permissions = models.CharField(max_length=300, blank=True, null=True)

    class Meta:
        unique_together = ('following', 'follower')