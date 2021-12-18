#!/usr/bin/env python
# coding: utf-8

import subprocess as sc
import time
import re
import requests
import json
import psycopg2

# defining endpoints
root_endpoint = "http://localhost:8000/api/"
auth_endpoint = root_endpoint + 'auth/'
course_endpoint = root_endpoint + 'courses/'
course_member_endpoint = root_endpoint + '1/course_members/'
chapter_endpoint = root_endpoint + '1/chapters/'
material_endpoint = root_endpoint + '1/1/materials/'
task_endpoint = root_endpoint + '1/1/tasks/'
student_work_endpoint = root_endpoint + '1/1/tasks/1/student-works/'
submit_endpoint = student_work_endpoint + '1/submit/'
grades_endpoint = root_endpoint + '1/grades/'


# get docker-compose logs (from a specific service)
def get_logs(tail='50', svc=''):
    cmd = ['docker-compose', 'logs', '--no-color', f'--tail={tail}']
    if svc:
        cmd.append('--no-log-prefix')
        cmd.append(svc)
    return sc.run(cmd, capture_output=True)

def poll_logs_until_match(pattern, tail='50', svc='', timeout=30, supress_logs=False):
    while timeout > 0:
        logs = get_logs(tail=tail, svc=svc).stdout.decode()
        matches = re.findall(pattern, logs)
        if matches:
            return matches
        if not supress_logs:
            print(f"Couldn't find a match for pattern '{pattern}'; sleeping...", flush=True)
        time.sleep(5)
        timeout -= 1
    return []       

# get a 2FA or email-confirmation token printed to console
def get_last_email_token():
    email_code_matches = poll_logs_until_match("((To finish registration, please, confirm your email by entering the following code:)|(If this is you, please, use the code below to finish logging in\.))\n\n\s+(\w+)", svc='desk2-api', timeout=2)
    if not email_code_matches:
        return None
    return email_code_matches[-1][3][-7:]


def stop_services():
    print('Stopping services and exiting...', flush=True)
    sc.run(['docker-compose', 'down'])

def start_services():
    print("Running 'docker-compose up -d postgres'...", flush=True)
    sc.run(['docker-compose', 'up', '-d', 'postgres'], capture_output=True)
    print("Running 'docker-compose up -d redis'...", flush=True)
    sc.run(['docker-compose', 'up', '-d', 'redis'], capture_output=True)
    postgres_ready = poll_logs_until_match('database system is ready to accept connections', svc='postgres')
    if not postgres_ready:
        print("Couldn't start postgres", flush=True)
        stop_services()
        return False
    
    print("Running 'docker-compose up -d desk2-api'...", flush=True)
    sc.run(['docker-compose', 'up', '-d', 'desk2-api'], capture_output=True)
    
    res = poll_logs_until_match('Starting development server', svc='desk2-api')
    if not res:
        print("ERROR: couldn't start services", flush=True)
        stop_services()
        return False
    
    unapplied_migrations = poll_logs_until_match('unapplied migration', tail='all', svc='desk2-api', timeout=1, supress_logs=True)
    if unapplied_migrations:
        print("ERROR: couldn't apply migrations", flush=True)
        stop_services()
        return False
        
    print('Started services', flush=True)
    return True


# data shared between tests
test_common_data = {
    "passed": []
}

class TestCase:
    def __init__(self, name, func, prerequisites_passed=[]):
        self.name = name
        self.func = func
        self.prerequisites_passed = prerequisites_passed
        
    def run(self):
        print(f'Running "{self.name}" test scenario...', flush=True)
        try:
            prerequisites_failed = [x for x in self.prerequisites_passed if x not in test_common_data["passed"]]
            prerequisites_met = len(prerequisites_failed) == 0
            if not prerequisites_met:
                print("Test failed: the following prerequisite tests haven't passed:", flush=True)
                print("\n".join(prerequisites_failed), flush=True)
                return False
            res = self.func()
            if res:
                print('Test successful', flush=True)
                test_common_data["passed"].append(self.name)
            else:
                print('Test failed', flush=True)
            return res
        except Exception as e:
            print(f'Test failed with an exception:\n\t{e}', flush=True)
            return False


def assert_response_code(response, expected_code, action_description):
    res = True
    if response.status_code != expected_code:
        print(f'Expected status code {expected_code} when {action_description}, received', response.status_code, flush=True)
        print(f'Response json:\n\t{response.json()}', flush=True)
        res = False
    assert res


