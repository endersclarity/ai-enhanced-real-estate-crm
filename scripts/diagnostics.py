#!/usr/bin/env python3
"""
Tier 2: Fail-fast diagnostic suite for Real Estate CRM
Tests the ACTUAL working Docker environment
"""
import sys
import time
import requests
import json
from typing import Dict, List, Tuple

class Colors:
    """Terminal colors for output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

class DiagnosticSuite:
    def __init__(self, base_url: str = "http://localhost:5000", docker_mode: bool = False):
        self.base_url = base_url
        self.docker_mode = docker_mode
        self.results = []
        self.start_time = time.time()
        
    def print_header(self):
        """Print diagnostic header"""
        print(f"\n{Colors.BOLD}🔍 REAL ESTATE CRM - DIAGNOSTIC SUITE{Colors.ENDC}")
        print(f"{'='*50}")
        print(f"Target: {self.base_url}")
        print(f"Mode: {'Docker' if self.docker_mode else 'Local'}")
        print(f"{'='*50}\n")
        
    def test(self, name: str, test_func) -> bool:
        """Run a single test with timing and error handling"""
        print(f"Testing: {name}...", end='', flush=True)
        start = time.time()
        
        try:
            result, message = test_func()
            elapsed = time.time() - start
            
            if result:
                print(f" {Colors.GREEN}✓{Colors.ENDC} ({elapsed:.2f}s)")
                if message:
                    print(f"  └─ {message}")
            else:
                print(f" {Colors.RED}✗{Colors.ENDC} ({elapsed:.2f}s)")
                print(f"  └─ {Colors.RED}ERROR: {message}{Colors.ENDC}")
                self.fail_fast(name, message)
                
            self.results.append((name, result, message, elapsed))
            return result
            
        except Exception as e:
            elapsed = time.time() - start
            print(f" {Colors.RED}✗{Colors.ENDC} ({elapsed:.2f}s)")
            print(f"  └─ {Colors.RED}EXCEPTION: {str(e)}{Colors.ENDC}")
            self.fail_fast(name, str(e))
            return False
            
    def fail_fast(self, test_name: str, error: str):
        """Stop execution on critical failure"""
        print(f"\n{Colors.RED}{Colors.BOLD}💥 CRITICAL FAILURE in {test_name}{Colors.ENDC}")
        print(f"Error: {error}")
        print(f"\nDiagnostic suite halted. Fix this issue before proceeding.")
        print(f"Total time: {time.time() - self.start_time:.2f}s")
        sys.exit(1)
        
    def test_server_health(self) -> Tuple[bool, str]:
        """Test if server is responding"""
        try:
            response = requests.get(f"{self.base_url}/", timeout=5)
            if response.status_code == 200:
                return True, f"Server responded with {len(response.content)} bytes"
            return False, f"Server returned status {response.status_code}"
        except requests.exceptions.ConnectionError:
            return False, "Cannot connect to server"
        except requests.exceptions.Timeout:
            return False, "Server timeout"
            
    def test_static_assets(self) -> Tuple[bool, str]:
        """Test if static assets are accessible"""
        try:
            # Check if Bootstrap CSS loads (from CDN in this case)
            response = requests.get(f"{self.base_url}/", timeout=5)
            if 'bootstrap' in response.text.lower():
                return True, "Static assets configured correctly"
            return False, "Bootstrap CSS not found in HTML"
        except Exception as e:
            return False, str(e)
            
    def test_database_connectivity(self) -> Tuple[bool, str]:
        """Test database connection via API"""
        try:
            response = requests.get(f"{self.base_url}/api/crpa/transactions", timeout=5)
            data = response.json()
            
            if response.status_code == 200 and 'success' in data:
                count = data.get('count', 0)
                return True, f"Database connected, {count} transactions found"
            return False, f"API returned: {data}"
        except Exception as e:
            return False, f"Database API error: {str(e)}"
            
    def test_crpa_dashboard(self) -> Tuple[bool, str]:
        """Test CRPA dashboard loads"""
        try:
            response = requests.get(f"{self.base_url}/crpa_dashboard", timeout=5)
            if response.status_code == 200:
                # Check for jQuery which we fixed
                has_jquery = 'jquery' in response.text.lower()
                has_bootstrap = 'bootstrap' in response.text.lower()
                
                if has_jquery and has_bootstrap:
                    return True, "CRPA dashboard loads with all dependencies"
                else:
                    missing = []
                    if not has_jquery: missing.append("jQuery")
                    if not has_bootstrap: missing.append("Bootstrap")
                    return False, f"Missing dependencies: {', '.join(missing)}"
            return False, f"Dashboard returned status {response.status_code}"
        except Exception as e:
            return False, str(e)
            
    def test_ai_chatbot(self) -> Tuple[bool, str]:
        """Test AI chatbot endpoint"""
        try:
            test_message = {"message": "Hello, this is a diagnostic test"}
            response = requests.post(
                f"{self.base_url}/chat", 
                json=test_message,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'response' in data:
                    return True, f"AI responded: '{data['response'][:50]}...'"
                return False, "AI response missing 'response' field"
            return False, f"AI returned status {response.status_code}"
        except Exception as e:
            return False, f"AI integration error: {str(e)}"
            
    def test_client_api(self) -> Tuple[bool, str]:
        """Test client management API"""
        try:
            response = requests.get(f"{self.base_url}/clients", timeout=5)
            if response.status_code == 200:
                # Should return HTML page
                if 'client' in response.text.lower():
                    return True, "Client management page accessible"
            return False, f"Client page returned status {response.status_code}"
        except Exception as e:
            return False, str(e)
            
    def test_form_generation_ready(self) -> Tuple[bool, str]:
        """Test if form generation infrastructure is ready"""
        try:
            # Test the enhanced architecture endpoint
            response = requests.get(f"{self.base_url}/api/crpa/test_architecture", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    components = data.get('components', {})
                    return True, f"Form generation ready: {len(components)} components loaded"
                return False, data.get('error', 'Unknown error')
            return False, f"Architecture test returned {response.status_code}"
        except Exception as e:
            return False, f"Form generation not ready: {str(e)}"
            
    def print_summary(self):
        """Print test summary"""
        print(f"\n{Colors.BOLD}📊 DIAGNOSTIC SUMMARY{Colors.ENDC}")
        print(f"{'='*50}")
        
        passed = sum(1 for _, result, _, _ in self.results if result)
        total = len(self.results)
        
        for name, result, message, elapsed in self.results:
            status = f"{Colors.GREEN}PASS{Colors.ENDC}" if result else f"{Colors.RED}FAIL{Colors.ENDC}"
            print(f"{status} | {name} ({elapsed:.2f}s)")
            
        print(f"{'='*50}")
        print(f"Total: {passed}/{total} tests passed")
        print(f"Time: {time.time() - self.start_time:.2f}s")
        
        if passed == total:
            print(f"\n{Colors.GREEN}{Colors.BOLD}✅ ALL DIAGNOSTICS PASSED!{Colors.ENDC}")
            print("System is ready for development.")
        else:
            print(f"\n{Colors.RED}{Colors.BOLD}❌ DIAGNOSTICS FAILED{Colors.ENDC}")
            print("Fix the issues above before proceeding.")
            
    def run_all(self):
        """Run all diagnostic tests"""
        self.print_header()
        
        # Critical tests (fail-fast)
        self.test("Server Health", self.test_server_health)
        self.test("Static Assets", self.test_static_assets)
        self.test("Database Connectivity", self.test_database_connectivity)
        
        # Feature tests
        self.test("CRPA Dashboard", self.test_crpa_dashboard)
        self.test("AI Chatbot Integration", self.test_ai_chatbot)
        self.test("Client Management", self.test_client_api)
        self.test("Form Generation Ready", self.test_form_generation_ready)
        
        self.print_summary()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run diagnostic tests for Real Estate CRM")
    parser.add_argument('--url', default='http://localhost:5000', help='Base URL to test')
    parser.add_argument('--docker', action='store_true', help='Running in Docker mode')
    args = parser.parse_args()
    
    suite = DiagnosticSuite(args.url, args.docker)
    suite.run_all()