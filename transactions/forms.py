# transactions/forms.py
from django import forms
from .models import EmailFilter

class EmailFilterForm(forms.ModelForm):
    class Meta:
        model = EmailFilter
        fields = ['vendor', 'email_domain', 'bill_identifier', 'category']
        labels = {
            'vendor': 'Vendor',
            'email_domain': 'Email Domain',
            'bill_identifier': 'Preceding Text of Bill Amount',
            'category': 'Category',
        }