def populate_test_db():
    print('Populating a test database', flush=True)
    try:
        conn = psycopg2.connect(
            database='university',
            user='postgres',
            password='postgres',
            host='127.0.0.1',
            port=5432
        )
        cur = conn.cursor()
        # add faculty
        cur.execute('INSERT INTO university_structures_faculty(title, description, abbreviation) VALUES (%s, %s, %s)',
                    ("Institute for Applied System Analysis", "The best", "IASA"))

        # add department
        cur.execute('INSERT INTO university_structures_department(title, description, faculty_id, abbreviation) VALUES (%s, %s, %s, %s)',
                    ("Computed Aided Design", "It's ours", 1, "CAD"))

        # add specialty
        cur.execute('INSERT INTO university_structures_speciality(title, code) VALUES (%s, %s)',
                    ("Computer Science", 122))

        # add group
        cur.execute('INSERT INTO university_structures_group(name, study_year, department_id, speciality_id) VALUES (%s, %s, %s, %s)',
                    ("DA-92", 3, 1, 1))
        
        # add scientific degree
        cur.execute("INSERT INTO university_structures_degree(name) VALUES ('PhD')")
        
        # add teacher position
        cur.execute("INSERT INTO university_structures_position(name) VALUES ('TA')")

        conn.commit()
    except Exceptionception as e:
        print(f"Failed to populate a database:\n\t{e}", flush=True)
        conn.rollback()
        return False
    finally:
        conn.close()
    return True


# test scenarios
def student_registration_should_succeed():
    user_registration_obj = {
        "first_name": "Yuuichi",
        "last_name": "Onodera",
        "email": "asanoinio@yahoo.com",
        "profile_type": "student",
        "password": "JustAsimplePasasfj1",
        "email-token": "",
        "department": 1,
        "group": 1,
        "student_card_id": 12345678
    }
    
    email_token_response = requests.post(auth_endpoint + 'token/send-token/email-confirm/', data={"email": user_registration_obj["email"]})
    assert_response_code(email_token_response, 200, 'asking for an email token')
    
    time.sleep(2)
    
    user_registration_obj["email-token"] = get_last_email_token()
    user_registration_response = requests.post(auth_endpoint + 'user/', data=json.dumps(user_registration_obj), headers={'content-type': 'application/json'})
    assert_response_code(user_registration_response, 201, 'registering a user')
    
    # asking for a 2FA code
    jwt_token_data = {
        "email": user_registration_obj["email"],
        "password": user_registration_obj["password"]
    }

    first_jwt_response = requests.post(auth_endpoint + 'token/obtain/', data=json.dumps(jwt_token_data), headers={'content-type': 'application/json'})
    assert_response_code(first_jwt_response, 401, 'asking for a JWT without a 2FA code')
    
    # using a 2FA code in a JWT request
    time.sleep(2)
    jwt_token_data['2FA_code'] = get_last_email_token()
    second_jwt_response = response = requests.post(auth_endpoint + 'token/obtain/', data=json.dumps(jwt_token_data), headers={'content-type': 'application/json'})
    assert_response_code(second_jwt_response, 200, 'asking for a JWT with a 2FA code')
    
    jwt = response.json()['access']
    get_user_response = requests.get(auth_endpoint + 'user/', headers={'Authorization': f'Bearer {jwt}'})
    assert_response_code(get_user_response, 200, 'getting a user with JWT')
    
    test_common_data["student_jwt"] = jwt
    test_common_data["student_obj"] = user_registration_obj
    
    return True

