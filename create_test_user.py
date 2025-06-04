import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'budget_tracker.settings')
django.setup()

from django.contrib.auth.models import User
from api.models import Category

def create_test_user():
    # Create test user
    username = 'testuser'
    password = 'testpass123'
    email = 'test@example.com'

    if not User.objects.filter(username=username).exists():
        user = User.objects.create_user(username=username, email=email, password=password)
        print(f"Created test user: {username}")

        # Create default categories
        default_categories = [
            ('Salary', 'income'),
            ('Freelance', 'income'),
            ('Investments', 'income'),
            ('Groceries', 'expense'),
            ('Rent', 'expense'),
            ('Utilities', 'expense'),
            ('Transportation', 'expense'),
            ('Entertainment', 'expense'),
            ('Healthcare', 'expense'),
            ('Shopping', 'expense'),
        ]

        for name, type in default_categories:
            Category.objects.create(name=name, type=type, user=user)
            print(f"Created category: {name} ({type})")

if __name__ == '__main__':
    create_test_user() 