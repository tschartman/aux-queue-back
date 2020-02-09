from users.serializers import UsersSerializer, SpotifyAuthSerializer, FreindSerializer
from users.models import CustomUser, Friend
from rest_framework import viewsets
from users.permissions import IsAuthenticatedOrCreate, IsUser, IsRelation
from rest_framework import generics

class UserViewset(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UsersSerializer
    permission_classes = (IsAuthenticatedOrCreate, IsUser)

    def get_queryset(self):
        queryset = self.queryset
        query_set = queryset.filter(email=self.request.user.email)
        return query_set

    def perform_create(self, serializer):
        serializer.save()


class SpotifyAuthDetail(generics.RetrieveUpdateDestroyAPIView):

    queryset = CustomUser.objects.all()
    serializer_class = SpotifyAuthSerializer
    permission_classes = (IsUser,)

class FreindViewSet(viewsets.ModelViewSet):
    query_set = Item.objects.all()
    serializer_class = FreindSerializer
    permission_classes = [permissions.IsRelation]

    def get_queryset(self):
        queryset = self.queryset
        return query_set

    @action(detail=True, renderer_classes=[renderers.StaticHTMLRenderer])
    def perform_create(self, serializer):
        serializer.save(friend_one=self.request.user)
