from django.urls import path
from .views import RegisterView, UserProfileView, CurrentUserView, LoginView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('register', RegisterView.as_view()),  # Same view without trailing slash
    path('login/', LoginView.as_view(), name='login'),
    path('login', LoginView.as_view()),  # Same view without trailing slash
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('me/', CurrentUserView.as_view(), name='current-user'),
]
