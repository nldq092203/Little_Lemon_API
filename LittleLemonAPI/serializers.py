from rest_framework import serializers
from .models import MenuItem, Category, Cart, Order, OrderItem
from rest_framework.validators import UniqueTogetherValidator
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email']
        
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'slug', 'title']

class MenuItemSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'price', 'featured', 'category', 'category_id']

class CartSerializer(serializers.ModelSerializer):
    menuitem = MenuItemSerializer(read_only=True)
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        default = serializers.CurrentUserDefault()
    )
    class Meta:
        model = Cart
        fields = ['id', 'user', 'menuitem', 'quantity', 'unit_price', 'price']
        validators = UniqueTogetherValidator(
            queryset = Cart.objects.all(),
            fields = ['menuitem', 'user']
        )

class OrderSerializer(serializers.ModelSerializer):
    menuitem = MenuItemSerializer(read_only=True)
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        default = serializers.CurrentUserDefault()
    )
    class Meta:
        model = Order
        fields = ['id', 'user', 'delivery_crew', 'status', 'total', 'date']

class OrderItemSerializer(serializers.ModelSerializer):
    order = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        default = serializers.CurrentUserDefault()
    )
    menuitem = MenuItemSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'order', 'menuitem', 'quantity', 'unit_price', 'price']
        validators = UniqueTogetherValidator(
            queryset = OrderItem.objects.all(),
            fields = ['order', 'menuitem']
        )