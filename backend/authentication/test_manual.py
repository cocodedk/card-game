#!/usr/bin/env python
"""
Manual test script for authentication endpoints.
This script directly tests the authentication functionality without Django's test framework.
"""

import unittest
from unittest.mock import patch, MagicMock
import json

from .models import UserProfile
from backend.authentication.serializers import UserSerializer, ChangePasswordSerializer
from backend.authentication.views import RegisterView, LoginView, LogoutView, ChangePasswordView, UserProfileView, CurrentUserView

class MockRequest:
    """Mock request object for testing views"""
    def __init__(self, data=None, user=None):
        self.data = data or {}
        self.user = user

class MockResponse:
    """Mock response object for testing views"""
    def __init__(self, data=None, status=200):
        self.data = data or {}
        self.status_code = status

class AuthenticationTests(unittest.TestCase):
    """Test case for authentication views"""

    def setUp(self):
        """Set up test data"""
        # Create a test user
        self.test_user = UserProfile(
            username="testuser",
            email="testuser@example.com",
            first_name="Test",
            last_name="User"
        )
        self.test_user.uid = "test123"  # Mock the UID
        self.test_user.save = MagicMock()
        self.test_user.check_password = MagicMock(return_value=True)
        self.test_user.set_password = MagicMock()

        # Mock the Player model
        self.player_patcher = patch('backend.authentication.views.Player')
        self.mock_player = self.player_patcher.start()
        self.mock_player_instance = MagicMock()
        self.mock_player_instance.save.return_value = self.mock_player_instance
        self.mock_player.return_value = self.mock_player_instance

        # Mock get_tokens_for_user
        self.tokens_patcher = patch('backend.authentication.views.get_tokens_for_user')
        self.mock_get_tokens = self.tokens_patcher.start()
        self.mock_get_tokens.return_value = {
            'access': 'mock_access_token',
            'refresh': 'mock_refresh_token'
        }

        # Mock RefreshToken
        self.refresh_token_patcher = patch('backend.authentication.views.RefreshToken')
        self.mock_refresh_token = self.refresh_token_patcher.start()
        self.mock_token_instance = MagicMock()
        self.mock_refresh_token.return_value = self.mock_token_instance

        # Mock UserProfile.nodes
        self.nodes_patcher = patch('backend.authentication.models.UserProfile.nodes')
        self.mock_nodes = self.nodes_patcher.start()
        self.mock_nodes.get.return_value = self.test_user
        self.mock_nodes.filter.return_value.exists.return_value = False

    def tearDown(self):
        """Clean up after tests"""
        self.player_patcher.stop()
        self.tokens_patcher.stop()
        self.refresh_token_patcher.stop()
        self.nodes_patcher.stop()

    def test_register_view(self):
        """Test user registration"""
        print("Testing user registration...")

        # Create a mock request
        request_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "newpassword123",
            "confirm_password": "newpassword123",
            "first_name": "New",
            "last_name": "User"
        }

        # Mock the serializer
        with patch('backend.authentication.views.RegisterSerializer') as mock_serializer_class:
            mock_serializer = MagicMock()
            mock_serializer.is_valid.return_value = True
            mock_serializer.save.return_value = self.test_user
            mock_serializer.data = request_data
            mock_serializer_class.return_value = mock_serializer

            # Create the view
            view = RegisterView()
            view.get_serializer = MagicMock(return_value=mock_serializer)

            # Call the view
            request = MockRequest(data=request_data)
            response = view.post(request)

            # Check the response
            self.assertEqual(response.status_code, 201)
            self.assertTrue('tokens' in response.data)
            self.assertTrue('user' in response.data)
            self.assertTrue('message' in response.data)

            print("✅ Registration test passed")

    def test_login_view(self):
        """Test user login"""
        print("Testing user login...")

        # Create a mock request
        request_data = {
            "username": "testuser",
            "password": "testpassword123"
        }

        # Create the view
        view = LoginView()

        # Call the view
        request = MockRequest(data=request_data)
        response = view.post(request)

        # Check the response
        self.assertEqual(response.status_code, 200)
        self.assertTrue('tokens' in response.data)
        self.assertTrue('user' in response.data)

        print("✅ Login test passed")

    def test_change_password_view(self):
        """Test changing password"""
        print("Testing change password...")

        # Create a mock request
        request_data = {
            "current_password": "testpassword123",
            "new_password": "newpassword123",
            "confirm_new_password": "newpassword123"
        }

        # Mock the serializer
        with patch('backend.authentication.views.ChangePasswordSerializer') as mock_serializer_class:
            mock_serializer = MagicMock()
            mock_serializer.is_valid.return_value = True
            mock_serializer.validated_data = request_data
            mock_serializer_class.return_value = mock_serializer

            # Create the view
            view = ChangePasswordView()

            # Call the view
            request = MockRequest(data=request_data, user=self.test_user)
            response = view.post(request)

            # Check the response
            self.assertEqual(response.status_code, 200)
            self.assertTrue('message' in response.data)

            # Verify the password was changed
            self.test_user.set_password.assert_called_once_with("newpassword123")
            self.test_user.save.assert_called_once()

            print("✅ Change password test passed")

    def test_logout_view(self):
        """Test user logout"""
        print("Testing logout...")

        # Create a mock request
        request_data = {
            "refresh": "mock_refresh_token"
        }

        # Create the view
        view = LogoutView()

        # Call the view
        request = MockRequest(data=request_data, user=self.test_user)
        response = view.post(request)

        # Check the response
        self.assertEqual(response.status_code, 200)
        self.assertTrue('message' in response.data)

        # Verify the token was blacklisted
        self.mock_token_instance.blacklist.assert_called_once()

        print("✅ Logout test passed")

    def test_current_user_view(self):
        """Test getting current user info"""
        print("Testing current user endpoint...")

        # Mock the serializer
        with patch('backend.authentication.views.UserSerializer') as mock_serializer_class:
            mock_serializer = MagicMock()
            mock_serializer.data = {
                "uid": "test123",
                "username": "testuser",
                "email": "testuser@example.com",
                "first_name": "Test",
                "last_name": "User"
            }
            mock_serializer_class.return_value = mock_serializer

            # Create the view
            view = CurrentUserView()

            # Call the view
            request = MockRequest(user=self.test_user)
            response = view.get(request)

            # Check the response
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data["username"], "testuser")

            print("✅ Current user test passed")

def run_tests():
    """Run all tests"""
    test_suite = unittest.TestLoader().loadTestsFromTestCase(AuthenticationTests)
    unittest.TextTestRunner(verbosity=2).run(test_suite)

if __name__ == "__main__":
    print("Starting authentication tests...")
    run_tests()
    print("\nAll tests completed!")
