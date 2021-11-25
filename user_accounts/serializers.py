from django.contrib.auth.password_validation import validate_password
from rest_framework.serializers import ModelSerializer, Serializer, ValidationError
from rest_framework import serializers

from .models import UserAccount, TeacherProfile, StudentProfile
from utils.normalizers import Normalizer
from utils.serializers import NormalizedModelSerializer


class UserAccountSerializer(NormalizedModelSerializer):
    class Meta:
        model = UserAccount
        exclude = ['password']
        read_only_fields = ['is_active', 'is_admin', 'edited', 'created', 'last_login', 'id', 'email', 'email_confirmed']
        normalize_for_type = {str: Normalizer.first_capital}

    def save(self, **kwargs):
        instance = super().save(**kwargs)

        if 'password' in kwargs:
            instance.set_password(kwargs['password'])
            instance.save()

        return instance


class UserAccountPublicSerializer(ModelSerializer):
    class Meta:
        model = UserAccount
        fields = ['id', 'first_name', 'last_name', 'middle_name']


class TeacherProfileSerializer(ModelSerializer):
    class Meta:
        model = TeacherProfile
        exclude = ['user', 'id']


class StudentProfileSerializer(ModelSerializer):
    class Meta:
        model = StudentProfile
        exclude = ['user', 'id']


class PasswordSerializer(Serializer):
    """
    Serializer class used for changing user password.
    Requires instance keyword attribute into its __init__ method.
    """
    new_password = serializers.CharField(required=True)
    current_password = serializers.CharField(required=True)

    def validate_current_password(self, value):
        msg_text = 'Does not match with current password.'

        if not self.instance.check_password(self.initial_data['current_password']):
            raise ValidationError(msg_text)

        return value

    def validate_new_password(self, value):
        validate_password(value, user=self.instance)

        return value

    def update(self, instance, validated_data):
        instance.set_password(validated_data['new_password'])
        instance.save()

        return instance
