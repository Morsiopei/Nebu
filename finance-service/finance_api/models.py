import uuid
from django.db import models
from django.conf import settings # To reference the AUTH_USER_MODEL

class Account(models.Model):
    """ Represents a financial account linked by the user """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='finance_accounts')
    plaid_item_id = models.CharField(max_length=100, unique=True, help_text="Plaid Item ID")
    plaid_account_id = models.CharField(max_length=100, unique=True, help_text="Plaid Account ID")
    name = models.CharField(max_length=100)
    official_name = models.CharField(max_length=200, null=True, blank=True)
    mask = models.CharField(max_length=4, null=True, blank=True, help_text="Last 4 digits")
    account_type = models.CharField(max_length=50, help_text="e.g., depository")
    account_subtype = models.CharField(max_length=50, help_text="e.g., checking, savings")
    current_balance = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    available_balance = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    currency_code = models.CharField(max_length=3, default='USD')
    last_sync_time = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.mask}) - {self.user.username}" # Assumes username exists

class Transaction(models.Model):
    """ Represents a single financial transaction """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='finance_transactions')
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='transactions')
    plaid_transaction_id = models.CharField(max_length=100, unique=True, help_text="Plaid Transaction ID")

    amount = models.DecimalField(max_digits=12, decimal_places=2, help_text="Positive for credits, negative for debits")
    currency_code = models.CharField(max_length=3, default='USD')
    description = models.TextField(null=True, blank=True, help_text="Original description from bank")
    merchant_name = models.CharField(max_length=255, null=True, blank=True)
    category = models.CharField(max_length=100, null=True, blank=True, help_text="Suggested or user-defined category") # AI can help refine
    plaid_category_primary = models.CharField(max_length=100, null=True, blank=True, help_text="Plaid primary category")
    plaid_category_detailed = models.CharField(max_length=100, null=True, blank=True, help_text="Plaid detailed category")

    date = models.DateField(help_text="Date the transaction occurred")
    datetime = models.DateTimeField(null=True, blank=True, help_text="Timestamp if available")
    authorized_date = models.DateField(null=True, blank=True)
    authorized_datetime = models.DateTimeField(null=True, blank=True)

    payment_channel = models.CharField(max_length=50, null=True, blank=True) # e.g., online, in store
    pending = models.BooleanField(default=False)
    # plaid_payment_meta = models.JSONField(null=True, blank=True) # Store raw payment meta if needed
    # plaid_location_meta = models.JSONField(null=True, blank=True) # Store raw location meta if needed

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(fields=['user', 'date']),
            models.Index(fields=['account', 'date']),
        ]

    def __str__(self):
        return f"{self.date} - {self.description or self.merchant_name} ({self.amount})"

# --- Add other models as needed ---
# class Budget(models.Model): ...
# class FinancialGoal(models.Model): ...
# class BillReminder(models.Model): ...
