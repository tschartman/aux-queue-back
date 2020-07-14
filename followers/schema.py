import graphene
from graphql_jwt.decorators import login_required
from graphene_django.types import DjangoObjectType, ObjectType
from graphene_subscriptions.events import CREATED, DELETED, UPDATED
from users.models import CustomUser
from followers.models import Relationship
from django.db.models import Q
from rest_framework.permissions import AllowAny
from rest_framework import permissions

class RelationshipType(DjangoObjectType):
    class Meta:
        model = Relationship

class Subscription(graphene.ObjectType):
    relationship_created = graphene.Field(RelationshipType, userName=graphene.String())
    relationship_deleted = graphene.Field(RelationshipType, id=graphene.ID())
    relationships_deleted = graphene.Field(RelationshipType, userName=graphene.String())
    relationship_updated = graphene.Field(RelationshipType, id=graphene.ID())
    relationships_updated = graphene.Field(RelationshipType, userName=graphene.String())

    def resolve_relationship_created(root, info, userName):
        user = CustomUser.objects.get(user_name=userName)
        return root.filter(
            lambda event:
                event.operation == CREATED and
                isinstance(event.instance, Relationship) and
                (event.instance.follower == user or event.instance.following == user)
        ).map(lambda event: event.instance)
    
    def resolve_relationship_deleted(root, info, id):
        return root.filter(
            lambda event:
                event.operation == DELETED and
                isinstance(event.instance, Relationship) and
                event.instance.pk == int(id)
        ).map(lambda event: event.instance)

    def resolve_relationships_deleted(root, info, userName):
        user = CustomUser.objects.get(user_name=userName)
        return root.filter(
            lambda event:
                event.operation == DELETED and
                isinstance(event.instance, Relationship) and
                (event.instance.follower == user or event.instance.following == user)
        ).map(lambda event: event.instance)

    def resolve_relationship_updated(root, info, id):
        return root.filter(
            lambda event:
                event.operation == UPDATED and
                isinstance(event.instance, Relationship) and
                event.instance.pk == int(id)
        ).map(lambda event: event.instance)

    def resolve_relationships_updated(root, info, userName):
        user = CustomUser.objects.get(user_name=userName)
        return root.filter(
            lambda event:
                event.operation == UPDATED and
                isinstance(event.instance, Relationship) and
                (event.instance.follower == user or event.instance.following == user)
        ).map(lambda event: event.instance)

class Query(ObjectType):
    following = graphene.List(RelationshipType,)
    followers = graphene.List(RelationshipType,)
    follow = graphene.Field(RelationshipType, userName=graphene.String())
    follower = graphene.Field(RelationshipType, userName=graphene.String())

    def resolve_followers(self, info, **kwargs):
        user = info.context.user
        return Relationship.objects.filter(following=user)

    def resolve_following(self, info, **kwargs):
        user = info.context.user
        return Relationship.objects.filter(follower=user)

    def resolve_follow(self, info, **kwargs):
        user = info.context.user
        following = CustomUser.objects.get(user_name=kwargs.get('userName'))
        try:
            follow = Relationship.objects.get(follower=user, following=following)
            return follow
        except Relationship.DoesNotExist:
            return None

    def resolve_follower(self, info, **kwargs):
        user = info.context.user
        follower = CustomUser.objects.get(user_name=kwargs.get('userName'))
        try:
            follower = Relationship.objects.get(following=user, follower=follower)
            return follower
        except Relationship.DoesNotExist:
            return None


class FollowerInput(graphene.InputObjectType):
    id = graphene.ID()
    userName = graphene.String()
    status = graphene.String()


class SendFollowRequest(graphene.Mutation):
    class Arguments:
        input = FollowerInput(required=True)
    ok = graphene.Boolean()
    following = graphene.Field(RelationshipType)

    @staticmethod
    def mutate(root, info, input=None):
        ok = True
        follower = info.context.user
        following = CustomUser.objects.get(user_name=input.userName)
        if follower is None or following is None:
            return SendFollowerRequest(ok=False, Relationship=None)
        Relationship_instance = Relationship(
            follower = follower,
            following = following,
            action_user_id = info.context.user.id
            )
        Relationship_instance.save()
        return SendFollowRequest(ok=ok, following=Relationship_instance)

class UpdateFollowRequest(graphene.Mutation):
    class Arguments:
        input = FollowerInput(required=True)
    ok = graphene.Boolean()
    following = graphene.Field(RelationshipType)

    @staticmethod
    def mutate(root, info, input=None):
        ok = False
        follower = info.context.user
        try:
            Relationship_instance = Relationship.objects.get(id=input.id, follower=follower)
            ok = True
            Relationship_instance.status = ["pending", "accepted", "declined", "blocked"].index(input.status)
            Relationship_instance.action_user_id = info.context.user.id
            Relationship_instance.save()
            return UpdateFollowRequest(ok=ok, following=Relationship_instance)
        except Relationship.DoesNotExist:
            return UpdateFollowRequest(ok=ok, following=None)

class UpdateFollowerRequest(graphene.Mutation):
    class Arguments:
        input = FollowerInput(required=True)
    ok = graphene.Boolean()
    follower = graphene.Field(RelationshipType)

    @staticmethod
    def mutate(root, info, input=None):
        ok = False
        following = info.context.user
        Relationship_instance = Relationship.objects.get(id=input.id, following=following)
        if Relationship_instance:
            ok = True
            Relationship_instance.status = ["pending", "accepted", "declined", "blocked"].index(input.status)
            Relationship_instance.action_user_id = info.context.user.id
            Relationship_instance.save()
            return UpdateFollowerRequest(ok=ok, follower=Relationship_instance)
        return UpdateFollowerRequest(ok=ok, follower=None)

class RemoveFollowRequest(graphene.Mutation):
    class Arguments:
        input = FollowerInput(required=True)
    ok = graphene.Boolean()

    @staticmethod
    def mutate(root, info, input=None):
        ok = False
        follower = info.context.user
        Relationship_instance = Relationship.objects.get(id=input.id, follower=follower)
        if Relationship_instance:
            ok = True
            Relationship_instance.delete()
            return RemoveFollowRequest(ok=ok)
        return RemoveFollowRequest(ok=ok)

class RemoveFollowerRequest(graphene.Mutation):
    class Arguments:
        input = FollowerInput(required=True)
    ok = graphene.Boolean()

    @staticmethod
    def mutate(root, info, input=None):
        ok = False
        following = info.context.user
        Relationship_instance = Relationship.objects.get(id=input.id, following=following)
        if Relationship_instance:
            ok = True
            Relationship_instance.delete()
            return RemoveFollowerRequest(ok=ok)
        return RemoveFollowerRequest(ok=ok)


class Mutation(graphene.ObjectType):
    send_follow_request = SendFollowRequest.Field()
    update_follow_request = UpdateFollowRequest.Field()
    update_follower_request = UpdateFollowerRequest.Field()
    remove_follow_request = RemoveFollowRequest.Field()
    remove_follower_request = RemoveFollowerRequest.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)