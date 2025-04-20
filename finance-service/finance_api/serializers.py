from rest_framework import serializers
from .models import Account, Transaction
# from django.contrib.auth import get_user_model # If needed for nested user info

# User = get_user_model() # Careful if User model is complex or defined elsewhere

class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = [
            'id', 'name', 'mask', 'account_type', 'account_subtype',
            'current_balance', 'available_balance', 'currency_code',
            'last_sync_time'
        ]
        # Typically read-only as they are synced from Plaid
        read_only_fields = fields


class TransactionSerializer(serializers.ModelSerializer):
    # Optionally make account display more info instead of just ID
    # account = AccountSerializer(read_only=True) # Use simplified nested serializer if needed
    account_id = serializers.UUIDField(source='account.id', read_only=True) # Simple way to show account ID

    class Meta:
        model = Transaction
        fields = [
            'id', 'account_id', 'plaid_transaction_id', 'amount', 'currency_code',
            'description', 'merchant_name', 'category', 'plaid_category_primary',
            'plaid_category_detailed', 'date', 'datetime', 'pending',
            'created_at', 'updated_at'
        ]
        # Most fields are read-only from Plaid, except potentially 'category' if user can edit it
        read_only_fields = [
             'id', 'account_id', 'plaid_transaction_id', 'amount', 'currency_code',
             'description', 'merchant_name', 'plaid_category_primary', 'plaid_category_detailed',
             'date', 'datetime', 'pending', 'created_at', 'updated_at'
        ]

    # Add custom validation or update logic if user can modify fields like 'category'
    # def update(self, instance, validated_data):
    #     instance.category = validated_data.get('category', instance.category)
    #     # Add more fields user can update
    #     instance.save()
    #     return instance

# --- Add serializers for other models (Budget, Goal, etc.) ---
