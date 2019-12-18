from users.serializers import UsersSerializer
from users.models import CustomUser
from rest_framework import viewsets
from users.permissions import IsAuthenticatedOrCreate

class UserViewset(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UsersSerializer
    permission_classes = (IsAuthenticatedOrCreate,)

    def perform_create(self, serializer):
        serializer.save()