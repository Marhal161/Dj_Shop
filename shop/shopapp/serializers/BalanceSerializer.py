from rest_framework import serializers
from ..models import BalanceTransaction, User

class BalanceTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BalanceTransaction
        fields = ['id', 'amount', 'created_at']
        read_only_fields = ['transaction_type', 'created_at']

    def validate_amount(self, value):
        """
        Проверка суммы транзакции
        """
        if value <= 0:
            raise serializers.ValidationError("Сумма должна быть больше нуля")
        return value

    def create(self, validated_data):
        """
        Создание транзакции и обновление баланса пользователя
        """
        user = self.context['request'].user
        amount = validated_data['amount']

        # Создаем транзакцию
        transaction = BalanceTransaction.objects.create(
            user=user,
            amount=amount,
            transaction_type='DEPOSIT'
        )

        # Обновляем баланс пользователя
        user.balance += amount
        user.save()

        return transaction