from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView
from rest_framework.routers import DefaultRouter
from django.urls import path, include

from .views import AuthenticationViewSet, ChangePasswordView, CheckTokenView, SendTokenView, TokenObtainView, \
    ChangeEmailView, ResetPasswordView

app_name = 'user_account'

auth_router = DefaultRouter()
auth_router.register(r'user', AuthenticationViewSet, basename='user')

urlpatterns = [
    path('token/obtain/', TokenObtainView.as_view(), name='jwt-obtain'),
    path('token/refresh/', TokenRefreshView.as_view(), name='jwt-refresh'),

    path('', include(auth_router.urls)),
    path('user/change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('user/change-email/', ChangeEmailView.as_view(), name='change-email'),

    path('password-reset/', ResetPasswordView.as_view(), name='reset-password'),

    path('token/check-token/<token_type>/', CheckTokenView.as_view(), name='check-token'),
    path('token/send-token/<token_type>/', SendTokenView.as_view(), name='send-token'),
]