def teacher_registration_should_succeed():
    teacher_registration_object = {
        "first_name": "Eikichi",
        "last_name": "Onizuka",
        "email": "tofujisawa@yahoo.com",
        "profile_type": "teacher",
        "password": "__23535somecommonsensE55",
        "email-token": "",
        "department": 1,
        "position": 1,
        "scientific_degree": 1
    }
    
    email_token_response = requests.post(auth_endpoint + 'token/send-token/email-confirm/', data={"email": teacher_registration_object["email"]})
    assert_response_code(email_token_response, 200, 'asking for an email token')
    
    time.sleep(2)
    
    teacher_registration_object["email-token"] = get_last_email_token()
    user_registration_response = requests.post(auth_endpoint + 'user/', data=json.dumps(teacher_registration_object), headers={'content-type': 'application/json'})
    assert_response_code(user_registration_response, 201, 'registering a user')
    
    # asking for a 2FA code
    jwt_token_data = {
        "email": teacher_registration_object["email"],
        "password": teacher_registration_object["password"]
    }

    first_jwt_response = requests.post(auth_endpoint + 'token/obtain/', data=json.dumps(jwt_token_data), headers={'content-type': 'application/json'})
    assert_response_code(first_jwt_response, 401, 'asking for a JWT without a 2FA code')
    
    # using a 2FA code in a JWT request
    time.sleep(2)
    jwt_token_data['2FA_code'] = get_last_email_token()
    second_jwt_response = response = requests.post(auth_endpoint + 'token/obtain/', data=json.dumps(jwt_token_data), headers={'content-type': 'application/json'})
    assert_response_code(second_jwt_response, 200, 'asking for a JWT with a 2FA code')
    
    jwt = response.json()['access']
    get_user_response = requests.get(auth_endpoint + 'user/', headers={'Authorization': f'Bearer {jwt}'})
    assert_response_code(get_user_response, 200, 'getting a user with JWT')
    
    test_common_data["teacher_jwt"] = jwt
    test_common_data["teacher_obj"] = teacher_registration_object
    
    return True

def course_creation_should_succeed():
    course_creation_obj = {
        "title": "Discrete Maths",
        "description": "Test course lalala",
        "department": 1,
        "speciality": 1
    }
    
    jwt = test_common_data["teacher_jwt"]
    course_creation_response = requests.post(course_endpoint, data=json.dumps(course_creation_obj), 
                                             headers={'content-type': 'application/json', 'Authorization': f'Bearer {jwt}'})
    
    assert_response_code(course_creation_response, 201, 'creating a course')
    
    get_courses_response = requests.get(course_endpoint, headers={'Authorization': f'Bearer {jwt}'})
    assert_response_code(get_courses_response, 200, 'getting a list of courses')

    if not course_creation_response.json() in get_courses_response.json():
        print("Couldn't find a newly created course among the existing courses", flush=True)
        return False
    
    return True

def course_member_addition_should_succeed():
    student = test_common_data["student_obj"]
    student_jwt = test_common_data["student_jwt"]
    member_addition_obj = {
        "email": student["email"],
        "member_type": "student"
    }
    
    teacher_jwt = test_common_data["teacher_jwt"]
    member_addition_response = requests.post(course_member_endpoint + 'add-members/', data=json.dumps(member_addition_obj), 
                                             headers={'content-type': 'application/json', 'Authorization': f'Bearer {teacher_jwt}'})
    
    assert_response_code(member_addition_response, 204, 'adding a course member')
    
    get_course_members_request = requests.get(course_member_endpoint, headers={'Authorization': f'Bearer {teacher_jwt}'})
    assert_response_code(get_course_members_request, 200, 'getting course members')

    if len(get_course_members_request.json()) < 2:
        print(f'Got {len(get_course_members_request.json())} course members, expected at least 2', flush=True)
        return False
    
    get_enrolled_courses_response = requests.get(course_endpoint + '?enrolled=true', headers={'Authorization': f'Bearer {student_jwt}'})
    assert_response_code(get_enrolled_courses_response, 200, 'getting enrolled courses')
    
    if len(get_enrolled_courses_response.json()) < 1:
        print(f'Got {len(get_enrolled_courses_response.json())} enrolled courses, expected at least 1', flush=True)
        return False
    
    return True

def chapter_addition_should_succeed():
    chapter_creation_obj = {
        "title": "Boolean Algebra",
        "description": "Boolean algebra is the branch of algebra in which the values of the variables are the truth values true and false, usually denoted 1 and 0",
        "course": 1
    }

    teacher_jwt = test_common_data["teacher_jwt"]
    chapter_creation_response = requests.post(chapter_endpoint, data=json.dumps(chapter_creation_obj), 
                                             headers={'content-type': 'application/json', 'Authorization': f'Bearer {teacher_jwt}'})

    assert_response_code(chapter_creation_response, 201, 'creating a chapter')
    
    return True

