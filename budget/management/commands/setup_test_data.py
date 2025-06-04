from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from budget.models import Category, Transaction, Budget, Goal, RecurringTransaction
from decimal import Decimal
from datetime import datetime, timedelta
import random

class Command(BaseCommand):
    help = 'Sets up test data for the application'

    def handle(self, *args, **kwargs):
        # Create test user
        test_user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='Test@123',
            first_name='Test',
            last_name='User'
        )
        self.stdout.write(self.style.SUCCESS('Created test user'))

        # Create categories
        categories = [
            {'name': 'Groceries', 'type': 'expense'},
            {'name': 'Utilities', 'type': 'expense'},
            {'name': 'Entertainment', 'type': 'expense'},
            {'name': 'Transportation', 'type': 'expense'},
            {'name': 'Salary', 'type': 'income'},
            {'name': 'Freelance', 'type': 'income'},
            {'name': 'Investments', 'type': 'income'},
        ]

        created_categories = []
        for cat_data in categories:
            category = Category.objects.create(
                user=test_user,
                name=cat_data['name'],
                type=cat_data['type']
            )
            created_categories.append(category)
        self.stdout.write(self.style.SUCCESS('Created categories'))

        # Create transactions
        today = datetime.now()
        for i in range(30):  # Last 30 days of transactions
            date = today - timedelta(days=i)
            # Create 2-3 transactions per day
            for _ in range(random.randint(2, 3)):
                is_expense = random.choice([True, False])
                category = random.choice([c for c in created_categories if c.type == ('expense' if is_expense else 'income')])
                amount = Decimal(str(random.randint(10, 1000)))
                
                Transaction.objects.create(
                    user=test_user,
                    amount=amount,
                    category=category,
                    date=date,
                    description=f"Test transaction {i}",
                    type='expense' if is_expense else 'income'
                )
        self.stdout.write(self.style.SUCCESS('Created transactions'))

        # Create budgets
        for category in [c for c in created_categories if c.type == 'expense']:
            Budget.objects.create(
                user=test_user,
                category=category,
                amount=Decimal(str(random.randint(500, 2000))),
                month=today.month,
                year=today.year
            )
        self.stdout.write(self.style.SUCCESS('Created budgets'))

        # Create goals
        goals = [
            {'name': 'Emergency Fund', 'target_amount': 10000, 'current_amount': 5000},
            {'name': 'Vacation Fund', 'target_amount': 5000, 'current_amount': 2000},
            {'name': 'New Car', 'target_amount': 25000, 'current_amount': 8000},
        ]

        for goal_data in goals:
            Goal.objects.create(
                user=test_user,
                name=goal_data['name'],
                target_amount=goal_data['target_amount'],
                current_amount=goal_data['current_amount'],
                target_date=today + timedelta(days=random.randint(30, 365)),
                category=random.choice([c for c in created_categories if c.type == 'expense'])
            )
        self.stdout.write(self.style.SUCCESS('Created goals'))

        # Create recurring transactions
        recurring = [
            {'name': 'Monthly Rent', 'amount': 1500, 'frequency': 'monthly'},
            {'name': 'Netflix Subscription', 'amount': 15, 'frequency': 'monthly'},
            {'name': 'Gym Membership', 'amount': 50, 'frequency': 'monthly'},
            {'name': 'Salary', 'amount': 5000, 'frequency': 'monthly'},
        ]

        for rec_data in recurring:
            RecurringTransaction.objects.create(
                user=test_user,
                name=rec_data['name'],
                amount=rec_data['amount'],
                frequency=rec_data['frequency'],
                start_date=today,
                category=random.choice(created_categories)
            )
        self.stdout.write(self.style.SUCCESS('Created recurring transactions'))

        self.stdout.write(self.style.SUCCESS('Successfully set up test data'))
        self.stdout.write(self.style.SUCCESS('Test account credentials:'))
        self.stdout.write(self.style.SUCCESS('Email: test@example.com'))
        self.stdout.write(self.style.SUCCESS('Password: Test@123')) 