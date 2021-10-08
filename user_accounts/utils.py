from .serializers import TeacherProfileSerializer, StudentProfileSerializer


def get_serializer_for_profile(request_data):
    if request_data.get('profile_type', '') == 'student':
        return StudentProfileSerializer(data=request_data)

    if request_data.get('profile_type', '') == 'teacher':
        return TeacherProfileSerializer(data=request_data)
