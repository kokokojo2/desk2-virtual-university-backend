from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView

from django.urls import path


urlpatterns = [
    path('token/obtain/', TokenObtainPairView.as_view(), name='jwt-obtain'),
    path('token/refresh/', TokenRefreshView.as_view(), name='jwt-refresh'),


]
