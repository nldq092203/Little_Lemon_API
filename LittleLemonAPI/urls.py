from django.urls import path
from . import views
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('menu-items', views.MenuItemsView.as_view(), name="menu-items"),
    path('categories', views.CategoriesView.as_view(), name="categories"),
    # path('items-of-day', views.itemDay, name="items-of-day"),
    path('menu-items/<int:pk>', views.SimpleMenuItemView.as_view(), name="menu-item-simple"),
    path('orders', views.OrdersView.as_view(), name="orders"),
    path('orders/<int:pk>', views.SimpleOrderView.as_view(), name="order-simple"),
    path('groups/manager/users', views.managers, name="manager"),
    path('groups/delivery-crew/users', views.delivery_crew, name="delivery-crew"),
    path('api-token-auth', obtain_auth_token),
    path('cart/menu-items', views.CartView.as_view(), name='cart-menu-items'),
    path('cart/orders', views.OrdersView.as_view(), name='cart-orders'),
]