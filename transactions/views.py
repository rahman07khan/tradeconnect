from django.shortcuts import render
from orders.models import *
from users.models import *
from transactions.models import *
from django.db import transaction
import graphene
from graphene_django import DjangoObjectType
import time
import jwt
from rest_framework.views import APIView,status
from orders.function import *
from django.db.models import Sum
from rest_framework.response import Response
from datetime import timedelta
from django.utils import timezone
# from .models import send_amount_to_seller
from django.shortcuts import render
from orders.models import *
from users.models import CustomUser, RoleMaster,Rolemapping
from rest_framework.views import APIView,status
from rest_framework.response import Response
from django.db import transaction
from django.conf import settings
import boto3
from django.utils import timezone
from botocore.config import Config
import time
from orders.function import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from .models import *
from django.utils import timezone
from datetime import timedelta



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

class ProcessPaymentsView(APIView):
    
    def get(self, request):
        rolename = getrolename(request)  
        if rolename != MANAGER:
            return Response({
                "status": "error",
                "message": "Only manager has permission"
            }, status=status.HTTP_400_BAD_REQUEST)

        date = request.query_params.get('date')

        if date:
            try:
                date = timezone.datetime.strptime(date, "%Y-%m-%d").date() 
            except ValueError:
                return Response({
                    "status": "error",
                    "message": "Invalid date format, please provide it in YYYY-MM-DD format"
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            date = timezone.now().date()
        pending_payments = PaymentDetails.objects.filter(is_send_user=False, payment_status='success')
        if not pending_payments:
            return Response({"status": "success", "message": "No pending payments"})

        seller_data = []
        
        for payment in pending_payments:
            order_details = payment.OrderDetails
            order_queryset = OrderTracking.objects.filter(order=order_details, status='delivered')
            return_date = calculate_return_date(order_queryset)

            if return_date and return_date.date() == date:
                for order in order_queryset:
                    for data in order_details.checkout.all():
                        seller = data.user
                        seller_data.append({
                            'seller_id': seller.id,
                            'seller_name': seller.username,
                            'total_amount': payment.total_amount,
                            'product_id': data.product.id,
                            'product_name': data.product.name,
                            'order_id': order_details.id  
                        })

        if seller_data:
            return Response({
                "status": "success",
                "message": seller_data
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "status": "error",
                "message": "No matching orders for the provided date."
            }, status=status.HTTP_400_BAD_REQUEST)




    def put(self, request):
        pending_payments = PaymentDetails.objects.filter(is_send_user=False, payment_status='success') 
        results = []        
        for payment in pending_payments:
            try:
                order_tracking = OrderTracking.objects.filter(order=payment.OrderDetails, status='delivered').order_by('-updated_at').first()
                if order_tracking:
                    payment_sent = send_amount_to_seller(payment, order_tracking)
                    print("order",payment)
                    if payment_sent:
                        results.append({
                            'order_id': order_tracking.order.id,
                            'message': f"Payment of {payment.total_amount} sent to seller."
                        })
                    elif payment_sent is None:
                        results.append({
                            'order_id': order_tracking.order.id,
                            'message': "Order status is not 'delivered'."
                        })
                    else:
                        results.append({
                            'order_id': order_tracking.order.id,
                            'message': "Return window is still open."
                        })
            except OrderTracking.DoesNotExist:
                results.append({
                    'payment_id': payment.id,
                    'message': "Order tracking not found."
                })
        return Response({"status":"success",'data': results}, status=status.HTTP_200_OK)

# refund process 
class RefundDetailsType(DjangoObjectType):
    class Meta:
        model = RefundDetails
        fields = ['id', 'order', 'amount', 'status', 'created_at', 'updated_at', 'is_active']  
    

class ProcessRefund(graphene.Mutation):
    class Arguments:
        order_id = graphene.ID(required=True)
        description = graphene.String()

    status = graphene.String()
    message = graphene.String()
    refund = graphene.Field(RefundDetailsType)

    def mutate(self, info, order_id,description):
        user_id = getuserid(info.context)
        try:
            with transaction.atomic():
                order = OrderDetails.objects.select_related('payment').get(id=order_id, user_id=user_id, is_active=True)

                if order.refunds.filter(is_active=True).exists():
                    return ProcessRefund(status="error", message="Refund has already been processed for this order.", refund=None)

                latest_tracking = OrderTracking.objects.filter(order=order,status = 'delivered').order_by('-updated_at')

                if not latest_tracking or not latest_tracking.updated_at:
                    return ProcessRefund(status="error", message="No tracking information found for this order.", refund=None)

                now = timezone.now()
                tracking_update_time = latest_tracking.updated_at
                if now - tracking_update_time > timedelta(days=14):
                    return ProcessRefund(status="error", message="Refund period of 14 days has exceeded.", refund=None)

                if order.payment.payment_status != 'success':
                    return ProcessRefund(status="error", message="Cannot refund a failed payment.", refund=None)

                wallet = WalletDetails.objects.get(user_id=user_id)
                wallet.balance += order.payment.total_amount
                wallet.save()

                wallet_transaction = WalletTransaction(
                    wallet=wallet,
                    transaction_type='CREDIT',
                    amount=order.payment.total_amount,
                    description=f"Refund for Order ID {order_id}",
                    created_by=user_id
                )
                wallet_transaction.save()

                refund = RefundDetails(
                    order=order,
                    amount=order.payment.total_amount,
                    description = description,
                    status='completed',
                    is_active=True
                )
                refund.save()

                return ProcessRefund(status="success", message="Refund processed successfully.")

        except OrderDetails.DoesNotExist:
            return ProcessRefund(status="error", message="Order not found.", refund=None)
        except Exception as e:
            return ProcessRefund(status="error", message=str(e), refund=None)

# create order by payment

class CreateOrderView(APIView):

    def post(self, request):
        user_id = request.user.id
        wallet_transaction_id = request.data.get('wallet_transaction_id')

        products = BuyProducts.objects.filter(user_id=user_id, is_active=True)

        if not products.exists():
            return Response({"status": "error", "message": "No active products found in the cart"}, status=400)

        try:
            with transaction.atomic():
                total_amount = products.aggregate(total_price=Sum('price'))['total_price']
                wallet_transaction = WalletTransaction.objects.get(id=wallet_transaction_id)
                wallet = WalletDetails.objects.get(user_id=user_id)

                if wallet.balance < total_amount:
                    return Response({"status": "failed", "message": "Insufficient balance in wallet"}, status=400)

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
                order_details.save()

                for product in products:
                    order_details.checkout.add(product)  

                products.update(is_active=False)

                return Response({"status": "success", "message": "Order placed successfully"})

        except WalletTransaction.DoesNotExist:
            return Response({"status": "error", "message": "Invalid wallet transaction"}, status=400)

        except Exception as e:
            return Response({"status": "error", "message": str(e)}, status=500)

# returnstagemaster CRUD

class CreateReturnStageMasterView(APIView):

    def post(self, request):
        user=request.user
        data = request.data
        stage_no = data.get('stage_no')
        stage_name = data.get('stage_name')
        description = data.get('description', '')
        created_by = request.user.id  

        
        if not (stage_no or stage_name):
            return Response({"status": "error", "message": "Stage number and name are required"}, status=400)
        
        rolemap = getrolename(request)
        if rolemap in [ADMIN,MANAGER]:

            try:
                with transaction.atomic():

                    return_stage = ReturnStageMaster(
                        stage_no=stage_no,
                        stage_name=stage_name,
                        description=description,
                        created_by=created_by,
                        modified_by=created_by 
                    )
                    return_stage.save()

                    return Response({"status": "success", "message": "Return stage created successfully"}, status=201)

            except Exception as e:
                return Response({"status": "error", "message": str(e)}, status=500)
        
        else:
            return Response({ "status":"error","message":"only admin and manager is access" },status=400) 

# returnpolicytype
        

class ReturnPolicyTypeView(APIView):

    def post(self,request):
        user = request.user
        data = request.data
        name = data.get('name')
        stages = data.get('stages',[])
        created_by = user.id

        if not (name or stages):
            return Response({"status":"error","message":"name and stage are required"},status = 400)
        
        rolename = getrolename(request)

        if rolename in  ADMIN:
            try:
                with transaction.atomic():
                    return_policy_type = ReturnPolicyType(
                        name=name,
                        stages=stages,  
                        created_by=created_by,
                        modified_by=created_by  
                    )
                    return_policy_type.save()

                    return Response({"status": "success", "message": "Return policy type created successfully"}, status=200)

            except Exception as e:
                return Response({"status": "error", "message": str(e)}, status=400)
            
        else:
            return Response({"status":"error","message":"only admin has the access"},status = 400)


