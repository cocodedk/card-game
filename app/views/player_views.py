from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from app.serializers.player_serializer import PlayerRegistrationSerializer

class PlayerRegistrationView(APIView):
    def post(self, request):
        serializer = PlayerRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            player = serializer.save()
            return Response({
                'message': 'Player registered successfully',
                'username': player.username,
                'uid': player.uid
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
