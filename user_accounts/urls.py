from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView
from rest_framework.routers import DefaultRouter
from django.urls import path, include

from .views import AuthenticationViewSet


auth_router = DefaultRouter()
auth_router.register(r'user', AuthenticationViewSet, basename='user')

urlpatterns = [
    path('token/obtain/', TokenObtainPairView.as_view(), name='jwt-obtain'),
    path('token/refresh/', TokenRefreshView.as_view(), name='jwt-refresh'),

    path('', include(auth_router.urls)),
]
