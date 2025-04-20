from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # path('admin/', admin.site.urls), # Optional: Enable admin for this service if needed
    # Include the API endpoints from your finance_api app
    # Prefix with '/api/finance/' matching the gateway routing (or adjust gateway)
    path('api/finance/', include('finance_api.urls')),

    # Add other top-level URL patterns for this service if necessary
]
