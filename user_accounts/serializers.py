from rest_framework.serializers import ModelSerializer

from .models import UserAccount, TeacherProfile, StudentProfile
from utils.normalizers import Normalizer
from utils.serializers import NormalizedModelSerializer


class UserAccountSerializer(NormalizedModelSerializer):
    class Meta:
        model = UserAccount
        exclude = ['password']
        read_only_fields = ['is_active', 'is_admin', 'edited', 'created', 'last_login', 'id']
        normalize_for_type = {str: Normalizer.first_capital}

    def save(self, **kwargs):
        instance = super().save(**kwargs)

        if 'password' in kwargs:
            instance.set_password(kwargs['password'])
            instance.save()

        return instance


class TeacherProfileSerializer(ModelSerializer):
    class Meta:
        model = TeacherProfile
        exclude = ['user', 'id']


class StudentProfileSerializer(ModelSerializer):
    class Meta:
        model = StudentProfile
        exclude = ['user', 'id']
