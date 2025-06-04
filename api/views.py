from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum
from django.utils import timezone
from datetime import datetime
from .models import Category, Transaction, Budget, RecurringTransaction, Goal, Notification, UserProfile
from .serializers import CategorySerializer, TransactionSerializer, BudgetSerializer, RecurringTransactionSerializer, GoalSerializer, NotificationSerializer, UserProfileSerializer, UserSerializer
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from rest_framework.views import APIView

class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer

    def get_queryset(self):
        queryset = Transaction.objects.filter(user=self.request.user)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date and end_date:
            queryset = queryset.filter(date__range=[start_date, end_date])
        
        # Filter by category
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category_id=category)
        
        # Filter by amount range
        min_amount = self.request.query_params.get('min_amount')
        max_amount = self.request.query_params.get('max_amount')
        if min_amount:
            queryset = queryset.filter(amount__gte=min_amount)
        if max_amount:
            queryset = queryset.filter(amount__lte=max_amount)
        
        return queryset.order_by('-date')

    def perform_create(self, serializer):
        transaction = serializer.save(user=self.request.user)
        self.check_budget_and_goals(transaction)

    def perform_update(self, serializer):
        transaction = serializer.save(user=self.request.user)
        self.check_budget_and_goals(transaction)

    def check_budget_and_goals(self, transaction):
        # Budget notification
        today = timezone.now().date()
        start_of_month = today.replace(day=1)
        budgets = Budget.objects.filter(user=transaction.user, month__gte=start_of_month, category=transaction.category)
        if budgets.exists():
            budget = budgets.first()
            spent = Transaction.objects.filter(user=transaction.user, category=transaction.category, date__gte=start_of_month).aggregate(Sum('amount'))['amount__sum'] or 0
            if spent > budget.amount:
                Notification.objects.create(
                    user=transaction.user,
                    message=f"Budget exceeded for {transaction.category.name}! Budget: {budget.amount}, Spent: {spent}"
                )
        # Goal notification
        goals = Goal.objects.filter(user=transaction.user, is_active=True, category=transaction.category)
        for goal in goals:
            if goal.goal_type == 'save':
                # Check if saved enough
                saved = Transaction.objects.filter(user=transaction.user, category=goal.category, date__lte=goal.target_date, date__gte=start_of_month, amount__gt=0).aggregate(Sum('amount'))['amount__sum'] or 0
                if saved >= goal.amount:
                    Notification.objects.create(
                        user=transaction.user,
                        message=f"Congratulations! You achieved your savings goal: {goal.name}"
                    )
                    goal.is_active = False
                    goal.save()
            elif goal.goal_type == 'spend':
                spent = Transaction.objects.filter(user=transaction.user, category=goal.category, date__lte=goal.target_date, date__gte=start_of_month, amount__lt=0).aggregate(Sum('amount'))['amount__sum'] or 0
                if abs(spent) >= goal.amount:
                    Notification.objects.create(
                        user=transaction.user,
                        message=f"You reached your spending goal: {goal.name}"
                    )
                    goal.is_active = False
                    goal.save()

    @action(detail=False, methods=['get'])
    def summary(self, request):
        # Get current month's transactions
        today = timezone.now()
        start_of_month = today.replace(day=1)
        
        transactions = Transaction.objects.filter(
            user=request.user,
            date__gte=start_of_month
        )
        
        # Calculate totals
        total_income = transactions.filter(category__type='income').aggregate(Sum('amount'))['amount__sum'] or 0
        total_expenses = transactions.filter(category__type='expense').aggregate(Sum('amount'))['amount__sum'] or 0
        balance = total_income - total_expenses
        
        # Get category-wise totals
        category_totals = transactions.values('category__name', 'category__type').annotate(
            total=Sum('amount')
        ).order_by('category__type', 'category__name')
        
        return Response({
            'total_income': total_income,
            'total_expenses': total_expenses,
            'balance': balance,
            'category_totals': category_totals
        })

class BudgetViewSet(viewsets.ModelViewSet):
    serializer_class = BudgetSerializer

    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get'])
    def monthly_summary(self, request):
        # Get current month's budget and expenses
        today = timezone.now()
        start_of_month = today.replace(day=1)
        
        budgets = Budget.objects.filter(
            user=request.user,
            month__gte=start_of_month
        )
        
        transactions = Transaction.objects.filter(
            user=request.user,
            date__gte=start_of_month
        )
        
        # Calculate budget vs actual for each category
        budget_summary = []
        for budget in budgets:
            actual = transactions.filter(category=budget.category).aggregate(Sum('amount'))['amount__sum'] or 0
            budget_summary.append({
                'category': budget.category.name,
                'budgeted': budget.amount,
                'actual': actual,
                'difference': budget.amount - actual
            })
        
        return Response(budget_summary)

class RecurringTransactionViewSet(viewsets.ModelViewSet):
    serializer_class = RecurringTransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return RecurringTransaction.objects.filter(user=self.request.user)

class GoalViewSet(viewsets.ModelViewSet):
    serializer_class = GoalSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Goal.objects.filter(user=self.request.user)

class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'status': 'marked as read'})

class UserProfileViewSet(viewsets.ModelViewSet):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserProfile.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

# Analytics endpoints
class AnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        # Trends: income/expense per month for last 12 months
        from django.db.models.functions import TruncMonth
        from api.models import Transaction
        import datetime
        today = timezone.now().date()
        one_year_ago = today - datetime.timedelta(days=365)
        qs = Transaction.objects.filter(user=user, date__gte=one_year_ago)
        trends = qs.annotate(month=TruncMonth('date')).values('month', 'category__type').annotate(total=Sum('amount')).order_by('month', 'category__type')
        # Top categories
        top_categories = qs.values('category__name', 'category__type').annotate(total=Sum('amount')).order_by('-total')[:5]
        # Net worth progression (cumulative income - expenses)
        net_worth = []
        balance = 0
        months = sorted(set([t['month'] for t in trends]))
        for month in months:
            month_income = sum(t['total'] for t in trends if t['month'] == month and t['category__type'] == 'income')
            month_expense = sum(t['total'] for t in trends if t['month'] == month and t['category__type'] == 'expense')
            balance += month_income - month_expense
            net_worth.append({'month': month, 'net_worth': balance})
        # Budget vs actual (current month)
        start_of_month = today.replace(day=1)
        budgets = Budget.objects.filter(user=user, month__gte=start_of_month)
        transactions = Transaction.objects.filter(user=user, date__gte=start_of_month)
        budget_vs_actual = []
        for budget in budgets:
            actual = transactions.filter(category=budget.category).aggregate(Sum('amount'))['amount__sum'] or 0
            budget_vs_actual.append({
                'category': budget.category.name,
                'budgeted': budget.amount,
                'actual': actual,
                'difference': budget.amount - actual
            })
        return Response({
            'trends': list(trends),
            'top_categories': list(top_categories),
            'net_worth': net_worth,
            'budget_vs_actual': budget_vs_actual
        })

class UserProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 