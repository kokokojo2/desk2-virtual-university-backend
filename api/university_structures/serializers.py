from rest_framework.serializers import ModelSerializer
from . import models


class FacultySerializer(ModelSerializer):
    class Meta:
        model = models.Faculty
        fields = '__all__'


class DepartmentSerializer(ModelSerializer):
    faculty = FacultySerializer(read_only=True)

    class Meta:
        model = models.Department
        fields = '__all__'


class SpecialitySerializer(ModelSerializer):
    class Meta:
        model = models.Speciality
        fields = '__all__'


class GroupSerializer(ModelSerializer):
    speciality = SpecialitySerializer(read_only=True)
    department = DepartmentSerializer(read_only=True)

    class Meta:
        model = models.Group
        fields = '__all__'


class DegreeSerializer(ModelSerializer):
    class Meta:
        model = models.Degree
        fields = '__all__'


class PositionSerializer(ModelSerializer):
    class Meta:
        model = models.Position
        fields = '__all__'
