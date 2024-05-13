

from django.urls import path
from rest_framework_simplejwt.views import TokenVerifyView

from user import views

urlpatterns = [
    path('create/', views.CreateUserView.as_view(), name='create'),
    path('activate/<str:uidb64>/<str:token>/', views.activate, name='activate'),
    path('token/', views.CustomObtainTokenPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', views.CustomCookieTokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('token/logout/', views.LogoutView.as_view(), name='token_logout'),
    path('password-reset/', views.PasswordResetView.as_view(), name='password_reset'),
    path('password-reset/<str:uid>/confirm/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('me/', views.RequestUserDetailView.as_view(), name='user_detail'),
    path('me/change-password/', views.ChangePasswordView.as_view(), name='change_password'),
    path('<int:pk>/delete/', views.DeleteUserView.as_view(), name='user_delete')
]
