from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import UserSerializer, UserProfileSerializer, RegisterSerializer
from .models import UserProfile
from game.models import Player
from .jwt_auth import get_tokens_for_user

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
            user_id=profile.user_id,
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

class UserProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserProfileSerializer

    def get_object(self):
        # Get the user_id from the authenticated user
        user_id = self.request.user.user_id
        return UserProfile.nodes.get(user_id=user_id)

class CurrentUserView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        # The request.user is now a UserProfile instance
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
