from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MaxValueValidator
import os

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
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

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

    def __str__(self):
        return f'Review by {self.user.username} for {self.product.name}'

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, through='CartItem')

    def __str__(self):
        return f'Cart of {self.user.username}'

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

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
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=[('DEPOSIT', 'Deposit'), ('WITHDRAW', 'Withdraw')])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.transaction_type} of {self.amount} by {self.user.username}'
