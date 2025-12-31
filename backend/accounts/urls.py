from django.urls import path
from .views import SignupView, CustomTokenObtainPairView, CurrentUserView, AllUsersView
from rest_framework_simplejwt.views import TokenRefreshView

app_name = 'accounts'

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('signin/', CustomTokenObtainPairView.as_view(), name='signin'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('me/', CurrentUserView.as_view(), name='current_user'),
    path('users/', AllUsersView.as_view(), name='all_users'),
]
