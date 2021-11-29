from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('user_accounts.urls')),
    path('api/structures/', include('university_structures.urls')),
    path('api/', include('courses.urls')),
]
