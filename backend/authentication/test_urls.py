"""
URL configuration for authentication tests.
"""

from django.urls import path, include

urlpatterns = [
    path('api/auth/', include('backend.authentication.urls')),
]
