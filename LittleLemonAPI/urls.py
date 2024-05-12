from django.urls import path
from . import views
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('menu-items', views.MenuItemsView.as_view(), name="menu-items"),
    path('categories', views.CategoriesView.as_view(), name="categories"),
    path('items-of-day', views.itemDay, name="items-of-day"),
    path('groups/manager/users', views.managers, name="manager"),
    path('api-token-auth', obtain_auth_token)
]