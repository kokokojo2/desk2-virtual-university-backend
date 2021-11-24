from django.db.models import Prefetch
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from rest_framework import mixins
from rest_framework import status
from rest_framework.decorators import action
from django.utils import timezone

from courses.models import Course, CourseMember, Task, Grade, Chapter, Attachment, StudentWork, Material
from courses.serializers import CourseSerializer, GradeSerializer, TaskSerializer, AttachmentSerializer, \
    ChapterSerializer, CourseMemberSerializer, StudentWorkSerializer,\
    MaterialSerializer
from .permissions import IsGlobalTeacherOrReadOnly, BaseIsOwnerOrAllowMethods,\
    BaseIsTeacherOrAllowMethods, IsTeacher, IsStudent, IsActiveTask, IsEditableStudentWork


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


class AttachmentMixin:
    """Provides functionality for adding and deleting attachments. Should be used only with ViewSets, which model has
    genericRelation to the attachment model."""
    @action(methods=['POST'], detail=True, url_path='attachments')
    def add_attachment(self, request, **kwargs):
        pk = kwargs.get('pk', None)
        target_object = self.get_object()
        attachment_serializer = AttachmentSerializer(data=request.data)

        if attachment_serializer.check_and_save(pk, ContentType.objects.get_for_model(self.serializer_class.Meta.model)):
            target_object.save()  # updates Post.edited_at field with current datetime
            return Response(attachment_serializer.data, status=status.HTTP_200_OK)

        return Response(attachment_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['DELETE'], detail=True, url_path=r'attachments/(?P<attachment_id>\d+)')
    def delete_attachment(self, request, **kwargs):
        attachment_id = kwargs.get('attachment_id', None)
        target_obj = self.get_object()
        try:
            attachment = target_obj.attachment_set.get(pk=attachment_id)
        except Attachment.DoesNotExist:
            return Response({'detail': 'Attachment not found.'}, status=status.HTTP_404_NOT_FOUND)

        attachment.delete()
        target_obj.save()

        return Response(status=status.HTTP_204_NO_CONTENT)


class MaterialViewSet(ModelViewSet, AttachmentMixin):

    class IsTeacherOrReadOnly(BaseIsTeacherOrAllowMethods):
        allow_methods = SAFE_METHODS

    class IsOwnerOrAllowCreate(BaseIsOwnerOrAllowMethods):
        owner_field = 'author'
        course_member = True
        allow_methods = SAFE_METHODS + ('POST', )

    class IsOwner(BaseIsOwnerOrAllowMethods):
        owner_field = 'author'
        course_member = True

    permission_classes = [IsAuthenticated, IsTeacherOrReadOnly, IsOwnerOrAllowCreate]
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer

    def get_queryset(self):
        queryset = self.queryset.filter(chapter=self.request.chapter).\
            select_related('chapter').select_related('author')

        if not self.request.course_member.is_teacher:
            return queryset.filter(is_archived=False, published_at__lte=timezone.now())

        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.course_member, chapter=self.request.chapter)

    def get_permissions(self):
        permission_classes = self.permission_classes

        if self.action == 'add_attachment' or self.action == 'delete_attachment':
            permission_classes = [IsAuthenticated, self.IsOwner]

        return [permission() for permission in permission_classes]


class TaskViewSet(MaterialViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer


class GradeViewSet(mixins.CreateModelMixin,
                   mixins.ListModelMixin,
                   mixins.DestroyModelMixin,
                   GenericViewSet):
    class IsTeacherOrReadOnly(BaseIsTeacherOrAllowMethods):
        allow_methods = SAFE_METHODS

    class IsOwnerOrAllowCreate(BaseIsOwnerOrAllowMethods):
        owner_field = 'grader'
        course_member = True
        allow_methods = SAFE_METHODS + ('POST', )

    permission_classes = [IsAuthenticated, IsTeacherOrReadOnly, IsOwnerOrAllowCreate]
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer

    def get_queryset(self):
        if not self.request.course_member.is_teacher:
            return self.queryset.filter(work__owner=self.request.course_member)

        # if this code is reached, the course_member is a teacher
        queryset = self.queryset.filter(grader__course=self.request.course)

        # from get query params
        student_id = self.request.GET.get('student-id', False)
        task_id = self.request.GET.get('task-id', False)

        if student_id:
            queryset = queryset.filter(work__owner__id=student_id)
        if task_id:
            queryset = queryset.filter(work__task__id=task_id)

        return queryset

    def perform_create(self, serializer):
        instance = serializer.save(grader=self.request.course_member)
        student_work = instance.work
        student_work.status = student_work.GRADED
        student_work.save()

    def perform_destroy(self, instance):
        student_work = instance.work
        student_work.status = student_work.SUBMITTED
        student_work.save()
        instance.delete()


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


class StudentWorkViewSet(mixins.CreateModelMixin,
                         mixins.ListModelMixin,
                         mixins.DestroyModelMixin,
                         mixins.UpdateModelMixin,
                         GenericViewSet,
                         AttachmentMixin):
    class IsOwner(BaseIsOwnerOrAllowMethods):
        owner_field = 'owner'
        course_member = True

    queryset = StudentWork.objects.all()
    serializer_class = StudentWorkSerializer
    db_exception_msg = 'You have already created the StudentWork object for this task.'

    def get_queryset(self):
        queryset = self.queryset.filter(task=self.request.task)
        if not self.request.course_member.is_teacher:
            return queryset.filter(owner=self.request.course_member)

        # teacher cannot view the works that have not been yet submitted.
        return queryset.filter(status__in=(StudentWork.GRADED, StudentWork.SUBMITTED))

    def perform_create(self, serializer):
        serializer.save(owner=self.request.course_member, task=self.request.task)

    def get_permissions(self):
        permission_classes = [IsAuthenticated]

        if self.action == 'list':
            permission_classes += [IsTeacher | IsStudent]

        if self.action == 'create':
            permission_classes += [IsStudent, IsActiveTask]

        if self.action == 'update' or self.action == 'destroy' or self.action == 'partial_update':
            permission_classes += [self.IsOwner, IsEditableStudentWork, IsActiveTask]

        if self.action == 'submit' or self.action == 'unsubmit':
            permission_classes += [self.IsOwner, IsActiveTask]

        if self.action == 'add_attachment' or self.action == 'delete_attachment':
            permission_classes = [self.IsOwner, IsEditableStudentWork, IsActiveTask]

        return [permission() for permission in permission_classes]

    @action(methods=['POST'], detail=True)
    def submit(self, request, **kwargs):
        instance = self.get_object()
        if not instance.is_graded:
            instance.status = instance.SUBMITTED
            instance.submitted_at = timezone.now()

            instance.save()
            return Response(self.serializer_class(instance).data, status=status.HTTP_200_OK)

        return Response({'detail': 'This work is already graded.'}, status=status.HTTP_403_FORBIDDEN)

    @action(methods=['POST'], detail=True)
    def unsubmit(self, request, **kwargs):
        instance = self.get_object()
        if not instance.is_graded:
            instance.status = instance.ASSIGNED
            instance.submitted_at = None

            instance.save()
            return Response(self.serializer_class(instance).data, status=status.HTTP_200_OK)

        return Response({'detail': 'This work is already graded.'}, status=status.HTTP_403_FORBIDDEN)
