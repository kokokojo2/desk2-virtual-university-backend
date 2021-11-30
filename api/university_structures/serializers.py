from rest_framework.serializers import ModelSerializer
from . import models

from utils.serializers import PrimaryKeyWriteMixin


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


class GroupNestedSerializer(PrimaryKeyWriteMixin, GroupSerializer):
    pass


class PositionNestedSerializer(PrimaryKeyWriteMixin, PositionSerializer):
    pass


class DegreeNestedSerializer(PrimaryKeyWriteMixin, DegreeSerializer):
    pass


class DepartmentNestedSerializer(PrimaryKeyWriteMixin, DepartmentSerializer):
    pass
