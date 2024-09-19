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
    def post(self,request):
        user=request.user
        data=request.data
        first_name=data.get('first_name')
        last_name=data.get('last_name')
        email=data.get('email')
        password=data.get('password')
        mobile_number=data.get('mobile_number')
        username=first_name+" "+last_name
        role_name=data.get('role')
        
        #check email and mobile number it is already exits
        if CustomUser.objects.filter(email=email) or CustomUser.objects.filter(mobile_number=mobile_number):
            return Response({
                "status":"error",
                "message":"email or mobile_number is already exists."
            },status=status.HTTP_400_BAD_REQUEST)
        
        if role_name not in ['manager', 'buyer', 'seller']:
            return Response({
                "status": "error",
                "message": "Invalid role."
            }, status=status.HTTP_400_BAD_REQUEST)

        
        if role_name == 'manager':
            try:
                user_mapping = Rolemapping.objects.get(user=user)
                user_role_name = user_mapping.role.name
            except Rolemapping.DoesNotExist:
                return Response({
                    "status": "error",
                    "message": "User does not have a role assignment."
                }, status=status.HTTP_403_FORBIDDEN)

            if user_role_name != 'admin':
                return Response({
                    "status": "error",
                    "message": "Only admin can create a manager."
                }, status=status.HTTP_403_FORBIDDEN)
        try:
    
            role = RoleMaster.objects.get(name=role_name)
        except RoleMaster.DoesNotExist:
            return Response({
                "status": "error",
                "message": "Role does not exist."
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                
                new_user = CustomUser.objects.create(
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    password=make_password(password),
                    mobile_number=mobile_number,
                    username=username,
                    created_by=user.id if role_name=='manager' else 1,
                    modified_by=user.id if role_name=='manager' else 1
                    )
                
              
                Rolemapping.objects.create(
                    user=new_user,
                    role=role,
                    created_by=user.id if role_name=='manager' else 1,
                    modified_by=user.id if role_name=='manager' else 1
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
    def post(self,request):
        data=request.data
        mobile_number=data.get('mobile_number')
        password=data.get('password')
        if not mobile_number or not  password:
            return Response({
                "status":"error",
                "message":"mobile_number and password is required to give"
            },status=status.HTTP_400_BAD_REQUEST)
        try:
            with transaction.atomic():
                user=CustomUser.objects.get(mobile_number=mobile_number)
                if check_password(password,user.password):
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
