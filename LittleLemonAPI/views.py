from rest_framework.permissions import IsAdminUser, IsAuthenticated, BasePermission
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User, Group
from .serializers import UserSerializer, MenuItemSerializer, CategorySerializer, OrderSerializer, CartSerializer, OrderItemSerializer
from rest_framework import status, generics
from .models import MenuItem, Category, Cart, Order, OrderItem
import random
from decimal import Decimal
from datetime import datetime

class IsManager(BasePermission):
    def has_permission(self,request, view):
        if request.user:
            return request.user.groups.filter(name="Manager")
        return False

class IsOwner(BasePermission):
    def has_object_permission(self,request, view, obj):
        return obj.user == request.user

class IsDeliveryCrew(BasePermission):
    def has_object_permission(self,request, view, obj):
        return obj.delivery_crew == request.user

class IsManagerOrOwnerOrDeliveryCrew(BasePermission):
    def has_permission(self,request, view):
        return IsManager().has_permission(request, view)
    
    def has_object_permission(self,request, view, obj):
        return IsOwner().has_object_permission(request, view, obj) or IsDeliveryCrew().has_object_permission(request, view, obj)
class IsManagerOrOwner(BasePermission):
    def has_permission(self,request, view):
        return IsManager().has_permission(request, view)
    
    def has_object_permission(self,request, view, obj):
        return IsOwner().has_object_permission(request, view, obj) 
    
@api_view(['POST', 'GET'])
@permission_classes([IsAdminUser])
def managers(request):
    managers = Group.objects.get(name='Manager')
    if request.method == 'POST':
        username = request.data['username']
        if username:
            user = get_object_or_404(User, username=username)
            managers.user_set.add(user)
            return Response({"message": "user added to manager group"}, status=status.HTTP_201_CREATED)
        return Response({"message": "error"}, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'GET':
        users = managers.user_set.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
    elif request.method == 'DELETE':
        user = get_object_or_404(User, username=request.data['username'])
        managers = Group.objects.get(name="Manager")
        managers.user_set.remove(user)
        return Response({"message": "user removed from the manager group"}, 200)


@api_view(['POST', 'GET'])
@permission_classes([IsManager])
def delivery_crew(request):
    delivery_crew = Group.objects.get(name='Delivery Crew')
    if request.method == 'POST':
        username = request.data['username']
        if username:
            user = get_object_or_404(User, username=username)
            delivery_crew.user_set.add(user)
            return Response({"message": "user add to delivery crew"}, status=status.HTTP_201_CREATED)
        return Response({"message":"error"}, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'GET':
        users = delivery_crew.user_set.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
    elif request.method == 'DELETE':
        if not request.user.is_superuser:
            if not request.user.groups.filter(name='Manager').exists():
                return Response({"message":"forbidden"}, status.HTTP_403_FORBIDDEN)
        user = get_object_or_404(User, username=request.data['username'])
        dc = Group.objects.get(name="Delivery Crew")
        dc.user_set.remove(user)
        return Response({"message": "user removed from the delivery crew group"}, 200)


class MenuItemsView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    search_fields = ['category__title']
    ordering_fields = ['price', 'inventory']
    
    def get_permissions(self):
        if (self.request.method == 'GET'):
            return []
        return [IsAdminUser()]

class SimpleMenuItemView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    
    def get_permissions(self):
        if(self.request.method == 'GET'):
            return []
        return [IsManager()]
    
class CategoriesView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if (self.request.method == 'GET'):
            return []
        return [IsAdminUser()]

# @api_view(['PUT'])
# @permission_classes([IsManager])
# def itemDay(request):
#     all_items = MenuItem.objects.all()
#     featured_items = []
#     for item in all_items:
#         item.featured = random.choice([True, False])
#         item.save()
#         if item.featured:
#             featured_items.append(item)
#     items = MenuItemSerializer(featured_items, many=True)
#     return Response(items.data, status=status.HTTP_200_OK)

class SimpleOrderView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    
    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsManagerOrOwnerOrDeliveryCrew()]

        elif self.request.method in ['PUT', 'PATCH']:
            if self.request.data.get('delivery_crew'):
                return [IsManager()]
            elif self.request.data.get('status'):
                return [IsDeliveryCrew()]
        
        elif self.request.method == 'DELETE':
            return [IsManagerOrOwner()]
        return super().get_permissions()

class CartView(generics.ListCreateAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_class = [IsAuthenticated()]

    def get_queryset(self):
        return Cart.objects.all().filter(user=self.request.user).order_by('id')
    
    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data['user'] = self.request.user.id
        data['unit_price'] = MenuItem.objects.get(id=data['menuitem']).price
        data['price'] = Decimal(data['unit_price']) * int(data['quantity'])
        cart_serializer = CartSerializer(data=data)

        if cart_serializer.is_valid():
            cart_serializer.save()
            return Response(cart_serializer.data, status=status.HTTP_201_CREATED)
        return Response(cart_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, *args, **kwargs):
        Cart.objects.all().filter(user=request.user).delete()
        return Response("ok")
    
    
class OrdersView(generics.ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Order.objects.all().order_by('id')
        elif self.request.user.groups.count()==0: #Normal customer - no group
            return Order.objects.all().filter(user=self.request.user).order_by('id')
        elif self.request.user.groups.filter(name='Delivery Crew').exists(): #Delivery crew
            return Order.objects.all().filter(delivery_crew=self.request.user).order_by('id')  #Only show orders assigned to him
        else: # Manager
            return Order.objects.all().order_by('id')
        # else:
        #     return Order.objects.all()
    
    def create(self, request, *args, **kwargs):
        menuitem_count = Cart.objects.all().filter(user=request.user).count()
        if (menuitem_count == 0):
            return Response({"message": "No item in cart"})
        
        data = request.data.copy()
        total = self.get_total_price(self.request.user)
        data['total'] = total
        data['user'] = request.user.id
        data['date'] = datetime.now().date()
        order_serializer = OrderSerializer(data=data)

        if (order_serializer.is_valid()):
            order = order_serializer.save()

            items = Cart.objects.all().filter(user=request.user)
            for item in items:
                order_item = OrderItem(order=order, menuitem=item.menuitem, quantity=item.quantity, unit_price=item.unit_price, price=item.price)
                order_item.save()
            
            Cart.objects.all().filter(user=request.user).delete()

            return Response(order_serializer.data, status=status.HTTP_201_CREATED)
        return Response(order_serializer.errors, status=status.HTTP_400_BAD_REQUEST)  
            

    def get_total_price(self, user):
        total = 0
        items = Cart.objects.all().filter(user=user)
        for item in items:
            total += item.price
        return total
        
 
class SingleOrderView(generics.RetrieveUpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        if self.request.user.groups.count()==0: # Normal user, not belonging to any group = Customer
            return Response('Not Ok')
        else: #everyone else - Super Admin, Manager and Delivery Crew
            return super().update(request, *args, **kwargs)




    