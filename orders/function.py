
ADMIN="Admin"
MANAGER = "manager"
SELLER = "seller"
CREDIT = "credit"
DEBIT = "debit"

from django.db import transaction
from datetime import timedelta
from django.utils import timezone

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
