from os import path
from django.db import models
from django.core.validators import MinLengthValidator
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from user_accounts.models import UserAccount
from university_structures.models import Department, Speciality
from utils.validators import get_regex_validator


class Course(models.Model):
    title = models.CharField(max_length=128, validators=[MinLengthValidator(2), get_regex_validator('title')])
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
    speciality = models.ForeignKey(Speciality, null=True, on_delete=models.SET_NULL)
    owner = models.ForeignKey(UserAccount, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.title

    def is_user_enrolled(self, user):
        return bool(self.coursemember_set.filter(user=user))

    def get_course_member_if_exists(self, user):
        try:
            return self.coursemember_set.get(user=user)
        except CourseMember.DoesNotExist:
            return None

    def get_chapter_if_exists(self, chapter_id):
        try:
            return self.chapter_set.get(pk=chapter_id)
        except Chapter.DoesNotExist:
            return None


class CourseMember(models.Model):
    class Meta:
        unique_together = ('user', 'course')

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    STUDENT = 'S'
    TEACHER = 'T'
    AUDITOR = 'A'

    STATUSES = (
        (STUDENT, 'student'),
        (TEACHER, 'teacher'),
        (AUDITOR, 'auditor'),
    )

    role = models.CharField(max_length=1, choices=STATUSES, default=AUDITOR)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def is_teacher(self):
        return self.role == self.TEACHER

    def __str__(self):
        return f'{self.user.first_name}  {self.user.last_name}'


class Chapter(models.Model):
    title = models.CharField(max_length=128, validators=[MinLengthValidator(3), get_regex_validator('title')])
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    def get_task_if_exists(self, task_id):
        try:
            return self.task_set.get(pk=task_id)
        except Task.DoesNotExist:
            return None


class Attachment(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

    file = models.FileField(upload_to='attachments/')

    def __str__(self):
        return self.file_name

    @property
    def file_name(self):
        return path.basename(self.file.name)


class Post(models.Model):
    title = models.CharField(max_length=128, validators=[MinLengthValidator(4), get_regex_validator('title')])
    body = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField()  # can be time in future for planned posts
    is_archived = models.BooleanField(default=False)

    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE)
    author = models.ForeignKey(CourseMember, on_delete=models.CASCADE)
    attachment_set = GenericRelation(Attachment)

    class Meta:
        abstract = True
        ordering = ['-created_at']

    @property
    def is_planned(self):
        return self.published_at > timezone.now()

    def __str__(self):
        return self.title


class Material(Post):
    pass


class Task(Post):
    max_grade = models.PositiveSmallIntegerField()
    deadline = models.DateTimeField()

    @property
    def deadline_passed(self):
        return self.deadline < timezone.now()

    def __str__(self):
        return self.title


class StudentWork(models.Model):
    class Meta:
        unique_together = ('task', 'owner')
        ordering = ['submitted_at']

    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    owner = models.ForeignKey(CourseMember, on_delete=models.CASCADE)

    ASSIGNED = 'A'
    SUBMITTED = 'S'
    GRADED = 'G'

    STATUSES = (
        (ASSIGNED, 'Assigned'),
        (SUBMITTED, 'Submitted'),
        (GRADED, 'Graded'),
    )
    status = models.CharField(max_length=1, choices=STATUSES, default=ASSIGNED)
    answer = models.TextField(blank=True)
    submitted_at = models.DateTimeField(null=True)

    attachment_set = GenericRelation(Attachment)

    @property
    def is_graded(self):
        return self.status == self.GRADED

    @property
    def is_submitted(self):
        return self.status == self.SUBMITTED

    def __str__(self):
        return f'Answer to the {self.task.title} task'


class Grade(models.Model):
    description = models.CharField(max_length=128, blank=True, validators=[get_regex_validator('description')])
    amount = models.PositiveSmallIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    work = models.OneToOneField(StudentWork, on_delete=models.CASCADE)
    grader = models.ForeignKey(CourseMember, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f'{self.amount} {self.description}'
