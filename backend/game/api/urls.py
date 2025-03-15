from django.urls import path
from backend.game.api.views import (
    PlayCardView,
    DrawCardView,
    AnnounceOneCardView,
    GetGameStateView,
    CreateGameView,
    JoinGameView,
    StartGameView
)

urlpatterns = [
    # Game creation and management
    path('games/create/', CreateGameView.as_view(), name='create_game'),
    path('games/<str:game_id>/join/', JoinGameView.as_view(), name='join_game'),
    path('games/<str:game_id>/start/', StartGameView.as_view(), name='start_game'),

    # Game state
    path('games/<str:game_id>/state/', GetGameStateView.as_view(), name='get_game_state'),

    # Game actions
    path('games/<str:game_id>/play-card/', PlayCardView.as_view(), name='play_card'),
    path('games/<str:game_id>/draw-card/', DrawCardView.as_view(), name='draw_card'),
    path('games/<str:game_id>/announce-one-card/', AnnounceOneCardView.as_view(), name='announce_one_card'),
]
