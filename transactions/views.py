from django.shortcuts import render
from orders.models import *
from users.models import *
from transactions.models import *
from django.db import transaction
import graphene
from graphene_django import DjangoObjectType
import time
import jwt
from orders.function import *
from django.db.models import Sum


def getrolename(request):
    token = request.META.get('HTTP_AUTHORIZATION').split(' ')[1]
    payload = jwt.decode(token, options={"verify_signature": False})  
    role_name = payload.get('role_name')
    return role_name


def getuserid(request):
    token = request.META.get('HTTP_AUTHORIZATION').split(' ')[1]
    payload = jwt.decode(token, options={"verify_signature": False})  
    user_id = payload.get('user_id')
    return user_id


class BaseMutation(graphene.Mutation):
    status = graphene.String()
    message = graphene.String()

    class Meta:
        abstract = True

# WalletDetails CRUD
        

class WalletDetailsType(DjangoObjectType):
    created_at = graphene.Float()
    modified_at = graphene.Float()

    class Meta:
        model = WalletDetails 
        fields = ['id', 'user', 'balance','currency', 'created_at', 'modified_at', 'is_active']

    def resolve_created_at(self, info):
        return time.mktime(self.created_at.timetuple())

    def resolve_modified_at(self, info):
        return time.mktime(self.modified_at.timetuple())
    
class WalletDetailsCreate(BaseMutation):

    class Arguments:
        balance = graphene.String(required=True)
        currency = graphene.String(default_value = 'INR')

    def mutate(self, info, balance, currency):
        user_id = getuserid(info.context)
        transaction.set_autocommit(False)
        try:
            walletdetails = WalletDetails(
                balance=balance,
                currency=currency,
                user_id=user_id,
                created_by=user_id,
            )
            walletdetails.save()
            transaction.commit()

            return WalletDetailsCreate(status="success", message="Feedback created successfully")
        except Exception as e:
            return WalletDetailsCreate(status="error", message=str(e))

class WalletQuery(graphene.ObjectType):
    wallet_list = graphene.List(WalletDetailsType, is_active=graphene.Boolean())

    def resolve_wallet_list(self, info, is_active=True):
        return WalletDetails.objects.filter(is_active=is_active)

# WalletTransaction CRUD

class WalletTransactionType(DjangoObjectType):
    created_at = graphene.Float()
    modified_at = graphene.Float()

    class Meta:
        model  = WalletTransaction
        fileds = ['id', 'wallet', 'transaction_type', 'amount', 'description', 'card_info', 'created_at', 'modified_at', 'is_active']

    def resolve_created_at(self,info):
        return time.mktime(self.created_at.timetuple())
    
    def resolve_modified_at(self,info):
        return time.mktime(self.modified_at.timetuple())

class WalletTransactionCreate(BaseMutation):
    class Arguments:
        wallet_id = graphene.ID(required=True)
        transaction_type = graphene.String(required = True)
        amount = graphene.Decimal(required = True)
        description = graphene.String()
        card_number = graphene.Int()
        card_type = graphene.String()
        expiry_date = graphene.String()
        cvv = graphene.Int()

    def mutate(self,info,wallet_id,transaction_type,amount,description=None,card_number = None,card_type =None,expiry_date = None,cvv =None):
        
        user_id = getuserid(info.context)

        transaction.set_autocommit(False)
        try:
            wallet = WalletDetails.objects.get(id=wallet_id,user_id=user_id)

            card_info = {
                'card_number':card_number,
                'card_type':card_type,
                'expiry_date':expiry_date,
                'cvv':cvv
            }

            if transaction_type == CREDIT:
                wallet.balance += amount
            
            elif transaction_type == DEBIT:
                if wallet.balance < amount :
                    return WalletTransactionCreate(status="error", message="Insufficient balance")
                wallet.balance -= amount 
            
            else:
                return WalletTransactionCreate(status="error", message="Invalid transaction type")

            wallet.save()

            transaction_entry = WalletTransaction(
                wallet=wallet,
                transaction_type=transaction_type,
                amount=amount,
                description=description,
                card_info=card_info,
                created_by=user_id
            )
            transaction_entry.save()
            transaction.commit()

            return WalletTransactionCreate(status="success", message="Transaction successful")

        except WalletDetails.DoesNotExist:
            return WalletTransactionCreate(status="error", message="Wallet not found")
        except Exception as e:
            return WalletTransactionCreate(status="error", message=str(e))
        
class WalletTransactionQuery(graphene.ObjectType):
    wallet_transaction = graphene.List(WalletTransactionType,wallet_id = graphene.Int(),is_active = graphene.Boolean())

    def resolve_wallet_transactions(self, info, wallet_id=None, is_active=True):
        if wallet_id:
            return WalletTransaction.objects.filter(wallet_id=wallet_id, is_active=is_active)
        return WalletTransaction.objects.filter(is_active=is_active)
    
# PaymentDetails CRUD
class PaymentType(DjangoObjectType):
    class Meta:
        model = PaymentDetails
        
