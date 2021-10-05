from courses.models import Faculty,Department,Course,\
    CourseMember,Task,Grade,Chapter,Attachment,StudentWork
from rest_framework import viewsets
from rest_framework import permissions
from courses.serializers import FacultySerializer,CourseSerializer,GradeSerializer,\
    TaskSerializer,AttachmentSerializer,DepartmentSerializer,ChapterSerializer,\
    CourseMemberSerializer,StudentWorkSerializer


class FacultyViewSet(viewsets.ModelViewSet):
    queryset = Faculty.objects.all()
    serializer_class = FacultySerializer


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer


class CourseMemberViewSet(viewsets.ModelViewSet):
    queryset = CourseMember.objects.all()
    serializer_class = CourseMemberSerializer


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer


class GradeViewSet(viewsets.ModelViewSet):
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer


class ChapterViewSet(viewsets.ModelViewSet):
    queryset = Chapter.objects.all()
    serializer_class = ChapterSerializer

class AttachmentViewSet(viewsets.ModelViewSet):
    queryset = Attachment.objects.all()
    serializer_class = AttachmentSerializer


class StudentWorkViewSet(viewsets.ModelViewSet):
    queryset = StudentWork.objects.all()
    serializer_class = StudentWorkSerializer

