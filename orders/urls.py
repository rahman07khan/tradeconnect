from django.urls import path
from orders.views import CategoryView,ProductView,CartItemUserApi

urlpatterns = [
    path('categories/',CategoryView.as_view(),name='categories'),
    path('products/',ProductView.as_view(),name='products'),
     path('cart/',CartItemUserApi.as_view(),name='cart')
]
