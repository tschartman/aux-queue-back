import graphene
from party.models import Party, Song
from graphene_django.types import DjangoObjectType, ObjectType
from followers.models import Relationship
from users.models import CustomUser

class PartyType(DjangoObjectType):
    class Meta:
        model = Party

class SongType(DjangoObjectType):
    class Meta:
        model = Song

class Query(ObjectType):
    party = graphene.Field(PartyType,)
    following_parties = graphene.List(PartyType,)

    def resolve_following_parties(self, info, **kwargs):
        user = info.context.user
        following = Relationship.objects.filter(follower=user, status=1).values('following')
        return Party.objects.filter(host__in=following)
    
    def resolve_party(self, info, **kwargs):
        user = info.context.user
        try:
            return Party.objects.get(host=user)
        except Party.DoesNotExist:
            try:
                return Party.objects.get(guests=user)
            except Party.DoesNotExist:
                return None

class JoinPartyInput(graphene.InputObjectType):
    userName = graphene.String()

class SuggestSongInput(graphene.InputObjectType):
    title = graphene.String()
    artist = graphene.String()
    album = graphene.String()
    coverUri = graphene.String()
    songUri = graphene.String()

class CreateParty(graphene.Mutation):
    ok = graphene.Boolean()
    party = graphene.Field(PartyType)

    @staticmethod
    def mutate(root, info, input=None):
        ok = False
        user = info.context.user
        if user:
            try:
                party = Party.objects.get(guests=user)
                party.guests.remove(user)
                party_instance = Party(
                    host = user,
                )
                party_instance.save()
                return CreateParty(ok=True, pary=party_instance)
            except Party.DoesNotExist:
                party_instance = Party(
                    host = user,
                )
                party_instance.save()
                return CreateParty(ok=True, pary=party_instance)
        return CreateParty(ok=ok, pary=None)

class JoinParty(graphene.Mutation):
    class Arguments:
        input = JoinPartyInput(required=True)
    ok = graphene.Boolean()
    party = graphene.Field(PartyType)

    @staticmethod
    def mutate(root, info, input=None):
        ok = False
        user = info.context.user
        try:
            party = Party.objects.get(host=user)
            return JoinParty(ok=ok, party=None)
        except Party.DoesNotExist:
            try:
                party = Party.objects.get(guests=user)
                party.guests.remove(user)
                following = CustomUser.objects.get(user_name=input.userName)
                followingRel = Relationship.objects.get(following=following, follower=user, status=1)
                party_instance = Party.objects.get(host=following)
                if followingRel and party_instance:
                    party_instance.guests.add(user)
                    return JoinParty(ok=True, party=party_instance)
                return JoinParty(ok=ok, party=None)
            except Party.DoesNotExist:
                following = CustomUser.objects.get(user_name=input.userName)
                followingRel = Relationship.objects.get(following=following, follower=user, status=1)
                party_instance = Party.objects.get(host=following)
                if followingRel and party_instance:
                    party_instance.guests.add(user)
                    return JoinParty(ok=True, party=party_instance)
                return JoinParty(ok=ok, party=None)

class SuggestSong(graphene.Mutation):
    class Arguments:
        input = SuggestSongInput(required=True)
    ok = graphene.Boolean()

    @staticmethod
    def mutate(root, info, input=None):
        ok=False
        user = info.context.user
        party = Party.objects.get(guests=user)
        song = {}
        try:
            song = Song.objects.get(song_uri=input.songUri)
        except Song.DoesNotExist:
            song = Song(
                title = input.title,
                artist = input.artist,
                album = input.album,
                cover_uri = input.coverUri,
                song_uri = input.songUri,
                requester = user
            )
            song.save()
        if user and party and song:
            party.queue
            party.queue.add(song)
            return SuggestSong(ok=True)
        return SuggestSong(ok=ok)


class Mutation(graphene.ObjectType):
    create_party = CreateParty.Field()
    join_party = JoinParty.Field()
    suggest_song = SuggestSong.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)