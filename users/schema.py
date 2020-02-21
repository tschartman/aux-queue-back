import graphene
from graphql_jwt.decorators import login_required
from graphene_django.types import DjangoObjectType, ObjectType
from users.models import CustomUser
from django.db.models import Q
from rest_framework.permissions import AllowAny
from rest_framework import permissions
from auxqueue.applications.username_generator import Generator
from auxqueue.applications.spotify import SpotfyMiddleware

class CustomUserType(DjangoObjectType):
    class Meta:
        model = CustomUser
        fields = ("first_name", "last_name", "user_name", "email", "access_token", "refresh_token",)
class CustomUsersType(DjangoObjectType):
    class Meta:
        model = CustomUser
        fields = ("user_name",)

class Query(ObjectType):
    user = graphene.Field(CustomUserType,)
    users = graphene.List(CustomUsersType,)

    def resolve_user(self, info, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            return None
        return user
    
    @login_required
    def resolve_users(self, info, **kwargs):
        return CustomUser.objects.all()

class UserInput(graphene.InputObjectType):
    firstName = graphene.String()
    lastName = graphene.String()
    userName = graphene.String()

class UserCreationInput(graphene.InputObjectType):
    firstName = graphene.String()
    lastName = graphene.String()
    email = graphene.String()

class TokenInput(graphene.InputObjectType):
    accessToken = graphene.String()
    refreshToken = graphene.String()

class CreateUser(graphene.Mutation):
    class Arguments:
        input = UserCreationInput(required=True)
    
    ok = graphene.Boolean()
    user = graphene.Field(CustomUserType)
    userName = graphene.String()
    @staticmethod
    def mutate(root, info, input=None):
        ok = True
        user_instance = CustomUser(
            first_name = input.firstName,
            last_name = input.lastName,
            email = input.email,
            user_name = Generator.generate_username()
        )
        user_instance.save()
        return CreateUser(ok=ok, user=user_instance)

class UpdateUser(graphene.Mutation):
    class Arguments:
        input = UserInput(required=True)

    ok = graphene.Boolean()
    user = graphene.Field(CustomUserType)

    @staticmethod
    def mutate(root, info, input=None):
        ok = False
        user_instance = info.context.user
        if user_instance:
            ok = True
            user_instance.first_name = input.firstName
            user_instance.last_name = input.lastName
            user_instance.user_name = input.userName
            user_instance.save()
            return UpdateUser(ok=ok, user=user_instance)
        return UpdateUser(ok=ok, user=None)

class UpdateTokens(graphene.Mutation):
    class Arguments:
        input = TokenInput(required=True)

    ok = graphene.Boolean()
    user = graphene.Field(CustomUserType)

    @staticmethod
    def mutate(root, info, input=None):
        ok = False
        user_instance = info.context.user
        if user_instance:
            ok = True
            user_instance.access_token = input.accessToken
            user_instance.refresh_token = input.refreshToken
            user_instance.save()
            return UpdateTokens(ok=ok, user=user_instance)
        return UpdateTokens(ok=ok, user=None)

class RefreshTokens(graphene.Mutation):
    ok = graphene.Boolean()
    user = graphene.Field(CustomUserType)
    @staticmethod
    def mutate(root, info):
        ok = False
        user_instance = info.context.user
        if user_instance:
            ok = True
            token = SpotfyMiddleware.refresh(user_instance.refresh_token)
            user_instance.access_token = token
            user_instance.save()
            return RefreshTokens(ok=ok, user=user_instance)
        return RefreshTokens(ok=ok, user=None)
            


class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field()
    update_user = UpdateUser.Field()
    update_tokens = UpdateTokens.Field()
    refresh_tokens = RefreshTokens.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)
