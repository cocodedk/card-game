from django.urls import path, include
from .views import health_check, register_player

urlpatterns = [
    # Health check endpoint
    path('', health_check, name='health_check'),
    # Authentication API endpoints
    path('auth/', include('backend.authentication.urls')),
    # Player API endpoints (alias to authentication for registration)
    path('players/', include('backend.authentication.urls')),
    # Direct path for player registration
    path('players/register', register_player, name='player-register'),
    # Game API endpoints
    path('games/', include('backend.game.urls')),
]
