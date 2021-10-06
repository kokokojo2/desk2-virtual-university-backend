from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from utils.validators import get_regex_validator


class Faculty(models.Model):
    title = models.CharField(max_length=128, unique=True, validators=[get_regex_validator('title')])
    description = models.TextField(blank=True)

    def __str__(self):
        return self.title


class Department(models.Model):
    title = models.CharField(max_length=128, unique=True, validators=[get_regex_validator('title')])
    description = models.TextField(blank=True)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Speciality(models.Model):
    title = models.CharField(max_length=128, unique=True, validators=[get_regex_validator('title')])
    code = models.PositiveSmallIntegerField()

    def __str__(self):
        return f'{self.code} {self.title}'


class Group(models.Model):
    name = models.CharField(max_length=5, validators=[
        get_regex_validator('group name', custom_pattern='[А-Я][А-Я]-[0-9][0-9]$')
    ])
    study_year = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(6)])

    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    speciality = models.ForeignKey(Speciality, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.name}'


class Degree(models.Model):
    name = models.CharField(max_length=128, unique=True, validators=[get_regex_validator('name')])

    def __str__(self):
        return f'{self.name}'


class Position(models.Model):
    name = models.CharField(max_length=128, unique=True, validators=[get_regex_validator('name')])

    def __str__(self):
        return f'{self.name}'
