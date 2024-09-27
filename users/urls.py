from django.urls import path
from users.views import RolemasterView,RegisterUserApi,LoginUserApi,RoleLogin

urlpatterns=[
    
    path('roles/',RolemasterView.as_view(),name='roles'),
    path('register/',RegisterUserApi.as_view(),name='register'),
    path('login/',LoginUserApi.as_view(),name='login-user'),
    path('rolelogin/',RoleLogin.as_view(),name='rolelogin'),
   
]
