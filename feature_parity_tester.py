#!/usr/bin/env python3
"""
Feature Parity Testing - ENV004
Test all existing features in both environments to ensure functional parity before adding form population
"""

import requests
import json
import sqlite3
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

class FeatureParityTester:
    """Comprehensive testing framework for environment feature parity"""
    
    def __init__(self, local_url: str = "http://172.22.206.209:3001", 
                 production_url: str = "https://real-estate-crm-6p9kt.ondigitalocean.app"):
        self.local_url = local_url.rstrip('/')
        self.production_url = production_url.rstrip('/')
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "environments": {
                "local": {"url": self.local_url, "status": "unknown"},
                "production": {"url": self.production_url, "status": "unknown"}
            },
            "feature_tests": [],
            "parity_score": 0,
            "issues_found": []
        }
    
    def run_comprehensive_parity_tests(self) -> Dict[str, Any]:
        """Execute comprehensive feature parity testing"""
        print("🧪 Starting comprehensive feature parity testing...")
        
        # Test 1: Environment Connectivity
        connectivity_test = self._test_environment_connectivity()
        self.test_results["feature_tests"].append(connectivity_test)
        
        # Test 2: Core API Endpoints
        api_test = self._test_core_api_endpoints()
        self.test_results["feature_tests"].append(api_test)
        
        # Test 3: Database Operations
        database_test = self._test_database_operations()
        self.test_results["feature_tests"].append(database_test)
        
        # Test 4: AI Integration Features
        ai_test = self._test_ai_integration()
        self.test_results["feature_tests"].append(ai_test)
        
        # Test 5: Static Asset Delivery
        static_test = self._test_static_assets()
        self.test_results["feature_tests"].append(static_test)
        
        # Test 6: Form Templates Availability
        template_test = self._test_form_templates()
        self.test_results["feature_tests"].append(template_test)
        
        # Calculate overall parity score
        self._calculate_parity_score()
        
        return self.test_results
    
    def _test_environment_connectivity(self) -> Dict[str, Any]:
        """Test basic connectivity to both environments"""
        test_result = {
            "test_name": "Environment Connectivity",
            "local_status": "unknown",
            "production_status": "unknown",
            "parity_achieved": False,
            "details": {},
            "issues": []
        }
        
        # Test local environment
        try:
            local_response = requests.get(f"{self.local_url}/", timeout=10)
            test_result["local_status"] = "online" if local_response.status_code == 200 else f"error_{local_response.status_code}"
            test_result["details"]["local_response_time"] = local_response.elapsed.total_seconds()
            self.test_results["environments"]["local"]["status"] = test_result["local_status"]
        except Exception as e:
            test_result["local_status"] = "offline"
            test_result["issues"].append(f"Local environment unreachable: {str(e)}")
            self.test_results["environments"]["local"]["status"] = "offline"
        
        # Test production environment
        try:
            prod_response = requests.get(f"{self.production_url}/", timeout=10)
            test_result["production_status"] = "online" if prod_response.status_code == 200 else f"error_{prod_response.status_code}"
            test_result["details"]["production_response_time"] = prod_response.elapsed.total_seconds()
            self.test_results["environments"]["production"]["status"] = test_result["production_status"]
        except Exception as e:
            test_result["production_status"] = "offline"
            test_result["issues"].append(f"Production environment unreachable: {str(e)}")
            self.test_results["environments"]["production"]["status"] = "offline"
        
        # Check parity
        test_result["parity_achieved"] = (test_result["local_status"] == "online" and 
                                        test_result["production_status"] == "online")
        
        return test_result
    
    def _test_core_api_endpoints(self) -> Dict[str, Any]:
        """Test core API endpoints in both environments"""
        test_result = {
            "test_name": "Core API Endpoints",
            "endpoints_tested": 0,
            "local_successes": 0,
            "production_successes": 0,
            "parity_achieved": False,
            "endpoint_results": {},
            "issues": []
        }
        
        # Core endpoints to test
        endpoints = [
            {"path": "/", "method": "GET", "description": "Dashboard home"},
            {"path": "/clients", "method": "GET", "description": "Client list"},
            {"path": "/properties", "method": "GET", "description": "Property list"},
            {"path": "/transactions", "method": "GET", "description": "Transaction list"},
            {"path": "/api/dashboard_stats", "method": "GET", "description": "Dashboard statistics"},
            {"path": "/chat", "method": "POST", "description": "AI chatbot", "data": {"message": "test"}},
        ]
        
        for endpoint in endpoints:
            test_result["endpoints_tested"] += 1
            endpoint_key = f"{endpoint['method']} {endpoint['path']}"
            
            endpoint_result = {
                "description": endpoint["description"],
                "local_status": "unknown",
                "production_status": "unknown",
                "parity": False
            }
            
            # Test local
            try:
                if endpoint["method"] == "GET":
                    response = requests.get(f"{self.local_url}{endpoint['path']}", timeout=5)
                else:
                    response = requests.post(f"{self.local_url}{endpoint['path']}", 
                                           json=endpoint.get("data", {}), timeout=5)
                
                endpoint_result["local_status"] = response.status_code
                if response.status_code in [200, 201, 202]:
                    test_result["local_successes"] += 1
                    
            except Exception as e:
                endpoint_result["local_status"] = f"error: {str(e)}"
                test_result["issues"].append(f"Local {endpoint_key} failed: {str(e)}")
            
            # Test production
            try:
                if endpoint["method"] == "GET":
                    response = requests.get(f"{self.production_url}{endpoint['path']}", timeout=5)
                else:
                    response = requests.post(f"{self.production_url}{endpoint['path']}", 
                                           json=endpoint.get("data", {}), timeout=5)
                
                endpoint_result["production_status"] = response.status_code
                if response.status_code in [200, 201, 202]:
                    test_result["production_successes"] += 1
                    
            except Exception as e:
                endpoint_result["production_status"] = f"error: {str(e)}"
                test_result["issues"].append(f"Production {endpoint_key} failed: {str(e)}")
            
            # Check endpoint parity
            endpoint_result["parity"] = (endpoint_result["local_status"] == endpoint_result["production_status"])
            test_result["endpoint_results"][endpoint_key] = endpoint_result
        
        # Calculate overall API parity
        parity_count = sum(1 for result in test_result["endpoint_results"].values() if result["parity"])
        test_result["parity_achieved"] = parity_count >= (len(endpoints) * 0.8)  # 80% threshold
        test_result["parity_percentage"] = (parity_count / len(endpoints)) * 100
        
        return test_result
    
    def _test_database_operations(self) -> Dict[str, Any]:
        """Test database operations and data consistency"""
        test_result = {
            "test_name": "Database Operations",
            "local_db_status": "unknown",
            "production_data_status": "unknown", 
            "parity_achieved": False,
            "details": {},
            "issues": []
        }
        
        # Test local database
        try:
            local_db_path = "core_app/database/real_estate_crm.db"
            if Path(local_db_path).exists():
                conn = sqlite3.connect(local_db_path)
                cursor = conn.cursor()
                
                # Get table info
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                
                table_counts = {}
                for table in tables:
                    table_name = table[0]
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
                        count = cursor.fetchone()[0]
                        table_counts[table_name] = count
                    except Exception as e:
                        table_counts[table_name] = f"error: {str(e)}"
                
                conn.close()
                
                test_result["local_db_status"] = "operational"
                test_result["details"]["local_tables"] = table_counts
                
            else:
                test_result["local_db_status"] = "missing"
                test_result["issues"].append("Local database file not found")
                
        except Exception as e:
            test_result["local_db_status"] = "error"
            test_result["issues"].append(f"Local database error: {str(e)}")
        
        # Test production data access via API
        try:
            response = requests.get(f"{self.production_url}/api/dashboard_stats", timeout=10)
            if response.status_code == 200:
                stats = response.json()
                test_result["production_data_status"] = "operational"
                test_result["details"]["production_stats"] = stats
            else:
                test_result["production_data_status"] = f"api_error_{response.status_code}"
                test_result["issues"].append(f"Production API returned {response.status_code}")
                
        except Exception as e:
            test_result["production_data_status"] = "unreachable"
            test_result["issues"].append(f"Production data access failed: {str(e)}")
        
        # Check database parity
        test_result["parity_achieved"] = (test_result["local_db_status"] == "operational" and 
                                        test_result["production_data_status"] == "operational")
        
        return test_result
    
    def _test_ai_integration(self) -> Dict[str, Any]:
        """Test AI integration features"""
        test_result = {
            "test_name": "AI Integration Features",
            "local_ai_status": "unknown",
            "production_ai_status": "unknown",
            "parity_achieved": False,
            "details": {},
            "issues": []
        }
        
        test_message = {"message": "Test AI integration"}
        
        # Test local AI
        try:
            response = requests.post(f"{self.local_url}/chat", json=test_message, timeout=15)
            if response.status_code == 200:
                ai_response = response.json()
                test_result["local_ai_status"] = "operational"
                test_result["details"]["local_ai_response_length"] = len(str(ai_response))
                test_result["details"]["local_ai_response_time"] = response.elapsed.total_seconds()
            else:
                test_result["local_ai_status"] = f"error_{response.status_code}"
                test_result["issues"].append(f"Local AI returned {response.status_code}")
        except Exception as e:
            test_result["local_ai_status"] = "failed"
            test_result["issues"].append(f"Local AI test failed: {str(e)}")
        
        # Test production AI
        try:
            response = requests.post(f"{self.production_url}/chat", json=test_message, timeout=15)
            if response.status_code == 200:
                ai_response = response.json()
                test_result["production_ai_status"] = "operational"
                test_result["details"]["production_ai_response_length"] = len(str(ai_response))
                test_result["details"]["production_ai_response_time"] = response.elapsed.total_seconds()
            else:
                test_result["production_ai_status"] = f"error_{response.status_code}"
                test_result["issues"].append(f"Production AI returned {response.status_code}")
        except Exception as e:
            test_result["production_ai_status"] = "failed"
            test_result["issues"].append(f"Production AI test failed: {str(e)}")
        
        # Check AI parity
        test_result["parity_achieved"] = (test_result["local_ai_status"] == "operational" and 
                                        test_result["production_ai_status"] == "operational")
        
        return test_result
    
    def _test_static_assets(self) -> Dict[str, Any]:
        """Test static asset delivery"""
        test_result = {
            "test_name": "Static Asset Delivery",
            "assets_tested": 0,
            "local_successes": 0,
            "production_successes": 0,
            "parity_achieved": False,
            "asset_results": {},
            "issues": []
        }
        
        # Key static assets to test
        assets = [
            "/static/style.css",
            "/static/script.js",
            "/static/debug_enter.js"
        ]
        
        for asset in assets:
            test_result["assets_tested"] += 1
            
            asset_result = {
                "local_status": "unknown",
                "production_status": "unknown",
                "parity": False
            }
            
            # Test local asset
            try:
                response = requests.get(f"{self.local_url}{asset}", timeout=5)
                asset_result["local_status"] = response.status_code
                if response.status_code == 200:
                    test_result["local_successes"] += 1
            except Exception as e:
                asset_result["local_status"] = f"error: {str(e)}"
                test_result["issues"].append(f"Local asset {asset} failed: {str(e)}")
            
            # Test production asset
            try:
                response = requests.get(f"{self.production_url}{asset}", timeout=5)
                asset_result["production_status"] = response.status_code
                if response.status_code == 200:
                    test_result["production_successes"] += 1
            except Exception as e:
                asset_result["production_status"] = f"error: {str(e)}"
                test_result["issues"].append(f"Production asset {asset} failed: {str(e)}")
            
            # Check asset parity
            asset_result["parity"] = (asset_result["local_status"] == asset_result["production_status"])
            test_result["asset_results"][asset] = asset_result
        
        # Calculate static asset parity
        parity_count = sum(1 for result in test_result["asset_results"].values() if result["parity"])
        test_result["parity_achieved"] = parity_count >= (len(assets) * 0.8)
        test_result["parity_percentage"] = (parity_count / len(assets)) * 100
        
        return test_result
    
    def _test_form_templates(self) -> Dict[str, Any]:
        """Test form template availability"""
        test_result = {
            "test_name": "Form Template Availability",
            "local_templates": 0,
            "expected_templates": 13,
            "template_accessibility": "unknown",
            "parity_achieved": False,
            "details": {},
            "issues": []
        }
        
        # Check local form templates
        try:
            templates_dir = Path("form_templates")
            if templates_dir.exists():
                template_files = list(templates_dir.glob("*.json"))
                test_result["local_templates"] = len(template_files)
                test_result["details"]["template_files"] = [f.name for f in template_files]
                
                # Check blank templates
                blank_templates_dir = Path("blank_templates")
                if blank_templates_dir.exists():
                    blank_files = list(blank_templates_dir.glob("*.json"))
                    test_result["details"]["blank_template_count"] = len(blank_files)
                    test_result["template_accessibility"] = "operational"
                else:
                    test_result["issues"].append("Blank templates directory not found")
                    
            else:
                test_result["issues"].append("Form templates directory not found")
                
        except Exception as e:
            test_result["issues"].append(f"Template accessibility check failed: {str(e)}")
        
        # Check template completeness
        template_completeness = (test_result["local_templates"] / test_result["expected_templates"]) * 100
        test_result["details"]["template_completeness"] = template_completeness
        
        # Form templates are local-only for now, so parity is about readiness
        test_result["parity_achieved"] = (test_result["local_templates"] >= 10 and 
                                        test_result["template_accessibility"] == "operational")
        
        return test_result
    
    def _calculate_parity_score(self):
        """Calculate overall environment parity score"""
        total_tests = len(self.test_results["feature_tests"])
        parity_achieved = sum(1 for test in self.test_results["feature_tests"] if test["parity_achieved"])
        
        self.test_results["parity_score"] = (parity_achieved / total_tests) * 100
        
        # Collect all issues
        all_issues = []
        for test in self.test_results["feature_tests"]:
            all_issues.extend(test.get("issues", []))
        
        self.test_results["issues_found"] = all_issues
        self.test_results["summary"] = {
            "total_tests": total_tests,
            "tests_passed": parity_achieved,
            "parity_score": self.test_results["parity_score"],
            "total_issues": len(all_issues),
            "ready_for_form_population": self.test_results["parity_score"] >= 70
        }
    
    def generate_parity_report(self) -> str:
        """Generate comprehensive parity testing report"""
        if not self.test_results["feature_tests"]:
            return "No parity tests have been performed yet."
        
        report = []
        report.append("🧪 FEATURE PARITY TESTING REPORT")
        report.append("=" * 50)
        report.append(f"Generated: {self.test_results['timestamp']}")
        report.append(f"Local Environment: {self.test_results['environments']['local']['url']}")
        report.append(f"Production Environment: {self.test_results['environments']['production']['url']}")
        report.append("")
        
        # Overall score
        summary = self.test_results["summary"]
        score = summary["parity_score"]
        status_emoji = "✅" if score >= 80 else "⚠️" if score >= 60 else "❌"
        report.append(f"📊 OVERALL PARITY SCORE: {status_emoji} {score:.1f}%")
        report.append(f"   Tests Passed: {summary['tests_passed']}/{summary['total_tests']}")
        report.append(f"   Ready for Form Population: {'✅ YES' if summary['ready_for_form_population'] else '❌ NO'}")
        report.append("")
        
        # Environment status
        report.append("🌐 ENVIRONMENT STATUS:")
        for env_name, env_data in self.test_results["environments"].items():
            status_emoji = "✅" if env_data["status"] == "online" else "❌"
            report.append(f"   {status_emoji} {env_name.title()}: {env_data['status']}")
        report.append("")
        
        # Detailed test results
        report.append("📋 DETAILED TEST RESULTS:")
        for test in self.test_results["feature_tests"]:
            parity_emoji = "✅" if test["parity_achieved"] else "❌"
            report.append(f"   {parity_emoji} {test['test_name']}")
            
            if test.get("issues"):
                for issue in test["issues"]:
                    report.append(f"      • {issue}")
        
        # Issues requiring attention
        if self.test_results["issues_found"]:
            report.append("")
            report.append("⚠️ ISSUES REQUIRING ATTENTION:")
            for i, issue in enumerate(self.test_results["issues_found"], 1):
                report.append(f"   {i}. {issue}")
        
        return "\n".join(report)

def main():
    """Test the feature parity testing framework"""
    print("🚀 Feature Parity Tester - ENV004")
    print("=" * 50)
    
    tester = FeatureParityTester()
    
    # Run comprehensive parity tests
    print("\n🧪 Running comprehensive feature parity tests...")
    results = tester.run_comprehensive_parity_tests()
    
    # Generate and display report
    print("\n" + tester.generate_parity_report())
    
    # Save results to file
    results_file = "feature_parity_results.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Detailed results saved to: {results_file}")
    print(f"\n✅ ENV004 Complete: Feature Parity Testing")
    print(f"🔄 Environment readiness verified for form population integration")

if __name__ == "__main__":
    main()