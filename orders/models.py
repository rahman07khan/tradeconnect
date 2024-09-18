from django.db import models
from users.models import CustomUser

# Create your models here.
class CategoryMaster(models.Model):
    name=models.CharField(max_length=50)
    description=models.CharField(max_length=50,blank=True,null=True)
    is_active=models.BooleanField(default=True)
    created_at=models.DateTimeField(auto_now_add=True)
    created_by=models.IntegerField(blank=True,null=True)
    modified_at=models.DateTimeField(auto_now_add=True)
    modified_by=models.IntegerField(blank=True,null=True)
    
    
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
    
class BuyProduct(models.Model):
    category=models.ForeignKey(CategoryMaster,on_delete=models.CASCADE)
    product=models.ForeignKey(ProductMaster,on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    quantity=models.PositiveIntegerField()
    total=models.DecimalField(max_digits=10, decimal_places=2)
    is_active=models.BooleanField(default=True)
    created_at=models.DateTimeField(auto_now_add=True)
    created_by=models.IntegerField(blank=True,null=True)
    modified_at=models.DateTimeField(auto_now_add=True)
    modified_by=models.IntegerField(blank=True,null=True)
    