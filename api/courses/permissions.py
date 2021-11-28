from rest_framework.permissions import BasePermission, SAFE_METHODS

from user_accounts.models import TeacherProfile
from courses.models import CourseMember


class BaseIsOwnerOrAllowMethods(BasePermission):
    """Inherit from this class and specify the below fields to create a concrete IsOwner permission."""
    owner_field = ''
    course_member = False
    allow_methods = ()
    message = 'You are not the owner of this object.'

    def has_object_permission(self, request, view, obj):

        if request.method in self.allow_methods:
            return True

        owner = getattr(obj, self.owner_field, None)
        if owner:
            if self.course_member:
                return owner.user == request.user

            return owner == request.user

        raise AttributeError('The specified owner field does not exist on a given model.')


class IsGlobalTeacher(BasePermission):
    """
    Grants permission to a request if request.user is a teacher (has a teacher profile type)
    """
    message = 'Only teacher account can perform this action.'

    def has_permission(self, request, view):
        return isinstance(request.user.profile, TeacherProfile)


class IsGlobalTeacherOrReadOnly(IsGlobalTeacher):

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        return super().has_permission(request, view)


class IsTeacher(BasePermission):
    """
    This permission should only be used on a course detail views.
    """
    message = 'You are not a teacher in this course.'

    def has_permission(self, request, view):
        return request.course_member.role == CourseMember.TEACHER

    def has_object_permission(self, request, view, obj):
        # needs to be defined in order to use correctly bitwise operators on a permission classes
        # https://github.com/encode/django-rest-framework/issues/7117
        return self.has_permission(request, view)


class IsStudent(BasePermission):
    """
    This permission should only be used on a course detail views.
    """
    message = 'You are not a student in this course.'

    def has_permission(self, request, view):
        return request.course_member.role == CourseMember.STUDENT

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class BaseIsTeacherOrAllowMethods(IsTeacher):
    allow_methods = ()

    def has_permission(self, request, view):
        if request.method in self.allow_methods:
            return True

        return super().has_permission(request, view)


class IsActiveTask(BasePermission):
    """Should be used only with task-detailed views."""
    def has_permission(self, request, view):
        return not request.task.is_planned and not request.task.is_archived


class IsEditableStudentWork(BasePermission):
    message = 'This StudentWork is submitted or graded and therefore cannot be editable.'

    def has_object_permission(self, request, view, obj):
        return obj.status == obj.ASSIGNED
