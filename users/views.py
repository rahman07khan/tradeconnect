from django.shortcuts import render
from rest_framework.views import APIView,status
from rest_framework.response import Response
from users.models import CustomUser,RoleMaster,Rolemapping
from django.db import transaction
from django.shortcuts import render
from rest_framework.views import APIView,Response,status
from .models import CustomUser,RoleMaster,Rolemapping
from django.db import transaction
from django.contrib.auth.hashers import make_password,check_password
from rest_framework_simplejwt.tokens import RefreshToken



# Create your views here.

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
        user_id=request.user.id
        maps=Rolemapping.objects.get(user=user_id)
        user_type=request.query_params.get("user_type")
        if maps.role.name in ['admin','manager']:
            try:
                
                users=CustomUser.objects.filter(is_active=True)
                data=[]
                if user_type:
                    if user_type=="buyer":
                        for user in users:
                            mapping=Rolemapping.objects.get(id=user.id)
                            if mapping.role.name=="buyer":
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
                        for user in users:
                            mapping=Rolemapping.objects.get(id=user.id)
                            if mapping.role.name=="seller":
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
                    for user in users:
                        mapping=Rolemapping.objects.get(id=RegisterUserApi.id)
                        if mapping.role.name in ['seller','buyer']:
                            data.append({
                                "username":user.username,
                                "first_name":user.first_name,
                                "last_name":user.last_name,
                                "email":user.email,
                                "mobile_number":user.mobile_number,
                                "rolename":mapping.role.name
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
        
        #check role_name
        for role in role_name:
            if role not in ['manager', 'buyer', 'seller']:
                return Response({
                    "status": "error",
                    "message": "Invalid role."
                }, status=status.HTTP_400_BAD_REQUEST)


            #check if role_name is manager
            if role == 'manager':
                #print(role)
                try:
                    user_mapping = Rolemapping.objects.get(user=user)
                    role_ids=user_mapping.roles
                    roles=RoleMaster.objects.filter(id__in=role_ids)
                    role_names=[role.name for role in roles]
                    if 'admin'not in role_names:

                        return Response({
                            "status": "error",
                            "message": "Only admin can create a manager."
                        }, status=status.HTTP_403_FORBIDDEN)
                except Rolemapping.DoesNotExist:
                    return Response({
                        "status": "error",
                        "message": "User does not have a role assignment."
                    }, status=status.HTTP_403_FORBIDDEN)
                
        #gather the role_id     
        role_id = [role.id for role in RoleMaster.objects.filter(name__in=role_name)]
        if not role_id:
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
                    created_by=user.id if user  else 1
                    )
     
              #map the user with their role
                Rolemapping.objects.create(
                    user=new_user,
                    roles=role_id,
                    created_by=user.id if user else 1
                )
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
                if check_password(password,user.password):
                    #create token
                    token=RefreshToken.for_user(user)
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
        user_id=request.user.id
        maps=Rolemapping.objects.get(user=user_id)
        user_type=request.query_params.get("user_type")
        if maps.role.name in ['admin','manager']:
            try:
                
                users=CustomUser.objects.filter(is_active=True)
                data=[]
                if user_type:
                    if user_type=="buyer":
                        for user in users:
                            mapping=Rolemapping.objects.get(id=user.id)
                            if mapping.role.name=="buyer":
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
                        for user in users:
                            mapping=Rolemapping.objects.get(id=user.id)
                            if mapping.role.name=="seller":
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
                    for user in users:
                        mapping=Rolemapping.objects.get(id=RegisterUserApi.id)
                        if mapping.role.name in ['seller','buyer']:
                            data.append({
                                "username":user.username,
                                "first_name":user.first_name,
                                "last_name":user.last_name,
                                "email":user.email,
                                "mobile_number":user.mobile_number,
                                "rolename":mapping.role.name
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
            if role not in ['manager', 'buyer', 'seller']:
                return Response({
                    "status": "error",
                    "message": "Invalid role."
                }, status=status.HTTP_400_BAD_REQUEST)


            #check if role_name is manager
            if role == 'manager':
                users=Rolemapping.objects.filter(user=user,roles__name='admin')
              
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
                    created_by=user.id if user  else 1
                    )
     
              #map the user with their role
                new_user_roles= Rolemapping.objects.create(
                    user=new_user,
                    created_by=user.id if user else 1
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