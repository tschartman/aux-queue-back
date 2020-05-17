import graphene
from rx import Observable
from graphene_subscriptions.events import CREATED, DELETED, UPDATED
from graphene_subscriptions.events import SubscriptionEvent
from party.models import Party, SuggestedSong, Rating, Song, Guest
from graphene_django.types import DjangoObjectType, ObjectType
from followers.models import Relationship
from users.models import CustomUser
from auxqueue.applications.spotify import refresh, getCurrentSong
from django.db.models import Q
import json

class PartyType(DjangoObjectType):
    class Meta:
        model = Party

class GuestType(DjangoObjectType):
    class Meta:
        model = Guest

class SuggestedSongType(DjangoObjectType):
    class Meta:
        model = SuggestedSong

class SongType(DjangoObjectType):
    class Meta:
        model = Song

class RatingType(DjangoObjectType):
    class Meta:
        model = Rating

class PartySubscription(graphene.ObjectType):
    party_created = graphene.Field(PartyType)
    party_deleted = graphene.Field(PartyType)
    party_updated = graphene.Field(PartyType, id=graphene.ID())

    def resolve_party_created(root, info):
        return root.filter(
            lambda event:
                event.operation == CREATED and
                isinstance(event.instance, Party)
        ).map(lambda event: event.instance)

    def resolve_party_deleted(root, info):
        return root.filter(
            lambda event:
                event.operation == DELETED and
                isinstance(event.instance, Party)
        ).map(lambda event: event.instance)

    def resolve_party_updated(root, info, id):
        return root.filter(
            lambda event: 
                event.operation == UPDATED and
                isinstance(event.instance, Party)  and
                event.instance.pk == int(id)
        ).map(lambda event: event.instance)

class Query(ObjectType):
    party = graphene.Field(PartyType,)
    parties = graphene.List(PartyType,)
    
    def resolve_parties(self, info, **kwargs):
        user = info.context.user
        following = Relationship.objects.filter(follower=user, status=1).values('following')
        return Party.objects.filter(Q(host__in=following) | Q(host=user))

    def resolve_party(self, info, **kwargs):
        user = info.context.user
        try:
            return Party.objects.get(host=user)
        except Party.DoesNotExist:
            try:
                return Party.objects.get(guests__user=user)
            except Party.DoesNotExist:
                return None

class JoinPartyInput(graphene.InputObjectType):
    userName = graphene.String()

class RemoveFromPartyInput(graphene.InputObjectType):
    id = graphene.ID()

class EditPartyInput(graphene.InputObjectType):
    name = graphene.String()

class SuggestSongInput(graphene.InputObjectType):
    title = graphene.String()
    artist = graphene.String()
    album = graphene.String()
    coverUri = graphene.String()
    songUri = graphene.String()

class UpdateAllowedRequestsInput(graphene.InputObjectType):
    amount = graphene.Int()
    id = graphene.ID()

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
                party = Party.objects.get(guests__user=user)
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
                party = Party.objects.get(guests__user=user)
                guest = party.guests.get(user=user)
                party.guests.remove(guest)
                try:
                    following = CustomUser.objects.get(user_name=input.userName)
                    followingRel = Relationship.objects.get(following=following, follower=user, status=1)
                    party_instance = Party.objects.get(host=following)
                    party_instance.guests.create(user=user)
                    party_instance.save()
                    return JoinParty(ok=True, party=party_instance)
                except (CustomUser.DoesNotExist, Relationship.DoesNotExist, Party.DoesNotExist) as error:
                    return JoinParty(ok=ok, party=None)
            except Party.DoesNotExist:
                try:
                    following = CustomUser.objects.get(user_name=input.userName)
                    followingRel = Relationship.objects.get(following=following, follower=user, status=1)
                    party_instance = Party.objects.get(host=following)
                    party_instance.guests.create(user=user)
                    party_instance.save()
                    return JoinParty(ok=True, party=party_instance)
                except (CustomUser.DoesNotExist, Relationship.DoesNotExist, Party.DoesNotExist) as error:
                    return JoinParty(ok=ok, party=None)


