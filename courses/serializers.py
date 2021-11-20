from courses.models import Course, CourseMember, Material, Task, Grade, Chapter, Attachment, StudentWork
from rest_framework import serializers

from utils.serializers import NormalizedModelSerializer
from utils.normalizers import Normalizer
from user_accounts.serializers import UserAccountPublicSerializer
from .serializer_fields import CourseRelatedHyperlinkedIdentityField, ChapterRelatedHyperlinkedIdentityField


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


class ChapterNestedSerializer(serializers.HyperlinkedModelSerializer):
    detail_url = CourseRelatedHyperlinkedIdentityField(view_name='chapter-detail', read_only=True)

    class Meta:
        model = Chapter
        fields = ['id', 'title', 'detail_url']


class AttachmentNestedSerializer(serializers.ModelSerializer):
    detail_url = CourseRelatedHyperlinkedIdentityField(view_name='attachment-detail', read_only=True)

    class Meta:
        model = Attachment
        fields = ['id', 'file', 'detail_url', 'file_name']


class BasePostSerializer(NormalizedModelSerializer):
    author = CourseMemberSerializer(read_only=True)
    attachment_set = AttachmentNestedSerializer(many=True, read_only=True)

    class Meta:
        fields = ['id', 'title', 'body', 'created_at', 'edited_at', 'published_at', 'is_archived',
                  'is_planned', 'chapter', 'author', 'attachment_set']

        read_only_fields = ['author']
        normalize_for_field = {'title': Normalizer.first_capital}


class MaterialSerializer(BasePostSerializer):
    class Meta(BasePostSerializer.Meta):
        model = Material


class MaterialNestedSerializer(serializers.HyperlinkedModelSerializer):
    detail_url = ChapterRelatedHyperlinkedIdentityField(view_name='material-detail', read_only=True)

    class Meta:
        fields = ['id', 'title', 'published_at', 'detail_url', 'is_archived', 'is_planned']
        model = Material


class TaskSerializer(BasePostSerializer):
    class Meta(BasePostSerializer.Meta):
        model = Task


class TaskNestedSerializer(serializers.HyperlinkedModelSerializer):
    detail_url = ChapterRelatedHyperlinkedIdentityField(view_name='task-detail', read_only=True)

    class Meta:
        fields = ['id', 'title', 'published_at', 'deadline', 'detail_url', 'is_archived', 'is_planned', 'deadline_passed']
        model = Task


class ChapterSerializer(NormalizedModelSerializer):
    task_set = TaskNestedSerializer(read_only=True, many=True)
    material_set = MaterialNestedSerializer(read_only=True, many=True)

    class Meta:
        model = Chapter
        fields = ['id', 'title', 'description', 'created_at', 'task_set', 'material_set']
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
