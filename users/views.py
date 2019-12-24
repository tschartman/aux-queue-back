from users.serializers import UsersSerializer, SpotifyAuthSerializer
from users.models import CustomUser
from rest_framework import viewsets
from users.permissions import IsAuthenticated, IsUser
from rest_framework import generics
from rest_auth.registration.views import RegisterView

class CustomRegisterView(RegisterView):
    queryset = CustomUser.objects.all()

class UserViewset(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UsersSerializer
    permission_classes = (IsAuthenticated, IsUser)

    def get_queryset(self):
        queryset = self.queryset
        query_set = queryset.filter(email=self.request.user.email)
        return query_set

class SpotifyAuthDetail(generics.RetrieveUpdateAPIView):

    queryset = CustomUser.objects.all()
    serializer_class = SpotifyAuthSerializer
    permission_classes = (IsUser,)
