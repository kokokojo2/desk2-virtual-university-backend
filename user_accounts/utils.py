from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode

from .serializers import TeacherProfileSerializer, StudentProfileSerializer
from .models import TeacherProfile, StudentProfile, UserAccount
from .tokens import EmailConfirmationTokenGenerator


def get_serializer_for_profile(request_data):
    if request_data.get('profile_type', '') == 'student':
        return StudentProfileSerializer(data=request_data)

    if request_data.get('profile_type', '') == 'teacher':
        return TeacherProfileSerializer(data=request_data)


def get_serializer_for_profile_obj(obj, request_data=None, partial=False):
    _serializer = None
    if isinstance(obj, StudentProfile):
        _serializer = StudentProfileSerializer

    if isinstance(obj, TeacherProfile):
        _serializer = TeacherProfileSerializer

    if request_data and _serializer:
        return _serializer(obj, request_data, partial=partial)

    if not request_data and _serializer:
        return _serializer(obj, partial=partial)


def serializer_check_save(serializer, raise_exception, **kwargs):
    if serializer.is_valid(raise_exception=raise_exception):
        return True, serializer.save(**kwargs)

    else:
        return False, serializer.errors


def confirm_user_email(uidb64, token):
    """
    Handles email confirmation process.
    :param uidb64: uid in base64 encoding from url
    :param token: confirmation token for EmailConfirmationTokenGenerator from url
    :return: user object if user is confirmed, None - user is not confirmed
    """

    token_generator = EmailConfirmationTokenGenerator()
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = UserAccount.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, UserAccount.DoesNotExist):
        user = None

    if user and token_generator.check_token(user, token):
        user.is_active = True
        user.save()

        return user
