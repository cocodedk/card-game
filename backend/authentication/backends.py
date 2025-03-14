from django.contrib.auth.backends import BaseBackend
from .models import UserProfile

class Neo4jBackend(BaseBackend):
    """
    Custom authentication backend that uses Neo4j UserProfile for authentication
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Try to find the user by username
            profile = UserProfile.nodes.get(username=username)

            # Check password
            if profile.check_password(password):
                return profile
        except UserProfile.DoesNotExist:
            # Try to find the user by email
            try:
                profile = UserProfile.nodes.get(email=username)

                # Check password
                if profile.check_password(password):
                    return profile
            except UserProfile.DoesNotExist:
                return None

        return None

    def get_user(self, user_id):
        try:
            return UserProfile.nodes.get(user_id=user_id)
        except UserProfile.DoesNotExist:
            return None
