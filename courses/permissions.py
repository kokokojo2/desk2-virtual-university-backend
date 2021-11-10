from rest_framework.permissions import BasePermission, SAFE_METHODS
from itertools import chain
from user_accounts.models import TeacherProfile


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
