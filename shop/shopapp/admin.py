from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Product, Category, ProductScreenshot

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'available_quantity', 'get_categories']
    list_filter = ['categories']
    search_fields = ['name', 'description']
    list_editable = ['price', 'available_quantity']
    filter_horizontal = ['categories']

    def get_categories(self, obj):
        return ", ".join([category.name for category in obj.categories.all()])
    get_categories.short_description = 'Категории'

@admin.register(ProductScreenshot)
class ProductScreenshotAdmin(admin.ModelAdmin):
    list_display = ['product', 'order', 'image_preview']
    list_filter = ['product']
    ordering = ['product', 'order']

    def image_preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="200" height="200" />')
        return "Нет изображения"
    
    image_preview.short_description = 'Предпросмотр изображения'