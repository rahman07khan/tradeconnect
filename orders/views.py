from django.shortcuts import render
from orders.models import CategoryMaster
from rest_framework.views import APIView,status
from rest_framework.response import Response
from django.db import transaction



#CategoryMaster CRUD
class CategoryView(APIView):
    def get(self,request):
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
            },status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            
    def post(self,request):
        try:
            data=request.data
            name=data.get("name")
            description=data.get("description")
            
            with transaction.atomic():
                category=CategoryMaster(
                    name=name,
                    description=description,
                    created_by=1,
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
            },status=status.HTTP_500_INTERNAL_SERVER_ERROR)  
            
    
    def put(self,request):
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
            },status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    def delete(self,request):
        try:
            data=request.data 
            category_id=data.get("category_id")
            
            with transaction.atomic():
                categories=CategoryMaster.objects.get(id=category_id)
                if not categories.is_active:
                    return Response({
                        "status":"error",
                        "message":"only category with active is allow to delete"    
                    })
                categories.is_active=False
                
                categories.save()
                return Response({
                    "status":"success",
                    "message":"category is not active"
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
            },status=status.HTTP_500_INTERNAL_SERVER_ERROR)