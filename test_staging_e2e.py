#!/usr/bin/env python3
"""
End-to-End Test Suite for Real Estate CRM (Staging)
READ-ONLY tests that verify functionality without modifying data
"""

import requests
import json
import time
from datetime import datetime
from colorama import init, Fore, Style
import sys

init(autoreset=True)

# Configuration
STAGING_URL = "http://localhost:5002"
TIMEOUT = 10
TEST_RESULTS = []

class TestResult:
    def __init__(self, test_name, passed, message="", duration=0):
        self.test_name = test_name
        self.passed = passed
        self.message = message
        self.duration = duration

def print_test_header(category):
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"{Fore.CYAN}Testing: {category}")
    print(f"{Fore.CYAN}{'='*60}")

def test_endpoint(name, endpoint, expected_status=200, check_content=None):
    """Test a single endpoint"""
    start_time = time.time()
    try:
        response = requests.get(f"{STAGING_URL}{endpoint}", timeout=TIMEOUT)
        duration = time.time() - start_time
        
        if response.status_code == expected_status:
            if check_content:
                for content in check_content:
                    if content not in response.text:
                        result = TestResult(name, False, f"Missing expected content: {content}", duration)
                        print_result(result)
                        return result
            
            result = TestResult(name, True, f"Status: {response.status_code}", duration)
        else:
            result = TestResult(name, False, f"Expected {expected_status}, got {response.status_code}", duration)
        
    except Exception as e:
        duration = time.time() - start_time
        result = TestResult(name, False, f"Error: {str(e)}", duration)
    
    print_result(result)
    TEST_RESULTS.append(result)
    return result

def test_api_endpoint(name, endpoint, expected_keys=None):
    """Test API endpoints that return JSON"""
    start_time = time.time()
    try:
        response = requests.get(f"{STAGING_URL}{endpoint}", timeout=TIMEOUT)
        duration = time.time() - start_time
        
        if response.status_code == 200:
            try:
                data = response.json()
                if expected_keys:
                    missing_keys = [key for key in expected_keys if key not in data]
                    if missing_keys:
                        result = TestResult(name, False, f"Missing keys: {missing_keys}", duration)
                    else:
                        result = TestResult(name, True, "All expected keys present", duration)
                else:
                    result = TestResult(name, True, f"Valid JSON response", duration)
            except json.JSONDecodeError:
                result = TestResult(name, False, "Invalid JSON response", duration)
        else:
            result = TestResult(name, False, f"Status: {response.status_code}", duration)
            
    except Exception as e:
        duration = time.time() - start_time
        result = TestResult(name, False, f"Error: {str(e)}", duration)
    
    print_result(result)
    TEST_RESULTS.append(result)
    return result

def test_static_assets(name, asset_path, content_type=None):
    """Test static asset availability"""
    start_time = time.time()
    try:
        response = requests.get(f"{STAGING_URL}{asset_path}", timeout=TIMEOUT)
        duration = time.time() - start_time
        
        if response.status_code == 200:
            if content_type and content_type not in response.headers.get('Content-Type', ''):
                result = TestResult(name, False, f"Wrong content type: {response.headers.get('Content-Type')}", duration)
            else:
                result = TestResult(name, True, f"Asset loaded successfully", duration)
        else:
            result = TestResult(name, False, f"Status: {response.status_code}", duration)
            
    except Exception as e:
        duration = time.time() - start_time
        result = TestResult(name, False, f"Error: {str(e)}", duration)
    
    print_result(result)
    TEST_RESULTS.append(result)
    return result

def print_result(result):
    """Print individual test result"""
    if result.passed:
        status = f"{Fore.GREEN}✓ PASS"
    else:
        status = f"{Fore.RED}✗ FAIL"
    
    print(f"{status} {Style.RESET_ALL}{result.test_name:50} ({result.duration:.2f}s)")
    if not result.passed and result.message:
        print(f"  {Fore.YELLOW}→ {result.message}")

