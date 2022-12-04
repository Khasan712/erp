from django.urls import path
from api.v1.users.views import (
    UserListView,
    # UserDetailListView,
    UserRegistrationView,
    LogoutAPIView,
    DetailUserViews,
    CreateSourcDirectorOriganizationAPI,
    EmailVerify,
    CustomTokenObtainPairView,
    UserDetailByAccessToken
)
from rest_framework_simplejwt import views as jwt_views


urlpatterns = [
    path('list/', UserListView.as_view()),
    path('me/', UserDetailByAccessToken.as_view()),

    # User register, login, logout and detal views
    path('register/', UserRegistrationView.as_view()),
    path('logout/', LogoutAPIView.as_view()),
    path('detail/<int:pk>/', DetailUserViews.as_view()),
    path('register/organization/', CreateSourcDirectorOriganizationAPI.as_view()),
    path('email/verify/', EmailVerify.as_view(), name='email-verify'),
    
    
    # path('token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh')
]