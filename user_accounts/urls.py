from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView
from rest_framework.routers import DefaultRouter
from django.urls import path, include

from .views import AuthenticationViewSet, ChangePasswordView


auth_router = DefaultRouter()
auth_router.register(r'user', AuthenticationViewSet, basename='user')

urlpatterns = [
    path('token/obtain/', TokenObtainPairView.as_view(), name='jwt-obtain'),
    path('token/refresh/', TokenRefreshView.as_view(), name='jwt-refresh'),

    path('change-password/', ChangePasswordView.as_view(), name='change-password'),

    path('', include(auth_router.urls)),
]
