from rest_framework.permissions import BasePermission, SAFE_METHODS
from itertools import chain

from user_accounts.models import TeacherProfile
from courses.models import CourseMember


class BaseIsOwnerOrAllowMethods(BasePermission):
    """Inherit from this class and specify the below fields to create a concrete IsOwner permission."""
    owner_field = ''
    allow_methods = ()
    message = 'You are not the owner of this object.'

    def has_object_permission(self, request, view, obj):

        if request.method in self.allow_methods:
            return True

        owner = getattr(obj, self.owner_field, None)
        if owner:
            return owner == request.user

        raise AttributeError('The specified owner field does not exist on a given model.')


class IsOwnerOrReadOnly(BasePermission):
    """
    Grants permission to modify the object if the request.user is the owner of a object.
    Grants read-only permission for every request.

    Uses generic mechanism to get the owner object.
    """
    message = 'You are not the owner.'
    default_owner_lookup_fields = ('owner', 'author')
    custom_owner_lookup_fields = ()  # override this field to provide custom owner lookup fields

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        for potential_owner_field in chain(self.default_owner_lookup_fields, self.custom_owner_lookup_fields):
            owner = getattr(obj, potential_owner_field, None)
            if owner:
                return owner == request.user

        raise AttributeError('Permission checker has not found the owner field of a given object. Make sure an '
                             'appropriate model has an owner field with the name from one of default_owner_lookup_fields'
                             ' or provide a custom owner field name by overriding custom_owner_lookup_fields.')


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
    message = 'You are not a teacher.'

    def has_permission(self, request, view):
        print('is teacher', request.course_member.role == CourseMember.TEACHER)
        return request.course_member.role == CourseMember.TEACHER

    def has_object_permission(self, request, view, obj):
        # needs to be defined in order to use correctly bitwise operators on a permission classes
        # https://github.com/encode/django-rest-framework/issues/7117
        return self.has_permission(request, view)


class BaseIsTeacherOrAllowMethods(IsTeacher):
    allow_methods = ()

    def has_permission(self, request, view):
        if request.method in self.allow_methods:
            return True

        return super().has_permission(request, view)
