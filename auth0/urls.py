from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView)

from . import views



urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('signup/', views.SingupView.as_view(), name='authd_signup'),
    path('verify-email/<str:verify_key>/', views.VerifyEmailView.as_view()),
    path('password/reset/', views.ResetPasswordView.as_view()),
    path('password/reset/verify/<str:verify_key>/',
         views.ResetPasswordVerifyView.as_view())
]