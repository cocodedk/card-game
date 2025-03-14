from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GameViewSet

router = DefaultRouter()
router.register(r'', GameViewSet, basename='game')

# Define custom routes for the viewset
custom_routes = [
    # Player search endpoint
    path('search/players/', GameViewSet.as_view({'get': 'search_players'}), name='player-search'),
]

urlpatterns = custom_routes + [
    path('', include(router.urls)),
]
