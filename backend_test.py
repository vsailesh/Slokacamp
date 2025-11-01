#!/usr/bin/env python3
"""
Backend Authentication System Test Suite for SlokaCamp
Tests all authentication endpoints with comprehensive scenarios
"""

import requests
import json
import os
from datetime import datetime

# Get backend URL from frontend .env file
def get_backend_url():
    try:
        with open('/app/frontend/.env', 'r') as f:
            for line in f:
                if line.startswith('REACT_APP_BACKEND_URL='):
                    return line.split('=', 1)[1].strip()
    except FileNotFoundError:
        pass
    return "http://localhost:8001"

BASE_URL = get_backend_url()
API_URL = f"{BASE_URL}/api"

print(f"Testing backend at: {API_URL}")

class TestResults:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
    
    def add_pass(self, test_name):
        self.passed += 1
        print(f"✅ PASS: {test_name}")
    
    def add_fail(self, test_name, error):
        self.failed += 1
        self.errors.append(f"{test_name}: {error}")
        print(f"❌ FAIL: {test_name} - {error}")
    
    def summary(self):
        total = self.passed + self.failed
        print(f"\n{'='*60}")
        print(f"TEST SUMMARY: {self.passed}/{total} tests passed")
        if self.errors:
            print(f"\nFAILED TESTS:")
            for error in self.errors:
                print(f"  - {error}")
        print(f"{'='*60}")

results = TestResults()

# Test data
admin_credentials = {
    "email": "admin@slokcamp.com",
    "password": "Admin@123"
}

test_user_data = {
    "email": "test@example.com",
    "password": "Test@123",
    "full_name": "Test User"
}

# Global variables to store tokens
admin_token = None
user_token = None

def test_signup_valid_data():
    """Test POST /api/auth/signup with valid data"""
    try:
        # First, try to delete the test user if it exists (cleanup)
        try:
            signin_response = requests.post(f"{API_URL}/auth/signin", json={
                "email": test_user_data["email"],
                "password": test_user_data["password"]
            })
            if signin_response.status_code == 200:
                # User exists, we'll test with a different email
                test_email = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}@example.com"
                signup_data = test_user_data.copy()
                signup_data["email"] = test_email
            else:
                signup_data = test_user_data.copy()
        except:
            signup_data = test_user_data.copy()
        
        response = requests.post(f"{API_URL}/auth/signup", json=signup_data)
        
        if response.status_code == 201:
            data = response.json()
            if "access_token" in data and "user" in data:
                global user_token
                user_token = data["access_token"]
                results.add_pass("Signup with valid data")
            else:
                results.add_fail("Signup with valid data", "Missing access_token or user in response")
        else:
            results.add_fail("Signup with valid data", f"Status {response.status_code}: {response.text}")
    except Exception as e:
        results.add_fail("Signup with valid data", f"Exception: {str(e)}")

def test_signup_duplicate_email():
    """Test POST /api/auth/signup with duplicate email"""
    try:
        # Try to signup with the same email again
        response = requests.post(f"{API_URL}/auth/signup", json=test_user_data)
        
        if response.status_code == 400:
            data = response.json()
            if "already registered" in data.get("detail", "").lower():
                results.add_pass("Signup duplicate email rejection")
            else:
                results.add_fail("Signup duplicate email rejection", f"Wrong error message: {data.get('detail')}")
        else:
            results.add_fail("Signup duplicate email rejection", f"Expected 400, got {response.status_code}")
    except Exception as e:
        results.add_fail("Signup duplicate email rejection", f"Exception: {str(e)}")

def test_signin_admin():
    """Test POST /api/auth/signin with admin credentials"""
    try:
        response = requests.post(f"{API_URL}/auth/signin", json=admin_credentials)
        
        if response.status_code == 200:
            data = response.json()
            if "access_token" in data and "user" in data:
                global admin_token
                admin_token = data["access_token"]
                user_data = data["user"]
                if user_data.get("role") == "admin":
                    results.add_pass("Admin signin")
                else:
                    results.add_fail("Admin signin", f"User role is {user_data.get('role')}, expected 'admin'")
            else:
                results.add_fail("Admin signin", "Missing access_token or user in response")
        else:
            results.add_fail("Admin signin", f"Status {response.status_code}: {response.text}")
    except Exception as e:
        results.add_fail("Admin signin", f"Exception: {str(e)}")

def test_signin_user():
    """Test POST /api/auth/signin with regular user credentials"""
    try:
        response = requests.post(f"{API_URL}/auth/signin", json={
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        })
        
        if response.status_code == 200:
            data = response.json()
            if "access_token" in data and "user" in data:
                global user_token
                user_token = data["access_token"]
                results.add_pass("User signin")
            else:
                results.add_fail("User signin", "Missing access_token or user in response")
        else:
            results.add_fail("User signin", f"Status {response.status_code}: {response.text}")
    except Exception as e:
        results.add_fail("User signin", f"Exception: {str(e)}")

def test_signin_invalid_credentials():
    """Test POST /api/auth/signin with invalid credentials"""
    try:
        response = requests.post(f"{API_URL}/auth/signin", json={
            "email": "wrong@example.com",
            "password": "wrongpassword"
        })
        
        if response.status_code == 401:
            results.add_pass("Signin invalid credentials rejection")
        else:
            results.add_fail("Signin invalid credentials rejection", f"Expected 401, got {response.status_code}")
    except Exception as e:
        results.add_fail("Signin invalid credentials rejection", f"Exception: {str(e)}")

