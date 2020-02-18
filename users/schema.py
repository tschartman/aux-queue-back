import graphene
from graphql_jwt.decorators import login_required
from graphene_django.types import DjangoObjectType, ObjectType
from users.models import CustomUser
from django.db.models import Q
from rest_framework.permissions import AllowAny
from rest_framework import permissions

class CustomUserType(DjangoObjectType):
    class Meta:
        model = CustomUser



class Query(ObjectType):
    user = graphene.Field(CustomUserType,)
    users = graphene.List(CustomUserType,)

    def resolve_user(self, info, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            return None
        return user
    
    @login_required
    def resolve_users(self, info, **kwargs):
        return CustomUser.objects.all()

class UserInput(graphene.InputObjectType):
    id = graphene.ID()
    firstName = graphene.String()
    lastName = graphene.String()
    email = graphene.String()


class UpdateUser(graphene.Mutation):
    class Arguments:
        input = UserInput(required=True)

    ok = graphene.Boolean()
    user = graphene.Field(CustomUserType)

    @staticmethod
    def mutate(root, info, id, input=None):
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

class Mutation(graphene.ObjectType):
    update_user = UpdateUser.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)
