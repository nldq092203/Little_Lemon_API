from django.contrib import admin
from .models import Category, MenuItem, Cart, Order, OrderItem
# Register your models here.
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'title')

class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'title')
    inlines = []

admin.site.register(Category, CategoryAdmin)
admin.site.register(Cart)
admin.site.register(MenuItem, MenuItemAdmin)
admin.site.register(Order)
admin.site.register(OrderItem)