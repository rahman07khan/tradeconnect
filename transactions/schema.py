import graphene
from transactions.views import * 

class Mutation(graphene.ObjectType):
    create_wallet = WalletDetailsCreate.Field()
    create_wallet_transaction = WalletTransactionCreate.Field()
    create_payment = PaymentCreate.Field()
    create_shipment = ShipmentTaken.Field()
    update_ordertrack = UpdateOrderTrackStatus.Field()

class Query(WalletQuery,WalletTransactionQuery,PaymentQuery,graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
