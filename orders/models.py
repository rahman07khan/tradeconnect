from django.db import models
from users.models import CustomUser
from simple_history.models import HistoricalRecords
from django.contrib.postgres.fields import ArrayField
 
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

"""sub category"""
class SubCategory(models.Model):
    name=models.CharField(max_length=50)
    description=models.TextField(max_length=100,null=True,blank=True)
    category=models.ForeignKey(CategoryMaster, on_delete=models.CASCADE,related_name='category')
    created_at=models.DateTimeField(auto_now_add=True)
    created_by=models.IntegerField(blank=True,null=True)
    modified_at=models.DateTimeField(auto_now_add=True)
    modified_by=models.IntegerField(blank=True,null=True)
    is_active=models.BooleanField(default=True)
    history = HistoricalRecords()

    
"""product table"""   
class ProductMaster(models.Model):
    name=models.CharField(max_length=30)
    description=models.CharField(max_length=50,blank=True,null=True)
    price=models.DecimalField(max_digits=10, decimal_places=2)
    quantity=models.PositiveIntegerField()
    category=models.ForeignKey(CategoryMaster, on_delete=models.CASCADE)
    sub_category=models.ForeignKey(SubCategory,on_delete=models.CASCADE,null=True,blank=True)
    images=ArrayField(models.TextField(),null=True,blank=True)
    view_count=models.IntegerField(default=0)
    is_active=models.BooleanField(default=True)
    created_at=models.DateTimeField(auto_now_add=True)
    created_by=models.IntegerField(blank=True,null=True)
    modified_at=models.DateTimeField(auto_now_add=True)
    modified_by=models.IntegerField(blank=True,null=True)
    refund = models.BooleanField(default=False)
    refund_period = models.IntegerField(blank=True,null=True)
    history = HistoricalRecords()

class ProductView(models.Model):
    product=models.ForeignKey(ProductMaster,on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    is_active=models.BooleanField(default=True)
    created_at=models.DateTimeField(auto_now_add=True)
    modified_at=models.DateTimeField(auto_now_add=True)
    history = HistoricalRecords()

    
""" buy product"""
# class BuyProduct(models.Model):
#     category=models.ForeignKey(CategoryMaster,on_delete=models.CASCADE)
#     product=models.ForeignKey(ProductMaster,on_delete=models.CASCADE)
#     user = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
#     cart_id=models.CharField(max_length=15,null=True)
#     quantity=models.PositiveIntegerField()
#     price=models.DecimalField(max_digits=10, decimal_places=2)
#     is_active=models.BooleanField(default=True)
#     created_at=models.DateTimeField(auto_now_add=True)
#     created_by=models.IntegerField(blank=True,null=True)
#     modified_at=models.DateTimeField(auto_now_add=True)
#     modified_by=models.IntegerField(blank=True,null=True)
#     history = HistoricalRecords()


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


class BuyProducts(models.Model):
    category=models.ForeignKey(CategoryMaster,on_delete=models.CASCADE)
    product=models.ForeignKey(ProductMaster,on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    cart_id=models.CharField(max_length=15,null=True)
    quantity=models.PositiveIntegerField(null = True)
    price=models.DecimalField(max_digits=10, decimal_places=2)
    images=ArrayField(models.TextField(),null=True,blank=True)
    is_active=models.BooleanField(default=True)
    created_at=models.DateTimeField(auto_now_add=True)
    created_by=models.IntegerField(blank=True,null=True)
    modified_at=models.DateTimeField(auto_now_add=True)
    modified_by=models.IntegerField(blank=True,null=True)
    history = HistoricalRecords()

class Likes(models.Model):
    product = models.ForeignKey(ProductMaster,related_name='likes',on_delete = models.CASCADE , db_index = True)
    user = models.ForeignKey(CustomUser,related_name='likes',on_delete=models.CASCADE)
    created_at=models.DateTimeField(auto_now_add=True)
    created_by=models.IntegerField(blank=True,null=True)
    modified_at=models.DateTimeField(auto_now_add=True)
    modified_by=models.IntegerField(blank=True,null=True)
    is_active=models.BooleanField(default=True)
    history = HistoricalRecords()

    class Meta:
        db_table = 'likes'
        indexes = [ models.Index(fields=['product'])]
        indexes = [ models.Index(fields=['user']) ]
        ordering = ['-created_at']


class feedbackmaster(models.Model):
    feedback_type = models.CharField(max_length=50)
    is_report = models.BooleanField(default=False)
    description = models.TextField(blank=True, null=True)
    created_at=models.DateTimeField(auto_now_add=True)
    created_by=models.IntegerField(blank=True,null=True)
    modified_at=models.DateTimeField(auto_now_add=True)
    modified_by=models.IntegerField(blank=True,null=True)
    is_active=models.BooleanField(default=True)
    history = HistoricalRecords()

    class Meta:
        db_table = 'feedbackmaster'
        ordering = ['-created_at']

class Feedback(models.Model):
    product = models.ForeignKey(ProductMaster, related_name='feedbacks', on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser,related_name='feedbacks', on_delete=models.CASCADE)
    feedback_master = models.ForeignKey(feedbackmaster, on_delete=models.SET_NULL, null=True, blank=True)  
    content = models.TextField()
    rating = models.IntegerField(blank=True,null=True)
    created_at=models.DateTimeField(auto_now_add=True)
    created_by=models.IntegerField(blank=True,null=True)
    modified_at=models.DateTimeField(auto_now_add=True)
    modified_by=models.IntegerField(blank=True,null=True)
    is_active=models.BooleanField(default=True)
    history = HistoricalRecords()

    class Meta:
        db_table = 'feedback'
        ordering = ['-created_at']

class Comment(models.Model):
    product = models.ForeignKey(ProductMaster, related_name='comments', on_delete=models.CASCADE , db_index = True)
    user = models.ForeignKey(CustomUser,related_name='comments', on_delete=models.CASCADE)
    first_comment = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE) 
    content = models.TextField()
    created_at=models.DateTimeField(auto_now_add=True)
    created_by=models.IntegerField(blank=True,null=True)
    modified_at=models.DateTimeField(auto_now_add=True)
    modified_by=models.IntegerField(blank=True,null=True)
    is_active=models.BooleanField(default=True)
    history = HistoricalRecords()

    class Meta:
        db_table = 'comment'
        indexes = [ models.Index(fields=['product']) ]
        indexes = [ models.Index(fields=['user']) ]
        indexes = [models.Index(fields=['first_comment'])]
        ordering = ['-created_at']

class Wishlist(models.Model):
    product = models.ForeignKey(ProductMaster,related_name='wishlist',on_delete = models.CASCADE , db_index = True)
    user = models.ForeignKey(CustomUser,related_name='wishlist',on_delete=models.CASCADE)
    created_at=models.DateTimeField(auto_now_add=True)
    created_by=models.IntegerField(blank=True,null=True)
    modified_at=models.DateTimeField(auto_now_add=True)
    modified_by=models.IntegerField(blank=True,null=True)
    is_active=models.BooleanField(default=True)
    history = HistoricalRecords()

    class Meta:
        db_table = 'wishlist'
        indexes = [ models.Index(fields=['user']) ]
        ordering = ['-created_at']
