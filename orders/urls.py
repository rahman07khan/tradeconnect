from django.urls import path
from orders.views import CategoryView,ProductViewAPI,CartItemUserApi,GetProductBySeller,BuyProductUserApi,FeedbackMasterAPI,LikesAPI,WishListAPI,CommentAPI
from graphene_django.views import GraphQLView
from django.views.decorators.csrf import csrf_exempt

from .schema import schema 

urlpatterns = [
    path('categories/',CategoryView.as_view(),name='categories'),
    path('products/',ProductViewAPI.as_view(),name='products'),
    path('cart/',CartItemUserApi.as_view(),name='cart'),
    path('specific/',GetProductBySeller.as_view(),name='specific'),
    path('checkout/',BuyProductUserApi.as_view(),name='buy-product'),
    path('feedback/', FeedbackMasterAPI.as_view()),
    path("graphql/", csrf_exempt(GraphQLView.as_view(graphiql=True, schema=schema))),
    path("likes/",LikesAPI.as_view(),name='likes'),
    path("wish/",WishListAPI.as_view(),name='wish'),
    path("comment/",CommentAPI.as_view(),name='comment'),
]
