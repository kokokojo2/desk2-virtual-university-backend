from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import resolve
from rest_framework.status import HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND
from rest_framework_simplejwt.authentication import JWTAuthentication, InvalidToken

from .models import Course
from .views import CourseMemberViewSet


class CourseMiddleware:
    """
    Activates if path has a parameter of a *course_id*. It does the following:

    * ensures that **Course** object with *pk* that equals to course_id exists. If not - returns 404 HTTP response.

    * ensures that user that wants to access a view is enrolled in the *Course* object
    (corresponding *CourseMember* object exists). If not - returns 403 HTTP response.

    * if two previous requirements are satisfied, sets corresponding *Course* and *CourseMember* objects as an
    attributes of the request object. They can be accessed in a view as *request.course* and *request.course_member*.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        jwt_authenticator = JWTAuthentication()
        user = request.user

        try:
            authentication_result = jwt_authenticator.authenticate(request)
            user = authentication_result[0] if authentication_result else request.user
        except InvalidToken:
            pass

        view, _, kwargs = resolve(request.path)  # to get url params of a path
        if user.is_authenticated and 'course_id' in kwargs.keys():
            course = get_object_or_404(Course, pk=kwargs['course_id'])

            course_member = course.get_course_member_if_exists(user)

            if not course_member:
                if view.__name__ is not CourseMemberViewSet.__name__ or request.method != 'POST':
                    return JsonResponse({'detail': 'You are not enrolled in this course.'}, status=HTTP_403_FORBIDDEN)

            setattr(request, 'course', course)
            setattr(request, 'course_member', course_member)

            if 'chapter_id' in kwargs.keys():
                chapter = course.get_chapter_if_exists(kwargs['chapter_id'])
                if not chapter:
                    return JsonResponse(
                        {'detail': f'This course does not have chapter with id {kwargs["chapter_id"]}.'},
                        status=HTTP_404_NOT_FOUND
                    )

                setattr(request, 'chapter', chapter)

                if 'task_id' in kwargs.keys():
                    task = chapter.get_task_if_exists(kwargs['task_id'])
                    if not task:
                        return JsonResponse(
                            {'detail': f'This course does not have a task with id {kwargs["task_id"]}.'},
                            status=HTTP_404_NOT_FOUND
                        )

                    setattr(request, 'task', task)

        response = self.get_response(request)

        return response
