from rest_framework import serializers
from users.models import CustomUser

class UsersSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    #friends = serializers.HyperlinkedRelatedField(many=True, view_name='friend-detail', read_only=True)

    class Meta:
        model = CustomUser
        fields = ['email', 'first_name', 'last_name', 'is_staff', 'is_active', 'date_joined', 'url', 'id', 'password']
        read_only_fields = ['date_joined']

    def create(self, validated_data):
        user = super(UsersSerializer, self).create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user

class SpotifyAuthSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ['access_token', 'refresh_token']

# class FreindSerializer(serializers.HyperlinkedModelSerializer):
#     creator = serializers.ReadOnlyField(source='owner.email')

#         class Meta:
#             model = Friend
#             fields = ('url', 'id', 'creator', 'friend', 'accepted', 'blocked', 'permissions')