from django.urls import path
from users.views import RolemasterView

urlpatterns=[
    
     path('roles/',RolemasterView.as_view(),name='roles'),
]