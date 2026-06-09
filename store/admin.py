from django.contrib import admin

from .models import (
    Cart,
    CartItem,
    Category,
    Coupon,
    Order,
    OrderItem,
    Product,
    ProductImage,
    Review,
    Wishlist,
)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock', 'discount_percent', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('name', 'description', 'category__name')
    exclude = ('discount_percent',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_amount', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('user__username',)

admin.site.register(Category)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(OrderItem)
admin.site.register(Review)
admin.site.register(Wishlist)
admin.site.register(ProductImage)
admin.site.register(Coupon)
