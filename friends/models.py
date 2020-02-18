from django.db import models
from auxqueue import settings

# Create your models here.

class Friendship(models.Model):
    user_one = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='user_one', on_delete=models.CASCADE)
    user_two = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='user_two', on_delete=models.CASCADE)
    status = models.SmallIntegerField(default=0)
    action_user_id = models.SmallIntegerField(default=0)
    permissions = models.CharField(max_length=300, blank=True, null=True)
    
    class Meta:
        unique_together = ('user_one', 'user_two',)

