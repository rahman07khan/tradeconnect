from django.shortcuts import render
from rest_framework.views import APIView,status
from rest_framework.response import Response
from users.models import CustomUser,RoleMaster,Rolemapping
from django.db import transaction


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
                roles=RoleMaster.objects.get(id=role_id)
                if not roles.is_active:
                    return Response({
                        "status":"error",
                        "message":"only roles with active is allow to update"    
                    })
                roles.is_active=False
                roles.save()
                return Response({
                    "status":"success",
                    "message":"role is not active"
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