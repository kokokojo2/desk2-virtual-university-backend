from django.db import models
from django.core.validators import MinLengthValidator


class Faculty(models.Model):
    title = models.CharField(max_length=128, unique=True, validators=[MinLengthValidator(2)])
    description = models.TextField(blank=True)

    def __str__(self):
        return self.title


class Department(models.Model):
    title = models.CharField(max_length=128, unique=True, validators=[MinLengthValidator(2)])
    description = models.TextField(blank=True)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Speciality(models.Model):
    title = models.CharField(max_length=128, unique=True, validators=[MinLengthValidator(2)])
    code = models.PositiveSmallIntegerField()

    def __str__(self):
        return f'{self.code} {self.title}'


class Group(models.Model):
    name = models.CharField(max_length=5)
    study_year = models.PositiveSmallIntegerField()

    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    speciality = models.ForeignKey(Speciality, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.name}'
