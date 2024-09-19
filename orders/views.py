from django.shortcuts import render
from orders.models import CategoryMaster,ProductMaster,BuyProduct,CartItems
from users.models import CustomUser,Rolemapping
from rest_framework.views import APIView,status
from rest_framework.response import Response
from django.db import transaction

#CategoryMaster CRUD
class CategoryView(APIView):
    def get(self,request):
        user_id=request.user.id
        maps=Rolemapping.objects.get(user=user_id)
        if maps.role.name in ['admin','manager']:
            try:
                category=CategoryMaster.objects.filter(is_active=True)
                data=[]
                for categories in category:
                    data.append({
                        "category_id":categories.id,
                        "name":categories.name,
                        "description":categories.description,
                        "is_active":categories.is_active,
                        "created_by":categories.created_by,
                        "modified_by":categories.modified_by
                    })
                    return Response({
                        "status":"success",
                        "message":"data retrieve successfully",
                        "data":data
                    },status=status.HTTP_200_OK)
            except CategoryMaster.DoesNotExist:
                return Response({
                    "status":"error",
                    "message":"category not found"
                },status=status.HTTP_400_BAD_REQUEST)        
            except Exception as e:
                return Response({
                    "status":"failed",
                    "message":str(e)
                },status=status.HTTP_400_BAD_REQUEST)
        elif Rolemapping.DoesNotExist:
            return Response({
                "status":"error",
                "message":"role not found"
            },status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                "status":"error",
                "message":"only admin and manager is access"
            },status=status.HTTP_401_UNAUTHORIZED)
            
            
    def post(self,request):
        user_id=request.user.id
        maps=Rolemapping.objects.get(user=user_id)
        if maps.role.name in ['admin','manager']:
            try:
                data=request.data
                name=data.get("name")
                description=data.get("description")
                
                with transaction.atomic():
                    category=CategoryMaster(
                        name=name,
                        description=description,
                        created_by=request.user.id,
                    )
                    category.save()
                    return Response({
                        "status":"success",
                        "message":"category created successfully"
                    },status=status.HTTP_201_CREATED)  
            
            except Exception as e:
                return Response({
                    "status":"failed",
                    "message":str(e)
                },status=status.HTTP_400_BAD_REQUEST)  
        elif Rolemapping.DoesNotExist:
            return Response({
                "status":"error",
                "message":"role not found"
            },status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                "status":"error",
                "message":"only admin and manager is access"
            },status=status.HTTP_401_UNAUTHORIZED)
            
    
    def put(self,request):
        user_id=request.user.id
        maps=Rolemapping.objects.get(user=user_id)
        if maps.role.name in ['admin','manager']:
            try:
                data=request.data 
                category_id=data.get("category_id")
                name=data.get("name")
                description=data.get("description")
                
                with transaction.atomic():
                    categories=CategoryMaster.objects.get(id=category_id,is_active=True)
                    categories.name = name
                    categories.description = description
                    categories.modified_by=request.user.id
                
                    categories.save()
                    return Response({
                        "status":"success",
                        "message":"category updated successfully"
                    },status=status.HTTP_200_OK)
            except CategoryMaster.DoesNotExist:
                return Response({
                    "status":"error",
                    "message":"category not found or category is not active"
                },status=status.HTTP_400_BAD_REQUEST)        
            except Exception as e:
                return Response({
                    "status":"failed",
                    "message":str(e)
                },status=status.HTTP_400_BAD_REQUEST)
        elif Rolemapping.DoesNotExist:
            return Response({
                "status":"error",
                "message":"role not found"
            },status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                "status":"error",
                "message":"only admin and manager is access"
            },status=status.HTTP_401_UNAUTHORIZED)
            
    def delete(self,request):
        user_id=request.user.id
        maps=Rolemapping.objects.get(user=user_id)
        if maps.role.name in ['admin','manager']:
            try:
                data=request.data 
                category_id=data.get("category_id")
                
                with transaction.atomic():
                    categories=CategoryMaster.objects.get(id=category_id,is_active=True)
                    categories.is_active=False
                    
                    categories.save()
                    return Response({
                        "status":"success",
                        "message":"category is not active"
                    },status=status.HTTP_200_OK)
            except CategoryMaster.DoesNotExist:
                return Response({
                    "status":"error",
                    "message":"category not found or not active"
                },status=status.HTTP_400_BAD_REQUEST)        
            except Exception as e:
                return Response({
                    "status":"failed",
                    "message":str(e)
                },status=status.HTTP_400_BAD_REQUEST)
        elif Rolemapping.DoesNotExist:
            return Response({
                "status":"error",
                "message":"role not found"
            },status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                "status":"error",
                "message":"only admin and manager is access"
            },status=status.HTTP_401_UNAUTHORIZED)
            
            
