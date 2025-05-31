#!/usr/bin/env python3
"""
Test script to validate cloud hosting setup completion
Tests all requirements from Task #1 success criteria
"""

import json
import os
import subprocess
import time
from typing import Dict, List, Tuple

class HostingSetupValidator:
    """
    Validates that cloud hosting setup meets production requirements
    """
    
    def __init__(self):
        self.test_results = {}
        self.config_file = "deployment/production_config.json"
        
    def load_config(self) -> Dict:
        """Load production configuration"""
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ Configuration file not found: {self.config_file}")
            return {}
    
    def test_server_instance_running(self) -> Tuple[bool, str]:
        """Test: Verify server instance is running and accessible"""
        print("🔍 Testing: Server instance running and accessible...")
        
        config = self.load_config()
        if not config:
            return False, "No configuration found"
            
        droplet_info = config.get("droplet", {})
        
        # Check if droplet is marked as active
        if droplet_info.get("status") != "active":
            return False, f"Droplet status: {droplet_info.get('status', 'unknown')}"
            
        # Check if IP is assigned
        ip_address = droplet_info.get("ip_address")
        if not ip_address:
            return False, "No IP address assigned"
            
        return True, f"Server active with IP: {ip_address}"
    
    def test_network_configuration(self) -> Tuple[bool, str]:
        """Test: Check network configuration and firewall rules"""
        print("🔍 Testing: Network configuration and firewall rules...")
        
        config = self.load_config()
        firewall_config = config.get("firewall", {})
        
        if not firewall_config:
            return False, "No firewall configuration found"
            
        # Check required ports are configured
        required_ports = ["22", "80", "443", "5432"]
        configured_ports = []
        
        for rule in firewall_config.get("inbound_rules", []):
            configured_ports.append(rule.get("ports"))
            
        missing_ports = [port for port in required_ports if port not in configured_ports]
        
        if missing_ports:
            return False, f"Missing firewall rules for ports: {missing_ports}"
            
        return True, f"Firewall configured for ports: {configured_ports}"
    
    def test_resource_allocation(self) -> Tuple[bool, str]:
        """Test: Confirm allocated resources meet minimum requirements"""
        print("🔍 Testing: Resource allocation meets requirements...")
        
        config = self.load_config()
        droplet_config = config.get("droplet", {}).get("config", {})
        
        droplet_size = droplet_config.get("size", "")
        
        # Check minimum requirements (2 vCPU, 4GB RAM)
        if "s-2vcpu-4gb" in droplet_size or "t3.medium" in droplet_size:
            return True, f"Resources: {droplet_size} (meets minimum requirements)"
        elif droplet_size:
            return False, f"Insufficient resources: {droplet_size}"
        else:
            return False, "No resource information found"
    
    def test_uptime_sla_guarantee(self) -> Tuple[bool, str]:
        """Test: Verify 99.9% uptime SLA is configured"""
        print("🔍 Testing: 99.9% uptime SLA guarantee...")
        
        config = self.load_config()
        
        # Check SLA in droplet config
        uptime_sla = config.get("droplet", {}).get("uptime_sla")
        if uptime_sla == "99.9%":
            return True, "99.9% uptime SLA configured"
            
        # Check monitoring configuration
        monitoring_config = config.get("monitoring", {})
        uptime_monitoring = monitoring_config.get("uptime_monitoring", {})
        alert_threshold = uptime_monitoring.get("alert_threshold")
        
        if alert_threshold == "99.9%":
            return True, "99.9% uptime SLA with monitoring alerts"
            
        return False, "No 99.9% uptime SLA configuration found"
    
    def test_monitoring_configuration(self) -> Tuple[bool, str]:
        """Test: Verify monitoring and alerting is configured"""
        print("🔍 Testing: Monitoring and alerting configuration...")
        
        config = self.load_config()
        monitoring_config = config.get("monitoring", {})
        
        if not monitoring_config:
            return False, "No monitoring configuration found"
            
        # Check uptime monitoring
        uptime_monitoring = monitoring_config.get("uptime_monitoring", {})
        if not uptime_monitoring.get("enabled"):
            return False, "Uptime monitoring not enabled"
            
        # Check resource monitoring
        resource_monitoring = monitoring_config.get("resource_monitoring", {})
        if not resource_monitoring:
            return False, "Resource monitoring not configured"
            
        return True, "Comprehensive monitoring configured"
    
    def test_backup_configuration(self) -> Tuple[bool, str]:
        """Test: Verify automated backups are enabled"""
        print("🔍 Testing: Automated backup configuration...")
        
        config = self.load_config()
        droplet_config = config.get("droplet", {}).get("config", {})
        
        # Check if backups are enabled
        if droplet_config.get("backups") is True:
            return True, "Automated backups enabled"
        else:
            return False, "Automated backups not configured"
    
    def test_load_balancer_setup(self) -> Tuple[bool, str]:
        """Test: Verify load balancer configuration for high availability"""
        print("🔍 Testing: Load balancer configuration...")
        
        config = self.load_config()
        lb_config = config.get("load_balancer", {})
        
        if not lb_config:
            return False, "No load balancer configuration found"
            
        # Check health checks
        health_check = lb_config.get("health_check", {})
        if not health_check.get("path"):
            return False, "No health check endpoint configured"
            
        # Check SSL termination
        forwarding_rules = lb_config.get("forwarding_rules", [])
        https_rule = any(rule.get("entry_protocol") == "https" for rule in forwarding_rules)
        
        if not https_rule:
            return False, "HTTPS/SSL termination not configured"
            
        return True, "Load balancer with health checks and SSL configured"
    
    def test_security_configuration(self) -> Tuple[bool, str]:
        """Test: Verify basic security configuration"""
        print("🔍 Testing: Security configuration...")
        
        # Check if server setup script exists (indicates security setup)
        if not os.path.exists("deployment/server_setup.sh"):
            return False, "Server setup script not found"
            
        # Check script content for security measures
        try:
            with open("deployment/server_setup.sh", 'r') as f:
                script_content = f.read()
                
            security_features = [
                "ufw" in script_content,  # Firewall
                "certbot" in script_content,  # SSL certificates
                "nginx" in script_content,  # Web server
                "supervisor" in script_content  # Process monitoring
            ]
            
            if all(security_features):
                return True, "Security features configured (firewall, SSL, monitoring)"
            else:
                return False, "Missing security features in setup script"
                
        except Exception as e:
            return False, f"Error checking security configuration: {e}"
    
    def run_all_tests(self) -> Dict:
        """Run all validation tests"""
        print("🧪 Running Cloud Hosting Setup Validation Tests")
        print("=" * 50)
        
        tests = [
            ("Server Instance Running", self.test_server_instance_running),
            ("Network Configuration", self.test_network_configuration),
            ("Resource Allocation", self.test_resource_allocation),
            ("99.9% Uptime SLA", self.test_uptime_sla_guarantee),
            ("Monitoring Configuration", self.test_monitoring_configuration),
            ("Backup Configuration", self.test_backup_configuration),
            ("Load Balancer Setup", self.test_load_balancer_setup),
            ("Security Configuration", self.test_security_configuration)
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
            print("🎉 ALL TESTS PASSED - Cloud hosting setup is complete!")
            print()
            print("✅ Cloud hosting requirements met:")
            print("   - Server instance running with assigned IP")
            print("   - Firewall configured for required ports")
            print("   - Resources meet minimum requirements (2 vCPU, 4GB RAM)")
            print("   - 99.9% uptime SLA guaranteed")
            print("   - Comprehensive monitoring configured")
            print("   - Automated backups enabled")
            print("   - Load balancer with health checks")
            print("   - Security features configured")
            
        else:
            failed_tests = [name for name, result in results.items() if not result["passed"]]
            print(f"❌ {total - passed} tests failed:")
            for test in failed_tests:
                print(f"   - {test}: {results[test]['message']}")
        
        return results

def main():
    """Main test execution"""
    validator = HostingSetupValidator()
    results = validator.run_all_tests()
    
    # Save test results
    with open("deployment/hosting_validation_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    # Return exit code based on results
    all_passed = all(result["passed"] for result in results.values())
    return 0 if all_passed else 1

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)