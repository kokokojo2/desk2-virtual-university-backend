from django.core.mail import send_mail
from django.template.loader import render_to_string
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.core.validators import validate_email, ValidationError
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

from .utils import get_serializer_for_profile, get_serializer_for_profile_obj, serializer_check_save
from .serializers import UserAccountSerializer, PasswordSerializer
from .models import UserAccount
from .tokens import check_token, EmailConfirmationTokenGenerator, PasswordChangeTokenGenerator, TwoFATokenGenerator
from .tasks import send_2fa_token


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

        user_saved, user = serializer_check_save(
            user_serializer,
            True,
            password=request.data['password'],
            email=request.data['email']
        )

        if not user_saved:
            return Response(user, status=status.HTTP_400_BAD_REQUEST)

        profile_saved, result = serializer_check_save(profile_serializer, True, user=user)
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


class ChangePasswordView(APIView):

    def post(self, request):
        password_serializer = PasswordSerializer(data=request.data, instance=request.user)
        if password_serializer.is_valid():
            password_serializer.save()
            return Response({'status': 'Password changed'}, status=status.HTTP_204_NO_CONTENT)

        return Response(password_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordView(APIView):

    def post(self, request):
        token_generator = PasswordChangeTokenGenerator()
        user = UserAccount.objects.get(pk=request.data['uid'])  # TODO: get user from request

        if token_generator.check_token(request.data['token'], user):
            user.set_password(request.data['password'])
            user.save()

            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response({'status': 'Confirmation token is not valid.'}, status=status.HTTP_400_BAD_REQUEST)


class ChangeEmailView(APIView):

    def post(self, request):
        user = UserAccount.objects.get(pk=request.data['uid'])  # TODO: get user from request

        try:
            validate_email(request.data['email'])
        except ValidationError:
            return Response({'status': 'This email address is not valid.'}, status=status.HTTP_400_BAD_REQUEST)

        user.email = request.data['email']
        user.email_confirmed = False
        user.save()

        return Response(status=status.HTTP_204_NO_CONTENT)


class ConfirmEmailView(APIView):
    def post(self, request):
        token_generator = EmailConfirmationTokenGenerator()
        try:
            user = UserAccount.objects.get(pk=request.data['uid'])
        except UserAccount.DoesNotExist:
            return Response({'status': 'Invalid uid'}, status=status.HTTP_400_BAD_REQUEST)

        if token_generator.check_token(user, request.data['token']):

            user.email_confirmed = True
            user.save()

            tokens = RefreshToken.for_user(user)
            return Response({
                'refresh': str(tokens),
                'access': str(tokens.access_token)
            }, status=status.HTTP_200_OK)


class CheckTokenView(APIView):

    def post(self, request, token_type):
        token_generator = None
        if token_type == 'email-confirm':
            token_generator = EmailConfirmationTokenGenerator

        if token_type == 'password-reset':
            token_generator = PasswordChangeTokenGenerator

        if token_type == 'twoFA-auth':
            token_generator = TwoFATokenGenerator

        if not token_generator:
            return Response({'status': 'Invalid token type.'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'token_valid': check_token(token_generator, request.data['uid'], request.data['token'])}
                        , status=status.HTTP_200_OK)


class SendTokenView(APIView):

    def post(self, request, token_type):
        uid = request.data['uid']
        token_generator = None

        try:
            user = UserAccount.objects.get(pk=uid)
        except UserAccount.DoesNotExist:
            return Response({'status': 'User with this uid does not exist.'}, status=status.HTTP_404_NOT_FOUND)

        if token_type == 'password-reset':
            token_generator = PasswordChangeTokenGenerator()
        if token_type == 'email-confirm':
            token_generator = EmailConfirmationTokenGenerator()

        if not token_generator:
            return Response({'status': 'Invalid token type.'}, status=status.HTTP_400_BAD_REQUEST)

        email_body = render_to_string(f'email/{token_type}.html', {
            'user': user,
            'token': token_generator.make_token(user),
        })
        send_mail('Desk2 Team', email_body, 'noreply@desk2.com', [user.email], fail_silently=False)

        return Response({'status': 'Token sent.'}, status=status.HTTP_200_OK)
