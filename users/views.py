from users.serializers import UsersSerializer, SpotifyAuthSerializer
from users.models import CustomUser
from rest_framework import viewsets
from users.permissions import IsAuthenticatedOrCreate, IsUser
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

class SpotifyAuthDetail(generics.RetrieveUpdateAPIView):

    queryset = CustomUser.objects.all()
    serializer_class = SpotifyAuthSerializer
    permission_classes = (IsUser,)