class RemoveFromParty(graphene.Mutation):
    class Arguments:
        input = RemoveFromPartyInput(required=True)
    ok = graphene.Boolean()
    @staticmethod
    def mutate(root, info, input=None):
        ok = False
        user = info.context.user
        try:
            party = Party.objects.get(host=user)
            guest = party.guests.get(id=input.id)
            party.guests.remove(guest)
            party.save()
            return RemoveFromParty(ok=True)
        except (Party.DoesNotExist, Guest.DoesNotExist) as e:
            return RemoveFromParty(ok=ok) 

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
                party = Party.objects.get(guests__user=user)
                guest = party.guests.get(user=user)
                party.guests.remove(guest)
                party.save()
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
            party = Party.objects.get(guests__user=user)
            guest = party.guests.get(user=user)
            if guest.amount_requested >= guest.allowed_requests:
                return SuggestSong(ok=ok)
            try:
                song = Song.objects.get(song_uri=input.songUri)
                party.queue.get(song=song)
                return SuggestSong(ok=ok)
            except (SuggestedSong.DoesNotExist, Song.DoesNotExist) as e:
                try:
                    song = Song.objects.get(song_uri=input.songUri)
                    suggested = SuggestedSong(
                        requester = user,
                        song = song
                    )
                    suggested.save()
                    party.queue.add(suggested)
                    guest.amount_requested += 1
                    party.save()
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
                    guest.amount_requested += 1
                    guest.save()
                    party.save()
                    return SuggestSong(ok=True, suggested=suggested)
        except Party.DoesNotExist:
            return SuggestSong(ok=ok)

class UpdateAllowedRequests(graphene.Mutation):
    class Arguments:
        input = UpdateAllowedRequestsInput(required=True)
    ok = graphene.Boolean()
    guest = graphene.Field(GuestType)
    @staticmethod
    def mutate(root, info, input=None):
        ok=False
        try:
            party = Party.objects.get(guests__id=input.id)
            guest_instance = party.guests.get(id=input.id)
            guest_instance.allowed_requests = input.amount
            guest_instance.save()
            return UpdateAllowedRequests(ok=True, guest=guest_instance)
        except Party.DoesNotExist:
            return UpdateAllowedRequests(ok=ok)

class RateSong(graphene.Mutation):
    class Arguments:
        input = RateSongInput(required=True)
    ok = graphene.Boolean()
    @staticmethod
    def mutate(root, info, input=None):
        ok=False
        user = info.context.user
        try:
            party = Party.objects.get(guests__user=user)
            song = party.queue.get(id=input.id)
            try:
                rating_instance = song.rating.get(user=user)
                rating_instance.like = input.like
                rating_instance.save()
                party.save()
                return RateSong(ok=True)
            except Rating.DoesNotExist:
                song.rating.create(user=user, like=input.like)
                party.save()
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
        party = Party.objects.get(guests__user=user)
        song = party.queue.get(id=input.id)
        try:
            rating_instance = song.rating.get(user=user)
            rating_instance.delete()
            party.save()
            return RemoveRating(ok=True)
        except Rating.DoesNotExist:
            return RemoveRating(ok=False)
            
class RemoveSong(graphene.Mutation):
    class Arguments:
        input = RateSongInput(required=True)
    ok = graphene.Boolean()
    @staticmethod
    def mutate(root, info, input=None):
        ok=False
        user = info.context.user
        try:
            party = Party.objects.get(host=user)
            song = party.queue.get(id=input.id)
            party.queue.remove(song)
            party.save()
            return RemoveSong(ok=True)
        except (Party.DoesNotExist, Song.DoesNotExist) as e:
            return RemoveSong(ok=ok)

class RefreshCurrentSong(graphene.Mutation):
    class Arguments:
        input = JoinPartyInput(required=True)
    ok = graphene.Boolean()
    currentSong = graphene.Field(SongType)
    @staticmethod
    def mutate(root, info, input=None):
        ok=False
        user = info.context.user
        try:
            host = CustomUser.objects.get(user_name=input.userName)
            party = Party.objects.get(host=host)
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
            party.currently_playing = None
            party.save()
            return RefreshCurrentSong(ok=True, currentSong=None)
        except (Party.DoesNotExist, CustomUser.DoesNotExist) as e:
            return RefreshCurrentSong(ok=ok, currentSong=None)


class Mutation(graphene.ObjectType):
    create_party = CreateParty.Field()
    join_party = JoinParty.Field()
    leave_party = LeaveParty.Field()
    remove_from_party = RemoveFromParty.Field()
    shut_down_party = ShutDownParty.Field()
    suggest_song = SuggestSong.Field()
    update_allowed_requests = UpdateAllowedRequests.Field()
    rate_song = RateSong.Field()
    remove_song = RemoveSong.Field()
    remove_rating = RemoveRating.Field()
    refresh_current_song = RefreshCurrentSong.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)