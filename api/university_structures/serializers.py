from rest_framework.serializers import ModelSerializer
from . import models


class FacultySerializer(ModelSerializer):
    class Meta:
        model = models.Faculty
        fields = '__all__'


class DepartmentSerializer(ModelSerializer):
    class Meta:
        model = models.Department
        fields = '__all__'


class SpecialitySerializer(ModelSerializer):
    class Meta:
        model = models.Speciality
        fields = '__all__'


class GroupSerializer(ModelSerializer):
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
