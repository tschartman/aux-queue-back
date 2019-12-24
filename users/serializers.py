from rest_framework import serializers
from rest_auth.registration.serializers import RegisterSerializer
from users.models import CustomUser


class RegisterSerializer(RegisterSerializer):
    email = serializers.EmailField(required=True)
    password1 = serializers.CharField(write_only=True)

    def get_cleaned_data(self):
        super(RegisterSerializer, self).get_cleaned_data()

        return {
            'password1': self.validated_data.get('password1', ''),
            'email': self.validated_data.get('email', ''),
        }

class UsersSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ['email', 'is_staff', 'is_active', 'date_joined']
        read_only_fields = ['date_joined']

class SpotifyAuthSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ['access_token', 'refresh_token']