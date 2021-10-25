from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db import transaction

from .utils import get_serializer_for_profile, get_serializer_for_profile_obj, serializer_check_save
from .serializers import UserAccountSerializer
from .models import UserAccount


class AuthenticationViewSet(ViewSet):
    """
    Note: ViewSet base class instead of ModelViewSet is used to implement management of user and profile models in one
    request.
    """
    def _get_user_model(self, request, pk):
        queryset = UserAccount.objects.select_related('teacher_profile', 'student_profile')

        if request is not None and request.user.pk == pk:
            user = request.user
        else:
            user = get_object_or_404(queryset, pk=pk)

        return user

    def create(self, request):
        user_serializer = UserAccountSerializer(data=request.data)
        profile_serializer = get_serializer_for_profile(request.data)

        if profile_serializer is None:
            return Response(
                {'profile_type': 'Invalid profile type. Should be student or teacher.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            user_saved, result = serializer_check_save(user_serializer, True, password=request.data['password'])
            if not user_saved:
                return Response(result, status=status.HTTP_400_BAD_REQUEST)

            profile_saved, result = serializer_check_save(profile_serializer, True, user=result)
            if not profile_saved:
                return Response(result, status=status.HTTP_400_BAD_REQUEST)

        response_dict = user_serializer.data
        response_dict.update(profile_serializer.data)

        return Response(response_dict, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        user = self._get_user_model(request, pk)

        user_serializer = UserAccountSerializer(instance=user)
        profile_serializer = get_serializer_for_profile_obj(user.profile)

        result = profile_serializer.data
        result.update(user_serializer.data)

        return Response(result)

    def update(self, request, pk=None):
        user = self._get_user_model(request, pk)

        user_serializer = UserAccountSerializer(instance=user, data=request.data)
        profile_serializer = get_serializer_for_profile_obj(user.profile, request_data=request.data)

        with transaction.atomic():
            user_saved, result = serializer_check_save(user_serializer, True)
            if not user_saved:
                return Response(result, status=status.HTTP_400_BAD_REQUEST)

            profile_saved, result = serializer_check_save(profile_serializer, True)
            if not profile_saved:
                return Response(result, status=status.HTTP_400_BAD_REQUEST)

        result = profile_serializer.data
        result.update(user_serializer.data)

        return Response(result, status=status.HTTP_200_OK)

    def partial_update(self, request, pk=None):
        user = self._get_user_model(request, pk)

        user_serializer = UserAccountSerializer(instance=user, data=request.data, partial=True)
        profile_serializer = get_serializer_for_profile_obj(user.profile, request_data=request.data, partial=True)

        with transaction.atomic():
            user_saved, result = serializer_check_save(user_serializer, True)
            if not user_saved:
                return Response(result, status=status.HTTP_400_BAD_REQUEST)

            profile_saved, result = serializer_check_save(profile_serializer, True)
            if not profile_saved:
                return Response(result, status=status.HTTP_400_BAD_REQUEST)

        result = profile_serializer.data
        result.update(user_serializer.data)

        return Response(result, status=status.HTTP_200_OK)

    def destroy(self, request, pk=None):
        self._get_user_model(None, pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
