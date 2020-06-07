# your_app/signals.py
from django.db.models.signals import post_save, post_delete
from graphene_subscriptions.signals import post_save_subscription, post_delete_subscription

from party.models import Party, Song, Rating

post_save.connect(post_save_subscription, sender=Party, dispatch_uid="party_post_save")
post_save.connect(post_save_subscription, sender=Song, dispatch_uid="song_post_save")
post_save.connect(post_save_subscription, sender=Rating, dispatch_uid="rating_post_save")
post_delete.connect(post_delete_subscription, sender=Party, dispatch_uid="party_post_delete")