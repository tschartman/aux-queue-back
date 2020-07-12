# your_app/signals.py
from django.db.models.signals import post_save, post_delete
from graphene_subscriptions.signals import post_save_subscription, post_delete_subscription

from followers.models import Relationship

post_save.connect(post_save_subscription, sender=Relationship, dispatch_uid="relationship_post_save")
post_delete.connect(post_delete_subscription, sender=Relationship, dispatch_uid="relationship_post_delete")