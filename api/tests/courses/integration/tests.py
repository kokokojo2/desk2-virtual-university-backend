from django.test import Client
from tests import utility_funcs

from courses.models import *


class CourseViewSetTestCase(utility_funcs.AuthorizedViewSetTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.data_manager = utility_funcs.TestDataManager()
        cls.teacher = cls.data_manager.create_teacher('teacher@test.com')
        cls.student = cls.data_manager.create_student('student@test.com')
        cls.course = utility_funcs.populate_course(cls.teacher, [cls.student])

    def setUp(self):
        self.client = Client()
        self.course_json = {
                'title': 'Object-oriented programming',
                'description': 'Dummy desc.',
                'department': 1,
                'speciality': 1
            }

    def test_get_courses(self):
        response = self.get_response('course-list', self.teacher)
        self.assertEquals(self.course.title, response.data[0]['title'])

    def test_get_courses_enrolled(self):
        response = self.get_response('course-list', self.student, data={'enrolled': 'true'})
        self.assertEquals(self.course.title, response.data[0]['title'])

    def test_create_course(self):
        response = self.get_response(
            'course-list',
            self.teacher,
            data=self.course_json,
            method='POST',
            expected_status_code=201
        )

        self.assertEquals(self.course_json['title'], response.data['title'])
        self.course_json['id'] = response.data['id']

    def test_permission_to_create_course(self):
        response = self.get_response(
            'course-list',
            self.student,
            data=self.course_json,
            method='POST',
            expected_status_code=403
        )

        self.assertEquals('permission_denied', response.data['detail'].code)

    def test_update_course(self):
        updated_course = self.course_json
        updated_course['title'] = 'Math'

        response = self.get_response(
            'course-detail',
            self.teacher,
            pk=1,
            data=updated_course,
            method='PUT',
            expected_status_code=200
        )

        self.assertEquals(updated_course['title'], response.data['title'])

    def test_update_permissions(self):
        updated_course = self.course_json
        updated_course['title'] = 'Math'
        not_owner_but_teacher = self.data_manager.create_teacher('teacher1@test.com')

        response = self.get_response(
            'course-detail',
            not_owner_but_teacher,
            pk=1,
            data=updated_course,
            method='PUT',
            expected_status_code=403
        )

        self.assertEquals('permission_denied', response.data['detail'].code)

    def test_delete_course(self):
        self.get_response(
            'course-detail',
            self.teacher,
            pk=1,
            method='DELETE',
            expected_status_code=204
        )

        self.assertRaises(Course.DoesNotExist, Course.objects.get, pk=1)
