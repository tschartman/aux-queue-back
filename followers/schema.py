import graphene
from graphql_jwt.decorators import login_required
from graphene_django.types import DjangoObjectType, ObjectType
from users.models import CustomUser
from followers.models import Relationship
from django.db.models import Q
from rest_framework.permissions import AllowAny
from rest_framework import permissions


class RelationshipType(DjangoObjectType):
    class Meta:
        model = Relationship

class Query(ObjectType):
    following = graphene.List(RelationshipType,)
    followers = graphene.List(RelationshipType,)

    def resolve_followers(self, info, **kwargs):
        user = info.context.user
        return Relationship.objects.filter(following=user)

    def resolve_following(self, info, **kwargs):
        user = info.context.user
        return Relationship.objects.filter(follower=user)


class FollowerUserInput(graphene.InputObjectType):
    userName = graphene.String()
    email = graphene.String()
    firstName = graphene.String()
    lastName = graphene.String()
    accessToken = graphene.String()
    refreshToken = graphene.String()

class FollowerInput(graphene.InputObjectType):
    id = graphene.ID()
    userName = graphene.String()
    user_one = graphene.Field(FollowerUserInput)
    user_two = graphene.Field(FollowerUserInput)
    status = graphene.String()
    permissions = graphene.String()
    actionId = graphene.Int()


class SendFollowRequest(graphene.Mutation):
    class Arguments:
        input = FollowerInput(required=True)
    ok = graphene.Boolean()
    Relationship = graphene.Field(RelationshipType)

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
        return SendFollowRequest(ok=ok, Relationship=Relationship_instance)

class UpdateFollowRequest(graphene.Mutation):
    class Arguments:
        input = FollowerInput(required=True)
    ok = graphene.Boolean()
    Relationship = graphene.Field(RelationshipType)

    @staticmethod
    def mutate(root, info, input=None):
        ok = False
        following = info.context.user
        follower = CustomUser.objects.get(user_name=input.userName)
        Relationship_instance = Relationship.objects.get(following=following, follower=follower, status = 0)
        if Relationship_instance:
            ok = True
            Relationship_instance.status = ["pending", "accepted", "declined", "blocked"].index(input.status)
            Relationship_instance.action_user_id = info.context.user.id
            Relationship_instance.save()
            return UpdateFollowRequest(ok=ok, Relationship=Relationship_instance)
        return UpdateFollowerRequest(ok=ok, Relationship=None)

class RemoveFollowRequest(graphene.Mutation):
    class Arguments:
        input = FollowerInput(required=True)
    ok = graphene.Boolean()

    @staticmethod
    def mutate(root, info, input=None):
        ok = False
        follower = info.context.user
        following = CustomUser.objects.get(user_name=input.userName)
        Relationship_instance = Relationship.objects.get(Q(follower = follower, following = following, status = 1))
        if Relationship_instance:
            ok = True
            Relationship_instance.delete()
            return AcceptFollowerRequest(ok=ok)
        return AcceptFollowerRequest(ok=ok)

class RevokeFollowerRequest(graphene.Mutation):
    class Arguments:
        input = FollowerInput(required=True)
    ok = graphene.Boolean()

    @staticmethod
    def mutate(root, info, input=None):
        ok = False
        following = info.context.user
        follower = CustomUser.objects.get(user_name=input.userName)
        Relationship_instance = Relationship.objects.get(Q(follower = follower, following = following, status = 1))
        if Relationship_instance:
            ok = True
            Relationship_instance.delete()
            return AcceptFollowerRequest(ok=ok)
        return AcceptFollowerRequest(ok=ok)


class Mutation(graphene.ObjectType):
    send_follow_request = SendFollowRequest.Field()
    update_follow_request = UpdateFollowRequest.Field()
    remove_follow_request = RemoveFollowRequest.Field()
    revoke_follower_request = RevokeFollowerRequest.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)