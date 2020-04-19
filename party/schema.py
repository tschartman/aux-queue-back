import graphene
from party.models import Party, SuggestedSong, Rating, Song
from graphene_django.types import DjangoObjectType, ObjectType
from followers.models import Relationship
from users.models import CustomUser
from auxqueue.applications.spotify import refresh, getCurrentSong

class PartyType(DjangoObjectType):
    class Meta:
        model = Party

class SuggestedSongType(DjangoObjectType):
    class Meta:
        model = SuggestedSong

class SongType(DjangoObjectType):
    class Meta:
        model = Song

class RatingType(DjangoObjectType):
    class Meta:
        model = Rating

class Query(ObjectType):
    party = graphene.Field(PartyType,)
    parties = graphene.List(PartyType,)
    
    def resolve_parties(self, info, **kwargs):
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

class EditPartyInput(graphene.InputObjectType):
    name = graphene.String()

class SuggestSongInput(graphene.InputObjectType):
    title = graphene.String()
    artist = graphene.String()
    album = graphene.String()
    coverUri = graphene.String()
    songUri = graphene.String()

class RateSongInput(graphene.InputObjectType):
    like = graphene.Boolean()
    id = graphene.ID()

class CreateParty(graphene.Mutation):
    ok = graphene.Boolean()
    party = graphene.Field(PartyType)

    @staticmethod
    def mutate(root, info, input=None):
        ok = False
        user = info.context.user
        try:
            party = Party.objects.get(host=user)
            return CreateParty(ok=ok, party=None)
        except Party.DoesNotExist:
            try:
                party = Party.objects.get(guests=user)
                party.guests.remove(user)
                party_instance = Party(host = user)
                party_instance.save()
                return CreateParty(ok=True, party=party_instance)
            except Party.DoesNotExist:
                party_instance = Party(host = user)
                party_instance.save()
                return CreateParty(ok=True, party=party_instance)

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
                try:
                    following = CustomUser.objects.get(user_name=input.userName)
                    followingRel = Relationship.objects.get(following=following, follower=user, status=1)
                    party_instance = Party.objects.get(host=following)
                    party_instance.guests.add(user)
                    return JoinParty(ok=True, party=party_instance)
                except (CustomUser.DoesNotExist, Relationship.DoesNotExist, Party.DoesNotExist) as error:
                    return JoinParty(ok=ok, party=None)
            except Party.DoesNotExist:
                try:
                    following = CustomUser.objects.get(user_name=input.userName)
                    followingRel = Relationship.objects.get(following=following, follower=user, status=1)
                    party_instance = Party.objects.get(host=following)
                    party_instance.guests.add(user)
                    return JoinParty(ok=True, party=party_instance)
                except (CustomUser.DoesNotExist, Relationship.DoesNotExist, Party.DoesNotExist) as error:
                    return JoinParty(ok=ok, party=None)

class LeaveParty(graphene.Mutation):
    ok = graphene.Boolean()
    @staticmethod
    def mutate(root, info, input=None):
        ok = False
        user = info.context.user
        try:
            party = Party.objects.get(host=user)
            return LeaveParty(ok=ok)
        except Party.DoesNotExist:
            try:
                party = Party.objects.get(guests=user)
                party.guests.remove(user)
                return LeaveParty(ok=True)
            except Party.DoesNotExist:
                return LeaveParty(ok=ok)

class ShutDownParty(graphene.Mutation):
    ok = graphene.Boolean()
    @staticmethod
    def mutate(root, info, input=None):
        ok = False
        user = info.context.user
        try:
            party = Party.objects.get(host=user)
            party.delete()
            return ShutDownParty(ok=True)
        except Party.DoesNotExist:
            return ShutDownParty(ok=ok)

