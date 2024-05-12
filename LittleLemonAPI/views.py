from rest_framework.permissions import IsAdminUser, IsAuthenticated, BasePermission
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User, Group
from .serializers import UserSerializer, MenuItemSerializer, CategorySerializer, OrderSerializer, CartSerializer, OrderItemSerializer
from rest_framework import status, generics
from .models import MenuItem, Category, Cart, Order, OrderItem
import random

class IsManager(BasePermission):
    def has_permission(self,request, view):
        if request.user:
            return request.user.groups.filter(name="Manager")
        return False

@api_view(['POST', 'GET'])
@permission_classes([IsAdminUser])
def managers(request):
    username = request.data['username']
    if username:
        user = get_object_or_404(User, username=username)
        managers = Group.objects.get(name='Manager')
        if request.method == 'POST':
            managers.user_set.add(user)
            return Response({"message": "user added to manager group"}, status=status.HTTP_201_CREATED)
        elif request.method == 'GET':
            users = managers.user_set.all()
            serializer = UserSerializer(users, many=True)
            return Response(serializer.data)
    return Response({"message":"error"}, status=status.HTTP_400_BAD_REQUEST)


class MenuItemsView(generics.ListCreateAPIView):
    queryset = MenuItem
    serializer_class = MenuItemSerializer
    
    def get_permissions(self):
        if (self.request.method == 'GET'):
            return []
        return [IsAuthenticated()]
    
class CategoriesView(generics.ListCreateAPIView):
    queryset = Category
    serializer_class = CategorySerializer

    def get_permissions(self):
        if (self.request.method == 'GET'):
            return []
        return [IsAuthenticated()]

@api_view(['PUT'])
@permission_classes([IsManager])
def itemDay(request):
    all_items = MenuItem.objects.all()
    featured_items = []
    for item in all_items:
        item.featured = random.choice([True, False])
        item.save()
        if item.featured:
            featured_items.append(item)
    items = MenuItemSerializer(featured_items, many=True)
    return Response(items.data, status=status.HTTP_200_OK)