from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=10, choices=[('income', 'Income'), ('expense', 'Expense')])
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='categories')

    class Meta:
        verbose_name_plural = 'Categories'
        unique_together = ['name', 'user', 'type']

    def __str__(self):
        return f"{self.name} ({self.type})"

class Transaction(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=200)
    date = models.DateField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='transactions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.description} - {self.amount}"

class Budget(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    month = models.DateField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='budgets')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='budgets')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['month', 'category', 'user']

    def __str__(self):
        return f"{self.category.name} - {self.amount} ({self.month})"

class RecurringTransaction(models.Model):
    INTERVAL_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    interval = models.CharField(max_length=10, choices=INTERVAL_CHOICES)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='recurring_transactions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recurring_transactions')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.description} - {self.amount} ({self.interval})"

class Goal(models.Model):
    GOAL_TYPE_CHOICES = [
        ('save', 'Save'),
        ('spend', 'Spend'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='goals')
    name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    goal_type = models.CharField(max_length=10, choices=GOAL_TYPE_CHOICES)
    target_date = models.DateField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='goals')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - {self.amount} ({self.goal_type})"

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    currency = models.CharField(max_length=10, default='USD')
    profile_pic = models.ImageField(upload_to='profile_pics/', null=True, blank=True)

    def __str__(self):
        return f"Profile of {self.user.username}" 