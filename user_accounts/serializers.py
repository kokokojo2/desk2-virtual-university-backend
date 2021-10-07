from rest_framework.serializers import ModelSerializer

from .models import UserAccount


class UserAccountSerializer(ModelSerializer):
    class Meta:
        model = UserAccount
        exclude = ['password']
        read_only_fields = ['is_active', 'is_admin', 'edited', 'created']
