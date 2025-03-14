from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from .models import UserProfile
from rest_framework_simplejwt.models import TokenUser

class Neo4jJWTAuthentication(JWTAuthentication):
    """
    Custom JWT authentication that works with our neomodel UserProfile
    """

    def get_user(self, validated_token):
        """
        Attempt to find and return a user using the given validated token.
        """
        try:
            user_id = validated_token['user_id']

            # Get the UserProfile from Neo4j
            try:
                profile = UserProfile.nodes.get(user_id=user_id)
                return profile
            except UserProfile.DoesNotExist:
                return None

        except KeyError:
            return None

def get_tokens_for_user(profile):
    """
    Get JWT tokens for a UserProfile
    """
    # Create a token payload
    token_payload = {
        'user_id': profile.user_id,
        'username': profile.username,
        'email': profile.email,
    }

    # Create a refresh token with custom payload
    refresh = RefreshToken()

    # Add the custom claims
    for key, value in token_payload.items():
        refresh[key] = value

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }
