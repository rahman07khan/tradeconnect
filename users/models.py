from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField

# Create your models here.
class CustomUser(AbstractUser):
    username=models.CharField(max_length=50)
    first_name=models.CharField(max_length=50)
    last_name=models.CharField(max_length=50)
    email=models.EmailField(unique=True)
    password=models.CharField(max_length=100)
    mobile_number=models.BigIntegerField(blank=False,unique=True)
    is_active=models.BooleanField(default=True)
    created_at=models.DateTimeField(auto_now_add=True)
    created_by=models.IntegerField(blank=True,null=True)
    modified_at=models.DateTimeField(auto_now_add=True)
    modified_by=models.IntegerField(blank=True,null=True)
    last_login_role_id=models.IntegerField(blank=True,null=True)
    is_approval=models.BooleanField(default=False)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    
class RoleMaster(models.Model):
    name=models.CharField(max_length=50)
    description=models.CharField(max_length=50)
    # user=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    is_active=models.BooleanField(default=True)
    created_at=models.DateTimeField(auto_now_add=True)
    created_by=models.IntegerField(blank=True,null=True)
    modified_at=models.DateTimeField(auto_now_add=True)
    modified_by=models.IntegerField(blank=True,null=True)
    
    
class Rolemapping(models.Model):
    user=models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name='user_role')
    roles=models.ManyToManyField(RoleMaster)
    is_active=models.BooleanField(default=True)
    created_at=models.DateTimeField(auto_now_add=True)
    created_by=models.IntegerField(blank=True,null=True)
    modified_at=models.DateTimeField(auto_now_add=True)
    modified_by=models.IntegerField(blank=True,null=True)
    
class SellerDetail(models.Model):
    user=models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name='SellerDetail')
    bussiness_name=models.CharField(max_length=50)
    bussiness_email=models.EmailField(max_length=40)
    bussiness_ph=models.PositiveIntegerField(blank=True,null=True)    
    bussiness_address=models.CharField(max_length=50)
    shipping_address=models.CharField(max_length=50)
    organization=models.CharField(max_length=30)
    documents=ArrayField(models.TextField(),default=dict,null=True,blank=True)
    category=models.ForeignKey('orders.CategoryMaster',on_delete=models.CASCADE,related_name='SellerDetail')
    approval_status=models.CharField(default="pending")
    is_active=models.BooleanField(default=True)
    created_at=models.DateTimeField(auto_now_add=True)
    modified_by=models.IntegerField(blank=True,null=True)
    
    class Meta:
        db_table = 'SellerRegister'
        ordering = ['created_at']
   
