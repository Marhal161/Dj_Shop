from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Product, Category, ProductScreenshot, Review

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'available_quantity', 'get_categories', 'get_average_rating']
    list_filter = ['categories']
    search_fields = ['name', 'description']
    list_editable = ['price', 'available_quantity']
    filter_horizontal = ['categories']

    def get_categories(self, obj):
        return ", ".join([category.name for category in obj.categories.all()])
    get_categories.short_description = 'Категории'

    def get_average_rating(self, obj):
        rating = obj.get_rating()
        if rating is None:
            return "Нет оценок"
        return f"★ {rating}"
    get_average_rating.short_description = 'Рейтинг'

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

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'created_at', 'short_comment']
    list_filter = ['rating', 'created_at', 'product']
    search_fields = ['comment', 'user__username', 'product__name']
    readonly_fields = ['created_at']
    raw_id_fields = ['user', 'product']
    ordering = ['-created_at']

    def short_comment(self, obj):
        return obj.comment[:100] + '...' if len(obj.comment) > 100 else obj.comment
    short_comment.short_description = 'Комментарий'

    fieldsets = (
        ('Основная информация', {
            'fields': ('product', 'user', 'rating')
        }),
        ('Отзыв', {
            'fields': ('comment', 'created_at')
        }),
    )