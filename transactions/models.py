from django.db import models

# Create your models here.

class Transaction(models.Model):
    CATEGORY_CHOICES = [
        ('utilities', 'Utilities'),
        ('entertainment', 'Entertainment'),
        ('groceries', 'Groceries'),
        ('transportation', 'Transportation'),
        ('others', 'Others'),
    ]

    amount = models.DecimalField(max_digits=10, decimal_places=2)  # Amount of the transaction
    date = models.DateField()  # Date of the transaction
    description = models.CharField(max_length=255)  # Description or memo of the transaction
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)  # Category of the transaction
    vendor = models.CharField(max_length=255, blank=True, null=True)  # Vendor or source of the transaction (optional)
    
    def __str__(self):
        return f"{self.description} - {self.amount} on {self.date}"
