#!/usr/bin/env python3
"""
Docker Integration Test Suite
Runs INSIDE the Docker container to test actual application behavior
"""

import sys
import time
import requests
import json
import sqlite3
import os
from datetime import datetime

class DockerIntegrationTests:
    def __init__(self):
        self.base_url = "http://localhost:5000"
        self.results = []
        self.db_path = "/app/core_app/real_estate_crm.db"
        
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
            
    def test_environment(self):
        """Test Docker environment setup"""
        # Check we're in Docker
        assert os.path.exists("/app"), "Not running in Docker container"
        
        # Check virtual environment
        assert sys.prefix.startswith("/opt/venv"), f"Wrong venv: {sys.prefix}"
        
        # Check database exists
        assert os.path.exists(self.db_path), "Database file not found"
        
        # Check environment variables
        assert os.environ.get("FLASK_ENV") == "development", "Flask not in development mode"
        
        return True
        
    def test_database_operations(self):
        """Test database CRUD operations"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Test schema exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        required_tables = ['clients', 'properties', 'transactions']
        
        for table in required_tables:
            assert table in tables, f"Missing table: {table}"
            
        # Test insert and select
        test_client = (
            'Test', 'User', 'test@example.com', '555-0123',
            'Test City', 'Buyer', 100000, 500000, 'Downtown', 3
        )
        
        cursor.execute("""
            INSERT INTO clients (first_name, last_name, email, home_phone,
                               city, client_type, budget_min, budget_max,
                               area_preference, bedrooms)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, test_client)
        conn.commit()
        
        # Verify insert
        cursor.execute("SELECT * FROM clients WHERE email = 'test@example.com'")
        result = cursor.fetchone()
        assert result is not None, "Test client not inserted"
        
        # Clean up
        cursor.execute("DELETE FROM clients WHERE email = 'test@example.com'")
        conn.commit()
        conn.close()
        
        return True
        
    def test_flask_endpoints(self):
        """Test Flask application endpoints"""
        endpoints = [
            ("/", "text/html"),
            ("/clients", "text/html"),
            ("/properties", "text/html"),
            ("/transactions", "text/html"),
            ("/crpa_dashboard", "text/html"),
            ("/api/crpa/test_architecture", "application/json")
        ]
        
        for endpoint, expected_content_type in endpoints:
            response = requests.get(f"{self.base_url}{endpoint}", timeout=5)
            assert response.status_code == 200, f"{endpoint} returned {response.status_code}"
            
            content_type = response.headers.get('Content-Type', '')
            assert expected_content_type in content_type, \
                f"{endpoint} wrong content type: {content_type}"
                
        return True
        
    def test_static_assets(self):
        """Test static file serving"""
        response = requests.get(f"{self.base_url}/static/style.css", timeout=5)
        assert response.status_code == 200, "CSS file not accessible"
        assert 'text/css' in response.headers.get('Content-Type', ''), "Wrong CSS content type"
        
        return True
        
    def test_form_processing(self):
        """Test form generation capabilities"""
        # Test CRPA dashboard loads with jQuery
        response = requests.get(f"{self.base_url}/crpa_dashboard", timeout=5)
        assert response.status_code == 200, "CRPA dashboard failed"
        assert 'jquery' in response.text.lower(), "jQuery not loaded"
        assert 'bootstrap' in response.text.lower(), "Bootstrap not loaded"
        
        return True
        
    def test_ai_chatbot(self):
        """Test AI chatbot endpoint"""
        test_message = {"message": "Hello, this is a test"}
        
        response = requests.post(
            f"{self.base_url}/chat",
            json=test_message,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        assert response.status_code == 200, f"Chat endpoint failed: {response.status_code}"
        
        data = response.json()
        assert 'response' in data, "No response field in chat reply"
        assert len(data['response']) > 0, "Empty chat response"
        
        return True
        
    def test_data_validation(self):
        """Test form validation framework"""
        # Import and test validation framework
        sys.path.insert(0, '/app')
        from validation_framework import FormValidationFramework
        
        validator = FormValidationFramework()
        
        # Test email validation
        assert validator._validate_email("test@example.com")[0], "Valid email rejected"
        assert not validator._validate_email("invalid-email")[0], "Invalid email accepted"
        
        # Test phone validation
        assert validator._validate_phone("(555) 123-4567")[0], "Valid phone rejected"
        
        return True
        
    def test_crm_mapper(self):
        """Test CRM data mapping"""
        sys.path.insert(0, '/app/core_app')
        from crm_data_mapper import CrmDataMapper
        
        mapper = CrmDataMapper()
        
        # Test with dummy data
        test_data = {
            'client': {'first_name': 'John', 'last_name': 'Doe'},
            'property': {'address': '123 Main St', 'city': 'Testville'},
            'transaction': {'purchase_price': 500000}
        }
        
        mapped = mapper.map_to_crpa(test_data)
        assert 'buyer_name_1' in mapped, "Buyer name not mapped"
        assert mapped['buyer_name_1'] == 'John Doe', "Name mapping incorrect"
        
        return True
        
    def run_all_tests(self):
        """Run all integration tests"""
        self.log("Starting Docker Integration Tests", "INFO")
        self.log(f"Container: {os.environ.get('HOSTNAME', 'unknown')}", "INFO")
        self.log(f"Python: {sys.version.split()[0]}", "INFO")
        self.log(f"Working Directory: {os.getcwd()}", "INFO")
        
        # Run tests
        self.test("Environment Check", self.test_environment)
        self.test("Database Operations", self.test_database_operations)
        self.test("Flask Endpoints", self.test_flask_endpoints)
        self.test("Static Assets", self.test_static_assets)
        self.test("Form Processing", self.test_form_processing)
        self.test("AI Chatbot", self.test_ai_chatbot)
        self.test("Data Validation", self.test_data_validation)
        self.test("CRM Mapper", self.test_crm_mapper)
        
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
    tests = DockerIntegrationTests()
    tests.run_all_tests()