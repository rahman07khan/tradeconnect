from django.urls import path
from users.views import RolemasterView,RegisterUserApi,LoginUserApi,RoleLogin,RolemappingView,SellerApproval,SellerRegistrationAPI

urlpatterns=[
    
    path('roles/',RolemasterView.as_view(),name='roles'),
    path('register/',RegisterUserApi.as_view(),name='register'),
    path('login/',LoginUserApi.as_view(),name='login-user'),
    path('rolelogin/',RoleLogin.as_view(),name='role-login'),
    path('seller/',SellerApproval.as_view(),name='seller-approval'),
    path('rolemap/',RolemappingView.as_view(),name='rolemap'),
    path("seller_reg/",SellerRegistrationAPI.as_view(),name='seller_reg'),

   
]
