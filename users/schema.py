import graphene
import hashlib
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
        fields = ("first_name", "last_name", "user_name", "user_image", "email", "access_token", "refresh_token",)
class CustomUsersType(DjangoObjectType):
    class Meta:
        model = CustomUser
        fields = ("first_name", "last_name", "user_name", "user_image", "email", "access_token", "refresh_token",)

class Query(ObjectType):
    user = graphene.Field(CustomUserType,)
    users = graphene.List(CustomUsersType,)
    userName = graphene.String()

    def resolve_user(self, info, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            return None
        return user
    
    @login_required
    def resolve_users(self, info, **kwargs):
        return CustomUser.objects.all()

    def resolve_userName(self, info, **kwargs):
        userName = Generator.generate_username() 
        return userName


class UserInput(graphene.InputObjectType):
    firstName = graphene.String()
    lastName = graphene.String()
    email = graphene.String()

class UserCreationInput(graphene.InputObjectType):
    firstName = graphene.String()
    lastName = graphene.String()
    email = graphene.String()
    password = graphene.String()

class CheckUsernameInput(graphene.InputObjectType):
    userName = graphene.String()

class ChangePasswordInput(graphene.InputObjectType):
    oldPass = graphene.String()
    newPass = graphene.String()

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
        url = 'https://secure.gravatar.com/avatar'
        email_hash = hashlib.md5(input.email.encode('utf-8')).hexdigest()
        user_instance = CustomUser(
            first_name = input.firstName,
            last_name = input.lastName,
            email = input.email,
            user_name = Generator.generate_username(),
            user_image = '{url}/{hash}'.format(url=url, hash=email_hash)
        )
        user_instance.set_password(input.password)
        user_instance.save()
        return CreateUser(ok=ok, user=user_instance)

class CheckUserName(graphene.Mutation):
    class Arguments:
        input = CheckUsernameInput(required=True)

    ok = graphene.Boolean()

    @staticmethod
    def mutate(root, info, input=None):
        users = CustomUser.objects.filter(user_name=input.userName)
        if len(users) == 0:
            return CheckUserName(ok=True)
        return CheckUserName(ok = False)

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
            user_instance.email = input.email
            user_instance.save()
            return UpdateUser(ok=ok, user=user_instance)
        return UpdateUser(ok=ok, user=None)

class UpdateUserName(graphene.Mutation):
    class Arguments:
        input = CheckUsernameInput(required=True)
    ok = graphene.Boolean()
    userName = graphene.String()

    @staticmethod
    def mutate(root, info, input=None):
        ok = False
        unique = (len(CustomUser.objects.filter(user_name=input.userName)) == 0)
        user_instance = info.context.user
        if user_instance and unique:
            print(user_instance.user_name)
            ok = True
            user_instance.user_name = input.userName
            user_instance.save()
            return UpdateUserName(ok=ok, userName=user_instance.user_name)
        return UpdateUserName(ok=ok, userName=None)

class UpdatePassword(graphene.Mutation):
    class Arguments:
        input = ChangePasswordInput(required=True)
    ok = graphene.Boolean()
    error = graphene.String()
    @staticmethod
    def mutate(root, info, input=None):
        ok = False
        user_instance = info.context.user
        if user_instance:
            if user_instance.check_password(input.oldPass):
                user_instance.set_password(input.newPass)
                user_instance.save()
                return UpdatePassword(ok=True, error=None)
            return UpdatePassword(ok=False, error="Old Password Incorrect")
        return UpdatePassword(ok=False, error="Error Updating Password")

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
    update_user_name = UpdateUserName.Field()
    update_password = UpdatePassword.Field()
    update_tokens = UpdateTokens.Field()
    check_user_name = CheckUserName.Field()
    refresh_tokens = RefreshTokens.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)
