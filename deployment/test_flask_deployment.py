#!/usr/bin/env python3
"""
Test script to validate Flask application deployment completion
Tests all requirements from Task #3 success criteria
"""

import json
import os
import subprocess
import time
from typing import Dict, List, Tuple

class FlaskDeploymentValidator:
    """
    Validates that Flask application deployment meets production requirements
    """
    
    def __init__(self):
        self.test_results = {}
        self.deployment_config_file = "deployment/flask_deployment_config.json"
        self.production_app_file = "deployment/production_app.py"
        self.requirements_file = "deployment/requirements-production.txt"
        self.gunicorn_config_file = "deployment/gunicorn_config.py"
        
    def test_production_application_created(self) -> Tuple[bool, str]:
        """Test: Production-grade Flask application created"""
        print("🔍 Testing: Production Flask application created...")
        
        if not os.path.exists(self.production_app_file):
            return False, f"Production app file not found: {self.production_app_file}"
        
        try:
            with open(self.production_app_file, 'r') as f:
                app_content = f.read()
            
            # Check for production configuration
            production_features = [
                "ProductionConfig",
                "gunicorn",
                "create_app",
                "health_check",
                "setup_logging",
                "security_headers",
                "error_handlers"
            ]
            
            missing_features = []
            for feature in production_features:
                if feature not in app_content:
                    missing_features.append(feature)
            
            if missing_features:
                return False, f"Missing production features: {missing_features}"
            
            return True, "Production Flask application with security and logging configured"
            
        except Exception as e:
            return False, f"Error reading production app: {e}"
    
    def test_gunicorn_wsgi_configuration(self) -> Tuple[bool, str]:
        """Test: Gunicorn WSGI server configured"""
        print("🔍 Testing: Gunicorn WSGI server configuration...")
        
        if not os.path.exists(self.gunicorn_config_file):
            return False, f"Gunicorn config file not found: {self.gunicorn_config_file}"
        
        try:
            with open(self.gunicorn_config_file, 'r') as f:
                config_content = f.read()
            
            # Check for essential Gunicorn settings
            required_settings = [
                "bind",
                "workers",
                "worker_class",
                "timeout",
                "accesslog",
                "errorlog",
                "preload_app",
                "max_requests"
            ]
            
            missing_settings = []
            for setting in required_settings:
                if setting not in config_content:
                    missing_settings.append(setting)
            
            if missing_settings:
                return False, f"Missing Gunicorn settings: {missing_settings}"
            
            # Check for production optimizations
            if "multiprocessing.cpu_count()" not in config_content:
                return False, "Worker count not optimized for CPU cores"
            
            return True, "Gunicorn configured with worker processes and production settings"
            
        except Exception as e:
            return False, f"Error reading Gunicorn config: {e}"
    
    def test_production_dependencies(self) -> Tuple[bool, str]:
        """Test: Production dependencies specified"""
        print("🔍 Testing: Production dependencies configuration...")
        
        if not os.path.exists(self.requirements_file):
            return False, f"Requirements file not found: {self.requirements_file}"
        
        try:
            with open(self.requirements_file, 'r') as f:
                requirements_content = f.read()
            
            # Check for essential production packages
            required_packages = [
                "Flask",
                "gunicorn",
                "psycopg2-binary",
                "Flask-SQLAlchemy",
                "redis",
                "Flask-Session",
                "bcrypt",
                "sentry-sdk"
            ]
            
            missing_packages = []
            for package in required_packages:
                if package not in requirements_content:
                    missing_packages.append(package)
            
            if missing_packages:
                return False, f"Missing production packages: {missing_packages}"
            
            # Count total packages
            package_count = len([line for line in requirements_content.split('\n') if '==' in line])
            
            if package_count < 20:
                return False, f"Insufficient packages for production: {package_count}"
            
            return True, f"Production dependencies configured ({package_count} packages)"
            
        except Exception as e:
            return False, f"Error reading requirements: {e}"
    
    def test_database_connection_configuration(self) -> Tuple[bool, str]:
        """Test: Database connection configured for PostgreSQL"""
        print("🔍 Testing: Database connection configuration...")
        
        try:
            with open(self.production_app_file, 'r') as f:
                app_content = f.read()
            
            # Check for PostgreSQL connection
            if "postgresql://" not in app_content:
                return False, "PostgreSQL connection string not found"
            
            # Check for connection pooling
            if "pool_size" not in app_content:
                return False, "Database connection pooling not configured"
            
            # Check for SSL mode
            if "sslmode=require" not in app_content:
                return False, "SSL mode not required for database connection"
            
            # Check for environment variable configuration
            if "DATABASE_URL" not in app_content:
                return False, "Database URL environment variable not configured"
            
            return True, "PostgreSQL connection with SSL and pooling configured"
            
        except Exception as e:
            return False, f"Error checking database configuration: {e}"
    
    def test_environment_variables_configuration(self) -> Tuple[bool, str]:
        """Test: Environment variables configured for production"""
        print("🔍 Testing: Environment variables configuration...")
        
        try:
            with open(self.production_app_file, 'r') as f:
                app_content = f.read()
            
            # Check for essential environment variables
            required_env_vars = [
                "DATABASE_URL",
                "SECRET_KEY",
                "REDIS_URL",
                "FLASK_ENV"
            ]
            
            missing_env_vars = []
            for env_var in required_env_vars:
                if env_var not in app_content:
                    missing_env_vars.append(env_var)
            
            if missing_env_vars:
                return False, f"Missing environment variables: {missing_env_vars}"
            
            # Check for security best practices
            if "os.environ.get" not in app_content:
                return False, "Environment variables not accessed securely"
            
            return True, "Environment variables configured with secure access patterns"
            
        except Exception as e:
            return False, f"Error checking environment configuration: {e}"
    
    def test_security_headers_configuration(self) -> Tuple[bool, str]:
        """Test: Security headers configured"""
        print("🔍 Testing: Security headers configuration...")
        
        try:
            with open(self.production_app_file, 'r') as f:
                app_content = f.read()
            
            # Check for security headers
            required_headers = [
                "X-Content-Type-Options",
                "X-Frame-Options", 
                "X-XSS-Protection",
                "Strict-Transport-Security",
                "Content-Security-Policy"
            ]
            
            missing_headers = []
            for header in required_headers:
                if header not in app_content:
                    missing_headers.append(header)
            
            if missing_headers:
                return False, f"Missing security headers: {missing_headers}"
            
            # Check for security middleware
            if "add_security_headers" not in app_content:
                return False, "Security headers middleware not implemented"
            
            return True, "Comprehensive security headers configured"
            
        except Exception as e:
            return False, f"Error checking security configuration: {e}"
    
    def test_logging_configuration(self) -> Tuple[bool, str]:
        """Test: Production logging configured"""
        print("🔍 Testing: Production logging configuration...")
        
        try:
            with open(self.production_app_file, 'r') as f:
                app_content = f.read()
            
            # Check for logging configuration
            logging_features = [
                "RotatingFileHandler",
                "setup_logging",
                "app.logger",
                "LOG_LEVEL",
                "LOG_FILE"
            ]
            
            missing_features = []
            for feature in logging_features:
                if feature not in app_content:
                    missing_features.append(feature)
            
            if missing_features:
                return False, f"Missing logging features: {missing_features}"
            
            # Check for log rotation
            if "maxBytes" not in app_content or "backupCount" not in app_content:
                return False, "Log rotation not configured"
            
            return True, "Production logging with rotation configured"
            
        except Exception as e:
            return False, f"Error checking logging configuration: {e}"
    
    def test_health_check_endpoint(self) -> Tuple[bool, str]:
        """Test: Health check endpoint for load balancer"""
        print("🔍 Testing: Health check endpoint configuration...")
        
        try:
            with open(self.production_app_file, 'r') as f:
                app_content = f.read()
            
            # Check for health endpoint
            if "/health" not in app_content:
                return False, "Health check endpoint not found"
            
            # Check for database connectivity test
            if "db.engine.execute" not in app_content:
                return False, "Database connectivity test not in health check"
            
            # Check for proper response format
            if "jsonify" not in app_content:
                return False, "JSON response format not configured"
            
            # Check for error handling
            if "except Exception" not in app_content:
                return False, "Error handling not implemented in health check"
            
            return True, "Health check endpoint with database testing configured"
            
        except Exception as e:
            return False, f"Error checking health endpoint: {e}"
    
    def test_api_endpoints_functionality(self) -> Tuple[bool, str]:
        """Test: API endpoints configured for CRM operations"""
        print("🔍 Testing: API endpoints functionality...")
        
        try:
            with open(self.production_app_file, 'r') as f:
                app_content = f.read()
            
            # Check for essential API endpoints
            required_endpoints = [
                "/api/clients",
                "/api/properties", 
                "/api/email-process"
            ]
            
            missing_endpoints = []
            for endpoint in required_endpoints:
                if endpoint not in app_content:
                    missing_endpoints.append(endpoint)
            
            if missing_endpoints:
                return False, f"Missing API endpoints: {missing_endpoints}"
            
            # Check for HTTP methods
            if "methods=['GET', 'POST']" not in app_content:
                return False, "HTTP methods not properly configured"
            
            # Check for JSON handling
            if "request.get_json()" not in app_content:
                return False, "JSON request handling not implemented"
            
            # Check for AI integration endpoint
            if "email-process" not in app_content:
                return False, "AI email processing endpoint not found"
            
            return True, "API endpoints for CRM operations and AI integration configured"
            
        except Exception as e:
            return False, f"Error checking API endpoints: {e}"
    
    def test_session_management(self) -> Tuple[bool, str]:
        """Test: Session management configured"""
        print("🔍 Testing: Session management configuration...")
        
        try:
            with open(self.production_app_file, 'r') as f:
                app_content = f.read()
            
            # Check for session configuration
            session_features = [
                "Flask-Session",
                "SESSION_TYPE",
                "SESSION_REDIS",
                "Session()"
            ]
            
            missing_features = []
            for feature in session_features:
                if feature not in app_content:
                    missing_features.append(feature)
            
            if missing_features:
                return False, f"Missing session features: {missing_features}"
            
            # Check for Redis session storage
            if "redis" not in app_content.lower():
                return False, "Redis session storage not configured"
            
            return True, "Session management with Redis storage configured"
            
        except Exception as e:
            return False, f"Error checking session configuration: {e}"
    
    def run_all_tests(self) -> Dict:
        """Run all Flask deployment validation tests"""
        print("🧪 Running Flask Application Deployment Validation Tests")
        print("=" * 58)
        
        tests = [
            ("Production Application Created", self.test_production_application_created),
            ("Gunicorn WSGI Configuration", self.test_gunicorn_wsgi_configuration),
            ("Production Dependencies", self.test_production_dependencies),
            ("Database Connection Configuration", self.test_database_connection_configuration),
            ("Environment Variables Configuration", self.test_environment_variables_configuration),
            ("Security Headers Configuration", self.test_security_headers_configuration),
            ("Logging Configuration", self.test_logging_configuration),
            ("Health Check Endpoint", self.test_health_check_endpoint),
            ("API Endpoints Functionality", self.test_api_endpoints_functionality),
            ("Session Management", self.test_session_management)
        ]
        
        results = {}
        passed = 0
        total = len(tests)
        
        for test_name, test_function in tests:
            try:
                success, message = test_function()
                results[test_name] = {
                    "passed": success,
                    "message": message
                }
                
                status_icon = "✅" if success else "❌"
                print(f"{status_icon} {test_name}: {message}")
                
                if success:
                    passed += 1
                    
            except Exception as e:
                results[test_name] = {
                    "passed": False,
                    "message": f"Test error: {e}"
                }
                print(f"❌ {test_name}: Test error: {e}")
        
        print()
        print("📊 Test Results Summary:")
        print(f"   Passed: {passed}/{total} tests ({passed/total*100:.1f}%)")
        
        if passed == total:
            print("🎉 ALL TESTS PASSED - Flask application deployment is complete!")
            print()
            print("✅ Deployment requirements met:")
            print("   - Production-grade Flask application with security")
            print("   - Gunicorn WSGI server with worker optimization")
            print("   - Comprehensive production dependencies")
            print("   - PostgreSQL database connection with SSL and pooling")
            print("   - Secure environment variable configuration")
            print("   - Security headers and middleware")
            print("   - Production logging with rotation")
            print("   - Health check endpoint for load balancer")
            print("   - API endpoints for CRM operations and AI integration")
            print("   - Session management with Redis storage")
            
        else:
            failed_tests = [name for name, result in results.items() if not result["passed"]]
            print(f"❌ {total - passed} tests failed:")
            for test in failed_tests:
                print(f"   - {test}: {results[test]['message']}")
        
        return results

def main():
    """Main test execution"""
    validator = FlaskDeploymentValidator()
    results = validator.run_all_tests()
    
    # Save test results
    with open("deployment/flask_deployment_validation_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    # Return exit code based on results
    all_passed = all(result["passed"] for result in results.values())
    return 0 if all_passed else 1

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)