#ProductMaster Crud
class ProductView(APIView) :
    #get product details
    def get(self, request):
        user = request.user
        category_id = request.query_params.get('category_id')
        product_id = request.query_params.get('product_id')
        if not category_id:
            return Response({
                "status":"error",
                "message":"you would give category id must"
            },status=status.HTTP_400_BAD_REQUEST)
        try:
            maps = Rolemapping.objects.get(user=user.id)
            if maps.role.name not in ['admin', 'manager']:
                return Response({
                    "status": "error",
                    "message": "Only admin and manager can access this."
                }, status=status.HTTP_403_FORBIDDEN)
                      
            if category_id:

                category = CategoryMaster.objects.get(id=category_id,is_active=True)
                if product_id:
                    product = ProductMaster.objects.get(id=product_id, category=category,is_active=True)
                    data = {
                        'product_id': product.id,
                        'product_name': product.name,
                        'description': product.description,
                        'price': product.price,
                        'quantity': product.quantity,
                    }
                    return Response({
                        "status": "success",
                        "message": "Product details",
                        "data": data
                    }, status=status.HTTP_200_OK)
                
                else:
                    products = ProductMaster.objects.filter(category=category,is_active=True)
                    data = [{
                        'product_id': product.id,
                        'product_name': product.name,
                        'description': product.description,
                        'price': product.price,
                        'quantity': product.quantity,
                    } for product in products]
                    return Response({
                        "status": "success",
                        "message": "Products in the category",
                        "data": data
                    }, status=status.HTTP_200_OK)
            
        except Rolemapping.DoesNotExist:
            return Response({
                "status": "error",
                "message": "for this user role is not map."
            }, status=status.HTTP_404_NOT_FOUND)

        except CategoryMaster.DoesNotExist:
            return Response({
                "status": "error",
                "message": "category not exist."
            }, status=status.HTTP_400_BAD_REQUEST)

        except ProductMaster.DoesNotExist:
            return Response({
                "status": "error",
                "message": "product not exist."
            }, status=status.HTTP_400_BAD_REQUEST)
        
    def post(self,request):
        user_id=request.user.id
        maps=Rolemapping.objects.get(user=user_id)
        if maps.role.name in ['admin','manager','seller']:
            try:
                data=request.data
                name=data.get("name")
                description=data.get("description")
                price=data.get("price")
                quantity=data.get("quantity")
                category_id=data.get("category")
                category=CategoryMaster.objects.get(id=category_id,is_active=True)
                
                with transaction.atomic():
                    product=ProductMaster(
                        name=name,
                        description=description,
                        price=price,
                        quantity=quantity,
                        category=category,
                        created_by=user_id
                    )
                    product.save()
                    return Response({
                        "status":"success",
                        "message":"product created successfully"
                    },status=status.HTTP_201_CREATED)
            except CategoryMaster.DoesNotExist:
                return Response({
                "status":"error",
                "message":"category not found"
            },status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({
                    "status":"failed",
                    "message":str(e)
                },status=status.HTTP_400_BAD_REQUEST)
        elif Rolemapping.DoesNotExist:
            return Response({
                "status":"error",
                "message":"role not found"
            },status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                "status":"error",
                "message":"only admin and manager is access"
            },status=status.HTTP_401_UNAUTHORIZED)
            
    def put(self,request):
        user_id=request.user.id
        maps=Rolemapping.objects.get(user=user_id)
        if maps.role.name in ['admin','manager','seller']:
            try:
                data=request.data 
                product_id=data.get("product_id")
                name=data.get("name")
                description=data.get("description")
                price=data.get("price")
                quantity=data.get("quantity")
                category_id=data.get("category")
                category=CategoryMaster.objects.get(id=category_id,is_active=True)
                
                with transaction.atomic():
                    products=ProductMaster.objects.get(id=product_id,is_active=True)
                    products.name = name
                    products.description = description
                    products.price=price
                    products.quantity=quantity
                    products.category=category
                    products.modified_by=request.user.id
                
                    products.save()
                    return Response({
                        "status":"success",
                        "message":"product updated successfully"
                    },status=status.HTTP_200_OK)
            except CategoryMaster.DoesNotExist:
                return Response({
                "status":"error",
                "message":"category not found"
            },status=status.HTTP_400_BAD_REQUEST)
            except ProductMaster.DoesNotExist:
                return Response({
                    "status":"error",
                    "message":"product not found or product is not active"
                },status=status.HTTP_400_BAD_REQUEST)     
            except Exception as e:
                return Response({
                    "status":"failed",
                    "message":str(e)
                },status=status.HTTP_400_BAD_REQUEST)
        elif Rolemapping.DoesNotExist:
            return Response({
                "status":"error",
                "message":"role not found"
            },status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                "status":"error",
                "message":"only admin and manager is access"
            },status=status.HTTP_401_UNAUTHORIZED)
            
            
    def delete(self,request):
        user_id=request.user.id
        maps=Rolemapping.objects.get(user=user_id)
        if maps.role.name in ['admin','manager','seller']:
            try:
                data=request.data 
                product_id=data.get("product_id")
                
                with transaction.atomic():
                    products=ProductMaster.objects.get(id=product_id,is_active=True)
                    products.is_active=False
                    
                    products.save()
                return Response({
                        "status":"success",
                        "message":"product is not active"
                    },status=status.HTTP_200_OK)
            except ProductMaster.DoesNotExist:
                return Response({
                    "status":"error",
                    "message":"product not found or product is not active"
                },status=status.HTTP_400_BAD_REQUEST)     
            except Exception as e:
                return Response({
                    "status":"failed",
                    "message":str(e)
                },status=status.HTTP_400_BAD_REQUEST)
        elif Rolemapping.DoesNotExist:
            return Response({
                "status":"error",
                "message":"role not found"
            },status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                "status":"error",
                "message":"only admin and manager is access"
            },status=status.HTTP_401_UNAUTHORIZED) 
