from rest_framework import serializers
from .models import MenuItem, Category, Cart, Order, OrderItem
from rest_framework.validators import UniqueTogetherValidator
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']
        
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'slug', 'title']

class MenuItemSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True)
    # category = serializers.PrimaryKeyRelatedField(
    #     queryset=Category.objects.all()
    # )

    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'price', 'featured', 'category', 'category_id']
        # fields = ['id', 'title', 'price', 'featured', 'category']

class CartSerializer(serializers.ModelSerializer):
    # menuitem = MenuItemSerializer(read_only=True)
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        default = serializers.CurrentUserDefault()
    )

    def validate(self, attrs):
        attrs['price'] = attrs['quantity'] * attrs['unit_price']
        return attrs
    
    class Meta:
        model = Cart
        fields = ['user', 'menuitem', 'quantity', 'unit_price', 'price']
        validators = [
            UniqueTogetherValidator(
                queryset = Cart.objects.all(),
                fields = ['menuitem', 'user']
            )
        ]
        extra_kwargs ={
            'price': {'read_only': True}
        }


class OrderItemSerializer(serializers.ModelSerializer):
    order = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        default = serializers.CurrentUserDefault()
    )
    # menuitem = MenuItemSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'order', 'menuitem', 'quantity', 'unit_price', 'price']
        validators = UniqueTogetherValidator(
            queryset = OrderItem.objects.all(),
            fields = ['order', 'menuitem']
        )

class OrderSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        default = serializers.CurrentUserDefault()
    )
    orderitem = OrderItemSerializer(many=True, read_only=True, source='order')
    class Meta:
        model = Order
        fields = ['id', 'user', 'delivery_crew', 'status', 'total', 'date', 'orderitem']
        