#!/usr/bin/env python3
"""
Test script for Domain and SSL Configuration
Validates domain setup, SSL certificates, and security configuration
"""

import requests
import ssl
import socket
import subprocess
import json
import logging
from datetime import datetime
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DomainSSLTester:
    """Comprehensive testing for domain and SSL configuration"""
    
    def __init__(self, domain="narissarealty.com"):
        self.domain = domain
        self.test_results = {}
    
    def test_dns_resolution(self):
        """Test DNS resolution for the domain"""
        try:
            ip = socket.gethostbyname(self.domain)
            self.test_results["dns_resolution"] = {
                "status": "pass",
                "ip_address": ip,
                "message": f"Domain resolves to {ip}"
            }
            logger.info(f"DNS resolution successful: {self.domain} -> {ip}")
            return True
        except socket.gaierror as e:
            self.test_results["dns_resolution"] = {
                "status": "fail",
                "error": str(e),
                "message": "DNS resolution failed"
            }
            logger.error(f"DNS resolution failed: {e}")
            return False
    
    def test_http_redirect(self):
        """Test HTTP to HTTPS redirect"""
        try:
            response = requests.get(f"http://{self.domain}", 
                                  allow_redirects=False, 
                                  timeout=10)
            
            if response.status_code in [301, 302]:
                location = response.headers.get('Location', '')
                if location.startswith('https://'):
                    self.test_results["http_redirect"] = {
                        "status": "pass",
                        "redirect_code": response.status_code,
                        "location": location,
                        "message": "HTTP redirects to HTTPS"
                    }
                    logger.info("HTTP to HTTPS redirect working")
                    return True
            
            self.test_results["http_redirect"] = {
                "status": "fail",
                "status_code": response.status_code,
                "message": "HTTP does not redirect to HTTPS"
            }
            logger.error("HTTP to HTTPS redirect not working")
            return False
            
        except Exception as e:
            self.test_results["http_redirect"] = {
                "status": "error",
                "error": str(e),
                "message": "Failed to test HTTP redirect"
            }
            logger.error(f"HTTP redirect test failed: {e}")
            return False
    
    def test_ssl_certificate(self):
        """Test SSL certificate validity"""
        try:
            context = ssl.create_default_context()
            with socket.create_connection((self.domain, 443), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=self.domain) as ssock:
                    cert = ssock.getpeercert()
                    
                    # Extract certificate information
                    subject = dict(x[0] for x in cert['subject'])
                    issuer = dict(x[0] for x in cert['issuer'])
                    
                    self.test_results["ssl_certificate"] = {
                        "status": "pass",
                        "subject": subject.get('commonName', ''),
                        "issuer": issuer.get('organizationName', ''),
                        "not_before": cert['notBefore'],
                        "not_after": cert['notAfter'],
                        "version": cert['version'],
                        "serial_number": cert['serialNumber'],
                        "message": "SSL certificate is valid"
                    }
                    logger.info("SSL certificate is valid")
                    return True
                    
        except Exception as e:
            self.test_results["ssl_certificate"] = {
                "status": "fail",
                "error": str(e),
                "message": "SSL certificate validation failed"
            }
            logger.error(f"SSL certificate test failed: {e}")
            return False
    
    def test_security_headers(self):
        """Test security headers implementation"""
        try:
            response = requests.get(f"https://{self.domain}", timeout=10)
            headers = response.headers
            
            # Expected security headers
            expected_headers = {
                'X-Frame-Options': 'DENY',
                'X-Content-Type-Options': 'nosniff',
                'X-XSS-Protection': '1; mode=block',
                'Strict-Transport-Security': 'max-age'  # Partial match
            }
            
            header_results = {}
            all_passed = True
            
            for header, expected_value in expected_headers.items():
                if header in headers:
                    actual_value = headers[header]
                    if expected_value in actual_value or expected_value == actual_value:
                        header_results[header] = {
                            "status": "pass",
                            "value": actual_value
                        }
                    else:
                        header_results[header] = {
                            "status": "fail",
                            "value": actual_value,
                            "expected": expected_value
                        }
                        all_passed = False
                else:
                    header_results[header] = {
                        "status": "missing",
                        "expected": expected_value
                    }
                    all_passed = False
            
            self.test_results["security_headers"] = {
                "status": "pass" if all_passed else "partial",
                "headers": header_results,
                "message": "Security headers checked"
            }
            
            if all_passed:
                logger.info("All security headers present and correct")
            else:
                logger.warning("Some security headers missing or incorrect")
            
            return all_passed
            
        except Exception as e:
            self.test_results["security_headers"] = {
                "status": "error",
                "error": str(e),
                "message": "Failed to test security headers"
            }
            logger.error(f"Security headers test failed: {e}")
            return False
    
    def test_ssl_configuration(self):
        """Test SSL configuration strength"""
        try:
            # Use openssl command to test SSL configuration
            cmd = [
                "openssl", "s_client", 
                "-connect", f"{self.domain}:443",
                "-servername", self.domain,
                "-cipher", "HIGH:!aNULL:!eNULL:!EXPORT:!DES:!RC4:!MD5:!PSK:!SRP:!CAMELLIA"
            ]
            
            result = subprocess.run(cmd, input="", text=True, capture_output=True, timeout=10)
            
            if "Verify return code: 0 (ok)" in result.stdout:
                # Extract SSL information
                ssl_info = {}
                for line in result.stdout.split('\n'):
                    if 'Protocol' in line and 'TLS' in line:
                        ssl_info['protocol'] = line.strip()
                    elif 'Cipher' in line and ':' in line:
                        ssl_info['cipher'] = line.strip()
                
                self.test_results["ssl_configuration"] = {
                    "status": "pass",
                    "ssl_info": ssl_info,
                    "message": "SSL configuration is secure"
                }
                logger.info("SSL configuration test passed")
                return True
            else:
                self.test_results["ssl_configuration"] = {
                    "status": "fail",
                    "output": result.stdout[-500:],  # Last 500 chars
                    "message": "SSL configuration issues detected"
                }
                logger.error("SSL configuration test failed")
                return False
                
        except Exception as e:
            self.test_results["ssl_configuration"] = {
                "status": "error",
                "error": str(e),
                "message": "Failed to test SSL configuration"
            }
            logger.error(f"SSL configuration test failed: {e}")
            return False
    
    def test_certificate_auto_renewal(self):
        """Test certificate auto-renewal configuration"""
        try:
            # Check if certbot is installed
            result = subprocess.run(["which", "certbot"], capture_output=True, text=True)
            if result.returncode != 0:
                self.test_results["auto_renewal"] = {
                    "status": "fail",
                    "message": "Certbot not installed"
                }
                return False
            
            # Check crontab for renewal entry
            result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
            if "certbot renew" in result.stdout:
                self.test_results["auto_renewal"] = {
                    "status": "pass",
                    "message": "Certificate auto-renewal configured"
                }
                logger.info("Certificate auto-renewal is configured")
                return True
            else:
                self.test_results["auto_renewal"] = {
                    "status": "fail",
                    "message": "Certificate auto-renewal not configured"
                }
                logger.error("Certificate auto-renewal not configured")
                return False
                
        except Exception as e:
            self.test_results["auto_renewal"] = {
                "status": "error",
                "error": str(e),
                "message": "Failed to test auto-renewal configuration"
            }
            logger.error(f"Auto-renewal test failed: {e}")
            return False
    
    def test_application_accessibility(self):
        """Test application accessibility through HTTPS"""
        try:
            # Test main application
            response = requests.get(f"https://{self.domain}", timeout=15)
            
            if response.status_code == 200:
                self.test_results["application_access"] = {
                    "status": "pass",
                    "status_code": response.status_code,
                    "response_time": response.elapsed.total_seconds(),
                    "message": "Application accessible via HTTPS"
                }
                logger.info("Application is accessible via HTTPS")
                
                # Test health endpoint
                health_response = requests.get(f"https://{self.domain}/health", timeout=10)
                self.test_results["health_endpoint"] = {
                    "status": "pass" if health_response.status_code == 200 else "fail",
                    "status_code": health_response.status_code,
                    "message": "Health endpoint tested"
                }
                
                return True
            else:
                self.test_results["application_access"] = {
                    "status": "fail",
                    "status_code": response.status_code,
                    "message": f"Application returned status {response.status_code}"
                }
                logger.error(f"Application access failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.test_results["application_access"] = {
                "status": "error",
                "error": str(e),
                "message": "Failed to access application"
            }
            logger.error(f"Application accessibility test failed: {e}")
            return False
    
    def run_all_tests(self):
        """Run all domain and SSL tests"""
        logger.info(f"Starting comprehensive domain and SSL tests for {self.domain}")
        
        tests = [
            ("DNS Resolution", self.test_dns_resolution),
            ("HTTP Redirect", self.test_http_redirect),
            ("SSL Certificate", self.test_ssl_certificate),
            ("Security Headers", self.test_security_headers),
            ("SSL Configuration", self.test_ssl_configuration),
            ("Auto Renewal", self.test_certificate_auto_renewal),
            ("Application Access", self.test_application_accessibility)
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
            "domain": self.domain,
            "test_date": datetime.now().isoformat(),
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "success_rate": success_rate,
            "overall_status": "pass" if success_rate >= 85 else "fail",
            "detailed_results": self.test_results
        }
        
        # Save results
        with open("deployment/domain_ssl_test_results.json", "w") as f:
            json.dump(summary, f, indent=2)
        
        logger.info(f"Test Summary: {passed_tests}/{total_tests} tests passed ({success_rate:.1f}%)")
        
        return summary

def main():
    """Main execution function"""
    import sys
    domain = sys.argv[1] if len(sys.argv) > 1 else "narissarealty.com"
    
    tester = DomainSSLTester(domain)
    results = tester.run_all_tests()
    
    if results["overall_status"] == "pass":
        print(f"✅ Domain and SSL configuration tests PASSED for {domain}")
        sys.exit(0)
    else:
        print(f"❌ Domain and SSL configuration tests FAILED for {domain}")
        sys.exit(1)

if __name__ == "__main__":
    main()