class CartItemUserApi(APIView):
    def post(self,request):
        user=request.user
        data=request.data
        category_id=data.get('category')
        product_id=data.get('product')
        quantity=data.get('quantity')
        created_by=request.user.id
        

        #check category,product,quantity is given
        if not category_id or not product_id or not quantity:
           return Response({
                "status":"error",
                "message":"category,product,quantity is required"
            },status=status.HTTP_400_BAD_REQUEST) 
        
        try:
            maps = Rolemapping.objects.get(user=user.id)
            if maps.role.name != 'buyer':
                return Response({
                    "status": "error",
                    "message": "Only buyer can access this."
                }, status=status.HTTP_403_FORBIDDEN)
        
            product=ProductMaster.objects.get(id=product_id,is_active=True)
            if product.category == category_id and product.is_active == True:
                #check product quantity
                if product.quantity<quantity:
                    return Response({
                        "status": "error",
                        "message": f"only {product.quantity}is available."
                    }, status=status.HTTP_403_FORBIDDEN)
                
                with transaction.atomic():
                    items=CartItems.objects.create(
                        category=product.category,
                        product=product,
                        user=user,
                        quantity=quantity,
                        price=product.price,
                        created_by=created_by,
                    )
                    product.quantity -=quantity
                    product.save()
                    return Response({
                        "status":"success",
                        "message":"successfully product is added to cart"
                    },status=status.HTTP_201_CREATED)
        except Rolemapping.DoesNotExist:
            return Response({
                "status":"error",
                "message":"role is not map to user"
            },status=status.HTTP_400_BAD_REQUEST)
        
        except ProductMaster.DoesNotExist:
            return Response({
                "status":"error",
                "message":"product is not exists"
            },status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {
                    "status":"error",
                    "message":str(e)
                },status=status.HTTP_400_BAD_REQUEST
            )
            