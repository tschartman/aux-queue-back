from rest_framework import serializers
from .models import CustomUser

class UsersSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ('email', 'is_staff', 'is_active', 'date_joined' )
        read_only_fields = ('date_joined')