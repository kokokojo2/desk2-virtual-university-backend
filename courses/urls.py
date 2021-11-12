from django.urls import path, include
from rest_framework.routers import DefaultRouter

from courses.views import CourseViewSet, GradeViewSet, TaskViewSet, ChapterViewSet, CourseMemberViewSet, \
    AttachmentViewSet, StudentWorkViewSet, MaterialViewSet

display_per_course_router = DefaultRouter()
display_per_course_router.register('course_members', CourseMemberViewSet)
display_per_course_router.register('chapters', ChapterViewSet)
display_per_course_router.register('materials', MaterialViewSet)
display_per_course_router.register('tasks', TaskViewSet)
display_per_course_router.register('student_works', StudentWorkViewSet)
display_per_course_router.register('grades', GradeViewSet)
display_per_course_router.register('attachments', AttachmentViewSet)

courses_router = DefaultRouter()
courses_router.register('courses', CourseViewSet)

urlpatterns = [
    path('', include(courses_router.urls)),
    path('<int:course_id>/', include(display_per_course_router.urls)),
]
