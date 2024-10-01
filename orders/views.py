from django.shortcuts import render
from orders.models import CategoryMaster,ProductMaster,BuyProducts,CartItems,feedbackmaster,Feedback
from users.models import CustomUser, RoleMaster,Rolemapping
from rest_framework.views import APIView,status
from rest_framework.response import Response
from django.db import transaction
from django.conf import settings
import boto3
from django.utils import timezone
from botocore.config import Config
import jwt

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


def getrolename(request):
    token = request.META.get('HTTP_AUTHORIZATION').split(' ')[1]
    payload = jwt.decode(token, options={"verify_signature": False})  
    role_name = payload.get('role_name')
    return role_name

#CategoryMaster CRUD
class CategoryView(APIView):
    def get(self,request):
        user_id=request.user.id
        rolemap=Rolemapping.objects.get(user_id=user_id) 
        if rolemap.roles.name not in ['admin','manager']:
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
        rolemap=Rolemapping.objects.get(user_id=user_id) 
        if rolemap.roles.name not in ['admin','manager']:
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
        rolemap=Rolemapping.objects.get(user_id=user_id) 
        if rolemap.roles.name not in ['admin','manager']:
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
        rolemap=Rolemapping.objects.get(user_id=user_id) 
        if rolemap.roles.name not in ['admin','manager']:
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
        print(f"Received category_id: {category_id}, product_id: {product_id}")
        if not category_id:
            return Response({
                "status":"error",
                "message":"you would give category id must"
            },status=status.HTTP_400_BAD_REQUEST)
        try:
            rolemap=Rolemapping.objects.get(user_id=user.id) 
            if rolemap.roles.name not in ['admin','manager']:
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
                    products = ProductMaster.objects.filter(category=category,is_active=True).order_by('-created_at')
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
        rolemap=Rolemapping.objects.get(user_id=user_id) 
        if rolemap.roles.name in ['admin','manager']:
            try:
                data=request.data
                name=data.get("name")
                description=data.get("description")
                price=data.get("price")
                quantity=data.get("quantity")
                category_id=data.get("category")
                image = request.FILES.getlist('images')
                category=CategoryMaster.objects.get(id=category_id,is_active=True)
                if image:
                    image_urls= []
                    for image_file in image:
                        file_name = image_file.name
                        image_url = upload_image_s3(image_file, file_name)
                        if image_url: 
                            image_urls.append(image_url)
                    with transaction.atomic():
                        product=ProductMaster(
                            name=name,
                            description=description,
                            price=price,
                            quantity=quantity,
                            category=category,
                            images=image_urls,
                            created_by=user_id
                        )
                        # product.save()
                    return Response({
                        "status":"success",
                        "message":"product created successfully",
                        "image_url": image_urls  

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
        rolemap=Rolemapping.objects.get(user_id=user_id) 
        if rolemap.roles.name in ['admin','manager','seller']:
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
        rolemap=Rolemapping.objects.get(user_id=user_id) 
        if rolemap.roles.name in ['admin','manager','seller']:
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
    def get(self,request):
        users=request.user
        try:
            user=CustomUser.objects.get(id=users.id)
            rolemap=Rolemapping.objects.get(user_id=users.id) 
            if rolemap.roles.name=='buyer':
                cart=CartItems.objects.filter(user=user.id,is_active=True,bought_status="pending")
                data=[]
                for carts in cart:
                    data.append({ 
                        "product_id":carts.product.id,
                        "product_name":carts.product.name,
                        "quantity":carts.quantity,
                        "price":carts.price,
                        "total_cost":carts.quantity*carts.price,
                        "category":carts.category.name,
                })
                return Response({
                    "status":"success",
                    "message":"data retrieve successfully",
                    "data":data
                    },status=status.HTTP_200_OK)  
            else:
                return Response({
                    "status":"error",
                    "message":"only buyer can access",
                    },status=status.HTTP_403_FORBIDDEN)
        except Rolemapping.DoesNotExist:
            return Response({
                "status":"error",
                "message":"role is not map to user"
            },status=status.HTTP_400_BAD_REQUEST)
        
        except CartItems.DoesNotExist:
            return Response({
                "status":"error",
                "message":"cart is not exists"
            },status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {
                    "status":"error",
                    "message":str(e)
                },status=status.HTTP_400_BAD_REQUEST
            )


    def post(self,request):
        users=request.user
        data=request.data
        category_id=data.get('category')
        product_id=data.get('product')
        quantity=data.get('quantity')
        created_by=request.user.id
    
        
        # Check category, product, quantity is given
        if not category_id or not product_id or quantity is None:
            return Response({
                "status": "error",
                "message": "category, product, and quantity are required"
            }, status=status.HTTP_400_BAD_REQUEST) 

        # If quantity is less than 1
        if quantity < 1:
            return Response({
                "status": "error",
                "message": "quantity must be 1 and above"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Check role
        try:
            user=CustomUser.objects.get(id=users.id)
            rolemap=Rolemapping.objects.get(user_id=users.id) 
            if rolemap.roles.name!='buyer':
                return Response({
                    "status": "error",
                    "message": "Only buyer can access this."
                }, status=status.HTTP_403_FORBIDDEN)

            product = ProductMaster.objects.get(id=product_id, is_active=True)

            # Check category_id
            if product.category.id == category_id and product.is_active:
                # Check product quantity
                if product.quantity < quantity:
                    return Response({
                        "status": "error",
                        "message": f"Only {product.quantity} is available."
                    }, status=status.HTTP_400_BAD_REQUEST)

                with transaction.atomic():
                    items = CartItems.objects.create(
                        category=product.category,
                        product=product,
                        user=user,
                        quantity=quantity,
                        price=product.price,
                        created_by=created_by,
                    )
                return Response({
                    "status": "success",
                    "message": "Successfully added product to cart"
                }, status=status.HTTP_201_CREATED)

        except Rolemapping.DoesNotExist:
            return Response({
                "status": "error",
                "message": "Role is not mapped to user"
            }, status=status.HTTP_400_BAD_REQUEST)

        except ProductMaster.DoesNotExist:
            return Response({
                "status": "error",
                "message": "Product does not exist"
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request):
        users = request.user
        data = request.data
        cart_id = data.get('cart_id')
        quantity = data.get('quantity')
        modified_by = request.user.id

        #check the card_id and quantity is given
        if not cart_id or quantity is None:
            return Response({
                "status": "error",
                "message": "cart_id and quantity are required"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        #if quantity is less than 1
        if quantity <1:
            return Response({
                "status":"error",
                "message":"quantity is  must to be 1 and above"
            },status=status.HTTP_400_BAD_REQUEST)
        #check permission
        try:
            user=CustomUser.objects.get(id=users.id)
            rolemap=Rolemapping.objects.get(user_id=users.id) 
            if rolemap.roles.name!='buyer':
                return Response({
                    "status": "error",
                    "message": "Only buyer can access this."
                }, status=status.HTTP_403_FORBIDDEN)

            cart = CartItems.objects.get(id=cart_id, is_active=True)
           
            with transaction.atomic():
                #check the quantity, and add the product
                if quantity >cart.quantity:

                    if cart.product.quantity < quantity:#check the available of the product
                        return Response({
                            "status": "error",
                            "message": f"Only {cart.product.quantity} items are available."
                        }, status=status.HTTP_403_FORBIDDEN)
                    cart.quantity += quantity 
                #check the quantity and reduce the product
                elif quantity<cart.quantity:
                    cart.quantity -= quantity  

            cart.modified_by = modified_by
            cart.save()

            return Response({
                "status": "success",
                "message": "Successfully updated the cart."
            }, status=status.HTTP_200_OK)

        except Rolemapping.DoesNotExist:
            return Response({
                "status": "error",
                "message": "Role is not mapped to user."
            }, status=status.HTTP_400_BAD_REQUEST)
        except CartItems.DoesNotExist:
            return Response({
                "status": "error",
                "message": "Cart not found."
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
      
    def delete(self,request):
        users=request.user
        data=request.data
        cart_id=data.get('cart_id')
        #check cart_id
        if not cart_id:
            return Response({
                "status":"error",
                'message':"cart id is required"
            },status=status.HTTP_400_BAD_REQUEST)
        #check permission
        try:
            rolemap=Rolemapping.objects.get(user_id=users.id) 
            if rolemap.roles.name!='buyer':
                return Response({
                    "status":"error",
                    "message":"only buyer can access it"
                },status=status.HTTP_400_BAD_REQUEST)
            
            cart=CartItems.objects.get(id=cart_id,is_active=True)

            with transaction.atomic():
                #soft delete
                cart.is_active=False
                cart.save()
                return Response({
                    "status": "success",
                    "message": "Cart is successfully set as inactive."
                }, status=status.HTTP_200_OK)

        except Rolemapping.DoesNotExist:
            return Response({
                "status": "error",
                "message": "Role is not mapped to the user."
            }, status=status.HTTP_400_BAD_REQUEST)
        except CartItems.DoesNotExist:
            return Response({
                "status": "error",
                "message": "cart not found or already inactive."
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


            
            
class GetProductBySeller(APIView):
    def get(self,request):
        try:
            users=request.user
           
            sold=request.query_params.get("sold","all")
            rolemap=Rolemapping.objects.get(user_id=users.id) 
            if rolemap.roles.name=='seller':
                product=ProductMaster.objects.filter(is_active=True,created_by=users.id)
                data=[]
                if sold == 'all':
                    for products in product:
                        bought_products = BuyProducts.objects.filter(is_active=True, product=products.id)
                    
                        sold_quantity = "unsold"
                        
                        if bought_products:
                            for bought in bought_products:
                                sold_quantity = bought.quantity  
                                
                                data.append({
                                    "buyer_details": {
                                        "buyer_id": bought.user.id,
                                        "buyername": bought.user.username
                                    },
                                    'product_id': products.id,
                                    'product_name': products.name,
                                    'description': products.description,
                                    'price': products.price,
                                    'available_quantity': products.quantity,
                                    "category": products.category.name,
                                    "issold": True
                                })

                        else:
                            data.append({
                                "buyer_details": {},
                                'product_id': products.id,
                                'product_name': products.name,
                                'description': products.description,
                                'price': products.price,
                                'available_quantity': products.quantity,
                                "category": products.category.name,
                                "issold": False
                            })

                    return Response({
                        "status": "success",
                        "message": "Data retrieved successfully",
                        "data": {
                            "seller_name": users.username,
                            "seller_mail": users.email,
                            "data": data
                        }
                    })
                elif sold=='yes':
                    try:
                        for products in product: 
                            boughts=BuyProducts.objects.filter(is_active=True,product=products.id)   
                            for bought in boughts:
                                data.append(
                                    {
                                    "buyer details":{
                                        "buyer_id":bought.user.id,
                                        "buyername":bought.user.username
                                    }, 
                                    'product_id': bought.product.id,
                                    'product_name': bought.product.name,
                                    'description': bought.product.description,
                                    'price': bought.product.price,
                                    "category":bought.product.category.name,                                    
                                    'available_quantity': bought.product.quantity,
                                    "sold_quantity":bought.quantity,
                                    "issold":True
                                    })
                        return Response({
                            "status":"sucess",
                            "message":"data retrieve successfully",
                            "data":{
                                "seller_name":users.username,
                                "seller_mail":users.email,
                                "data":data
                            }})
                    except BuyProducts.DoesNotExist:
                        return Response({
                            "status":"error",
                            "message":"buy product does not exists"
                        },status=status.HTTP_400_BAD_REQUEST)
                    except Exception as e:
                        return Response({
                            "status":"failed",
                            "message":str(e)
                        },status=status.HTTP_400_BAD_REQUEST)

                    
                elif sold=='no':
                    try:
                        for products in product:
                            bought_products = BuyProducts.objects.filter(is_active=True, product=products.id)
                                            
                            if bought_products:
                                continue
                            else:
                                data.append(
                                    { 
                                    'product_id': products.id,
                                    'product_name': products.name,
                                    'description': products.description,
                                    'price': products.price,
                                    'available_quantity': products.quantity,
                                    "category":products.category.name,
                                    "issold":False
                                    })
                        return Response({
                            "status":"sucess",
                            "message":"data retrieve successfully",
                            "data":{
                                "seller_name":users.username,
                                "seller_mail":users.email,
                                "data":data
                            }})
                    except Exception as e:
                        return Response({
                            "status":"failed",
                            "message":str(e)
                        },status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({
                "status":"error",
                "message":"enter correct params"
            },status=status.HTTP_400_BAD_REQUEST)  
            else:
                return Response({
                "status":"error",
                "message":"only seller can access"
            },status=status.HTTP_401_UNAUTHORIZED)  
        except Rolemapping.DoesNotExist:
            return Response({
                "status":"error",
                "message":"role not found"
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


        
""""buying the product """
class BuyProductUserApi(APIView):
    
    def post(self,request):
        users=request.user
        data=request.data
        quantity=data.get('quantity')
        cart_id=data.get('cart_id')
        #role check
        try:
            user=CustomUser.objects.get(id=users.id)
            rolemap=Rolemapping.objects.get(user_id=users.id) 
            if rolemap.roles.name=='buyer':
                return Response({
                    "status":"error",
                    "message":"only buyer can access it"
                },status=status.HTTP_400_BAD_REQUEST)
            
             #if quantity is less than 1
            if quantity <1:
                return Response({
                    "status":"error",
                    "message":"quantity is  must to be 1 and above"
                },status=status.HTTP_400_BAD_REQUEST)
            
            created_by=request.user.id

            #the product in cart
            if cart_id:
                try:
                    with transaction.atomic():

                        cart_items=CartItems.objects.get(id=cart_id,is_active=True,user=user)

                        if quantity > cart_items.quantity:
                            return Response({
                                "status":"error",
                                "message":f"only{cart_items.quantity}is available in the cart"
                            },status=status.HTTP_400_BAD_REQUEST)
                        
                        remaining_quantity=cart_items.quantity-quantity
                        #assign the quantity to cart_items
                        cart_items.quantity=quantity
                        # cart_items.bought_status='completed'
                        cart_items.save()

                        buy=BuyProducts.objects.create(
                            user=user,
                            category=cart_items.category,
                            product=cart_items.product,
                            quantity=quantity,
                            price=quantity * cart_items.price,
                            cart_id=cart_id,
                            created_by=created_by
                        )
                        #add the remaining product to productmaster
                        if remaining_quantity>0:
                            cart_items.product.quantity +=remaining_quantity
                            cart_items.product.save()
                            
                        return Response({
                            "status":"success",
                            "message":"Successfully bought the product"
                        },status=status.HTTP_201_CREATED)
                except CartItems.DoesNotExist:
                    return Response({
                "status":"error",
                "message":"role is not map to user"
            },status=status.HTTP_400_BAD_REQUEST)   
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
        
    



class FeedbackMasterAPI(APIView):

    def get(self, request):
        feedback_id = request.query_params.get('feedback_id')
        try:
                feedbacks = feedbackmaster.objects.filter(is_report=False)
                data = [
                    {
                        "id": feedback.id,
                        "feedback_type": feedback.feedback_type,
                        "description": feedback.description,
                        "created_at": feedback.created_at,
                        "modified_at": feedback.modified_at,
                        "is_active": feedback.is_active,
                    }
                    for feedback in feedbacks
                ]
                return Response({
                    "status": "success",
                    "message": "Feedback list retrieved successfully",
                    "data": data
                }, status=status.HTTP_200_OK)
        except feedbackmaster.DoesNotExist:
            return Response({
                "status": "error",
                "message": "Feedback not found"
            }, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        user = request.user
        data = request.data
        feedback_type = data.get('feedback_type')
        is_report = data.get('is_report', False)
        description = data.get('description')
        created_by = request.user.id
        
        
        if not feedback_type:
            return Response({
                "status": "error",
                "message": "feedback_type is required"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        rolename = getrolename(request)
        try:

            if rolename == 'Admin':

                with transaction.atomic():
                    feedback = feedbackmaster.objects.create(
                        feedback_type=feedback_type,
                        is_report=is_report,
                        description=description,
                        created_by=created_by,
                        modified_by=created_by
                    )
                return Response({
                    "status": "success",
                    "message": "Feedback created successfully",
                }, status=status.HTTP_201_CREATED)
            
            else:
                return Response({"status":"error","message":"only admin can add feedback master"},status=400)

        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request):
        data = request.data
        feedback_id = data.get('feedback_id')
        feedback_type = data.get('feedback_type')
        is_report = data.get('is_report')
        description = data.get('description')
        modified_by = request.user.id

        try:
            feedback = feedbackmaster.objects.get(id=feedback_id, is_active=True)

            with transaction.atomic():
                feedback.feedback_type = feedback_type
                feedback.is_report = is_report
                feedback.description = description
                feedback.modified_by = modified_by
                feedback.save()

            return Response({
                "status": "success",
                "message": "Feedback updated successfully"
            }, status=status.HTTP_200_OK)

        except feedbackmaster.DoesNotExist:
            return Response({
                "status": "error",
                "message": "Feedback not found"
            }, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request):
        data = request.data
        feedback_id = data.get('feedback_id')
        if not feedback_id:
            return Response({"status":"error","message":"required fields"},status=400)
        feedback = feedbackmaster.objects.get(id=feedback_id, is_active=True)
        rolename = getrolename(request)
        
        try:
            if rolename == 'Admin':
                with transaction.atomic():
                    feedback.is_active = False
                    feedback.save()

                    return Response({
                        "status": "success",
                        "message": "Feedback deleted successfully"
                    }, status=status.HTTP_200_OK)

        except feedbackmaster.DoesNotExist:
            return Response({
                "status": "error",
                "message": "Feedback not found"
            }, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)