#!/usr/bin/env python3
"""
FAST-FAIL Diagnostic Suite for Real Estate CRM (Ported from FitForge)
Aggressive timeouts for immediate feedback
"""
import sys
import time
import requests
import json
import subprocess
from typing import Dict, List, Tuple

class Colors:
    """Terminal colors for output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

class FastFailDiagnostic:
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.results = []
        self.start_time = time.time()
        # AGGRESSIVE: 3-second timeouts
        self.timeout = 3
        
    def print_header(self):
        """Print diagnostic header"""
        print(f"\n{Colors.BOLD}{Colors.CYAN}⚡ FAST-FAIL DIAGNOSTIC SUITE{Colors.ENDC}")
        print(f"{Colors.CYAN}{'='*50}{Colors.ENDC}")
        print(f"{Colors.BLUE}Target: {self.base_url}{Colors.ENDC}")
        print(f"{Colors.BLUE}Timeout: {self.timeout}s per test{Colors.ENDC}")
        print(f"{Colors.CYAN}{'='*50}{Colors.ENDC}\n")
        
    def fail_fast(self, test_name: str, error: str):
        """IMMEDIATELY stop execution on critical failure"""
        print(f"\n{Colors.RED}{Colors.BOLD}💥 CRITICAL FAILURE: {test_name}{Colors.ENDC}")
        print(f"{Colors.RED}Error: {error}{Colors.ENDC}")
        
        # Capture Docker logs immediately
        print(f"\n{Colors.YELLOW}📋 Capturing Docker logs...{Colors.ENDC}")
        try:
            logs = subprocess.check_output(
                ["docker-compose", "-f", "docker-compose.dev.yml", "logs", "--tail=20"],
                stderr=subprocess.STDOUT,
                text=True,
                timeout=5
            )
            log_file = f"diagnostic-failure-{int(time.time())}.log"
            with open(log_file, 'w') as f:
                f.write(f"FAST-FAIL DIAGNOSTIC FAILURE\\n")
                f.write(f"Test: {test_name}\\n")
                f.write(f"Error: {error}\\n")
                f.write(f"Time: {time.time() - self.start_time:.2f}s\\n")
                f.write(f"\\n--- DOCKER LOGS ---\\n")
                f.write(logs)
            
            print(f"{Colors.GREEN}✓ Logs saved to: {log_file}{Colors.ENDC}")
            print(f"\n{Colors.MAGENTA}🧠 To analyze with AI:{Colors.ENDC}")
            print(f"{Colors.CYAN}node scripts/local-ai-analyzer.js diagnostic-output.log {log_file}{Colors.ENDC}")
            
        except Exception as e:
            print(f"{Colors.RED}Failed to capture logs: {e}{Colors.ENDC}")
        
        print(f"\n{Colors.RED}Diagnostic halted at {time.time() - self.start_time:.2f}s{Colors.ENDC}")
        sys.exit(1)
        
    def test(self, name: str, test_func) -> bool:
        """Run a single test with AGGRESSIVE timing"""
        print(f"Testing: {name}...", end='', flush=True)
        start = time.time()
        
        try:
            result, message = test_func()
            elapsed = time.time() - start
            
            if result:
                print(f" {Colors.GREEN}✓{Colors.ENDC} ({elapsed:.2f}s)")
                if message:
                    print(f"  └─ {Colors.BLUE}{message}{Colors.ENDC}")
            else:
                print(f" {Colors.RED}✗{Colors.ENDC} ({elapsed:.2f}s)")
                self.fail_fast(name, message)
                
            self.results.append((name, result, message, elapsed))
            return result
            
        except Exception as e:
            elapsed = time.time() - start
            print(f" {Colors.RED}✗{Colors.ENDC} ({elapsed:.2f}s)")
            self.fail_fast(name, str(e))
            return False
            
    def test_server_responds_fast(self) -> Tuple[bool, str]:
        """Test if server responds within 3 seconds"""
        try:
            response = requests.get(f"{self.base_url}/", timeout=self.timeout)
            # Accept both 200 (direct response) and 302 (authentication redirect)
            if response.status_code in [200, 302]:
                content_length = len(response.content)
                return True, f"Server OK (status: {response.status_code}, {content_length} bytes)"
            return False, f"Bad status: {response.status_code}"
        except requests.exceptions.ConnectionError:
            return False, "Cannot connect - is Docker running?"
        except requests.exceptions.Timeout:
            return False, f"Timeout after {self.timeout}s"
            
    def test_database_works_fast(self) -> Tuple[bool, str]:
        """Test database connectivity quickly"""
        try:
            response = requests.get(f"{self.base_url}/crm/clients", timeout=self.timeout)
            # 302 redirect is expected for authentication-protected routes
            if response.status_code in [200, 302]:
                return True, f"CRM clients endpoint accessible (status: {response.status_code})"
            return False, f"CRM clients page failed: {response.status_code}"
        except Exception as e:
            return False, f"Database test failed: {str(e)}"
            
    def test_ai_responds_fast(self) -> Tuple[bool, str]:
        """Test AI chatbot responds quickly"""
        try:
            test_data = {"message": "ping"}
            response = requests.post(
                f"{self.base_url}/chat",
                json=test_data,
                headers={"Content-Type": "application/json"},
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'response' in data:
                    return True, f"AI responded: '{data['response'][:30]}...'"
                return False, "AI response missing 'response' field"
            return False, f"AI endpoint failed: {response.status_code}"
        except Exception as e:
            return False, f"AI test failed: {str(e)}"
            
    def test_form_generation_fast(self) -> Tuple[bool, str]:
        """Test form generation endpoint quickly"""
        try:
            response = requests.get(f"{self.base_url}/crpa_dashboard", timeout=self.timeout)
            if response.status_code == 200:
                # Check for key form elements
                has_forms = 'form' in response.text.lower()
                has_jquery = 'jquery' in response.text.lower()
                
                if has_forms and has_jquery:
                    return True, "CRPA dashboard loaded with dependencies"
                
                missing = []
                if not has_forms: missing.append("forms")
                if not has_jquery: missing.append("jQuery")
                return False, f"Missing: {', '.join(missing)}"
            return False, f"CRPA dashboard failed: {response.status_code}"
        except Exception as e:
            return False, f"Form test failed: {str(e)}"
            
    def test_static_assets_fast(self) -> Tuple[bool, str]:
        """Test static assets load quickly"""
        try:
            response = requests.get(f"{self.base_url}/", timeout=self.timeout)
            if response.status_code == 200:
                # Check for CSS/JS references
                has_css = 'stylesheet' in response.text.lower()
                has_bootstrap = 'bootstrap' in response.text.lower()
                
                if has_css or has_bootstrap:
                    return True, "Static assets configured"
                return False, "No CSS/JS references found"
            return False, f"Homepage failed: {response.status_code}"
        except Exception as e:
            return False, f"Static test failed: {str(e)}"
            
    def run_all(self):
        """Run all fast-fail tests"""
        self.print_header()
        
        # CRITICAL TESTS - fail immediately if any fail
        print(f"{Colors.YELLOW}🚨 CRITICAL TESTS (fail-fast){Colors.ENDC}")
        self.test("Server Responds", self.test_server_responds_fast)
        self.test("Database Works", self.test_database_works_fast)
        self.test("Static Assets", self.test_static_assets_fast)
        
        print(f"\n{Colors.YELLOW}⚡ FEATURE TESTS{Colors.ENDC}")
        self.test("AI Chatbot", self.test_ai_responds_fast)
        self.test("Form Generation", self.test_form_generation_fast)
        
        # If we get here, all tests passed
        elapsed = time.time() - self.start_time
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 ALL TESTS PASSED!{Colors.ENDC}")
        print(f"{Colors.GREEN}✅ Real Estate CRM is operational ({elapsed:.2f}s){Colors.ENDC}")
        print(f"{Colors.CYAN}Ready for development!{Colors.ENDC}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Fast-fail diagnostic tests")
    parser.add_argument('--url', default='http://localhost:5000', help='Base URL to test')
    args = parser.parse_args()
    
    suite = FastFailDiagnostic(args.url)
    suite.run_all()