def material_addition_should_succeed():
    material_creation_obj = {
        "title": "Унарні та бінарні операції",
        "body": "A & B",
        "created_at": "2021-11-18T10:08:00.631458Z",
        "edited_at": "2021-11-18T10:08:00.631458Z",
        "published_at": "2021-11-06T18:01:54.826418Z"
    }

    teacher_jwt = test_common_data["teacher_jwt"]
    material_creation_response = requests.post(material_endpoint, data=json.dumps(material_creation_obj), 
                                             headers={'content-type': 'application/json', 'Authorization': f'Bearer {teacher_jwt}'})

    assert_response_code(material_creation_response, 201, 'adding a material')
    
    return True

def task_creation_should_succeed():
    task_creation_obj = {
        "title": "Proove 4 axioms of boolean algebra using the truth table",
        "body": "Not hard at all",
        "published_at": "2021-11-06T18:01:54.826418Z",
        "deadline": "2021-11-06T18:01:54.826418Z",
        "max_grade": 5
    }

    teacher_jwt = test_common_data["teacher_jwt"]
    task_creation_response = requests.post(task_endpoint, data=json.dumps(task_creation_obj), 
                                             headers={'content-type': 'application/json', 'Authorization': f'Bearer {teacher_jwt}'})

    assert_response_code(task_creation_response, 201, 'adding a task')
    
    return True

def student_work_creation_and_submission_should_succeed():
    student_work_creation_obj = {
        "answer": "I wrote a script to do that, lol"
    }
    student_jwt = test_common_data["student_jwt"]
    
    student_work_creation_response = requests.post(student_work_endpoint, data=json.dumps(student_work_creation_obj), 
                                             headers={'content-type': 'application/json', 'Authorization': f'Bearer {student_jwt}'})

    assert_response_code(student_work_creation_response, 201, 'creating a student work')
    
    submit_student_work_response = requests.post(submit_endpoint, headers={'Authorization': f'Bearer {student_jwt}'})
    assert_response_code(student_work_creation_response, 201, 'submitting a student work')
    
    return True

def student_work_grading_should_succeed():
    grade_creation_object = {
        "amount": 4,
        "work": 1
    }

    teacher_jwt = test_common_data["teacher_jwt"]
    grade_creation_response = requests.post(grades_endpoint, data=json.dumps(grade_creation_object), 
                                             headers={'content-type': 'application/json', 'Authorization': f'Bearer {teacher_jwt}'})

    assert_response_code(grade_creation_response, 201, 'grading a student work')
    
    student_jwt = test_common_data["student_jwt"]
    get_grades_response = requests.get(grades_endpoint, headers={'Authorization': f'Bearer {student_jwt}'})
    if not any([x["work"] == 1 for x in get_grades_response.json()]):
        print("Student couldn't see a grade for his work", flush=True)
        return False
    
    return True


test_cases = [
    TestCase('Student registration', student_registration_should_succeed),
    TestCase('Teacher registration', teacher_registration_should_succeed),
    TestCase('Course creation', course_creation_should_succeed, prerequisites_passed=['Teacher registration']),
    TestCase('Course member addition', course_member_addition_should_succeed, prerequisites_passed=['Student registration', 'Course creation']),
    TestCase('Chapter creation', chapter_addition_should_succeed, prerequisites_passed=['Course creation']),
    TestCase('Material addition', material_addition_should_succeed, prerequisites_passed=['Chapter creation']),
    TestCase('Task creation', task_creation_should_succeed, prerequisites_passed=['Chapter creation']),
    TestCase('Student work submission', student_work_creation_and_submission_should_succeed, prerequisites_passed=['Task creation', 'Course member addition']),
    TestCase('Student work grading', student_work_grading_should_succeed, prerequisites_passed=['Student work submission'])
]


# start services, run test cases, stop services
def run_tests(stop_services_at_cleanup=True):
    if not start_services():
        return
    if not populate_test_db():
        return
    
    try:
        test_common_data = {
            "passed": []
        }
        test_results = [x.run() for x in test_cases]
        failed_count = len([x for x in test_results if x == False])
        if failed_count:
            print(f'Failed {failed_count} out of {len(test_results)} test scenarios!', flush=True)
        else:
            print(f'Successfully ran {len(test_results)} test(s)', flush=True)
    except Exception as e:
        print(f'Failed. Caught an exception when running test scenarios:\n\t{e}', flush=True)
    finally:
        if stop_services_at_cleanup:
            stop_services()

run_tests(stop_services_at_cleanup=True)