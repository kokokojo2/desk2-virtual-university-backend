from courses.models import Course, CourseMember, Material, Task, Grade, Chapter, Attachment, StudentWork
from rest_framework import serializers

from utils.serializers import NormalizedModelSerializer, WriteOnCreationMixin
from utils.normalizers import Normalizer
from user_accounts.serializers import UserAccountPublicSerializer
from .serializer_fields import CourseRelatedHyperlinkedIdentityField


class RestrictedNestedPostSerializerMixin:
    # TODO: make this a mixin with a generic filtering by using filter methods
    """
    This mixin restricts from serialization Posts, that whether are planned or archived. (Suitable for serializing post
    list, when request came from student, that is not allowed to view planned or archived posts).
    """

    def to_representation(self, instance):
        if not instance.is_archived and not instance.is_planned:
            return super().to_representation(instance)


class CourseSerializer(NormalizedModelSerializer):
    owner = UserAccountPublicSerializer(read_only=True)

    class Meta:
        model = Course
        fields = '__all__'
        normalize_for_field = {'title': Normalizer.first_capital}


class CourseMemberSerializer(serializers.ModelSerializer):
    user = UserAccountPublicSerializer(read_only=True)
    role = serializers.SerializerMethodField()

    class Meta:
        model = CourseMember
        exclude = ['course']
        read_only_fields = ['user', 'course', 'role']

    def get_role(self, obj):
        for status in obj.STATUSES:
            if status[0] == obj.role:
                return status[1]


class PostSerializer(NormalizedModelSerializer):

    # TODO: check if is_planned property is included
    class Meta:
        fields = '__all__'
        read_only_fields = ['author']
        normalize_for_field = {'title': Normalizer.first_capital}


class MaterialSerializer(PostSerializer):
    class Meta:
        model = Material


class TaskSerializer(PostSerializer):
    class Meta:
        model = Task


class ChapterSerializer(WriteOnCreationMixin, NormalizedModelSerializer):
    class Meta:
        model = Chapter
        fields = '__all__'
        create_only_fields = ['course']
        normalize_for_field = {'title': Normalizer.first_capital}


class AttachmentSerializer(serializers.ModelSerializer):
    # TODO: add more user friendly serialization
    class Meta:
        model = Attachment
        fields = '__all__'


class StudentWorkSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentWork
        fields = '__all__'
        read_only_fields = ['owner']
        create_only_fields = ['task']


class GradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grade
        fields = '__all__'
        read_only_fields = ['grader']
