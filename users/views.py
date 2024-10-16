from django.shortcuts import render
from rest_framework.views import APIView,status
from rest_framework.response import Response
from users.models import CustomUser,RoleMaster,Rolemapping,SellerDetail
from django.db import transaction
from django.shortcuts import render
from rest_framework.views import APIView,Response,status
from orders.models import CategoryMaster
from django.db import transaction
from django.contrib.auth.hashers import make_password,check_password
from rest_framework_simplejwt.tokens import RefreshToken
from orders.function import *

class RolemasterView(APIView):
    """get role details"""
    def get(self,request):
        try:
            role=RoleMaster.objects.filter(is_active=True)
            data=[]
            for roles in role:
                data.append({
                    "role_id":roles.id,
                    "name":roles.name,
                    "description":roles.description,
                    "is_active":roles.is_active
                    })
            return Response({
                "status":"success",
                "message":"data retrieve successfully",
                "data":data
            },status=status.HTTP_200_OK)
        except RoleMaster.DoesNotExist:
            return Response({
                "staus":"error",
                "message":"role not found"
            },status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "status":"failed",
                "message":str(e)
            },status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    """create role"""
    def post(self,request):
        try:   
            data=request.data
            name=data.get("name")
            description=data.get("description")
            created_by=request.data.get('created_by')
            modified_by=request.data.get('modified_by')

            with transaction.atomic():
                user=RoleMaster(
                    name=name,
                    description=description,
                    created_by=1
                )  
                user.save()
                return Response({
                    "status":"sucess",
                    "message":"rolemaster created successfully"
                },status=status.HTTP_201_CREATED)
        except Exception as  e:
            return Response({
                "status":"fssiled",
                "message":str(e)
                },status=status.HTTP_400_BAD_REQUEST)
            
    """update role"""
    def put(self,request):
        try:
            data=request.data
            role_id=data.get("role_id")
            name=data.get("role_name")
            description=data.get("description")
                        
            with transaction.atomic():
                roles=RoleMaster.objects.get(id=role_id,is_active=True) 
                roles.name = name
                roles.description = description
        
                roles.save()
                return Response({
                    "status":"success",
                    "message":"data updated successfully"
                },status=status.HTTP_200_OK)
        except RoleMaster.DoesNotExist:
            return Response({
                "staus":"error",
                "message":"role not found or role is not active"
            },status=status.HTTP_400_BAD_REQUEST)           
        except Exception as e:
            return Response({
                "status":"failed",
                "message":str(e)
            },status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    """delete role"""       
    def delete(self,request):
        try:
            data=request.data
            role_id=request.data.get("role_id")
            
            with transaction.atomic():
                roles=RoleMaster.objects.get(id=role_id,is_active=True)
                # if not roles.is_active:
                #     return Response({
                #         "status":"error",
                #         "message":"only roles with active is allow to update"    
                #     })
                roles.is_active=False
                roles.save()
                return Response({
                    "status":"success",
                    "message":"role is not active"
                },status=status.HTTP_200_OK)
        except RoleMaster.DoesNotExist:
            return Response({
                "staus":"error",
                "message":"role not found or role is not active"
            },status=status.HTTP_400_BAD_REQUEST)           
        except Exception as e:
            return Response({
                "status":"failed",
                "message":str(e)
            },status=status.HTTP_400_BAD_REQUEST) 



#register
class RegisterUserApi(APIView):
    """get user"""
    def get(self,request):
        access_user=request.user
        try:
            maps=Rolemapping.objects.get(user=access_user,roles__name__in=['admin','manager'])
        except Rolemapping.DoesNotExist:
            return Response({
                "status":"error",
                "message":"Only admin and manager has a permission"
            },status=status.HTTP_400_BAD_REQUEST) 
        
        user_type=request.query_params.get("user_type")

        try:   
            users=CustomUser.objects.filter(is_active=True)
            data=[]
            if user_type:
                if user_type=="buyer":
                    mapping=Rolemapping.objects.filter(user__in=users,roles__name='buyer')
                    for map in mapping:
                        user=map.user
                        # print(map)
                        # print(user)     
                        data.append({
                            "username":user.username,
                            "first_name":user.first_name,
                            "last_name":user.last_name,
                            "email":user.email,
                            "mobile_number":user.mobile_number
                        })
                    return Response({
                            "status":"success",
                            "message":"data retrieve successfully",
                            "data":data
                        },status=status.HTTP_200_OK) 
                elif user_type=="seller":
                    mapping=Rolemapping.objects.filter(user__in=users,roles__name='seller')
                    for map in mapping:
                        user=map.user
                        data.append({
                            "username":user.username,
                            "first_name":user.first_name,
                            "last_name":user.last_name,
                            "email":user.email,
                            "mobile_number":user.mobile_number
                        }) 
                    return Response({
                            "status":"success",
                            "message":"data retrieve successfully",
                            "data":data
                        },status=status.HTTP_200_OK) 
            else:
                mapping=Rolemapping.objects.filter(user__in=users,roles__name__in=['seller','buyer'])
                for map in mapping:
                    user=map.user
                    role_name=[role.name for role in map.roles.all()]
                
                    data.append({
                        "username":user.username,
                        "first_name":user.first_name,
                        "last_name":user.last_name,
                        "email":user.email,
                        "mobile_number":user.mobile_number,
                        "rolename":role_name
                    }) 
                return Response({
                        "status":"success",
                        "message":"data retrieve successfully",
                        "data":data
                    },status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({
            "status":"error",
            "message":"users not found"
        },status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "status":"failed",
                "message":str(e)
            },status=status.HTTP_400_BAD_REQUEST)

    """create user"""
    def post(self,request):
        user=request.user
        data=request.data
        first_name=data.get('first_name')
        last_name=data.get('last_name')
        email=data.get('email')
        password=data.get('password')
        mobile_number=data.get('mobile_number')
        username=first_name+" "+last_name
        role_name=data.get('roles',[])
        
        #check email and mobile number it is already exits
        if CustomUser.objects.filter(email=email) or CustomUser.objects.filter(mobile_number=mobile_number):
            return Response({
                "status":"error",
                "message":"email or mobile_number is already exists."
            },status=status.HTTP_400_BAD_REQUEST)
        role_id=[]
        #check role_name
        for role in role_name:
            if role not in ['Admin','manager', 'buyer', 'seller','delivary_person']:
                return Response({
                    "status": "error",
                    "message": "Invalid role."
                }, status=status.HTTP_400_BAD_REQUEST)


            #check if role_name is manager
            if role == 'manager':
                users=Rolemapping.objects.filter(user=user,roles__name=ADMIN)
              
                if not users:
                    return Response({"status":"error",
                                     "message":"only admmin has a permission to create a manager"
                                     },status=status.HTTP_400_BAD_REQUEST)
            try:
                role_name=RoleMaster.objects.get(name=role)
                role_id.append(role_name.id)
                #print(role_id)
            except RoleMaster.DoesNotExist:
                return Response({
                    "status":"error",
                    "message":"role is not exists"
                },status=status.HTTP_400_BAD_REQUEST)
       
        try:
            with transaction.atomic():         
                new_user = CustomUser.objects.create(
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    password=make_password(password),
                    mobile_number=mobile_number,
                    username=username,
                    created_by = user.id if user.is_authenticated else 1
                    )
     
              #map the user with their role
                new_user_roles= Rolemapping.objects.create(
                    user=new_user,
                    created_by = user.id if user.is_authenticated else 1
                )
                new_user_roles.roles.set(role_id)
            return Response({
                "status": "success",
                "message": "User created and mapped successfully."
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)        

class LoginUserApi(APIView):
    #login user
    def post(self,request):
        data=request.data
        mobile_number=data.get('mobile_number')
        password=data.get('password')

        #check mobile_number and password is given
        if not mobile_number or not  password:
            return Response({
                "status":"error",
                "message":"mobile_number and password is required to give"
            },status=status.HTTP_400_BAD_REQUEST)
        #check mobile_number and password
        try:
            with transaction.atomic():
                user=CustomUser.objects.get(mobile_number=mobile_number)
                role=Rolemapping.objects.filter(user=user,roles__name='seller')
                if role:
                    if(user.is_approval == False):
                        return Response({
                            "status":"error",
                            "message":"Seller is need approval from manager"
                        },status=status.HTTP_400_BAD_REQUEST)

                if check_password(password,user.password):
                    #create token
                    token=RefreshToken.for_user(user)
                    roles = RoleMaster.objects.get(id=user.last_login_role_id)
                    token['role_id']=roles.id
                    token['role_name']=roles.name
                    access_token=str(token.access_token)
                    
                    return Response({
                        'status':"success",
                        "message":"login successfull",
                        "data":access_token
                    },status=status.HTTP_200_OK)
                else:
                    return Response({
                        "status":"error",
                        "message":"invaid email or password"
                    },status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
             return Response({
                        "status":"error",
                        "message":str(e)
                    },status=status.HTTP_400_BAD_REQUEST)

class RoleLogin(APIView):
    def post(self,request):
        try:
            users=request.user
            role_type=request.data.get('role_type')
            with transaction.atomic():
                user=CustomUser.objects.get(id=users.id)
                rolemap=Rolemapping.objects.get(user_id=user.id)
                print(rolemap.roles)
                print(role_type)
                if rolemap.roles.filter(id=role_type).exists():
                    user.last_login_role_id=role_type
                    user.save()
                    role=RoleMaster.objects.get(id=role_type)
                    token=RefreshToken.for_user(user)
                    token['role_id']=role.id
                    token['role_name']=role.name
                    access_token=str(token.access_token)
                    return Response({
                        'status':"success",
                        "message":"login successfull",
                        "data":access_token
                    },status=status.HTTP_200_OK)
                # for rolese in rolemap.roles:
                #     role=RoleMaster.objects.get(id=rolese)
                #     # print(role_type)
                #     if rolese==role_type:
                            
                #             token=RefreshToken.for_user(user)
                #             access_token=str(token.access_token)
                #             return Response({
                #                 'status':"success",
                #                 "message":"login successfull",
                #                 "data":access_token
                #             },status=status.HTTP_200_OK)
                return Response({
                        "status":"error",
                        "message":"roles not found"
                    },status=status.HTTP_400_BAD_REQUEST)
        except CustomUser.DoesNotExist:
            return Response({
                "status": "error",
                "message": "user does not exist."
            }, status=status.HTTP_400_BAD_REQUEST)
        except RoleMaster.DoesNotExist:
            return Response({
                "status": "error",
                "message": "Role does not exist."
            }, status=status.HTTP_400_BAD_REQUEST)
        except Rolemapping.DoesNotExist:
            return Response({
                "status": "error",
                "message": "Rolemap does not exist."
            }, status=status.HTTP_400_BAD_REQUEST)               
        except Exception as e:
             return Response({
                        "status":"error",
                        "message":str(e)
                    },status=status.HTTP_400_BAD_REQUEST)

class SellerApproval(APIView):
    def post(self,request):
        user=request.user
        data=request.data

        id=data.get('id')        
        try:
            with transaction.atomic():
       
                users=CustomUser.objects.get(id=id,is_approval=False)
                role=Rolemapping.objects.filter(user=users,roles__name='seller')
                if  not role:
                    return Response({
                        "status":"error",
                        "message":"seller is not exists"
                    },status=status.HTTP_400_BAD_REQUEST)
                try:

                    roles=Rolemapping.objects.get(user=user,roles__name='manager') 
                    users.is_approval=True
                    users.save()

                    return Response({
                        "status":"success",
                        "message":"Seller has approval to login"
                    },status=status.HTTP_200_OK)
                
                except Rolemapping.DoesNotExist:
                    return Response({
                        "status":"error",
                        "message":"manager is not exists"
                    },status=status.HTTP_400_BAD_REQUEST)
        except CustomUser.DoesNotExist:
                    return Response({
                        "status":"error",
                        "message":"user is not exists"
                    },status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
             return Response({
                        "status":"error",
                        "message":str(e)
                    },status=status.HTTP_400_BAD_REQUEST)
            
    def get(self,request):
        users=request.user
        try:
            roles=Rolemapping.objects.get(user_id=users,roles__name='manager')
            if roles:
                user=CustomUser.objects.filter(is_approval=False)       
                sellers=Rolemapping.objects.filter(roles__name='seller',user__in=user) 
                seller_details=[]  
                for seller in sellers:
                    seller_details=[ 
                        {
                            "id":seller.user.id,
                            "name":seller.user.username,
                            "mobile_number":seller.user.mobile_number,
                            "email":seller.user.email
                        }       
                        ]
                return Response({
                    "status":"success",
                    "message":"Approval not give to seller",
                    "data":seller_details
                },status=status.HTTP_200_OK)
        except Rolemapping.DoesNotExist:
            return Response({
                "status":"error",
                "message":"role is not exists"
            },status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "status":"error",
                "message":str(e)
            },status=status.HTTP_400_BAD_REQUEST)
                  
class RolemappingView(APIView):
    def get(self,request):
        try:
            print(request)
            users=request.user.id
            rolemap=Rolemapping.objects.prefetch_related('roles').get(user_id=users,is_active=True)
            print(rolemap)
            data=[]
            # for rolemaps in rolemap:
            roles=rolemap.roles.all()
            role_list = [role.name for role in roles]
            print(role_list)
            data.append({
                    'user_id': rolemap.user_id,
                    'roles': role_list,
                    'is_active': rolemap.is_active,
                    'created_at': rolemap.created_at,
                    'modified_at': rolemap.modified_at,
                })
            return Response({
                            "status":"success",
                            "message":"data retrieve successfully",
                            "data":data
                        },status=status.HTTP_200_OK)
        except Rolemapping.DoesNotExist:
            return Response({
                "status": "error",
                "message": "Rolemap does not exist."
            }, status=status.HTTP_400_BAD_REQUEST)               
        except Exception as e:
             return Response({
                        "status":"error",
                        "message":str(e)
                    },status=status.HTTP_400_BAD_REQUEST)
             
class SellerRegistrationAPI(APIView):
    def post(self, request):
        mobile_no = request.data.get("mobile_no")
        email = request.data.get("email")
        seller_details = request.data.get("Seller_detail")
        try:
        
            for seller_data in seller_details:
                business_name = seller_data.get("bussiness_name")
                business_email = seller_data.get("bussiness_email")
                category_id = seller_data.get("category_id")
                bussiness_ph=seller_data.get("bussiness_ph")
                bussiness_address=seller_data.get("bussiness_add")
                shipping_address=seller_data.get("shipping_add")
                organization=seller_data.get("organization")
                documents = request.FILES.getlist('documents', None)


                if not mobile_no or not email:
                    return Response({"status":"error","message": "Mobile number and email are required."}, status=status.HTTP_400_BAD_REQUEST)

                if not seller_details:
                    return Response({"status":"error","message":"Seller details are required and must be a list."}, status=status.HTTP_400_BAD_REQUEST)  
                    
                try:
                    transaction.set_autocommit(False)
                    user = CustomUser.objects.get(mobile_number=mobile_no, email=email)
                    category = CategoryMaster.objects.get(id=category_id)
                    role=RoleMaster.objects.get(name=SELLER,is_active=True)
                    

                    if not business_name or not business_email or not category_id:
                        transaction.rollback()
                        return Response({"status":"error","message": f"Missing required fields in seller data: {seller_data}"},status=status.HTTP_400_BAD_REQUEST)
                    
                    document_urls = []
                    if documents:
                                
                                for document in documents:
                                    file_name = document.name
                                    document_url = upload_image_s3(document, file_name)
                                    if document_url:
                                        document_urls.append(document_url)
                    rolemap_exists=Rolemapping.objects.get(user=user)
                    if role not in rolemap_exists.roles.all():
                        rolemap_exists.roles.add(role) 
                        rolemap_exists.save()
                        print(rolemap_exists.roles)
                    
                    seller_detail = SellerDetail(
                        user=user,
                        bussiness_name=business_name,
                        bussiness_email=business_email,
                        bussiness_ph=bussiness_ph,
                        bussiness_address=bussiness_address,
                        shipping_address=shipping_address,  
                        organization=organization,
                        documents=document_urls, 
                        category=category,
                    )
                    
                    seller_detail.save()
                    rolemap_exists.save()
                    transaction.commit()
                except CustomUser.DoesNotExist or RoleMaster.DoesNotExist:
                    return Response({"status":"error","message":"data not found."}, status=status.HTTP_404_NOT_FOUND)
                except CategoryMaster.DoesNotExist:
                        transaction.rollback()
                        return Response({"status":"error","message": f"Invalid category ID: {category_id}"}, status=status.HTTP_400_BAD_REQUEST)
                        
                except Exception as e:
                    transaction.rollback()
                    return Response({ "status": "failed", "message": str(e) }, status=status.HTTP_400_BAD_REQUEST)
            
            return Response({"status":"sucess","message": "Seller registered successfully"}, status=status.HTTP_201_CREATED)
        except Exception as e:
                    return Response({ "status": "failed", "message": str(e) }, status=status.HTTP_400_BAD_REQUEST)
        
    def get(self,request):
        role,user=getuserinfo(request)
        
        try:
            if role==MANAGER:
                sellers=SellerDetail.objects.filter(is_active=True,approval_status=PENDING)
                data=[]
                for seller in sellers:
                    data.append({
                        "seller_id":seller.id,
                        "bussiness_name": seller.bussiness_name,
                        "bussiness_email": seller.bussiness_email,
                        "bussiness_ph": seller.bussiness_ph,
                        "bussiness_add": seller.bussiness_address,
                        "shipping_add": seller.shipping_address,
                        "organization": seller.organization,
                        "category_id": seller.category.id,
                        "documents":seller.documents
                    })
                return Response({"status":"success","message":"data retrieved successfully","data":data},status=status.HTTP_200_OK)
            else:
                return Response({"status":"error","message":"Only Manager retrieve seller details"},status=status.HTTP_400_BAD_REQUEST)
        except SellerDetail.DoesNotExist:
                return Response({"status":"error","message":"seller not found"},status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
                return Response({"status":"failed","message":str(e)},status=status.HTTP_400_BAD_REQUEST)

    def put(self,request):
        role,user_id=getuserinfo(request)
        seller_id=request.data.get("seller_id")
        is_approval=request.data.get("is_approval")
        
        try:
            if role !=MANAGER:
                return Response({"status":"error","message":"Only Manager approve seller "},status=status.HTTP_400_BAD_REQUEST)
            try:
                transaction.set_autocommit(False)
                seller=SellerDetail.objects.get(id=seller_id,is_active=True)
                seller.approval_status=is_approval
                user=CustomUser.objects.get(id=seller.user.id,is_active=True)
                if not user.is_approval:    
                    if seller.approval_status==ACCEPTED:
                        user.is_approval=True
                        user.save()
                seller.save()
                transaction.commit()
                return Response({"status":"sucess","message": "Seller approval status updated successfully"}, status=status.HTTP_201_CREATED)
            

            except SellerDetail.DoesNotExist or CustomUser.DoesNotExist:
                transaction.rollback()
                return Response({"status":"error","message":"data not found"},status=status.HTTP_400_BAD_REQUEST)  
              
        except Exception as e:
            transaction.rollback()
            return Response({"status":"failed","message":str(e)},status=status.HTTP_400_BAD_REQUEST)
            
            
        