def test_get_me_with_valid_token():
    """Test GET /api/auth/me with valid JWT token"""
    try:
        if not admin_token:
            results.add_fail("Get current user with valid token", "No admin token available")
            return
        
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{API_URL}/auth/me", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            if "email" in data and "full_name" in data:
                results.add_pass("Get current user with valid token")
            else:
                results.add_fail("Get current user with valid token", "Missing user data in response")
        else:
            results.add_fail("Get current user with valid token", f"Status {response.status_code}: {response.text}")
    except Exception as e:
        results.add_fail("Get current user with valid token", f"Exception: {str(e)}")

def test_get_me_without_token():
    """Test GET /api/auth/me without token"""
    try:
        response = requests.get(f"{API_URL}/auth/me")
        
        if response.status_code == 401 or response.status_code == 403:
            results.add_pass("Get current user without token rejection")
        else:
            results.add_fail("Get current user without token rejection", f"Expected 401/403, got {response.status_code}")
    except Exception as e:
        results.add_fail("Get current user without token rejection", f"Exception: {str(e)}")

def test_get_me_with_invalid_token():
    """Test GET /api/auth/me with invalid token"""
    try:
        headers = {"Authorization": "Bearer invalid_token_here"}
        response = requests.get(f"{API_URL}/auth/me", headers=headers)
        
        if response.status_code == 401:
            results.add_pass("Get current user with invalid token rejection")
        else:
            results.add_fail("Get current user with invalid token rejection", f"Expected 401, got {response.status_code}")
    except Exception as e:
        results.add_fail("Get current user with invalid token rejection", f"Exception: {str(e)}")

def test_admin_users_with_admin_token():
    """Test GET /api/admin/users with admin JWT token"""
    try:
        if not admin_token:
            results.add_fail("Admin users list with admin token", "No admin token available")
            return
        
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{API_URL}/admin/users", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                # Check if admin user is in the list
                admin_found = any(user.get("email") == "admin@slokcamp.com" for user in data)
                if admin_found:
                    results.add_pass("Admin users list with admin token")
                else:
                    results.add_fail("Admin users list with admin token", "Admin user not found in users list")
            else:
                results.add_fail("Admin users list with admin token", "Empty or invalid users list")
        else:
            results.add_fail("Admin users list with admin token", f"Status {response.status_code}: {response.text}")
    except Exception as e:
        results.add_fail("Admin users list with admin token", f"Exception: {str(e)}")

def test_admin_users_with_user_token():
    """Test GET /api/admin/users with regular user JWT token"""
    try:
        if not user_token:
            results.add_fail("Admin users list with user token rejection", "No user token available")
            return
        
        headers = {"Authorization": f"Bearer {user_token}"}
        response = requests.get(f"{API_URL}/admin/users", headers=headers)
        
        if response.status_code == 403:
            results.add_pass("Admin users list with user token rejection")
        else:
            results.add_fail("Admin users list with user token rejection", f"Expected 403, got {response.status_code}")
    except Exception as e:
        results.add_fail("Admin users list with user token rejection", f"Exception: {str(e)}")

def test_admin_users_without_token():
    """Test GET /api/admin/users without token"""
    try:
        response = requests.get(f"{API_URL}/admin/users")
        
        if response.status_code == 401 or response.status_code == 403:
            results.add_pass("Admin users list without token rejection")
        else:
            results.add_fail("Admin users list without token rejection", f"Expected 401/403, got {response.status_code}")
    except Exception as e:
        results.add_fail("Admin users list without token rejection", f"Exception: {str(e)}")

def test_basic_connectivity():
    """Test basic API connectivity"""
    try:
        response = requests.get(f"{API_URL}/")
        if response.status_code == 200:
            results.add_pass("Basic API connectivity")
        else:
            results.add_fail("Basic API connectivity", f"Status {response.status_code}")
    except Exception as e:
        results.add_fail("Basic API connectivity", f"Exception: {str(e)}")

def main():
    print("Starting SlokaCamp Authentication System Tests...")
    print(f"Backend URL: {BASE_URL}")
    print(f"API URL: {API_URL}")
    print("-" * 60)
    
    # Test basic connectivity first
    test_basic_connectivity()
    
    # Test signup endpoints
    print("\n🔐 Testing Signup Endpoints...")
    test_signup_valid_data()
    test_signup_duplicate_email()
    
    # Test signin endpoints
    print("\n🔑 Testing Signin Endpoints...")
    test_signin_admin()
    test_signin_user()
    test_signin_invalid_credentials()
    
    # Test protected endpoints
    print("\n👤 Testing Protected User Endpoints...")
    test_get_me_with_valid_token()
    test_get_me_without_token()
    test_get_me_with_invalid_token()
    
    # Test admin endpoints
    print("\n👑 Testing Admin Endpoints...")
    test_admin_users_with_admin_token()
    test_admin_users_with_user_token()
    test_admin_users_without_token()
    
    # Print summary
    results.summary()
    
    return results.failed == 0

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)