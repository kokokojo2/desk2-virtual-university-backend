from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager


class UserAccountManager(BaseUserManager):
    def create_user(self, email, password, first_name, last_name, middle_name):
        if not all([email, password, first_name, last_name, middle_name]):
            raise ValueError("Some of the required arguments are None, please, specify not None arguments.")

        # TODO: add other fields normalization
        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            middle_name=middle_name,
        )
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password, first_name, last_name, middle_name):
        if not all([email, password, first_name, last_name, middle_name]):
            raise ValueError("Some of the required arguments are None, please, specify not None arguments.")

        # TODO: add fields normalization
        user = self.create_user(email, password, first_name, last_name, middle_name)
        user.is_admin = True
        user.save(using=self._db)

        return user


class UserAccount(AbstractBaseUser):
    first_name = models.CharField(max_length=128)
    last_name = models.CharField(max_length=128)
    middle_name = models.CharField(max_length=128)
    email = models.EmailField(unique=True, max_length=256)

    created = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    # TODO: add foreign key to a department
    USERNAME_FIELD = 'email'

    objects = UserAccountManager()

    @property
    def is_staff(self):
        return self.is_admin

    def has_module_perms(self, app_label):
        return self.is_admin

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def __str__(self):
        return f'{self.last_name} {self.first_name}'
