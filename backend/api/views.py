from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from authentication.views import RegisterView

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """
    Health check endpoint to verify API is running
    """
    return Response({"status": "ok"})

# Custom view to handle registration directly
@api_view(['POST'])
@permission_classes([AllowAny])
def register_player(request):
    """
    Custom view to handle player registration directly
    """
    # Create a new instance of RegisterView
    view = RegisterView.as_view()

    # Forward the request to the RegisterView
    return view(request._request)
