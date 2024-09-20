from django.db import models
from users.models import CustomUser
from simple_history.models import HistoricalRecords
# Create your models here.
"""category table"""
class CategoryMaster(models.Model):
    name=models.CharField(max_length=50)
    description=models.CharField(max_length=50,blank=True,null=True)
    is_active=models.BooleanField(default=True)
    created_at=models.DateTimeField(auto_now_add=True)
    created_by=models.IntegerField(blank=True,null=True)
    modified_at=models.DateTimeField(auto_now_add=True)
    modified_by=models.IntegerField(blank=True,null=True)
    history = HistoricalRecords()

    
"""product table"""   
class ProductMaster(models.Model):
    name=models.CharField(max_length=30)
    description=models.CharField(max_length=50,blank=True,null=True)
    price=models.DecimalField(max_digits=10, decimal_places=2)
    quantity=models.PositiveIntegerField()
    category=models.ForeignKey(CategoryMaster, on_delete=models.CASCADE)
    is_active=models.BooleanField(default=True)
    created_at=models.DateTimeField(auto_now_add=True)
    created_by=models.IntegerField(blank=True,null=True)
    modified_at=models.DateTimeField(auto_now_add=True)
    modified_by=models.IntegerField(blank=True,null=True)
    history = HistoricalRecords()

""" buy product"""
class BuyProduct(models.Model):
    category=models.ForeignKey(CategoryMaster,on_delete=models.CASCADE)
    product=models.ForeignKey(ProductMaster,on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    cart_id=models.CharField(max_length=15,null=True)
    quantity=models.PositiveIntegerField()
    price=models.DecimalField(max_digits=10, decimal_places=2)
    is_active=models.BooleanField(default=True)
    created_at=models.DateTimeField(auto_now_add=True)
    created_by=models.IntegerField(blank=True,null=True)
    modified_at=models.DateTimeField(auto_now_add=True)
    modified_by=models.IntegerField(blank=True,null=True)
    history = HistoricalRecords()


""""cart table"""
class CartItems(models.Model):
    category=models.ForeignKey(CategoryMaster,on_delete=models.CASCADE)
    product=models.ForeignKey(ProductMaster,on_delete=models.CASCADE)
    user=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    bought_status=models.CharField(max_length=50,default='pending')
    quantity=models.PositiveIntegerField()
    price=models.DecimalField(max_digits=10,decimal_places=2)
    created_at=models.DateTimeField(auto_now_add=True)
    created_by=models.IntegerField(blank=True,null=True)
    modified_at=models.DateTimeField(auto_now_add=True)
    modified_by=models.IntegerField(blank=True,null=True)
    is_active=models.BooleanField(default=True)
    history = HistoricalRecords()


