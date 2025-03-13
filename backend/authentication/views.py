from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from .serializers import UserSerializer, UserProfileSerializer, RegisterSerializer
from .models import UserProfile
from game.models import Player

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Create UserProfile
        profile = UserProfile.objects.create(user=user)

        # Create Neo4j Player node
        player = Player(
            user_id=user.id,
            username=user.username,
            display_name=user.get_full_name() or user.username
        ).save()

        # Link UserProfile to Neo4j Player
        profile.neo4j_player_id = player.id
        profile.save()

        return Response({
            "user": UserSerializer(user).data,
            "message": "User registered successfully"
        }, status=status.HTTP_201_CREATED)

class UserProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserProfileSerializer

    def get_object(self):
        return UserProfile.objects.get(user=self.request.user)

class CurrentUserView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
