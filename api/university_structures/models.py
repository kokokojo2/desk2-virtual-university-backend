from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from utils.validators import get_regex_validator


class Faculty(models.Model):
    class Meta:
        verbose_name_plural = 'Faculties'

    title = models.CharField(max_length=128, unique=True, validators=[
        get_regex_validator('title', numbers=False, special=False)
    ])
    description = models.TextField(blank=True)
    abbreviation = models.CharField(max_length=10, validators=[get_regex_validator('abbreviation')])

    def __str__(self):
        return self.abbreviation


class Department(models.Model):
    title = models.CharField(max_length=128, unique=True, validators=[
        get_regex_validator('title', numbers=False, special=False)
    ])
    description = models.TextField(blank=True)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    abbreviation = models.CharField(max_length=10, validators=[get_regex_validator('abbreviation')])

    def __str__(self):
        return self.abbreviation


class Speciality(models.Model):
    class Meta:
        verbose_name_plural = 'Specialities'

    title = models.CharField(max_length=128, unique=True, validators=[
        get_regex_validator('title', special=False)
    ])
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
    name = models.CharField(max_length=128, unique=True, validators=[
        get_regex_validator('name', numbers=False, special=False)
    ])

    def __str__(self):
        return f'{self.name}'


class Position(models.Model):
    name = models.CharField(max_length=128, unique=True, validators=[
        get_regex_validator('name', numbers=False, special=False)
    ])

    def __str__(self):
        return f'{self.name}'
