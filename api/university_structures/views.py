from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import Degree, Department, Speciality, Position, Faculty, Group
from .serializers import DegreeSerializer, PositionSerializer, SpecialitySerializer, FacultySerializer, \
    DepartmentSerializer, GroupSerializer


class DegreeViewSet(ReadOnlyModelViewSet):
    queryset = Degree.objects.all()
    serializer_class = DegreeSerializer


class PositionViewSet(ReadOnlyModelViewSet):
    queryset = Position.objects.all()
    serializer_class = PositionSerializer


class SpecialityViewSet(ReadOnlyModelViewSet):
    queryset = Speciality.objects.all()
    serializer_class = SpecialitySerializer


class FacultyViewSet(ReadOnlyModelViewSet):
    queryset = Faculty.objects.all()
    serializer_class = FacultySerializer


class DepartmentViewSet(ReadOnlyModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer


class GroupViewSet(ReadOnlyModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
