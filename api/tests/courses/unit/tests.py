from django.test import TestCase, RequestFactory
from django.urls import resolve
from tests import utility_funcs
from courses.permissions import *


class PermissionTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.teacher, cls.student = utility_funcs.populate_users('teacher@gmail.com', 'student@gmail.com')
        cls.course = utility_funcs.populate_course(cls.teacher, [cls.student])


class IsGlobalTeacherTestCase(PermissionTestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.permission = IsGlobalTeacher()

    def test_success(self):
        request = self.factory.get('api/courses/1/')
        setattr(request, 'user', self.teacher)
        self.assertEquals(True, self.permission.has_permission(request, None))

    def test_fail(self):
        request = self.factory.get('api/courses/1/')
        setattr(request, 'user', self.student)
        self.assertEquals(False, self.permission.has_permission(request, None))
