
ADMIN="Admin"
MANAGER = "manager"
SELLER = "seller"
CREDIT = "credit"
DEBIT = "debit"
ACCEPTED="accepted"
PENDING="pending"

from django.db import transaction
from datetime import timedelta
from django.utils import timezone
from django.conf import settings
import boto3
from botocore.config import Config
from rest_framework.response import Response
from rest_framework.views import status
import jwt





def send_amount_to_seller(payment, order_tracking):
    products = order_tracking.order.checkout.first()
    return_window_days = products.product.refund_period
    return_window = timedelta(days=return_window_days) 

    if order_tracking.status == 'delivered':
        if timezone.now() > (order_tracking.updated_at + return_window) and not payment.is_send_user:
            if payment.payment_status == 'success': 
                with transaction.atomic():
                    payment.to_sender_amount = payment.total_amount
                    payment.is_send_user = True  
                    payment.payment_status = 'completed'  
                    payment.save()  
                    return True
            return False
    else:
        return None


def calculate_return_date(order_queryset):
    return_dates = []
    for order in order_queryset:
        products = order.order.checkout.first()
        if products is None:
            print(f"Order {order.id} has no products in checkout.")
            continue
        return_window_days = products.product.refund_period
        return_window = timedelta(days=return_window_days)
        return_date = order.updated_at + return_window
        return_dates.append(return_date)
    return min(return_dates) if return_dates else None

def upload_image_s3( image_file, file_name):
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
            config=Config(signature_version='s3v4')
 
        )
       
        # Add timestamp to file name for uniqueness
        current_time=timezone.now().strftime('%Y-%m-%d %H:%M')
        
        timestamps = current_time
        file_extension = file_name.split('.')[-1]
        unique_filename = f"{file_name.split('.')[0]}_{timestamps}.{file_extension}"
        s3_client.upload_fileobj(
            image_file,
            settings.AWS_STORAGE_BUCKET_NAME,
            f"product_images/{unique_filename}",
            ExtraArgs={'ACL': 'public-read', 'ServerSideEncryption': 'AES256'}
 

        )
        # Generate the image URL
        image_url = f"https://{settings.AWS_S3_CUSTOM_DOMAIN}/product_images/{unique_filename}"
        
        return image_url
    except Exception as e:
              return Response({
                    "status":"failed",
                    "message":str(e)
                },status=status.HTTP_400_BAD_REQUEST)

def getuserinfo(request):
    token = request.META.get('HTTP_AUTHORIZATION').split(' ')[1]
    payload = jwt.decode(token, options={"verify_signature": False})  
    role_name = payload.get('role_name')
    user_id = payload.get('user_id')
    return role_name,user_id



