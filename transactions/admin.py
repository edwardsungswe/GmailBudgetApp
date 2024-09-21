# transactions/admin.py
from django.contrib import admin
from .models import Transaction
from .models import EmailFilter
# @admin.register(Transaction)
# class TransactionAdmin(admin.ModelAdmin):
#     list_display = ('amount', 'date', 'description', 'category', 'vendor')
#     list_filter = ('date', 'category')
#     search_fields = ('description', 'vendor')


admin.site.register(Transaction)  # Register Transaction model
admin.site.register(EmailFilter)   # Register EmailFilter model