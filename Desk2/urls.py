from django.contrib import admin
from django.urls import path, include
from courses import views
from rest_framework import routers

router = routers.DefaultRouter()
#router.register(r'courses', views.CourseViewSet)
router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('faculties/', views.FacultyView.as_view()),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
