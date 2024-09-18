from django.urls import path
from users.views import RolemasterView,RegisterUserApi,LoginUserApi

urlpatterns=[
    
    path('roles/',RolemasterView.as_view(),name='roles'),
    path('register/',RegisterUserApi.as_view(),name='register'),
    path('login/',LoginUserApi.as_view(),name='login-user'),
]