def run_tests():
    """Run all tests"""
    print(f"\n{Fore.MAGENTA}Real Estate CRM - Staging E2E Test Suite")
    print(f"{Fore.MAGENTA}Target: {STAGING_URL}")
    print(f"{Fore.MAGENTA}Mode: READ-ONLY (No data modifications)")
    print(f"{Fore.MAGENTA}Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test 1: Core Pages
    print_test_header("Core Pages")
    test_endpoint("Homepage", "/", check_content=["Dashboard", "Narissa Realty"])
    test_endpoint("Dashboard", "/dashboard", check_content=["Dashboard"])
    test_endpoint("Clients List", "/clients", check_content=["Clients"])
    test_endpoint("Properties List", "/properties", check_content=["Properties"])
    test_endpoint("Transactions List", "/transactions", check_content=["Transactions"])
    
    # Test 2: Form Pages (GET only)
    print_test_header("Form Pages (Read Access)")
    test_endpoint("New Client Form", "/clients/new", check_content=["Add New Client"])
    test_endpoint("Quick Add Client Form", "/clients/quick-add", check_content=["Quick Add Client"])
    test_endpoint("New Property Form", "/properties/new", check_content=["Add New Property"])
    test_endpoint("New Transaction Form", "/transactions/new", check_content=["Create New Transaction"])
    
    # Test 3: API Endpoints
    print_test_header("API Endpoints")
    test_api_endpoint("API Stats", "/api/stats", expected_keys=["clients", "properties", "transactions"])
    test_api_endpoint("API Health", "/api/health", expected_keys=["status", "timestamp"])
    test_endpoint("AI Chat Endpoint", "/api/ai/chat", expected_status=405)  # GET not allowed
    
    # Test 4: Static Assets
    print_test_header("Static Assets")
    test_static_assets("Main CSS", "/static/style.css", content_type="text/css")
    test_static_assets("Main JS", "/static/script.js", content_type="application/javascript")
    
    # Test 5: Special Features
    print_test_header("Special Features")
    test_endpoint("CRPA Dashboard", "/crpa_dashboard", check_content=["CRPA"])
    test_endpoint("AI Debug Chat", "/debug_chat", check_content=["AI", "Chat"])
    
    # Test 6: Error Handling
    print_test_header("Error Handling")
    test_endpoint("404 Page", "/this-page-does-not-exist", expected_status=404)
    test_endpoint("Invalid Client ID", "/clients/99999", expected_status=[200, 302, 404])  # Might redirect or 404
    
    # Test 7: Security Headers
    print_test_header("Security & Performance")
    start_time = time.time()
    try:
        response = requests.get(f"{STAGING_URL}/", timeout=TIMEOUT)
        duration = time.time() - start_time
        
        # Check for security headers
        headers_to_check = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": ["DENY", "SAMEORIGIN"],
        }
        
        security_passed = True
        security_messages = []
        
        for header, expected_values in headers_to_check.items():
            if isinstance(expected_values, list):
                if header not in response.headers or response.headers[header] not in expected_values:
                    security_passed = False
                    security_messages.append(f"Missing/incorrect {header}")
            else:
                if header not in response.headers or response.headers[header] != expected_values:
                    security_passed = False
                    security_messages.append(f"Missing/incorrect {header}")
        
        if security_passed:
            result = TestResult("Security Headers", True, "All security headers present", duration)
        else:
            result = TestResult("Security Headers", False, "; ".join(security_messages), duration)
        
        print_result(result)
        TEST_RESULTS.append(result)
        
    except Exception as e:
        result = TestResult("Security Headers", False, f"Error: {str(e)}", 0)
        print_result(result)
        TEST_RESULTS.append(result)
    
    # Test 8: Database Connectivity (via stats API)
    print_test_header("Database Connectivity")
    start_time = time.time()
    try:
        response = requests.get(f"{STAGING_URL}/api/stats", timeout=TIMEOUT)
        duration = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data.get('clients'), int) and isinstance(data.get('properties'), int):
                result = TestResult("Database Connection", True, "Database responding correctly", duration)
            else:
                result = TestResult("Database Connection", False, "Invalid data format", duration)
        else:
            result = TestResult("Database Connection", False, f"Status: {response.status_code}", duration)
            
    except Exception as e:
        duration = time.time() - start_time
        result = TestResult("Database Connection", False, f"Error: {str(e)}", duration)
    
    print_result(result)
    TEST_RESULTS.append(result)
    
    # Summary
    print_summary()

def print_summary():
    """Print test summary"""
    total_tests = len(TEST_RESULTS)
    passed_tests = sum(1 for r in TEST_RESULTS if r.passed)
    failed_tests = total_tests - passed_tests
    total_duration = sum(r.duration for r in TEST_RESULTS)
    
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"{Fore.CYAN}Test Summary")
    print(f"{Fore.CYAN}{'='*60}")
    
    print(f"\nTotal Tests: {total_tests}")
    print(f"{Fore.GREEN}Passed: {passed_tests}")
    print(f"{Fore.RED}Failed: {failed_tests}")
    print(f"Total Duration: {total_duration:.2f}s")
    
    if failed_tests > 0:
        print(f"\n{Fore.RED}Failed Tests:")
        for result in TEST_RESULTS:
            if not result.passed:
                print(f"  - {result.test_name}: {result.message}")
    
    # Exit code
    if failed_tests > 0:
        print(f"\n{Fore.RED}❌ TEST SUITE FAILED")
        sys.exit(1)
    else:
        print(f"\n{Fore.GREEN}✅ ALL TESTS PASSED!")
        sys.exit(0)

if __name__ == "__main__":
    run_tests()