from courses.models import Faculty
from rest_framework import viewsets
from rest_framework import permissions
from courses.serializers import GroupSerializer,UserSerializer,FacultySerializer
from django.contrib.auth.models import User, Group
from rest_framework.views import APIView
from rest_framework.response import Response

# class CourseViewSet(viewsets.ModelViewSet):
#     """
#     API endpoint that allows users to be viewed or edited.
#     """
#     queryset = Course.objects.all().order_by('-date_joined')
#     serializer_class = CourseSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]


class FacultyView(APIView):
    def get(self, request):
        faculties = Faculty.objects.all()
        serializer = FacultySerializer(faculties, many=True)
        return Response({"faculties": serializer.data})
