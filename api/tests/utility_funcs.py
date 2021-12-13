from university_structures import models as university_structures
from user_accounts import models as user_accounts
from courses import models as courses


def populate_users():
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
        email='teacher@test.com',
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
        email='student@test.com',
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
