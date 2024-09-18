from django.urls import path
from orders.views import CategoryView

urlpatterns = [
    path('categories/',CategoryView.as_view(),name='categories'),
]
