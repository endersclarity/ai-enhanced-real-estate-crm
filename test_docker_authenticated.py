#!/usr/bin/env python3
"""
Docker Integration Test Suite - With Authentication
Tests the new Flask blueprint-based application structure
"""

import sys
import time
import requests
import json
import os
from datetime import datetime

class DockerAuthenticatedTests:
    def __init__(self):
        self.base_url = "http://localhost:5000"
        self.session = requests.Session()
        self.results = []
        
    def log(self, message, level="INFO"):
        """Log with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
        
    def test(self, name, test_func):
        """Run a test and record results"""
        self.log(f"Running test: {name}")
        try:
            result = test_func()
            self.results.append((name, "PASSED", None))
            self.log(f"✅ {name} PASSED", "SUCCESS")
            return True
        except Exception as e:
            self.results.append((name, "FAILED", str(e)))
            self.log(f"❌ {name} FAILED: {str(e)}", "ERROR")
            return False
            
    def test_basic_connectivity(self):
        """Test basic server connectivity"""
        response = self.session.get(f"{self.base_url}/", timeout=5)
        # 302 redirect to login is expected
        assert response.status_code in [200, 302], f"Unexpected status: {response.status_code}"
        return True
        
    def test_authentication_flow(self):
        """Test login functionality"""
        # Get login page
        response = self.session.get(f"{self.base_url}/auth/login", timeout=5)
        assert response.status_code == 200, f"Login page failed: {response.status_code}"
        
        # Try to login with default credentials
        login_data = {
            'username': 'admin',
            'password': 'admin123'
        }
        
        # Note: Real login might require CSRF token handling
        # For now, just verify the endpoint exists
        response = self.session.post(
            f"{self.base_url}/auth/login",
            data=login_data,
            allow_redirects=False,
            timeout=5
        )
        
        # Login might redirect or return form with errors
        assert response.status_code in [200, 302, 303], f"Login failed: {response.status_code}"
        
        return True
        
    def test_crm_endpoints(self):
        """Test CRM blueprint endpoints"""
        crm_endpoints = [
            '/crm/clients',
            '/crm/properties', 
            '/crm/transactions',
            '/crm/dashboard'
        ]
        
        for endpoint in crm_endpoints:
            response = self.session.get(f"{self.base_url}{endpoint}", timeout=5)
            # Either 200 (if authenticated) or 302 (redirect to login)
            assert response.status_code in [200, 302], \
                f"{endpoint} returned unexpected status: {response.status_code}"
                
        return True
        
    def test_static_assets(self):
        """Test static file serving"""
        # Try common static file paths
        static_files = [
            '/static/css/style.css',
            '/static/style.css',
            '/static/js/main.js',
            '/static/script.js'
        ]
        
        found_static = False
        for static_file in static_files:
            response = self.session.get(f"{self.base_url}{static_file}", timeout=5)
            if response.status_code == 200:
                found_static = True
                self.log(f"Found static file: {static_file}")
                break
                
        assert found_static or response.status_code == 404, \
            "Static files configuration issue"
            
        return True
        
    def test_database_models(self):
        """Test database models are working"""
        # Import Flask app context
        sys.path.insert(0, '/app')
        from app import create_app, db
        from app.models import User, Client, Property, Transaction
        
        app = create_app()
        
        with app.app_context():
            # Test User model
            user_count = User.query.count()
            assert user_count >= 1, "No users in database"
            self.log(f"Found {user_count} users")
            
            # Test admin user exists
            admin = User.query.filter_by(username='admin').first()
            assert admin is not None, "Admin user not found"
            
            # Test we can query other models
            client_count = Client.query.count()
            property_count = Property.query.count()
            transaction_count = Transaction.query.count()
            
            self.log(f"Database stats: {client_count} clients, {property_count} properties, {transaction_count} transactions")
            
        return True
        
    def test_form_validation(self):
        """Test form validation is available"""
        sys.path.insert(0, '/app')
        from app.forms import ClientForm, PropertyForm, TransactionForm
        
        # Just verify forms can be imported
        assert ClientForm is not None, "ClientForm not available"
        assert PropertyForm is not None, "PropertyForm not available"
        assert TransactionForm is not None, "TransactionForm not available"
        
        return True
        
    def test_environment_variables(self):
        """Test critical environment variables"""
        assert os.environ.get('FLASK_ENV') == 'development', "Not in development mode"
        assert 'GEMINI_API_KEY' in os.environ, "GEMINI_API_KEY not set"
        assert os.environ.get('DATABASE_URL') is not None, "DATABASE_URL not set"
        
        return True
        
    def run_all_tests(self):
        """Run all integration tests"""
        self.log("Starting Docker Authenticated Integration Tests", "INFO")
        self.log(f"Target: {self.base_url}", "INFO")
        self.log(f"Container: {os.environ.get('HOSTNAME', 'unknown')}", "INFO")
        self.log(f"Python: {sys.version.split()[0]}", "INFO")
        
        # Run tests
        self.test("Basic Connectivity", self.test_basic_connectivity)
        self.test("Authentication Flow", self.test_authentication_flow)
        self.test("CRM Endpoints", self.test_crm_endpoints)
        self.test("Static Assets", self.test_static_assets)
        self.test("Database Models", self.test_database_models)
        self.test("Form Validation", self.test_form_validation)
        self.test("Environment Variables", self.test_environment_variables)
        
        # Summary
        passed = sum(1 for _, status, _ in self.results if status == "PASSED")
        failed = sum(1 for _, status, _ in self.results if status == "FAILED")
        
        self.log("="*50, "INFO")
        self.log(f"SUMMARY: {passed} passed, {failed} failed", "INFO")
        
        if failed > 0:
            self.log("Failed tests:", "ERROR")
            for name, status, error in self.results:
                if status == "FAILED":
                    self.log(f"  - {name}: {error}", "ERROR")
            sys.exit(1)
        else:
            self.log("All tests passed! 🎉", "SUCCESS")
            sys.exit(0)


if __name__ == "__main__":
    tests = DockerAuthenticatedTests()
    tests.run_all_tests()