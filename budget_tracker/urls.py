"""
URL configuration for budget_tracker project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from api.views import CategoryViewSet, TransactionViewSet, BudgetViewSet, RecurringTransactionViewSet, GoalViewSet, NotificationViewSet, UserProfileViewSet, AnalyticsView, UserProfileAPIView
from api.reports import TransactionsCSVReport, MonthlySummaryCSVReport

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'transactions', TransactionViewSet, basename='transaction')
router.register(r'budgets', BudgetViewSet, basename='budget')
router.register(r'recurring-transactions', RecurringTransactionViewSet, basename='recurringtransaction')
router.register(r'goals', GoalViewSet, basename='goal')
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'user-profiles', UserProfileViewSet, basename='userprofile')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/analytics/', AnalyticsView.as_view(), name='analytics'),
    path('api/reports/transactions/', TransactionsCSVReport.as_view(), name='transactions_csv_report'),
    path('api/reports/monthly-summary/', MonthlySummaryCSVReport.as_view(), name='monthly_summary_csv_report'),
    path('api/users/profile', UserProfileAPIView.as_view(), name='user-profile'),
]
