from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.http import HttpResponse
from .models import Transaction, Category
from django.utils import timezone
import csv
from datetime import datetime

class TransactionsCSVReport(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        transactions = Transaction.objects.filter(user=request.user).select_related('category')
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="transactions.csv"'
        writer = csv.writer(response)
        writer.writerow(['Date', 'Description', 'Category', 'Type', 'Amount'])
        for t in transactions:
            writer.writerow([
                t.date,
                t.description,
                t.category.name,
                t.category.type,
                t.amount
            ])
        return response

class MonthlySummaryCSVReport(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = timezone.now().date()
        start_of_month = today.replace(day=1)
        transactions = Transaction.objects.filter(user=request.user, date__gte=start_of_month).select_related('category')
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f"attachment; filename=monthly_summary_{today.strftime('%Y_%m')}.csv"
        writer = csv.writer(response)
        writer.writerow(['Date', 'Description', 'Category', 'Type', 'Amount'])
        for t in transactions:
            writer.writerow([
                t.date,
                t.description,
                t.category.name,
                t.category.type,
                t.amount
            ])
        return response 