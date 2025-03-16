from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.models import TokenUser
from rest_framework_simplejwt.exceptions import InvalidToken
from .models import UserProfile, BlacklistedToken


class Neo4jJWTAuthentication(JWTAuthentication):
    """
    Custom JWT authentication that works with our neomodel UserProfile
    """

    def get_user(self, validated_token):
        """
        Attempt to find and return a user using the given validated token.
        """
        try:
            user_uid = validated_token['user_uid']

            # Get the UserProfile from Neo4j
            try:
                profile = UserProfile.nodes.get(uid=user_uid)
                return profile
            except UserProfile.DoesNotExist:
                return None

        except KeyError:
            return None

    def get_validated_token(self, raw_token):
        """
        Override to check if the token is blacklisted
        """
        # First validate the token using the parent method
        validated_token = super().get_validated_token(raw_token)

        # Check if the token is blacklisted
        if BlacklistedToken.is_blacklisted(str(raw_token)):
            raise InvalidToken('Token is blacklisted')

        return validated_token

def get_tokens_for_user(profile):
    """
    Get JWT tokens for a UserProfile
    """
    # Create a token payload
    token_payload = {
        'user_uid': profile.uid,
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
