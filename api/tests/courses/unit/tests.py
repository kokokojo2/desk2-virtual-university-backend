from django.test import TestCase
from tests import utils


class PermissionTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.student, cls.teacher = utils.populate_users()
        cls.course = utils.populate_course(cls.teacher, cls.student)
