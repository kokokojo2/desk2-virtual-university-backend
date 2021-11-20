from django.db.models import Prefetch
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from rest_framework import mixins
from django.utils import timezone

from courses.models import Course, CourseMember, Task, Grade, Chapter, Attachment, StudentWork, Material
from courses.serializers import CourseSerializer, GradeSerializer, TaskSerializer, AttachmentSerializer, \
    ChapterSerializer, CourseMemberSerializer, StudentWorkSerializer,\
    MaterialSerializer
from .permissions import IsGlobalTeacherOrReadOnly, BaseIsOwnerOrAllowMethods,\
    BaseIsTeacherOrAllowMethods


class CourseViewSet(ModelViewSet):
    class IsOwnerOrReadOnly(BaseIsOwnerOrAllowMethods):
        owner_field = 'owner'
        allow_methods = SAFE_METHODS

    permission_classes = [IsAuthenticated, IsGlobalTeacherOrReadOnly, IsOwnerOrReadOnly]
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def perform_create(self, serializer):
        course = serializer.save(owner=self.request.user)
        CourseMember(user=self.request.user, course=course, role=CourseMember.TEACHER).save()

    def get_queryset(self):
        if self.request.GET.get('enrolled', False):
            return self.queryset.filter(coursemember__in=self.request.user.get_course_members_queryset())

        return self.queryset


class CourseMemberViewSet(mixins.CreateModelMixin,
                          mixins.RetrieveModelMixin,
                          mixins.ListModelMixin,
                          mixins.DestroyModelMixin,
                          GenericViewSet):
    class IsOwnerOrForbidDelete(BaseIsOwnerOrAllowMethods):
        owner_field = 'user'
        allow_methods = SAFE_METHODS + ('POST', )

    class IsTeacherOrForbidDelete(BaseIsTeacherOrAllowMethods):
        allow_methods = SAFE_METHODS + ('POST', )

    permission_classes = [IsAuthenticated, IsTeacherOrForbidDelete | IsOwnerOrForbidDelete]
    queryset = CourseMember.objects.all()
    serializer_class = CourseMemberSerializer
    db_exception_msg = 'You are already enrolled in this course.'

    def get_queryset(self):
        return self.queryset.filter(course=self.request.course).select_related('user')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, course=self.request.course)


class MaterialViewSet(ModelViewSet):

    class IsTeacherOrReadOnly(BaseIsTeacherOrAllowMethods):
        allow_methods = SAFE_METHODS

    class IsOwnerOrAllowCreate(BaseIsOwnerOrAllowMethods):
        owner_field = 'author'
        allow_methods = SAFE_METHODS + ('POST', )

    permission_classes = [IsAuthenticated, IsTeacherOrReadOnly, IsOwnerOrAllowCreate]
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer

    def get_queryset(self):
        queryset = self.queryset.filter(chapter__in=self.request.course.chapter_set.all()).\
            select_related('chapter').select_related('author')

        if not self.request.course_member.is_teacher:
            return queryset.filter(is_archived=False, published_at__lte=timezone.now())

        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.course_member)


class TaskViewSet(ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.course_member)


class GradeViewSet(ModelViewSet):
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer


class ChapterViewSet(ModelViewSet):
    class IsTeacherOrReadOnly(BaseIsTeacherOrAllowMethods):
        allow_methods = SAFE_METHODS

    permission_classes = [IsAuthenticated, IsTeacherOrReadOnly]
    serializer_class = ChapterSerializer
    queryset = Chapter.objects.all()

    def get_queryset(self):
        queryset = self.queryset.filter(course=self.request.course)
        if not self.request.course_member.is_teacher:
            return queryset.prefetch_related(
                Prefetch('material_set', queryset=Material.objects.filter(
                    is_archived=False,
                    published_at__lte=timezone.now()
                ))
            ).prefetch_related(
                Prefetch('task_set', queryset=Task.objects.filter(
                    is_archived=False,
                    published_at__lte=timezone.now()
                ))
            )

        return queryset.prefetch_related('material_set').prefetch_related('task_set')

    def perform_create(self, serializer):
        serializer.save(course=self.request.course)


class AttachmentViewSet(ModelViewSet):
    queryset = Attachment.objects.all()
    serializer_class = AttachmentSerializer


class StudentWorkViewSet(ModelViewSet):
    queryset = StudentWork.objects.all()
    serializer_class = StudentWorkSerializer
