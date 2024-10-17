from django.urls import path
from users.views import *
from .views import ProcessPaymentsView
from graphene_django.views import GraphQLView
from django.views.decorators.csrf import csrf_exempt

from transactions.views import *

from .schema import schema 

urlpatterns = [
    path("graphql/", csrf_exempt(GraphQLView.as_view(graphiql=True, schema=schema))),
    path("payment/",ProcessPaymentsView.as_view(),name='seller-payment'),
    # path('returns/initiate/', InitiateReturnAPI.as_view(), name='initiate-return-request'),
    path('payment/checkout/', CreateOrderView.as_view()),
    path('returnstage/',CreateReturnStageMasterView.as_view()),

]
