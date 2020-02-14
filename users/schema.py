import graphene
from graphene_django.types import DjangoObjectType, ObjectType
from users.models import CustomUser, Friendship
from django.db.models import Q

class CustomUserType(DjangoObjectType):
    class Meta:
        model = CustomUser

class FriendshipType(DjangoObjectType):
    class Meta:
        model = Friendship

class Query(ObjectType):
    user = graphene.Field(CustomUserType,)
    friend = graphene.Field(FriendshipType, email=graphene.String())
    users = graphene.List(CustomUserType,)
    friends = graphene.List(FriendshipType,)

    def resolve_user(self, info, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            return None
        return user
    
    def resolve_friend(self, info, **kwargs):
        email = kwargs.get('email')
        user_one = info.context.user
        user_two = CustomUser.objects.get(email=email)
        return Friendship.objects.get(Q(user_one = user_one, user_two = user_two, status = 1) | Q(user_two = user_one, user_one = user_two, status = 1) )

    def resolve_users(self, info, **kwargs):
        return CustomUser.objects.all()

    def resolve_friends(self, info, **kwargs):
        user = info.context.user
        return Friendship.objects.filter(Q(user_one = user) | Q(user_two = user))

class UserInput(graphene.InputObjectType):
    id = graphene.ID()
    firstName = graphene.String()
    lastName = graphene.String()
    email = graphene.String()

class FriendInput(graphene.InputObjectType):
    id = graphene.ID()
    email = graphene.String()
    user_one = graphene.Field(UserInput)
    user_two = graphene.Field(UserInput)
    status = graphene.String()
    permissions = graphene.String()
    actionId = graphene.Int()

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

class AcceptFriendRequest(graphene.Mutation):
    class Arguments:
        input = FriendInput(required=True)
    ok = graphene.Boolean()
    friendship = graphene.Field(FriendshipType)

    @staticmethod
    def mutate(root, info, input=None):
        ok = False
        user_two = info.context.user
        user_one = CustomUser.objects.get(email=input.email)
        friendship_instance = Friendship.objects.get(Q(user_one = user_one, user_two = user_two, status = 0))
        if friendship_instance:
            ok = True
            friendship_instance.status = 1
            friendship_instance.action_user_id = info.context.user.id
            friendship_instance.save()
            return AcceptFriendRequest(ok=ok, friendship=friendship_instance)
        return AcceptFriendRequest(ok=ok, friendship=None)

class UpdateFriendRequest(graphene.Mutation):
    class Arguments:
        input = FriendInput(required=True)
    ok = graphene.Boolean()
    friendship = graphene.Field(FriendshipType)

    @staticmethod
    def mutate(root, info, input=None):
        ok = False
        user_two = info.context.user
        user_one = CustomUser.objects.get(email=input.email)
        friendship_instance = Friendship.objects.get(Q(user_one = user_one, user_two = user_two, status = 1) | Q(user_two = user_one, user_one = user_two, status = 1) )
        if friendship_instance:
            ok = True
            friendship_instance.status = ["pending", "accepted", "declined", "blocked"].index(input.status)
            friendship_instance.action_user_id = info.context.user.id
            friendship_instance.save()
            return AcceptFriendRequest(ok=ok, friendship=friendship_instance)
        return AcceptFriendRequest(ok=ok, friendship=None)

class SendFriendRequest(graphene.Mutation):
    class Arguments:
        input = FriendInput(required=True)
    ok = graphene.Boolean()
    friendship = graphene.Field(FriendshipType)

    @staticmethod
    def mutate(root, info, input=None):
        ok = True
        user_one = info.context.user
        user_two = CustomUser.objects.get(email=input.email)
        if user_one is None or user_two is None:
            return SendFriendRequest(ok=False, friendship=None)
        friendship_instance = Friendship(
            user_one = user_one,
            user_two = user_two,
            action_user_id = info.context.user.id
            )
        friendship_instance.save()
        return SendFriendRequest(ok=ok, friendship=friendship_instance)

class Mutation(graphene.ObjectType):
    send_friend_request = SendFriendRequest.Field()
    accept_friend_request = AcceptFriendRequest.Field()
    update_friend_request = UpdateFriendRequest.Field()
    update_user = UpdateUser.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)
