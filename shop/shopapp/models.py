from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MaxValueValidator
import os
from django.utils import timezone
import random
import string

class User(AbstractUser):
    email = models.EmailField(unique=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    available_quantity = models.IntegerField()
    categories = models.ManyToManyField(Category, related_name='products')
    created_at = models.DateTimeField(default=timezone.now)

    def get_rating(self):
        """Вычисляет средний рейтинг на основе отзывов"""
        reviews = self.reviews.all()
        if not reviews:
            return None
        return round(sum(review.rating for review in reviews) / reviews.count(), 1)

    def __str__(self):
        return self.name

class ProductScreenshot(models.Model):
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE,
        related_name='screenshots'
    )
    
    def get_image_upload_path(self, filename):
       return f'screenshots/{self.product.name}_{self.order + 1}.jpg'

    image = models.ImageField(
        upload_to=get_image_upload_path,
        verbose_name='Скриншот',
        null=True,
        blank=True
    )
    
    order = models.PositiveIntegerField(
        default=0,
        validators=[MaxValueValidator(4)],
        verbose_name='Порядковый номер'
    )

    class Meta:
        ordering = ['order']
        verbose_name = 'Скриншот продукта'
        verbose_name_plural = 'Скриншоты продукта'
        constraints = [
            models.UniqueConstraint(
                fields=['product', 'order'],
                name='unique_product_screenshot_order'
            ),
        ]

    def __str__(self):
        return f'Скриншот {self.order + 1} для {self.product.name}'

    def save(self, *args, **kwargs):
        if not self.pk:
            screenshots_count = ProductScreenshot.objects.filter(
                product=self.product
            ).count()
            if screenshots_count >= 5:
                raise ValueError('Максимальное количество скриншотов (5) уже достигнуто')
        super().save(*args, **kwargs)
        print(f"Скриншот сохранен: {self.image.path}")  # Отладочный вывод
        
    def delete(self, *args, **kwargs):
        if self.image:
            if os.path.isfile(self.image.path):
                os.remove(self.image.path)
        super().delete(*args, **kwargs)

    def get_order_display(self):
        return self.order + 1


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def is_owner(self, user):
        return self.user == user

    def __str__(self):
        return f'Review by {self.user.username} for {self.product.name}'

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, through='CartItem')
    
    def get_total_price(self):
        return sum(item.get_total_price() for item in self.cartitem_set.all())

    def __str__(self):
        return f'Cart of {self.user.username}'

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def get_total_price(self):
        return self.product.price * self.quantity

    def __str__(self):
        return f'{self.quantity} x {self.product.name} in {self.cart}'

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, through='OrderItem')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Order {self.id} by {self.user.username}'

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'{self.quantity} x {self.product.name} in Order {self.order.id}'

class BalanceTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('DEPOSIT', 'Пополнение'),
        ('WITHDRAW', 'Списание'),
        ('PURCHASE_FAILED', 'Отказ в покупке'),
        ('PURCHASE_SUCCESS', 'Успешная покупка')
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    description = models.CharField(max_length=255, blank=True, null=True)
    game_key = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.transaction_type} of {self.amount} by {self.user.username}'

class Purchase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='purchases')
    game = models.ForeignKey(Product, on_delete=models.CASCADE)
    game_key = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def generate_game_key(self):
        """Генерация случайного ключа игры"""
        chars = string.ascii_uppercase + string.digits
        return ''.join(random.choice(chars) for _ in range(16))

    def save(self, *args, **kwargs):
        if not self.game_key:
            self.game_key = self.generate_game_key()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-created_at']
