from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from .utils import get_serializer_for_profile, get_serializer_for_profile_obj
from .serializers import UserAccountSerializer
from .models import UserAccount


class AuthenticationViewSet(ViewSet):
    """
    Note: ViewSet base class instead of ModelViewSet is used to implement management of user and profile models in one
    request.
    """

    def list(self, request):
        pass

    def create(self, request):
        user_serializer = UserAccountSerializer(data=request.data)
        profile_serializer = get_serializer_for_profile(request.data)

        if profile_serializer is None:
            return Response(
                {'profile_type': 'Invalid profile type. Should be student or teacher.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if user_serializer.is_valid():
            user_object = user_serializer.save(password=request.data['password'])
        else:
            return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        if profile_serializer.is_valid():
            profile_serializer.save(user=user_object)
        else:
            return Response(profile_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        response_dict = user_serializer.data
        response_dict.update(profile_serializer.data)

        return Response(response_dict, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        queryset = UserAccount.objects.select_related('teacher_profile', 'student_profile')

        if request.user.pk == pk:
            user = request.user
        else:
            user = get_object_or_404(queryset, pk=pk)

        user_serializer = UserAccountSerializer(instance=user)
        profile_serializer = get_serializer_for_profile_obj(user.profile)

        result = profile_serializer.data
        result.update(user_serializer.data)

        return Response(result)

    def update(self, request, pk=None):
        queryset = UserAccount.objects.select_related('teacher_profile', 'student_profile')

        if request.user.pk == pk:
            user = request.user
        else:
            user = get_object_or_404(queryset, pk=pk)

        user_serializer = UserAccountSerializer(instance=user, data=request.data)
        profile_serializer = get_serializer_for_profile_obj(user.profile, request_data=request.data)

        if user_serializer.is_valid():
            user_serializer.save()
        else:
            return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        if profile_serializer.is_valid():
            profile_serializer.save()
        else:
            return Response(profile_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        result = profile_serializer.data
        result.update(user_serializer.data)

        return Response(result, status=status.HTTP_200_OK)

    def partial_update(self, request, pk=None):
        pass

    def destroy(self, request, pk=None):
        pass
