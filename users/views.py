from users.serializers import UsersSerializer
from users.models import CustomUser
from rest_framework import viewsets

class UserViewset(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UsersSerializer

    def perform_create(self, serializer):
        serializer.save()