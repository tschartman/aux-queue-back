# your_app/signals.py
from django.db.models.signals import post_save, post_delete
from graphene_subscriptions.signals import post_save_subscription, post_delete_subscription

from party.models import Party

post_save.connect(post_save_subscription, sender=Party, dispatch_uid="party_post_save")
post_delete.connect(post_delete_subscription, sender=Party, dispatch_uid="party_post_delete")