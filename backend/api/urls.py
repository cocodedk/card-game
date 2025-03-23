from django.urls import path, include
from .views import health_check, register_player
from backend.game.views.game_views import list_rule_sets, create_rule_set

urlpatterns = [
    # Health check endpoint
    path('', health_check, name='health_check'),
    # Authentication API endpoints
    path('auth/', include('backend.authentication.urls')),
    # Player API endpoints (alias to authentication for registration)
    path('players/', include('backend.authentication.urls')),
    # Direct path for player registration
    path('players/register', register_player, name='player-register'),

    # Game rule sets endpoints (placed before games to avoid URL conflict)
    path('game-rules/', list_rule_sets, name='list_rule_sets'),
    path('game-rules/create/', create_rule_set, name='create_rule_set'),

    # Game API endpoints
    path('games/', include('backend.game.urls')),
]
