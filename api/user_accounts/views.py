from datetime import datetime

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.core.validators import validate_email, ValidationError
from django.contrib.auth import authenticate

from rest_framework.viewsets import ViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.decorators import action

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

from .utils import get_serializer_for_profile, get_serializer_for_profile_obj, serializer_check_save
from .serializers import UserAccountSerializer, PasswordSerializer
from .models import UserAccount
from .tokens import check_token, EmailConfirmationTokenGenerator, PasswordChangeTokenGenerator, TwoFATokenGenerator, \
    EmailConfirmationUnregisteredTokenGenerator
from .tasks import send_2fa_token


class AuthenticationViewSet(ViewSet):
    """
    Note: ViewSet base class instead of ModelViewSet is used to implement management of user and profile models in one
    request.
    """
    db_exception_msg = 'User with this email already exists.'

    def get_permissions(self):
        permission_classes = []
        if self.action and self.action.startswith(('list', 'edit', 'partial_edit', 'delete')):
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    def create(self, request):
        user_serializer = UserAccountSerializer(data=request.data)
        profile_serializer = get_serializer_for_profile(request.data)

        email = request.data.get('email', None)
        password = request.data.get('password', None)
        token = request.data.get('email-token', None)

        if not email:
            return Response({'email': 'This field is required.'}, status=status.HTTP_400_BAD_REQUEST)

        if not password:
            return Response({'password': 'This field is required.'}, status=status.HTTP_400_BAD_REQUEST)

        if not token:
            return Response({'email-token': 'This field is required.'}, status=status.HTTP_400_BAD_REQUEST)

        if profile_serializer is None:
            return Response(
                {'profile_type': 'Invalid profile type. Should be student or teacher.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not EmailConfirmationUnregisteredTokenGenerator().check_token(email, token, remove_from_storage=True):
            return Response({'email-token': 'Given token is invalid. Make sure to check your email.'},
                            status=status.HTTP_400_BAD_REQUEST)

        user_saved, user = serializer_check_save(user_serializer, False, password=password, email=email, email_confirmed=True)

        if not user_saved:
            return Response(user, status=status.HTTP_400_BAD_REQUEST)

        profile_saved, result = serializer_check_save(profile_serializer, False, user=user)

        if not profile_saved:
            user.delete()
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

        response_dict = user_serializer.data
        response_dict.update(profile_serializer.data)

        return Response(response_dict, status=status.HTTP_201_CREATED)

    def list(self, request):
        user = request.user

        user_serializer = UserAccountSerializer(instance=user)
        profile_serializer = get_serializer_for_profile_obj(user.profile)

        result = profile_serializer.data
        result.update(user_serializer.data)

        return Response(result)

    @action(detail=False, methods=['PUT'])
    def edit(self, request):
        user = request.user

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

    @edit.mapping.patch
    def partial_edit(self, request):
        user = request.user

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

    @edit.mapping.delete
    def delete(self, request):
        request.user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        password_serializer = PasswordSerializer(data=request.data, instance=request.user)
        if password_serializer.is_valid():
            password_serializer.save()
            return Response({'detail': 'Password changed'}, status=status.HTTP_204_NO_CONTENT)

        return Response(password_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordView(APIView):

    def post(self, request):
        token_generator = PasswordChangeTokenGenerator()
        try:
            user = UserAccount.objects.get(email=request.data['email'])
            token = request.data['token']
            password = request.data['password']
        except (UserAccount.DoesNotExist, KeyError):
            return Response({'detail': 'password, token or email fields are not specified.'},
                            status=status.HTTP_400_BAD_REQUEST)

        if user and password and token_generator.check_token(user, token, remove_from_storage=True):
            user.set_password(password)
            user.save()

            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response({'detail': 'Confirmation token is not valid.'}, status=status.HTTP_400_BAD_REQUEST)


class ChangeEmailView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        token = request.data.get('token', None)
        email = request.data.get('email', None)

        if not email:
            return Response({'email': 'This field is required.'}, status=status.HTTP_400_BAD_REQUEST)

        if not token:
            return Response({'token': 'This field is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            validate_email(email)
        except ValidationError:
            return Response({'email': 'Given email address is not valid.'}, status=status.HTTP_400_BAD_REQUEST)

        if not EmailConfirmationUnregisteredTokenGenerator().check_token(email, token, remove_from_storage=True):
            return Response({'token': 'Given token is invalid. Make sure to check your email'},
                            status=status.HTTP_400_BAD_REQUEST)

        user.email = email
        user.email_confirmed = True
        user.save()

        return Response(status=status.HTTP_204_NO_CONTENT)


class CheckTokenView(APIView):
    throttle_scope = 'token-check'

    def post(self, request, token_type):
        token_generator = None
        try:
            token = request.data['token']
            email = request.data['email']
        except KeyError:
            return Response({'detail': 'Email or token is not provided.'}, status=status.HTTP_400_BAD_REQUEST)

        if token_type == 'password-reset':
            token_generator = PasswordChangeTokenGenerator

        if token_type == 'twoFA-auth':
            token_generator = TwoFATokenGenerator

        if token_type == 'email-confirm':
            token_generator = EmailConfirmationUnregisteredTokenGenerator
            return Response({'token_valid': token_generator().check_token(email, token)},
                            status=status.HTTP_200_OK)

        if not token_generator:
            return Response({'detail': 'Invalid token type.'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'token_valid': check_token(token_generator, email, token)}
                        , status=status.HTTP_200_OK)


class SendTokenView(APIView):

    def post(self, request, token_type):
        token_generator = None

        email = request.data.get('email', None)
        if not email:
            return Response({'email': 'This field is required.'}, status=status.HTTP_400_BAD_REQUEST)

        if token_type == 'password-reset':
            token_generator = PasswordChangeTokenGenerator()
            user = self._get_user_if_exists(email)
            if not user:
                return Response({'detail': 'User with given email does not exist.'}, status=status.HTTP_404_NOT_FOUND)

            email_body = render_to_string(f'email/{token_type}.html', {
                'user': user,
                'token': token_generator.make_token(user),
            })

        if token_type == 'email-confirm':
            token_generator = EmailConfirmationUnregisteredTokenGenerator()
            user = self._get_user_if_exists(email)

            try:
                validate_email(email)
            except ValidationError:
                return Response({'email': 'Given email address is not valid.'}, status=status.HTTP_400_BAD_REQUEST)

            if user:
                return Response({'detail': 'User with given email already exists.'}, status=status.HTTP_404_NOT_FOUND)

            email_body = render_to_string(f'email/{token_type}.html', {'token': token_generator.make_token(email)})

        if not token_generator:
            return Response({'detail': 'Invalid token type.'}, status=status.HTTP_400_BAD_REQUEST)

        send_mail('Desk2 Team', email_body, 'noreply@desk2.com', [email], fail_silently=False)
        return Response({'detail': 'Token sent.'}, status=status.HTTP_200_OK)

    def _get_user_if_exists(self, email):
        try:
            return UserAccount.objects.get(email=email)
        except UserAccount.DoesNotExist:
            return None


class TokenObtainView(TokenObtainPairView):
    throttle_scope = 'token-check'

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        user = authenticate(username=request.data['email'], password=request.data['password'])

        if not user.email_confirmed:
            return Response({'detail': 'Mail verification is needed.'},
                            status=status.HTTP_403_FORBIDDEN)

        elif user.twoFA_enabled:
            if '2FA_code' not in request.data.keys():
                send_2fa_token.run(user.pk)  # TODO: change to async mode after SMTP server will ge configured
                return Response({'detail': '2FA verification is needed.'}, status=status.HTTP_401_UNAUTHORIZED)

            token_generator = TwoFATokenGenerator()
            if not token_generator.check_token(user, request.data['2FA_code']):
                return Response({'detail': '2FA token is not valid.'}, status=status.HTTP_400_BAD_REQUEST)

        user.last_login = datetime.now()
        user.save()

        return response
