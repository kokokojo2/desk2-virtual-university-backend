from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView
from rest_framework.routers import DefaultRouter
from django.urls import path, include

from .views import AuthenticationViewSet, ChangePasswordView, CheckTokenView, SendTokenView, TokenObtainView, \
    ConfirmEmailView, ChangeEmailView

app_name = 'user_account'

auth_router = DefaultRouter()
auth_router.register(r'user', AuthenticationViewSet, basename='user')

urlpatterns = [
    path('token/obtain/', TokenObtainView.as_view(), name='jwt-obtain'),
    path('token/refresh/', TokenRefreshView.as_view(), name='jwt-refresh'),

    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('change-email/', ChangeEmailView.as_view(), name='change-email'),
    path('check-token/<token_type>/', CheckTokenView.as_view(), name='check-token'),
    path('send-token/<token_type>/', SendTokenView.as_view(), name='send-token'),
    path('confirm-email/', ConfirmEmailView.as_view(), name='confirm-email'),
    path('', include(auth_router.urls)),
]
