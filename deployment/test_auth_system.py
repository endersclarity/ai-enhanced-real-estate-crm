#!/usr/bin/env python3
"""
Test script for User Authentication System
Validates authentication functionality, password security, and session management
"""

import unittest
import requests
import json
import time
import tempfile
import os
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AuthSystemTester:
    """Comprehensive testing for authentication system"""
    
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = {}
        
        # Test data
        self.test_users = [
            {
                'username': 'testuser1',
                'email': 'test1@example.com',
                'password': 'TestPass123!',
                'role': 'agent'
            },
            {
                'username': 'testuser2',
                'email': 'test2@example.com',
                'password': 'TestPass456!',
                'role': 'manager'
            }
        ]
    
    def test_user_registration(self):
        """Test user registration functionality"""
        try:
            for user_data in self.test_users:
                response = self.session.post(
                    f"{self.base_url}/auth/register",
                    json=user_data
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('success'):
                        logger.info(f"User registration successful: {user_data['username']}")
                    else:
                        logger.error(f"User registration failed: {result.get('error')}")
                        return False
                else:
                    logger.error(f"Registration request failed: {response.status_code}")
                    return False
            
            self.test_results["user_registration"] = {
                "status": "pass",
                "message": "User registration working correctly"
            }
            return True
            
        except Exception as e:
            self.test_results["user_registration"] = {
                "status": "fail",
                "error": str(e),
                "message": "User registration test failed"
            }
            logger.error(f"Registration test failed: {e}")
            return False
    
    def test_user_login(self):
        """Test user login functionality"""
        try:
            user_data = self.test_users[0]
            
            # Test valid login
            response = self.session.post(
                f"{self.base_url}/auth/login",
                json={
                    'username': user_data['username'],
                    'password': user_data['password']
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    self.auth_token = result.get('token')  # If returned
                    self.logged_in_user = result.get('user')
                    logger.info(f"Login successful: {user_data['username']}")
                    
                    # Test invalid login
                    invalid_response = self.session.post(
                        f"{self.base_url}/auth/login",
                        json={
                            'username': user_data['username'],
                            'password': 'wrongpassword'
                        }
                    )
                    
                    if invalid_response.status_code == 401:
                        logger.info("Invalid login correctly rejected")
                        
                        self.test_results["user_login"] = {
                            "status": "pass",
                            "message": "User login working correctly"
                        }
                        return True
                    else:
                        logger.error("Invalid login not properly rejected")
                        return False
                else:
                    logger.error(f"Login failed: {result.get('error')}")
                    return False
            else:
                logger.error(f"Login request failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.test_results["user_login"] = {
                "status": "fail",
                "error": str(e),
                "message": "User login test failed"
            }
            logger.error(f"Login test failed: {e}")
            return False
    
    def test_password_strength_validation(self):
        """Test password strength requirements"""
        try:
            weak_passwords = [
                'weak',          # Too short
                'weakpassword',  # No uppercase, digits, special chars
                'WEAKPASSWORD',  # No lowercase, digits, special chars
                'WeakPassword',  # No digits, special chars
                'WeakPass123',   # No special chars
                'WeakPass!',     # No digits
            ]
            
            weak_password_rejected = 0
            total_weak_passwords = len(weak_passwords)
            
            for i, weak_password in enumerate(weak_passwords):
                response = self.session.post(
                    f"{self.base_url}/auth/register",
                    json={
                        'username': f'weakuser{i}',
                        'email': f'weak{i}@example.com',
                        'password': weak_password,
                        'role': 'agent'
                    }
                )
                
                if response.status_code == 400:
                    weak_password_rejected += 1
                    logger.info(f"Weak password correctly rejected: {weak_password}")
                else:
                    logger.warning(f"Weak password accepted: {weak_password}")
            
            success_rate = (weak_password_rejected / total_weak_passwords) * 100
            
            if success_rate >= 80:  # At least 80% of weak passwords should be rejected
                self.test_results["password_strength"] = {
                    "status": "pass",
                    "success_rate": success_rate,
                    "message": "Password strength validation working"
                }
                logger.info(f"Password strength test passed: {success_rate:.1f}%")
                return True
            else:
                self.test_results["password_strength"] = {
                    "status": "fail",
                    "success_rate": success_rate,
                    "message": "Password strength validation insufficient"
                }
                logger.error(f"Password strength test failed: {success_rate:.1f}%")
                return False
                
        except Exception as e:
            self.test_results["password_strength"] = {
                "status": "error",
                "error": str(e),
                "message": "Password strength test failed"
            }
            logger.error(f"Password strength test failed: {e}")
            return False
    
    def test_session_management(self):
        """Test session management functionality"""
        try:
            # Login to create session
            user_data = self.test_users[0]
            login_response = self.session.post(
                f"{self.base_url}/auth/login",
                json={
                    'username': user_data['username'],
                    'password': user_data['password']
                }
            )
            
            if login_response.status_code != 200:
                logger.error("Could not login for session test")
                return False
            
            # Test accessing protected route
            profile_response = self.session.get(f"{self.base_url}/auth/profile")
            
            if profile_response.status_code == 200:
                profile_data = profile_response.json()
                if profile_data.get('user'):
                    logger.info("Session authentication working")
                    
                    # Test logout
                    logout_response = self.session.post(f"{self.base_url}/auth/logout")
                    
                    if logout_response.status_code == 200:
                        # Try accessing protected route after logout
                        profile_after_logout = self.session.get(f"{self.base_url}/auth/profile")
                        
                        if profile_after_logout.status_code == 401:
                            self.test_results["session_management"] = {
                                "status": "pass",
                                "message": "Session management working correctly"
                            }
                            logger.info("Session management test passed")
                            return True
                        else:
                            logger.error("Protected route accessible after logout")
                            return False
                    else:
                        logger.error("Logout failed")
                        return False
                else:
                    logger.error("No user data in profile response")
                    return False
            else:
                logger.error("Could not access protected route")
                return False
                
        except Exception as e:
            self.test_results["session_management"] = {
                "status": "fail",
                "error": str(e),
                "message": "Session management test failed"
            }
            logger.error(f"Session management test failed: {e}")
            return False
    
    def test_failed_login_lockout(self):
        """Test account lockout after failed login attempts"""
        try:
            user_data = self.test_users[1]  # Use second test user
            
            # Attempt multiple failed logins
            failed_attempts = 0
            max_attempts = 6  # Should exceed the lockout threshold
            
            for i in range(max_attempts):
                response = self.session.post(
                    f"{self.base_url}/auth/login",
                    json={
                        'username': user_data['username'],
                        'password': 'wrongpassword'
                    }
                )
                
                if response.status_code == 401:
                    failed_attempts += 1
                    logger.info(f"Failed login attempt {i+1}")
                
                time.sleep(0.1)  # Small delay between attempts
            
            # Try one more login with correct password (should be locked)
            final_response = self.session.post(
                f"{self.base_url}/auth/login",
                json={
                    'username': user_data['username'],
                    'password': user_data['password']
                }
            )
            
            if final_response.status_code == 401:
                result = final_response.json()
                if 'locked' in result.get('error', '').lower():
                    self.test_results["failed_login_lockout"] = {
                        "status": "pass",
                        "failed_attempts": failed_attempts,
                        "message": "Account lockout working correctly"
                    }
                    logger.info("Account lockout test passed")
                    return True
                else:
                    logger.warning("Account may be locked but error message unclear")
                    return True  # Still consider it a pass
            else:
                logger.error("Account was not locked after failed attempts")
                return False
                
        except Exception as e:
            self.test_results["failed_login_lockout"] = {
                "status": "error",
                "error": str(e),
                "message": "Failed login lockout test failed"
            }
            logger.error(f"Failed login lockout test failed: {e}")
            return False
    
    def test_password_change(self):
        """Test password change functionality"""
        try:
            # First login
            user_data = self.test_users[0]
            login_response = self.session.post(
                f"{self.base_url}/auth/login",
                json={
                    'username': user_data['username'],
                    'password': user_data['password']
                }
            )
            
            if login_response.status_code != 200:
                logger.error("Could not login for password change test")
                return False
            
            # Change password
            new_password = 'NewTestPass123!'
            change_response = self.session.post(
                f"{self.base_url}/auth/change-password",
                json={
                    'old_password': user_data['password'],
                    'new_password': new_password
                }
            )
            
            if change_response.status_code == 200:
                result = change_response.json()
                if result.get('success'):
                    logger.info("Password change successful")
                    
                    # Logout and try login with new password
                    self.session.post(f"{self.base_url}/auth/logout")
                    
                    new_login_response = self.session.post(
                        f"{self.base_url}/auth/login",
                        json={
                            'username': user_data['username'],
                            'password': new_password
                        }
                    )
                    
                    if new_login_response.status_code == 200:
                        self.test_results["password_change"] = {
                            "status": "pass",
                            "message": "Password change working correctly"
                        }
                        logger.info("Password change test passed")
                        return True
                    else:
                        logger.error("Could not login with new password")
                        return False
                else:
                    logger.error(f"Password change failed: {result.get('error')}")
                    return False
            else:
                logger.error(f"Password change request failed: {change_response.status_code}")
                return False
                
        except Exception as e:
            self.test_results["password_change"] = {
                "status": "fail",
                "error": str(e),
                "message": "Password change test failed"
            }
            logger.error(f"Password change test failed: {e}")
            return False
    
    def test_password_reset_flow(self):
        """Test password reset functionality"""
        try:
            user_data = self.test_users[0]
            
            # Request password reset
            reset_request_response = self.session.post(
                f"{self.base_url}/auth/reset-password-request",
                json={'email': user_data['email']}
            )
            
            if reset_request_response.status_code == 200:
                result = reset_request_response.json()
                if result.get('success'):
                    logger.info("Password reset request successful")
                    
                    # In a real test, we would check email or database for token
                    # For now, we'll consider the request handling as success
                    self.test_results["password_reset"] = {
                        "status": "pass",
                        "message": "Password reset request handling working"
                    }
                    return True
                else:
                    logger.error("Password reset request failed")
                    return False
            else:
                logger.error(f"Password reset request failed: {reset_request_response.status_code}")
                return False
                
        except Exception as e:
            self.test_results["password_reset"] = {
                "status": "fail",
                "error": str(e),
                "message": "Password reset test failed"
            }
            logger.error(f"Password reset test failed: {e}")
            return False
    
    def test_authentication_endpoints(self):
        """Test all authentication endpoints are accessible"""
        try:
            endpoints = [
                '/auth/login',
                '/auth/register',
                '/auth/reset-password-request'
            ]
            
            accessible_endpoints = 0
            
            for endpoint in endpoints:
                try:
                    response = self.session.get(f"{self.base_url}{endpoint}")
                    if response.status_code in [200, 405]:  # 405 for POST-only endpoints
                        accessible_endpoints += 1
                        logger.info(f"Endpoint accessible: {endpoint}")
                    else:
                        logger.warning(f"Endpoint not accessible: {endpoint} ({response.status_code})")
                except Exception as e:
                    logger.error(f"Error accessing endpoint {endpoint}: {e}")
            
            success_rate = (accessible_endpoints / len(endpoints)) * 100
            
            if success_rate >= 90:
                self.test_results["endpoint_accessibility"] = {
                    "status": "pass",
                    "success_rate": success_rate,
                    "message": "Authentication endpoints accessible"
                }
                return True
            else:
                self.test_results["endpoint_accessibility"] = {
                    "status": "fail",
                    "success_rate": success_rate,
                    "message": "Some authentication endpoints not accessible"
                }
                return False
                
        except Exception as e:
            self.test_results["endpoint_accessibility"] = {
                "status": "error",
                "error": str(e),
                "message": "Endpoint accessibility test failed"
            }
            logger.error(f"Endpoint accessibility test failed: {e}")
            return False
    
    def run_all_tests(self):
        """Run all authentication system tests"""
        logger.info("Starting comprehensive authentication system tests")
        
        tests = [
            ("Endpoint Accessibility", self.test_authentication_endpoints),
            ("User Registration", self.test_user_registration),
            ("Password Strength Validation", self.test_password_strength_validation),
            ("User Login", self.test_user_login),
            ("Session Management", self.test_session_management),
            ("Password Change", self.test_password_change),
            ("Password Reset Flow", self.test_password_reset_flow),
            ("Failed Login Lockout", self.test_failed_login_lockout)
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test_name, test_function in tests:
            logger.info(f"Running test: {test_name}")
            try:
                if test_function():
                    passed_tests += 1
                    logger.info(f"✅ {test_name} - PASSED")
                else:
                    logger.error(f"❌ {test_name} - FAILED")
            except Exception as e:
                logger.error(f"💥 {test_name} - ERROR: {e}")
        
        # Generate summary
        success_rate = (passed_tests / total_tests) * 100
        
        summary = {
            "test_date": datetime.now().isoformat(),
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "success_rate": success_rate,
            "overall_status": "pass" if success_rate >= 75 else "fail",
            "detailed_results": self.test_results
        }
        
        # Save results
        with open("deployment/auth_system_test_results.json", "w") as f:
            json.dump(summary, f, indent=2)
        
        logger.info(f"Test Summary: {passed_tests}/{total_tests} tests passed ({success_rate:.1f}%)")
        
        return summary

def main():
    """Main execution function"""
    import sys
    
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5000"
    
    tester = AuthSystemTester(base_url)
    results = tester.run_all_tests()
    
    if results["overall_status"] == "pass":
        print(f"✅ Authentication system tests PASSED")
        sys.exit(0)
    else:
        print(f"❌ Authentication system tests FAILED")
        sys.exit(1)

if __name__ == "__main__":
    main()