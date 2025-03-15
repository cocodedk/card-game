"""
WebSocket authentication middleware.
This module provides middleware for authenticating WebSocket connections.
"""

import re
from urllib.parse import parse_qs
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError

User = get_user_model()


class TokenAuthMiddleware:
    """
    Middleware for authenticating WebSocket connections using JWT tokens.
    """

    def __init__(self, inner):
        """
        Initialize the middleware.

        Args:
            inner: The inner application
        """
        self.inner = inner

    async def __call__(self, scope, receive, send):
        """
        Process the connection.

        Args:
            scope: The connection scope
            receive: The receive channel
            send: The send channel

        Returns:
            The result of the inner application
        """
        # Get the token from the query string
        query_string = scope.get('query_string', b'').decode()
        query_params = parse_qs(query_string)
        token = query_params.get('token', [''])[0]

        # If no token in query string, check for Authorization header
        if not token:
            headers = dict(scope.get('headers', []))
            auth_header = headers.get(b'authorization', b'').decode()

            # Check for Bearer token
            if auth_header.startswith('Bearer '):
                token = auth_header[7:]

        # Authenticate the token
        if token:
            try:
                # Validate the token
                access_token = AccessToken(token)
                user_id = access_token.payload.get('user_id')

                if user_id:
                    # Get the user
                    user = await self.get_user(user_id)
                    if user:
                        scope['user'] = user
                        scope['token'] = token
            except TokenError:
                pass

        # If no user was set, set AnonymousUser
        if 'user' not in scope:
            scope['user'] = AnonymousUser()

        # Continue processing
        return await self.inner(scope, receive, send)

    @database_sync_to_async
    def get_user(self, user_id):
        """
        Get a user by ID.

        Args:
            user_id: The user ID

        Returns:
            User: The user object or None
        """
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None


def TokenAuthMiddlewareStack(inner):
    """
    Convenience function for wrapping the middleware.

    Args:
        inner: The inner application

    Returns:
        The wrapped application
    """
    return TokenAuthMiddleware(inner)
