from rest_framework import serializers
from ..models import Review, User, Product

class ReviewSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    user_name = serializers.SerializerMethodField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'product', 'user', 'rating', 'comment', 'user_name', 'created_at']
        read_only_fields = ['user', 'created_at']

    def get_user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"

    def create(self, validated_data):
        # Получаем пользователя из контекста
        user = self.context.get('user')
        if not user:
            raise serializers.ValidationError("User is required")
        
        # Создаем отзыв с текущим пользователем
        validated_data['user'] = user
        return Review.objects.create(**validated_data)
    