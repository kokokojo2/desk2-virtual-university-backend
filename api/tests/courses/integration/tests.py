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
            'department': self.data_manager.departments[0].pk,
            'speciality': self.data_manager.specialities[0].pk
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
            url_params={'pk': self.course.pk},
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
            url_params={'pk': self.course.pk},
            data=updated_course,
            method='PUT',
            expected_status_code=403
        )

        self.assertEquals('permission_denied', response.data['detail'].code)

    def test_delete_course(self):
        temp_course = utility_funcs.populate_course(self.teacher, [])
        self.get_response(
            'course-detail',
            self.teacher,
            url_params={'pk': temp_course.pk},
            method='DELETE',
            expected_status_code=204
        )

        self.assertRaises(Course.DoesNotExist, Course.objects.get, pk=temp_course.pk)

class TaskViewSetTestCase(utility_funcs.AuthorizedViewSetTestCase):

    @classmethod
    def setUpTestData(cls):
        cls.data_manager = utility_funcs.TestDataManager()
        cls.teacher = cls.data_manager.create_teacher('teacher@test.com')
        cls.student = cls.data_manager.create_student('student@test.com')
        cls.course = utility_funcs.populate_course(cls.teacher, [cls.student])
        cls.chapter = cls.data_manager.create_chapter(cls.course)
        cls.task = cls.data_manager.create_task(cls.chapter,
                                                        cls.course.get_course_member_if_exists(cls.teacher),
                                                        is_archived=True)

    def setUp(self):
        self.task_json = {
            "title": "Task 3 chm",
            "body": "test",
            "published_at": timezone.now(),
            "deadline": timezone.now(),
            "max_grade": 12
        }

    def test_get_task(self):
        response = self.get_response(
            'task-list',
            self.teacher,
            url_params={'course_id': self.course.pk, 'chapter_id': self.chapter.pk},
        )

        self.assertEquals(self.task.pk, response.data[0]['id'])

    def test_create_task(self):
        self.get_response(
            'task-list',
            self.teacher,
            url_params={'course_id': self.course.pk, 'chapter_id': self.chapter.pk},
            expected_status_code=201,
            data=self.task_json,
            method='POST'
        )

    def test_create_task_student(self):
        self.get_response(
            'task-list',
            self.student,
            url_params={'course_id': self.course.pk, 'chapter_id': self.chapter.pk},
            expected_status_code=403,
            data=self.task_json,
            method='POST'
        )

    def test_get_inactive_task_student(self):
        self.task.is_archived = True
        self.task.save()

        response = self.get_response(
            'task-list',
            self.student,
            url_params={'course_id': self.course.pk, 'chapter_id': self.chapter.pk},
        )

        self.assertEquals(0, len(response.data))

        self.task.is_archived = False
        self.task.save()

    def test_partial_update_task(self):
        update_data = {'title': 'Updated task'}
        response = self.get_response(
            'task-detail',
            self.teacher,
            url_params={'course_id': self.course.pk, 'chapter_id': self.chapter.pk, 'pk': self.task.pk},
            expected_status_code=200,
            data=update_data,
            method='PATCH'
        )

        self.assertEquals(update_data['title'], response.data['title'])

    def test_delete_task_teacher(self):
        temp_task = self.data_manager.create_task(self.chapter, self.course.get_course_member_if_exists(self.teacher))

        self.get_response(
            'task-detail',
            self.teacher,
            url_params={'course_id': self.course.pk, 'chapter_id': self.chapter.pk, 'pk': temp_task.pk},
            expected_status_code=204,
            method='DELETE'
        )

        self.assertRaises(Task.DoesNotExist, Task.objects.get, pk=temp_task.pk)



class ChapterViewSetTestCase(utility_funcs.AuthorizedViewSetTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.data_manager = utility_funcs.TestDataManager()
        cls.teacher = cls.data_manager.create_teacher('teacher@test.com')
        cls.student = cls.data_manager.create_student('student@test.com')
        cls.course = utility_funcs.populate_course(cls.teacher, [cls.student])
        cls.chapter = cls.data_manager.create_chapter(cls.course)
        cls.material = cls.data_manager.create_material(cls.chapter, cls.course.get_course_member_if_exists(cls.teacher), is_archived=True)

    def setUp(self):
        self.edit_chapter_data = {'title': 'Edited'}

    def test_get_chapter(self):
        response = self.get_response(
            'chapter-list',
            self.teacher,
            url_params={'course_id': self.course.pk},
        )

        self.assertEquals(self.chapter.pk, response.data[0]['id'])

    def test_get_chapter_detail(self):
        response = self.get_response(
            'chapter-detail',
            self.teacher,
            url_params={'course_id': self.course.pk, 'pk': self.chapter.pk},
        )

        self.assertEquals(self.chapter.pk, response.data['id'])

    def test_get_chapter_that_does_not_exist(self):
        self.get_response(
            'chapter-detail',
            self.teacher,
            url_params={'course_id': self.course.pk, 'pk': 2001},
            expected_status_code=404
        )

    def test_get_chapter_with_inactive_materials_teacher(self):
        response = self.get_response(
            'chapter-detail',
            self.teacher,
            url_params={'course_id': self.course.pk, 'pk': self.chapter.pk},
            expected_status_code=200
        )

        self.assertEquals(self.material.pk, response.data['material_set'][0]['id'])

    def test_get_chapter_with_active_materials_teacher(self):
        response = self.get_response(
            'chapter-detail',
            self.student,
            url_params={'course_id': self.course.pk, 'pk': self.chapter.pk},
            expected_status_code=200
        )

        self.assertRaises(IndexError, response.data['material_set'].__getitem__, 0)

    def test_p_edit_chapter(self):
        response = self.get_response(
            'chapter-detail',
            self.teacher,
            url_params={'course_id': self.course.pk, 'pk': self.chapter.pk},
            expected_status_code=200,
            data=self.edit_chapter_data,
            method='PATCH'
        )

        self.assertEquals(self.edit_chapter_data['title'], response.data['title'])

    def test_edit_chapter_student(self):
        self.get_response(
            'chapter-detail',
            self.student,
            url_params={'course_id': self.course.pk, 'pk': self.chapter.pk},
            expected_status_code=403,
            data=self.edit_chapter_data,
            method='PATCH'
        )

    def test_delete_chapter(self):
        self.get_response(
            'chapter-detail',
            self.teacher,
            url_params={'course_id': self.course.pk, 'pk': self.chapter.pk},
            expected_status_code=204,
            method='DELETE'
        )

        self.assertRaises(Chapter.DoesNotExist, Chapter.objects.get, pk=self.chapter.pk)