from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import UserSerializer, UserProfileSerializer, RegisterSerializer, ChangePasswordSerializer
from .models import UserProfile, BlacklistedToken
from backend.game.models import Player
from .jwt_auth import get_tokens_for_user
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from datetime import datetime, timedelta
import jwt
from django.conf import settings

class RegisterView(generics.CreateAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        profile = serializer.save()

        # Get additional fields
        date_of_birth = request.data.get('date_of_birth', '')
        callsign = request.data.get('callsign', '')

        # Create Neo4j Player node
        player = Player(
            uid=profile.uid,
            username=profile.username,
            display_name=f"{profile.first_name} {profile.last_name}".strip() or profile.username,
            date_of_birth=date_of_birth,
            callsign=callsign
        ).save()

        # Generate tokens
        tokens = get_tokens_for_user(profile)

        return Response({
            "user": UserSerializer(profile).data,
            "tokens": tokens,
            "message": "User registered successfully"
        }, status=status.HTTP_201_CREATED)

class LoginView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response({"error": "Please provide both username and password"},
                           status=status.HTTP_400_BAD_REQUEST)

        # Try to authenticate with username
        try:
            profile = UserProfile.nodes.get(username=username)
            if not profile.check_password(password):
                return Response({"error": "Invalid credentials"},
                               status=status.HTTP_401_UNAUTHORIZED)

            # Generate tokens
            tokens = get_tokens_for_user(profile)

            return Response({
                "user": UserSerializer(profile).data,
                "tokens": tokens
            })

        except UserProfile.DoesNotExist:
            # Try with email
            try:
                profile = UserProfile.nodes.get(email=username)
                if not profile.check_password(password):
                    return Response({"error": "Invalid credentials"},
                                  status=status.HTTP_401_UNAUTHORIZED)

                # Generate tokens
                tokens = get_tokens_for_user(profile)

                return Response({
                    "user": UserSerializer(profile).data,
                    "tokens": tokens
                })

            except UserProfile.DoesNotExist:
                return Response({"error": "Invalid credentials"},
                              status=status.HTTP_401_UNAUTHORIZED)

class LogoutView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        try:
            # Get the refresh token from the request
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                return Response({"error": "Refresh token is required"},
                               status=status.HTTP_400_BAD_REQUEST)

            # Decode the token to get the user_uid and expiration
            try:
                # Note: This doesn't validate the token, just decodes it
                decoded_token = jwt.decode(
                    refresh_token,
                    options={"verify_signature": False}
                )
                user_uid = decoded_token.get('user_uid')
                exp = decoded_token.get('exp')

                # Create expiration datetime
                expires_at = datetime.fromtimestamp(exp) if exp else datetime.now() + timedelta(days=7)

                # Add the token to our Neo4j blacklist
                BlacklistedToken(
                    token=refresh_token,
                    user_uid=user_uid,
                    expires_at=expires_at
                ).save()

                return Response({"message": "Logout successful"},
                               status=status.HTTP_200_OK)
            except jwt.PyJWTError:
                return Response({"error": "Invalid token format"},
                               status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"error": str(e)},
                           status=status.HTTP_400_BAD_REQUEST)

class ChangePasswordView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            # Check if current password is correct
            if not request.user.check_password(serializer.validated_data['current_password']):
                return Response({"current_password": "Current password is incorrect"},
                               status=status.HTTP_400_BAD_REQUEST)

            # Set the new password
            request.user.set_password(serializer.validated_data['new_password'])
            request.user.save()

            return Response({"message": "Password changed successfully"},
                           status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserProfileSerializer

    def get_object(self):
        # Get the uid from the authenticated user
        return UserProfile.nodes.get(uid=self.request.user.uid)

class CurrentUserView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        # The request.user is now a UserProfile instance
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
