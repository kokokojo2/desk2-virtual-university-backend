from university_structures import models as university_structures
from user_accounts import models as user_accounts
from courses import models as courses
from django.utils import timezone
from django.urls import reverse
from django.test import TestCase
from rest_framework_simplejwt.tokens import RefreshToken


class TestDataManager:
    def __init__(self):
        self.faculties = []
        self.departments = []
        self.degrees = []
        self.positions = []
        self.specialities = []
        self.groups = []
        self.create_faculty()
        self.create_speciality()
        self.create_degree()
        self.create_position()
        self.create_department(self.faculties[0])
        self.create_group(self.departments[0], self.specialities[0])

    def create_teacher(self, email, **kwargs):
        department = kwargs.pop('department', self.departments[0])
        degree = kwargs.pop('degree', self.degrees[0])
        position = kwargs.pop('position', self.positions[0])

        teacher = user_accounts.UserAccount.objects.create(
            first_name='John',
            last_name='Loe',
            email=email,
            department=department
        )

        user_accounts.TeacherProfile.objects.create(
            position=position,
            scientific_degree=degree,
            user=teacher
        )

        return teacher

    def create_student(self, email, **kwargs):
        department = kwargs.pop('department', self.departments[0])
        group = kwargs.pop('group', self.groups[0])

        student = user_accounts.UserAccount.objects.create(
            first_name='Dane',
            last_name='Green',
            email=email,
            department=department
        )

        user_accounts.StudentProfile.objects.create(
            user=student,
            group=group,
            student_card_id=11122233
        )

        return student

    def create_faculty(self, **kwargs):
        if not kwargs:
            faculty = university_structures.Faculty.objects.create(
                title='Institute for Applied System Analysis',
                description='Dummy desc.',
                abbreviation='IASA'
            )
        else:
            faculty = university_structures.Faculty.objects.create(**kwargs)

        self.faculties.append(faculty)

    def create_department(self, faculty, **kwargs):
        if not kwargs:
            department = university_structures.Department.objects.create(
                title='Cathedra of System Design',
                description='Dummy desc.',
                faculty=faculty,
                abbreviation='SP'
            )
        else:
            department = university_structures.Department.objects.create(faculty=faculty, **kwargs)

        self.departments.append(department)

    def create_degree(self, **kwargs):
        if not kwargs:
            scientific_degree = university_structures.Degree.objects.create(
                name='Doctor'
            )
        else:
            scientific_degree = university_structures.Degree.objects.create(**kwargs)

        self.degrees.append(scientific_degree)

    def create_position(self, **kwargs):
        if not kwargs:
            position = university_structures.Position.objects.create(
                name='Doctor'
            )
        else:
            position = university_structures.Position.objects.create(**kwargs)

        self.positions.append(position)

    def create_speciality(self, **kwargs):
        if not kwargs:
            speciality = university_structures.Speciality.objects.create(
                title='Computer Science',
                code=122
            )
        else:
            speciality = university_structures.Speciality.objects.create(**kwargs)

        self.specialities.append(speciality)

    def create_group(self, department, speciality, **kwargs):
        if not kwargs:
            group = university_structures.Group.objects.create(
                name='ДА-92',
                study_year=3,
                department=department,
                speciality=speciality
            )
        else:
            group = university_structures.Group.objects.create(department=department, speciality=speciality, **kwargs)

        self.groups.append(group)


def populate_users(teacher_email, student_email):
    faculty = university_structures.Faculty.objects.create(
        title='Institute for Applied System Analysis',
        description='Dummy desc.',
        abbreviation='IASA'
    )

    department = university_structures.Department.objects.create(
        title='Cathedra of System Design',
        description='Dummy desc.',
        faculty=faculty,
        abbreviation='SP'
    )

    scientific_degree = university_structures.Degree.objects.create(
        name='Doctor'
    )

    position = university_structures.Position.objects.create(
        name='Lecturer'
    )

    teacher = user_accounts.UserAccount.objects.create(
        first_name='John',
        last_name='Loe',
        email=teacher_email,
        department=department
    )

    user_accounts.TeacherProfile.objects.create(
        position=position,
        scientific_degree=scientific_degree,
        user=teacher
    )

    student = user_accounts.UserAccount.objects.create(
        first_name='Dane',
        last_name='Green',
        email=student_email,
        department=department
    )

    speciality = university_structures.Speciality.objects.create(
        title='Computer Science',
        code=122
    )

    group = university_structures.Group.objects.create(
        name='ДА-92',
        study_year=3,
        department=department,
        speciality=speciality
    )

    user_accounts.StudentProfile.objects.create(
        user=student,
        group=group,
        student_card_id=11122233
    )

    return teacher, student


def populate_course(owner, students):
    course = courses.Course.objects.create(
        title='Linear Algebra',
        description='Test desc.',
        owner=owner,
    )

    courses.CourseMember.objects.create(
        user=owner,
        course=course,
        role=courses.CourseMember.TEACHER
    )

    for student in students:
        courses.CourseMember.objects.create(
            user=student,
            course=course,
            role=courses.CourseMember.STUDENT
        )

    return course


def populate_course_content(course, teacher, student):
    chapter = courses.Chapter.objects.create(
        title='Test chapter',
        description='The desc.',
        course=course
    )

    task = courses.Task.objects.create(
        title='Test task',
        body='Test body.',
        published_at=timezone.now(),
        chapter=chapter,
        author=teacher,
        max_grade=12,
        deadline=timezone.now()
    )

    student_work = courses.StudentWork.objects.create(
        task=task,
        owner=student,
    )

    return task, student_work


class ViewSetTestCase(TestCase):
    def _get_response(self, url_name, **kwargs):
        data = kwargs.pop('data', {})
        method = kwargs.pop('method', 'GET')
        expected_status_code = kwargs.pop('expected_status_code', 200)
        pk = kwargs.pop('pk', None)
        url = reverse(url_name) if not pk else reverse(url_name, kwargs={'pk': pk})

        func = self.client.get
        if method == 'POST':
            func = self.client.post
            kwargs['content_type'] = 'application/json'

        if method == 'PUT':
            func = self.client.put
            kwargs['content_type'] = 'application/json'

        if method == 'DELETE':
            func = self.client.delete

        response = func(url, data, **kwargs)
        self.assertEquals(expected_status_code, response.status_code)

        return response


class AuthorizedViewSetTestCase(ViewSetTestCase):
    def get_response(self, url_name, user, **kwargs):
        token = getattr(self, 'access_token', None)
        if not token:
            refresh = RefreshToken.for_user(user)
            self.token = str(refresh.access_token)

        return self._get_response(url_name, HTTP_AUTHORIZATION=f'Bearer {self.token}', **kwargs)
