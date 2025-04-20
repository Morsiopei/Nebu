from rest_framework import viewsets, permissions, status, generics
from rest_framework.response import Response
from rest_framework.decorators import action
from django.conf import settings
import plaid
from plaid.api import plaid_api
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.transactions_sync_request import TransactionsSyncRequest
from plaid.model.country_code import CountryCode
from plaid.model.products import Products

from .models import Account, Transaction
from .serializers import AccountSerializer, TransactionSerializer # Add other serializers
# from .tasks import sync_account_transactions_task # Import Celery task


# --- Plaid Configuration ---
# Ensure PLAID_CLIENT_ID, PLAID_SECRET, PLAID_ENV are in settings
PLAID_CLIENT_ID = settings.PLAID_CLIENT_ID
PLAID_SECRET = settings.PLAID_SECRET

if settings.PLAID_ENV == 'sandbox':
    plaid_host = plaid.Environment.Sandbox
elif settings.PLAID_ENV == 'development':
    plaid_host = plaid.Environment.Development
else:
    plaid_host = plaid.Environment.Production

plaid_configuration = plaid.Configuration(
    host=plaid_host,
    api_key={
        'clientId': PLAID_CLIENT_ID,
        'secret': PLAID_SECRET,
    }
)
plaid_api_client = plaid.ApiClient(plaid_configuration)
client = plaid_api.PlaidApi(plaid_api_client)


# --- Plaid Views ---

class CreateLinkTokenView(generics.GenericAPIView):
    """ Creates a Plaid Link token for the frontend to initialize Plaid Link """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            plaid_request = LinkTokenCreateRequest(
                user=LinkTokenCreateRequestUser(
                    client_user_id=str(request.user.id) # Use internal user ID
                ),
                client_name="Multifaceted AI App",
                products=[Products("transactions")], # Or auth, identity, etc.
                country_codes=[CountryCode('US')], # Or CA, GB, ES, FR, IE, NL
                language='en',
                # redirect_uri='YOUR_OAUTH_REDIRECT_URI', # Optional for OAuth flows
                # webhook='YOUR_WEBHOOK_URL' # Optional: Highly recommended for real-time updates
            )
            response = client.link_token_create(plaid_request)
            return Response({'link_token': response['link_token']})
        except plaid.ApiException as e:
            # Log the error details
            print(f"Plaid API Exception: {e.body}")
            return Response({"error": "Could not create Plaid link token."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            print(f"Error creating link token: {e}")
            return Response({"error": "An internal error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ExchangePublicTokenView(generics.GenericAPIView):
    """ Exchanges a Plaid public token (from frontend) for an access token and item ID """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        public_token = request.data.get('public_token')
        if not public_token:
            return Response({"error": "Public token is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            exchange_request = ItemPublicTokenExchangeRequest(public_token=public_token)
            exchange_response = client.item_public_token_exchange(exchange_request)
            access_token = exchange_response['access_token']
            item_id = exchange_response['item_id']

            # --- IMPORTANT SECURITY NOTE ---
            # DO NOT store the access_token directly in your Account model accessible via API.
            # Store it securely, perhaps in a separate encrypted model or use a secrets manager.
            # For this example, we won't store it directly on the Account model shown.
            # You would need a secure way to retrieve it when syncing.
            print(f"Received Item ID: {item_id}, Access Token: [REDACTED]")
            # TODO: Store item_id and access_token securely, associated with the request.user
            # Placeholder: Assume you have a secure way to store/retrieve access_token based on item_id

            # TODO: Fetch initial account details using the new access_token and create Account records
            # Example (needs error handling and secure token storage):
            # accounts_response = client.accounts_get(ItemGetRequest(access_token=access_token))
            # for acc_data in accounts_response['accounts']:
            #     Account.objects.update_or_create(
            #         plaid_account_id=acc_data['account_id'],
            #         defaults={
            #             'user': request.user,
            #             'plaid_item_id': item_id,
            #             'name': acc_data['name'],
            #             # ... map other fields ...
            #         }
            #     )

            # TODO: Trigger initial transaction sync (maybe async)
            # sync_account_transactions_task.delay(item_id)

            return Response({"message": "Public token exchanged successfully. Accounts are being synced."}, status=status.HTTP_200_OK)

        except plaid.ApiException as e:
            print(f"Plaid API Exception: {e.body}")
            return Response({"error": "Could not exchange public token."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            print(f"Error exchanging token: {e}")
            return Response({"error": "An internal error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# --- Application Data Views ---

class AccountViewSet(viewsets.ReadOnlyModelViewSet):
    """ Provides list and detail views for linked financial accounts """
    serializer_class = AccountSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Only return accounts belonging to the authenticated user
        return Account.objects.filter(user=self.request.user)

    # Optional: Action to trigger manual sync for an item
    # @action(detail=True, methods=['post'])
    # def sync(self, request, pk=None):
    #     account = self.get_object() # Gets the specific account by its UUID (pk)
    #     item_id = account.plaid_item_id
    #     # TODO: Trigger background sync task
    #     # sync_account_transactions_task.delay(item_id)
    #     return Response({"message": f"Sync initiated for item {item_id}."}, status=status.HTTP_202_ACCEPTED)


class TransactionViewSet(viewsets.ReadOnlyModelViewSet): # ReadOnly initially
    """ Provides list view for financial transactions with filtering """
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    # pagination_class = YourCustomPagination # Optional: If default page size isn't enough

    def get_queryset(self):
        # Only return transactions belonging to the authenticated user
        queryset = Transaction.objects.filter(user=self.request.user)

        # Filtering examples (add more as needed)
        account_id = self.request.query_params.get('account_id')
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        category = self.request.query_params.get('category')

        if account_id:
            queryset = queryset.filter(account__id=account_id)
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        if category:
            queryset = queryset.filter(category__iexact=category) # Case-insensitive match

        return queryset

    # --- Add update method if user can edit category ---
    # def update(self, request, *args, **kwargs):
    #     # Ensure only allowed fields (like 'category') are updated
    #     partial = kwargs.pop('partial', True) # Allow partial updates
    #     instance = self.get_object()
    #     # Only allow updating specific fields
    #     allowed_updates = {'category': request.data.get('category')}
    #     # Filter out None values if you don't want to nullify fields
    #     update_data = {k: v for k, v in allowed_updates.items() if v is not None}
    #
    #     serializer = self.get_serializer(instance, data=update_data, partial=partial)
    #     serializer.is_valid(raise_exception=True)
    #     self.perform_update(serializer)
    #     return Response(serializer.data)

# --- Add ViewSets for Budget, Goal, etc. ---
