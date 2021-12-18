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


class IsGlobalTeacherOrReadOnlyTestCase(PermissionTestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.permission = IsGlobalTeacherOrReadOnly()

    def test_success(self):
        request = self.factory.get('api/courses/1/')
        setattr(request, 'user', self.teacher)
        self.assertEquals(True, self.permission.has_permission(request, None))

    def test_fail(self):
        request = self.factory.post('api/courses/1/')
        setattr(request, 'user', self.student)
        self.assertEquals(False, self.permission.has_permission(request, None))


class IsTeacherTestCase(PermissionTestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.permission = IsTeacher()

    def test_success(self):
        request = self.factory.get('api/courses/1/')
        setattr(request, 'user', self.teacher)
        setattr(request, 'course_member', self.course.get_course_member_if_exists(self.teacher))
        self.assertEquals(True, self.permission.has_permission(request, None))

    def test_fail(self):
        request = self.factory.post('api/courses/1/')
        setattr(request, 'user', self.student)
        setattr(request, 'course_member', self.course.get_course_member_if_exists(self.student))
        self.assertEquals(False, self.permission.has_permission(request, None))


class IsStudentTestCase(PermissionTestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.permission = IsStudent()

    def test_success(self):
        request = self.factory.get('api/courses/1/')
        setattr(request, 'user', self.teacher)
        setattr(request, 'course_member', self.course.get_course_member_if_exists(self.student))
        self.assertEquals(True, self.permission.has_permission(request, None))

    def test_fail(self):
        request = self.factory.post('api/courses/1/')
        setattr(request, 'user', self.student)
        setattr(request, 'course_member', self.course.get_course_member_if_exists(self.teacher))
        self.assertEquals(False, self.permission.has_permission(request, None))
