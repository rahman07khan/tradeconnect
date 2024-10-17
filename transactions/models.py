from django.db import models
from users.models import *
from orders.models import *
from simple_history.models import HistoricalRecords
from django.utils import timezone
from datetime import timedelta

class WalletDetails(models.Model):
    user = models.ForeignKey(CustomUser,related_name='WalletDetails', on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  
    currency = models.CharField(max_length=10, default="INR")
    created_at=models.DateTimeField(auto_now_add=True)
    created_by=models.IntegerField(blank=True,null=True)
    modified_at=models.DateTimeField(auto_now_add=True)
    modified_by=models.IntegerField(blank=True,null=True)
    is_active=models.BooleanField(default=True)
    history = HistoricalRecords()

    class Meta:
        db_table = 'WalletDetails'

class WalletTransaction(models.Model):
    wallet = models.ForeignKey(WalletDetails,related_name='WalletTransaction',on_delete = models.CASCADE)
    transaction_type = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10,decimal_places=2)
    description = models.TextField(blank=True, null=True)
    card_info = models.JSONField(null=True, blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    created_by=models.IntegerField(blank=True,null=True)
    modified_at=models.DateTimeField(auto_now_add=True)
    modified_by=models.IntegerField(blank=True,null=True)
    is_active=models.BooleanField(default=True)
    history = HistoricalRecords()

    class Meta:
        db_table = 'WalletTransaction'

class PaymentDetails(models.Model):
    user = models.ForeignKey(CustomUser,related_name='PaymentDetails',on_delete = models.CASCADE)
    # checkout = models.ManyToManyField(BuyProducts,related_name='PaymentDetails')
    wallet_transaction = models.ForeignKey(WalletTransaction,related_name='PaymentDetails',on_delete = models.CASCADE)
    total_amount = models.DecimalField(max_digits=10,decimal_places=2)
    payment_status = models.CharField(max_length = 20, default="pending")
    is_send_user =models.BooleanField(default=False) 
    to_sender_amount = models.FloatField(max_length=10,blank=True,null=True)
    created_at=models.DateTimeField(auto_now_add=True)
    created_by=models.IntegerField(blank=True,null=True)
    modified_at=models.DateTimeField(auto_now_add=True)
    modified_by=models.IntegerField(blank=True,null=True)
    is_active=models.BooleanField(default=True)
    is_send_user =models.BooleanField(default=False)
    to_sender_amount = models.FloatField(max_length=10,blank=True,null=True)
    history = HistoricalRecords()

    class Meta:
        db_table = 'PaymentDetails'
    
    
class OrderDetails(models.Model):
    user = models.ForeignKey(CustomUser, related_name='OrderDetails', on_delete=models.CASCADE)
    checkout = models.ManyToManyField(BuyProducts, related_name='OrderDetails',)
    payment = models.OneToOneField(PaymentDetails, related_name='OrderDetails', on_delete=models.CASCADE)
    order_status = models.CharField(max_length=20, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.IntegerField(blank=True, null=True)
    modified_at = models.DateTimeField(auto_now_add=True)
    modified_by = models.IntegerField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    history = HistoricalRecords()

    class Meta:
        db_table = 'OrderDetails'

    def update_order_status(self):
        if self.payment.payment_status == 'success':
            self.order_status = 'Placed'
        else:
            self.order_status = 'failed'
        self.save()



class ShipmentDetails(models.Model):
    order = models.OneToOneField('OrderDetails', related_name='ShipmentDetails', on_delete=models.CASCADE)
    delivery_person = models.ForeignKey(CustomUser, related_name='ShipmentDetails', on_delete=models.SET_NULL, null=True)
    pickup_date = models.DateTimeField(null=True, blank=True)
    delivery_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, default="pending") 
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.IntegerField(blank=True, null=True)
    modified_at = models.DateTimeField(auto_now=True)
    modified_by = models.IntegerField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    history = HistoricalRecords()

    class Meta:
        db_table = 'ShipmentDetails'


class OrderTracking(models.Model):
    order = models.ForeignKey('OrderDetails', related_name='OrderTracking', on_delete=models.CASCADE)
    status = models.CharField(max_length=50)  # Order statuses like 'processing', 'shipped', 'out_for_delivery', 'delivered'
    message = models.TextField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    class Meta:
        db_table = 'OrderTracking'

    def add_tracking(self, status, message):
        self.status = status
        self.message = message
        self.save()

class ReturnDetails(models.Model):
    order = models.ForeignKey(OrderDetails, on_delete=models.CASCADE, related_name='returns')
    product = models.ForeignKey(ProductMaster, on_delete=models.CASCADE, related_name='returns')
    pickup = models.BooleanField(default=False)  
    return_authorization = models.CharField(max_length=20,default='pending')
    inspect_status = models.BooleanField(default=False)  
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    reason = models.TextField( null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.IntegerField(blank=True, null=True)
    modified_at = models.DateTimeField(auto_now=True)
    modified_by = models.IntegerField(blank=True, null=True)
    class Meta:
        db_table = 'ReturnDetails'



class RefundDetails(models.Model):
    return_details = models.ForeignKey(ReturnDetails, related_name='refunds', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    return_fees = models.DecimalField(max_digits=10, decimal_places=2, default=50.00)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, default="pending") 
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.IntegerField(blank=True, null=True)
    modified_at = models.DateTimeField(auto_now=True)
    modified_by = models.IntegerField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'RefundDetails'




class ReturnStageMaster(models.Model):
    stage_no = models.PositiveIntegerField()
    stage_name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.IntegerField(blank=True, null=True)
    modified_at = models.DateTimeField(auto_now_add=True)
    modified_by = models.IntegerField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    history = HistoricalRecords()

    class Meta:
        db_table = 'ReturnStageMaster'


class ReturnPolicyType(models.Model):
    name = models.CharField(max_length=100)
    stages = ArrayField(models.PositiveIntegerField(), blank=True, null=True)  
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.IntegerField(blank=True, null=True)
    modified_at = models.DateTimeField(auto_now_add=True)
    modified_by = models.IntegerField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    history = HistoricalRecords()

    class Meta:
        db_table = 'ReturnPolicyType'



class ReturnStageDetails(models.Model):
    order = models.ForeignKey(OrderDetails, on_delete=models.CASCADE, related_name='return_stages')
    product = models.ForeignKey(BuyProducts, on_delete=models.CASCADE, related_name='return_stages')
    return_policy_type = models.ForeignKey(ReturnPolicyType, on_delete=models.CASCADE)
    stage = models.ForeignKey(ReturnStageMaster, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.IntegerField(blank=True, null=True)
    modified_at = models.DateTimeField(auto_now_add=True)
    modified_by = models.IntegerField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    history = HistoricalRecords()

    class Meta:
        db_table = 'ReturnStageDetails'
        unique_together = ['order', 'product', 'stage'] 
