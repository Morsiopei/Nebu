from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'accounts', views.AccountViewSet, basename='account')
router.register(r'transactions', views.TransactionViewSet, basename='transaction')
# Register other ViewSets here (BudgetViewSet, GoalViewSet, etc.)
# router.register(r'budgets', views.BudgetViewSet, basename='budget')

urlpatterns = [
    # Plaid specific endpoints
    path('plaid/create_link_token/', views.CreateLinkTokenView.as_view(), name='create_link_token'),
    path('plaid/exchange_public_token/', views.ExchangePublicTokenView.as_view(), name='exchange_public_token'),

    # Include router URLs for standard CRUD operations
    path('', include(router.urls)),

    # Add other specific non-ViewSet URLs if needed
    # path('insights/', views.FinancialInsightsView.as_view(), name='financial_insights'),
]
