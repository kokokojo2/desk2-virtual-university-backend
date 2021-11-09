from rest_framework.viewsets import ModelViewSet
from courses.models import Course, CourseMember, Task, Grade, Chapter, Attachment, StudentWork
from courses.serializers import CourseSerializer, GradeSerializer, TaskSerializer, AttachmentSerializer, \
    ChapterSerializer, CourseMemberSerializer, StudentWorkSerializer


class CourseViewSet(ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer


class CourseMemberViewSet(ModelViewSet):
    queryset = CourseMember.objects.all()
    serializer_class = CourseMemberSerializer


class TaskViewSet(ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer


class GradeViewSet(ModelViewSet):
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer


class ChapterViewSet(ModelViewSet):
    queryset = Chapter.objects.all()
    serializer_class = ChapterSerializer


class AttachmentViewSet(ModelViewSet):
    queryset = Attachment.objects.all()
    serializer_class = AttachmentSerializer


class StudentWorkViewSet(ModelViewSet):
    queryset = StudentWork.objects.all()
    serializer_class = StudentWorkSerializer
