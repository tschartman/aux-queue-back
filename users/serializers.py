from rest_framework import serializers
from users.models import CustomUser

class UsersSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['email', 'is_staff', 'is_active', 'date_joined', 'password']
        read_only_fields = ['date_joined']

    def create(self, validate_data):
        user = super(UserSerializer, self).create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user

class SpotifyAuthSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ['access_token', 'refresh_token']