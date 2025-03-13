from django.urls import path, include
from .views import health_check

urlpatterns = [
    # Health check endpoint
    path('', health_check, name='health_check'),
    # Authentication API endpoints
    path('auth/', include('authentication.urls')),
    # Game API endpoints
    path('games/', include('game.urls')),
]
