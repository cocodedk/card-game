from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from unittest.mock import patch, MagicMock

from backend.authentication.models import UserProfile
from backend.authentication.serializers import UserSerializer
from backend.authentication.jwt_auth import get_tokens_for_user


class AuthenticationTests(TestCase):
    """Test case for authentication views"""

    def setUp(self):
        """Set up test data"""
        self.client = APIClient()

        # Create a test user
        self.test_user = UserProfile(
            username="testuser",
            email="testuser@example.com",
            first_name="Test",
            last_name="User"
        )
        self.test_user.save()
        self.test_user.set_password("testpassword123")

        # Mock the Player model
        self.player_patcher = patch('backend.authentication.views.Player')
        self.mock_player = self.player_patcher.start()
        self.mock_player_instance = MagicMock()
        self.mock_player_instance.save.return_value = self.mock_player_instance
        self.mock_player.return_value = self.mock_player_instance

    def tearDown(self):
        """Clean up after tests"""
        self.player_patcher.stop()

    def test_register_view(self):
        """Test user registration"""
        url = reverse('register')
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "newpassword123",
            "confirm_password": "newpassword123",
            "first_name": "New",
            "last_name": "User"
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue('tokens' in response.data)
        self.assertTrue('user' in response.data)
        self.assertEqual(response.data['user']['username'], 'newuser')

        # Check that the user was created
        user_exists = UserProfile.nodes.filter(username='newuser').exists()
        self.assertTrue(user_exists)

    def test_login_view(self):
        """Test user login"""
        url = reverse('login')
        data = {
            "username": "testuser",
            "password": "testpassword123"
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('tokens' in response.data)
        self.assertTrue('user' in response.data)
        self.assertEqual(response.data['user']['username'], 'testuser')

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        url = reverse('login')
        data = {
            "username": "testuser",
            "password": "wrongpassword"
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue('error' in response.data)

    def test_current_user_view(self):
        """Test getting current user info"""
        url = reverse('current-user')

        # Get tokens for the test user
        tokens = get_tokens_for_user(self.test_user)

        # Set up authentication
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')

    def test_change_password_view(self):
        """Test changing password"""
        url = reverse('change-password')

        # Get tokens for the test user
        tokens = get_tokens_for_user(self.test_user)

        # Set up authentication
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")

        # Try with incorrect current password
        data = {
            "current_password": "wrongpassword",
            "new_password": "newpassword123",
            "confirm_new_password": "newpassword123"
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Try with correct data
        data = {
            "current_password": "testpassword123",
            "new_password": "newpassword123",
            "confirm_new_password": "newpassword123"
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('message' in response.data)

        # Verify the password was changed by trying to login
        login_url = reverse('login')
        login_data = {
            "username": "testuser",
            "password": "newpassword123"
        }

        login_response = self.client.post(login_url, login_data, format='json')

        self.assertEqual(login_response.status_code, status.HTTP_200_OK)

    @patch('backend.authentication.views.RefreshToken')
    def test_logout_view(self, mock_refresh_token):
        """Test user logout"""
        url = reverse('logout')

        # Get tokens for the test user
        tokens = get_tokens_for_user(self.test_user)

        # Set up authentication
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")

        # Mock the RefreshToken
        mock_token_instance = MagicMock()
        mock_refresh_token.return_value = mock_token_instance

        data = {
            "refresh": tokens['refresh']
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('message' in response.data)

        # Verify the token was blacklisted
        mock_token_instance.blacklist.assert_called_once()

    def test_logout_missing_token(self):
        """Test logout without providing a refresh token"""
        url = reverse('logout')

        # Get tokens for the test user
        tokens = get_tokens_for_user(self.test_user)

        # Set up authentication
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")

        # Don't provide a refresh token
        data = {}

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('error' in response.data)
