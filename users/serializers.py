from rest_framework import serializers
from users.models import CustomUser

class UsersSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ['email', 'is_staff', 'is_active', 'date_joined', 'password']
        read_only_fields = ['date_joined']
        write_only_fields = ['password']

class SpotifyAuthSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ['access_token', 'refresh_token']