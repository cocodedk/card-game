from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GameViewSet
from game.views.game_views import (
    create_game, play_card_view, list_rule_sets, create_rule_set
)

router = DefaultRouter()
router.register(r'', GameViewSet, basename='game')

# Define custom routes for the viewset
custom_routes = [
    # Player search endpoint
    path('search/players/', GameViewSet.as_view({'get': 'search_players'}), name='player-search'),
]

urlpatterns = custom_routes + [
    path('', include(router.urls)),
    path('games/create/', create_game, name='create_game'),
    path('games/<str:game_id>/play-card/', play_card_view, name='play_card'),
    path('rule-sets/', list_rule_sets, name='list_rule_sets'),
    path('rule-sets/create/', create_rule_set, name='create_rule_set'),
]