class SuggestSong(graphene.Mutation):
    class Arguments:
        input = SuggestSongInput(required=True)
    ok = graphene.Boolean()
    suggested = graphene.Field(SuggestedSongType)

    @staticmethod
    def mutate(root, info, input=None):
        ok=False
        user = info.context.user
        try:
            party = Party.objects.get(guests=user)
            try:
                song = Song.objects.get(song_uri=input.songUri)
                party.queue.get(song=song)
                return SuggestSong(ok=False)
            except (SuggestedSong.DoesNotExist, Song.DoesNotExist) as e:
                try:
                    song = Song.objects.get(song_uri=input.songUri)
                    suggested = SuggestedSong(
                        requester = user,
                        song = song
                    )
                    suggested.save()
                    party.queue.add(suggested)
                    return SuggestSong(ok=True, suggested=suggested)
                except Song.DoesNotExist:
                    song = Song(
                        title = input.title,
                        artist = input.artist,
                        album = input.album,
                        cover_uri = input.coverUri,
                        song_uri = input.songUri,
                    )
                    song.save()
                    suggested = SuggestedSong(
                        requester = user,
                        song = song
                    )
                    suggested.save()
                    party.queue.add(suggested)
                    return SuggestSong(ok=True, suggested=suggested)
        except Party.DoesNotExist:
            return SuggestSong(ok=ok)
            
class RateSong(graphene.Mutation):
    class Arguments:
        input = RateSongInput(required=True)
    ok = graphene.Boolean()
    @staticmethod
    def mutate(root, info, input=None):
        ok=False
        user = info.context.user
        try:
            party = Party.objects.get(guests=user)
            song = party.queue.get(id=input.id)
            try:
                rating_instance = song.rating.get(user=user)
                rating_instance.like = input.like
                rating_instance.save()
                return RateSong(ok=True)
            except Rating.DoesNotExist:
                song.rating.create(user=user, like=input.like)
                return RateSong(ok=True)
        except (Party.DoesNotExist, Song.DoesNotExist) as e:
            return RateSong(ok=ok)

class RemoveRating(graphene.Mutation):
    class Arguments:
        input = RateSongInput(required=True)
    ok = graphene.Boolean()
    @staticmethod
    def mutate(root, info, input=None):
        ok=False
        user = info.context.user
        party = Party.objects.get(guests=user)
        song = party.queue.get(id=input.id)
        try:
            rating_instance = song.rating.get(user=user)
            rating_instance.delete()
            return RemoveRating(ok=True)
        except Rating.DoesNotExist:
            return RemoveRating(ok=False)
            
class RefreshCurrentSong(graphene.Mutation):
    ok = graphene.Boolean()
    currentSong = graphene.Field(SongType)
    @staticmethod
    def mutate(root, info, input=None):
        ok=False
        user = info.context.user
        try:
            party = Party.objects.get(host=user)
            playing = getCurrentSong(party.host)
            if(playing != None and playing.get('item') != None):
                playing = playing.get('item')
                try:
                    current_song = Song.objects.get(song_uri = playing.get('uri'))
                    party.currently_playing = current_song
                    party.save()
                    return RefreshCurrentSong(ok=True, currentSong=current_song)
                except Song.DoesNotExist:
                    current_song = Song(
                        title = playing.get('name'),
                        artist = playing['artists'][0].get('name'),
                        album = playing['album'].get('name'),
                        cover_uri = playing['album']['images'][0].get('url'),
                        song_uri = playing.get('uri'),
                    )
                    current_song.save()
                    party.currently_playing = current_song
                    party.save()
                    return RefreshCurrentSong(ok=True, currentSong=current_song)
            return RefreshCurrentSong(ok=True, currentSong=None)
        except Party.DoesNotExist:
            return RefreshCurrentSong(ok=ok, currentSong=None)


class Mutation(graphene.ObjectType):
    create_party = CreateParty.Field()
    join_party = JoinParty.Field()
    leave_party = LeaveParty.Field()
    shut_down_party = ShutDownParty.Field()
    suggest_song = SuggestSong.Field()
    rate_song = RateSong.Field()
    remove_rating = RemoveRating.Field()
    refresh_current_song = RefreshCurrentSong.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)