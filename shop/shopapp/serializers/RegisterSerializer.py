from rest_framework import serializers
from ..models import User


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # Извлекаем email и генерируем username
        email = validated_data['email']
        username = email.split('@')[0]  # Берем часть до "@"

        # Проверяем, занят ли username
        if User.objects.filter(username=username).exists():
            # Если username занят, генерируем уникальный, добавляя номер
            i = 1
            while True:
                new_username = f"{username}_{i}"
                if not User.objects.filter(username=new_username).exists():
                    username = new_username
                    break
                i += 1

        password = validated_data.pop('password')
        user = User.objects.create_user(username=username, **validated_data, password=password)
        return user
