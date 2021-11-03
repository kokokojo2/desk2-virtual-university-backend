from django.db import models
from django.core.validators import MinLengthValidator
from django.conf import settings

from university_structures.models import Department, Speciality


class Course(models.Model):
    title = models.CharField(max_length=128, validators=[MinLengthValidator(2)])
    description = models.TextField(blank=True)

    ONGOING = 'O'
    ARCHIVED = 'A'

    STATUSES = (
        (ONGOING, 'Ongoing'),
        (ARCHIVED, 'Archived'),
    )
    status = models.CharField(max_length=1, choices=STATUSES, default=ONGOING)
    created_at = models.DateTimeField(auto_now_add=True)

    department = models.ForeignKey(Department, null=True, on_delete=models.SET_NULL)
    speciality = models.ForeignKey(Speciality, on_delete=models.SET_NULL)

    def __str__(self):
        return self.title


class CourseMember(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    STUDENT = 'S'
    TEACHER = 'T'
    AUDITOR = 'A'
    OWNER = 'O'

    STATUSES = (
        (STUDENT, 'Student'),
        (TEACHER, 'Teacher'),
        (AUDITOR, 'Auditor'),
        (OWNER, 'Owner'),
    )

    role = models.CharField(max_length=1, choices=STATUSES)


class Chapter(models.Model):
    title = models.CharField(max_length=128, validators=[MinLengthValidator(3)])
    description = models.TextField()

    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Post(models.Model):
    title = models.CharField(max_length=128, validators=[MinLengthValidator(4)])
    body = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField()  # can be time in future for planned posts

    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE)
    author = models.ForeignKey(CourseMember, on_delete=models.CASCADE)

    class Meta:
        abstract = True


class Material(Post):
    pass


class Task(Post):
    max_grade = models.PositiveSmallIntegerField(null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(auto_now=True)
    post_date = models.DateTimeField()
    deadline = models.DateTimeField()

    def __str__(self):
        return self.title


class Attachment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    file = models.FileField(upload_to='uploads/')

    def __str__(self):
        return self.file.name


class StudentWork(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    owner = models.ForeignKey(CourseMember, on_delete=models.CASCADE)

    ASSIGNED = 'A'
    SUBMITTED = 'B'
    GRADED = 'G'

    STATUSES = (
        (ASSIGNED, 'Assigned'),
        (SUBMITTED, 'Submitted'),
        (GRADED, 'Graded'),
    )
    status = models.CharField(max_length=1, choices=STATUSES, default=ASSIGNED)
    answer = models.TextField(blank=True)


class Grade(models.Model):
    description = models.CharField(max_length=128, blank=True)
    amount = models.PositiveSmallIntegerField()  # TODO: implement max grade validation on serializer level

    work = models.ForeignKey(StudentWork, on_delete=models.CASCADE)
    grader = models.ForeignKey(CourseMember, on_delete=models.SET_NULL, null=True)
