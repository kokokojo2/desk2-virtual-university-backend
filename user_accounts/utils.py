from .serializers import TeacherProfileSerializer, StudentProfileSerializer
from .models import TeacherProfile, StudentProfile


def get_serializer_for_profile(request_data):
    if request_data.get('profile_type', '') == 'student':
        return StudentProfileSerializer(data=request_data)

    if request_data.get('profile_type', '') == 'teacher':
        return TeacherProfileSerializer(data=request_data)


def get_serializer_for_profile_obj(obj, request_data=None):
    _serializer = None
    if isinstance(obj, StudentProfile):
        _serializer = StudentProfileSerializer

    if isinstance(obj, TeacherProfile):
        _serializer = TeacherProfileSerializer

    if request_data and _serializer:
        return _serializer(obj, request_data)

    if not request_data and _serializer:
        return _serializer(obj)
