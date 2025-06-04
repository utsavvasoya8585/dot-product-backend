from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Category, Transaction, Budget, RecurringTransaction, Goal, Notification, UserProfile

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')
        read_only_fields = ('id', 'username')

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'type')
        read_only_fields = ('user',)

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class TransactionSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_type = serializers.CharField(source='category.type', read_only=True)

    class Meta:
        model = Transaction
        fields = ('id', 'amount', 'description', 'date', 'category', 'category_name', 'category_type', 'created_at', 'updated_at')
        read_only_fields = ('user',)

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class BudgetSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_type = serializers.CharField(source='category.type', read_only=True)

    class Meta:
        model = Budget
        fields = ('id', 'amount', 'month', 'category', 'category_name', 'category_type', 'created_at', 'updated_at')
        read_only_fields = ('user',)

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class RecurringTransactionSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_type = serializers.CharField(source='category.type', read_only=True)

    class Meta:
        model = RecurringTransaction
        fields = (
            'id', 'amount', 'description', 'start_date', 'end_date', 'interval',
            'category', 'category_name', 'category_type', 'is_active', 'created_at', 'updated_at'
        )
        read_only_fields = ('user',)

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class GoalSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    class Meta:
        model = Goal
        fields = (
            'id', 'name', 'amount', 'goal_type', 'target_date', 'category', 'category_name',
            'is_active', 'created_at', 'updated_at'
        )
        read_only_fields = ('user',)

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ('id', 'message', 'created_at', 'is_read')
        read_only_fields = ('user',)

class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    class Meta:
        model = UserProfile
        fields = ('id', 'username', 'email', 'currency', 'profile_pic') 