class PaymentCreate(BaseMutation):
    
    class Arguments:
        wallet_transaction_id = graphene.Int(required=True)

    def mutate(self, info, wallet_transaction_id):
        user_id = getuserid(info.context)
        total_amount = 0
        transaction.set_autocommit(False)

        try:
            
            products = BuyProducts.objects.filter(user_id=user_id, is_active=True)
            
            total_amount = products.aggregate(total_price=Sum('price'))['total_price']

            if total_amount == 0:
                return PaymentCreate(status="error", message="No active products found in the cart")

            wallet_transaction = WalletTransaction.objects.get(id=wallet_transaction_id)
            wallet = WalletDetails.objects.get(user_id=user_id)

            if wallet.balance < total_amount:
                return PaymentCreate(status="failed", message="Insufficient balance in wallet")

            wallet.balance -= total_amount
            wallet.save()

            payment_details = PaymentDetails(
                user_id=user_id,
                wallet_transaction=wallet_transaction,
                total_amount=total_amount,
                payment_status='success',
                created_by=user_id
            )
            payment_details.save()

            order_details = OrderDetails(
                    user_id=user_id,
                    payment=payment_details,
                    created_by=user_id
                )
            order_details.update_order_status()
            order_details.save()
            order_details.checkout.add(*products)
            products.update(is_active=False)

            ordertrack = OrderTracking(
                order=order_details,
                status='processing'
            )
            ordertrack.save()

            transaction.commit()

            return PaymentCreate(status="success", message="Payment successful, order placed")

        except WalletTransaction.DoesNotExist:
            return PaymentCreate(status="error", message="Invalid wallet transaction")
        except Exception as e:
            transaction.rollback() 
            return PaymentCreate(status="error", message=str(e))

        
class PaymentQuery(graphene.ObjectType):
    payment_details = graphene.List(PaymentType,is_active = graphene.Boolean())

    payment_success  = graphene.List(PaymentType,is_active = graphene.Boolean())
    payment_failed  = graphene.List(PaymentType,is_active = graphene.Boolean())


    def resolve_payment_details(self,info,is_active=True):
        return PaymentDetails.objects.filter(is_active=is_active)
    
    def resolve_payment_success(self,info,is_active=True):
        user_id = getuserid(info.context)
        return PaymentDetails.objects.filter(user_id=user_id,is_active=is_active,payment_status='success')
    
    def resolve_payment_failed(self,info,is_active=True):
        user_id = getuserid(info.context)
        return PaymentDetails.objects.filter(user_id=user_id,is_active=is_active,payment_status='failed')


# Shipment of order took by the delivary person 
    
class ShipmentType(DjangoObjectType):
    class Meta:
        model = ShipmentDetails
    

class ShipmentTaken(BaseMutation):

    class Arguments():
        order_id = graphene.ID(required = True)
        pickup_date = graphene.Date(required = True)
        delivery_date = graphene.Date(required = True)

    def mutate(self,info,order_id,pickup_date,delivery_date):
        delivery_person_id = getuserid(info.context)
        transaction.set_autocommit(False)
        try:
            
            order = OrderDetails.objects.get(id = order_id)
            delivery_person = CustomUser.objects.get(id=delivery_person_id)

            shipment_details = ShipmentDetails(
                order = order,
                delivery_person = delivery_person,
                pickup_date = pickup_date,
                delivery_date = delivery_date,
                created_by = delivery_person_id
            )

            shipment_details.save()

            order_tracking = OrderTracking(order=order, status="shipped")
            order_tracking.save()

            transaction.commit()

            return ShipmentTaken(status="success", message="Delivery person assigned successfully." )
        except OrderDetails.DoesNotExist:
            transaction.rollback()
            return ShipmentTaken(status="error",message="Order not found.")
        except CustomUser.DoesNotExist:
            transaction.rollback()
            return ShipmentTaken(status="error",message="Delivery person not found.")
        except Exception as e:
            transaction.rollback()
            return ShipmentTaken(status="error",message=str(e))
        
class UpdateOrderTrackStatus(BaseMutation):
    class Arguments:
        order_id = graphene.ID(required=True)
        new_status = graphene.String(required=True) 

    def mutate(self, info, order_id, new_status):
        delivery_person_id = getuserid(info.context)
        transaction.set_autocommit(False)

        try:
            shipment_detail = ShipmentDetails.objects.get(order__id=order_id)

            order_tracking = OrderTracking.objects.filter(order=shipment_detail.order).last()  
            if order_tracking:
                order_tracking.status = new_status
                order_tracking.save()
            else:
                return UpdateOrderTrackStatus(status="error", message="No tracking record found for this order.")

            transaction.commit()

            return UpdateOrderTrackStatus(status="success", message="Order tracking status updated successfully.")

        except ShipmentDetails.DoesNotExist:
            transaction.rollback()
            return UpdateOrderTrackStatus(status="error", message="Shipment details not found.")
        except Exception as e:
            transaction.rollback()
            return UpdateOrderTrackStatus(status="error", message=str(e))

        
    

