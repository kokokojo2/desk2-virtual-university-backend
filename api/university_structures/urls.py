from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import FacultyViewSet, DepartmentViewSet, GroupViewSet, DegreeViewSet, PositionViewSet, SpecialityViewSet

router = DefaultRouter()
router.register('faculties', FacultyViewSet)
router.register('departments', DepartmentViewSet)
router.register('groups', GroupViewSet)
router.register('degrees', DegreeViewSet)
router.register('positions', PositionViewSet)
router.register('specialities', SpecialityViewSet)


urlpatterns = [
    path('', include(router.urls)),
]
