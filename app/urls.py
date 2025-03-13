from django.urls import path
from app.views.player_views import PlayerRegistrationView

urlpatterns = [
    # ... existing code ...
    path('api/players/register/', PlayerRegistrationView.as_view(), name='player-registration'),
    # ... existing code ...
]
