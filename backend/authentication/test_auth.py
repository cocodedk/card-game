#!/usr/bin/env python
"""
Test script for authentication endpoints.
This script tests registration, login, logout, and change password functionality.
"""

import requests
import json
import sys
import os
from pprint import pprint

# Base URL for API endpoints
BASE_URL = "http://localhost:8000/api/auth"

# Test user data
TEST_USER = {
    "username": "testuser",
    "email": "testuser@example.com",
    "password": "testpassword123",
    "confirm_password": "testpassword123",
    "first_name": "Test",
    "last_name": "User"
}

# Storage for tokens
tokens = {}

def print_separator():
    """Print a separator line"""
    print("\n" + "="*50 + "\n")

def test_register():
    """Test user registration"""
    print("Testing user registration...")

    url = f"{BASE_URL}/register/"
    response = requests.post(url, json=TEST_USER)

    print(f"Status Code: {response.status_code}")
    data = response.json()
    pprint(data)

    if response.status_code == 201:
        print("✅ Registration successful")
        # Save tokens for later use
        tokens["access"] = data["tokens"]["access"]
        tokens["refresh"] = data["tokens"]["refresh"]
        return True
    else:
        print("❌ Registration failed")
        return False

def test_login():
    """Test user login"""
    print("Testing user login...")

    url = f"{BASE_URL}/login/"
    login_data = {
        "username": TEST_USER["username"],
        "password": TEST_USER["password"]
    }

    response = requests.post(url, json=login_data)

    print(f"Status Code: {response.status_code}")
    data = response.json()
    pprint(data)

    if response.status_code == 200:
        print("✅ Login successful")
        # Update tokens
        tokens["access"] = data["tokens"]["access"]
        tokens["refresh"] = data["tokens"]["refresh"]
        return True
    else:
        print("❌ Login failed")
        return False

def test_current_user():
    """Test getting current user info"""
    print("Testing current user endpoint...")

    url = f"{BASE_URL}/me/"
    headers = {"Authorization": f"Bearer {tokens['access']}"}

    response = requests.get(url, headers=headers)

    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        pprint(data)
        print("✅ Got current user info")
        return True
    else:
        print("❌ Failed to get current user info")
        try:
            pprint(response.json())
        except:
            print(response.text)
        return False

def test_change_password():
    """Test changing password"""
    print("Testing change password...")

    url = f"{BASE_URL}/change-password/"
    headers = {"Authorization": f"Bearer {tokens['access']}"}

    # First, try with incorrect current password
    password_data = {
        "current_password": "wrongpassword",
        "new_password": "newpassword123",
        "confirm_new_password": "newpassword123"
    }

    response = requests.post(url, json=password_data, headers=headers)

    print(f"Status Code (wrong current password): {response.status_code}")
    pprint(response.json())

    if response.status_code != 400:
        print("❌ Change password validation failed - should reject wrong current password")
    else:
        print("✅ Correctly rejected wrong current password")

    # Now try with correct data
    password_data = {
        "current_password": TEST_USER["password"],
        "new_password": "newpassword123",
        "confirm_new_password": "newpassword123"
    }

    response = requests.post(url, json=password_data, headers=headers)

    print(f"Status Code (correct data): {response.status_code}")
    try:
        pprint(response.json())
    except:
        print(response.text)

    if response.status_code == 200:
        print("✅ Password changed successfully")
        # Update the test user password for future tests
        TEST_USER["password"] = "newpassword123"
        return True
    else:
        print("❌ Failed to change password")
        return False

def test_login_with_new_password():
    """Test login with the new password"""
    print("Testing login with new password...")

    url = f"{BASE_URL}/login/"
    login_data = {
        "username": TEST_USER["username"],
        "password": TEST_USER["password"]  # This should now be the new password
    }

    response = requests.post(url, json=login_data)

    print(f"Status Code: {response.status_code}")
    data = response.json()
    pprint(data)

    if response.status_code == 200:
        print("✅ Login with new password successful")
        # Update tokens
        tokens["access"] = data["tokens"]["access"]
        tokens["refresh"] = data["tokens"]["refresh"]
        return True
    else:
        print("❌ Login with new password failed")
        return False

def test_logout():
    """Test user logout"""
    print("Testing logout...")

    url = f"{BASE_URL}/logout/"
    headers = {"Authorization": f"Bearer {tokens['access']}"}
    logout_data = {"refresh": tokens["refresh"]}

    response = requests.post(url, json=logout_data, headers=headers)

    print(f"Status Code: {response.status_code}")
    try:
        pprint(response.json())
    except:
        print(response.text)

    if response.status_code == 200:
        print("✅ Logout successful")
        return True
    else:
        print("❌ Logout failed")
        return False

def test_access_after_logout():
    """Test that access is denied after logout"""
    print("Testing access after logout...")

    url = f"{BASE_URL}/me/"
    headers = {"Authorization": f"Bearer {tokens['access']}"}

    response = requests.get(url, headers=headers)

    print(f"Status Code: {response.status_code}")

    # The token might still be valid if it hasn't expired
    # But the refresh token should be blacklisted
    print("Note: Access token might still be valid until it expires")

    # Try to use the refresh token
    refresh_url = f"{BASE_URL}/token/refresh/"
    refresh_data = {"refresh": tokens["refresh"]}

    refresh_response = requests.post(refresh_url, json=refresh_data)

    print(f"Refresh Token Status Code: {refresh_response.status_code}")
    try:
        pprint(refresh_response.json())
    except:
        print(refresh_response.text)

    if refresh_response.status_code >= 400:
        print("✅ Refresh token is blacklisted as expected")
        return True
    else:
        print("❌ Refresh token is still valid after logout")
        return False

def run_tests():
    """Run all tests in sequence"""
    tests = [
        ("Registration", test_register),
        ("Login", test_login),
        ("Current User", test_current_user),
        ("Change Password", test_change_password),
        ("Login with New Password", test_login_with_new_password),
        ("Logout", test_logout),
        ("Access After Logout", test_access_after_logout)
    ]

    results = {}

    for name, test_func in tests:
        print_separator()
        print(f"Running test: {name}")
        try:
            result = test_func()
            results[name] = result
        except Exception as e:
            print(f"❌ Test failed with exception: {str(e)}")
            results[name] = False

    print_separator()
    print("Test Results Summary:")
    print_separator()

    all_passed = True
    for name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{name}: {status}")
        if not result:
            all_passed = False

    return all_passed

if __name__ == "__main__":
    print("Starting authentication tests...")
    success = run_tests()

    if success:
        print("\nAll tests passed successfully! 🎉")
        sys.exit(0)
    else:
        print("\nSome tests failed. Please check the output above for details.")
        sys.exit(1)
