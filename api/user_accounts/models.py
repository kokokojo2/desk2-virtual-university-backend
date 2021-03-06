from functools import partial

from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager

from university_structures.models import Department, Group, Degree, Position
from utils.normalizers import Normalizer
from utils.validators import get_regex_validator, validate_number_len


class UserAccountManager(BaseUserManager):
    def create_user(self, email, password, first_name, last_name, middle_name=None):
        if not all([email, password, first_name, last_name]):
            raise ValueError("Some of the required arguments are None, please, specify not None arguments.")

        user = self.model(
            email=self.normalize_email(email),
            first_name=Normalizer.first_capital(first_name),
            last_name=Normalizer.first_capital(last_name),
            middle_name=Normalizer.first_capital(middle_name) if middle_name else '',
        )
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, **kwargs):
        user = self.create_user(**kwargs)
        user.is_admin = True
        user.is_active = True
        user.type = user.STAFF
        user.save(using=self.db)

        return user


class UserAccount(AbstractBaseUser):
    """
    This is a user model used for authentication. The username field is email, so it should be unique.
    WARNING: access to the wrong reverse profile field raises **RelatedObjectDoesNotExist**,
    use safe **profile** property instead.
    """

    first_name = models.CharField(max_length=128, validators=[
        get_regex_validator('first name', whitespace=False, special=False, numbers=False)
    ])
    last_name = models.CharField(max_length=128, validators=[
        get_regex_validator('last name', whitespace=False, special=False, numbers=False)
    ])
    middle_name = models.CharField(blank=True, max_length=128, validators=[
        get_regex_validator('middle name', whitespace=False, special=False, numbers=False)
    ])
    email = models.EmailField(unique=True, max_length=256)

    created = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True)

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    email_confirmed = models.BooleanField(default=False)
    twoFA_enabled = models.BooleanField(default=True)
    department = models.ForeignKey(Department, null=True, on_delete=models.SET_NULL)
    objects = UserAccountManager()

    # only for admin filtering WARNING: do not use to check permissions
    TEACHER = 'T'
    STAFF = 'A'
    STUDENT = 'S'
    STATUSES = (
        (TEACHER, 'Teacher'),
        (STUDENT, 'Student'),
        (STAFF, 'Staff'),
    )

    # WARNING: won`t change if the user is_admin will be set to true in the admin
    registration_type = models.CharField(choices=STATUSES, blank=True, max_length=1)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    @property
    def is_staff(self):
        return self.is_admin

    @property
    def profile(self):
        """
        Returns an associated profile object.
        :return: an StudentProfile or TeacherProfile object.
        """

        try:
            model = self.student_profile
            return model
        except StudentProfile.DoesNotExist:
            try:
                model = self.teacher_profile
            except TeacherProfile.DoesNotExist:
                raise AttributeError('There is not any profile object related to this user.')

        return model

    def get_course_members_queryset(self, **kwargs):
        """
        Returns a queryset of a CourseMember objects associated with this user object.
        :param kwargs: any valid keyword args to be used with QuerySet.filter method.
        :return: a QuerySet object
        """
        return self.coursemember_set.filter(**kwargs)

    def get_course_member(self, course):
        """
        Returns a CourseMember object that is associated with a given course object and this user object.
        :param course: a Course object
        :return: a CourseMember object
        """
        return self.coursemember_set.get(course=course)

    def has_module_perms(self, app_label):
        return self.is_admin

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def __str__(self):
        return f'{self.first_name} {self.middle_name} {self.last_name}'


class TeacherProfile(models.Model):
    scientific_degree = models.ForeignKey(Degree, on_delete=models.CASCADE)
    position = models.ForeignKey(Position, on_delete=models.CASCADE)

    user = models.OneToOneField(UserAccount, related_name='teacher_profile', on_delete=models.CASCADE)

    def __str__(self):
        return f'Teacher information'


class StudentProfile(models.Model):
    student_card_id = models.BigIntegerField(validators=[partial(validate_number_len, digits_number=8)])
    user = models.OneToOneField(UserAccount, related_name='student_profile', on_delete=models.CASCADE)

    group = models.ForeignKey(Group, on_delete=models.CASCADE)

    def __str__(self):
        return f'Student information'


