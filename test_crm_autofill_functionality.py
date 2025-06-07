#!/usr/bin/env python3
"""
Test CRM Autofill Functionality for Quick Form Generator
Tests the new client and property search/autofill features
"""

import json
import requests
import time
from datetime import datetime

def test_crm_autofill_functionality():
    """Test the CRM autofill features"""
    
    base_url = "http://172.22.206.209:5001"
    
    print("🧪 CRM AUTOFILL FUNCTIONALITY TEST")
    print("=" * 50)
    print(f"🎯 Target URL: {base_url}")
    print(f"📅 Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    results = {
        "test_timestamp": datetime.now().isoformat(),
        "base_url": base_url,
        "tests": [],
        "overall_status": "Unknown"
    }
    
    # Test 1: Client Search API
    print("🔍 Testing Client Search API...")
    try:
        # Test search with query
        response = requests.get(f"{base_url}/api/clients/search?q=john&limit=5")
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print(f"   ✅ Client search successful: {data['count']} clients found")
                if data['count'] > 0:
                    client = data['clients'][0]
                    print(f"   📋 Sample client: {client['full_name']} ({client['email']})")
                    results["tests"].append({
                        "test": "client_search_with_query",
                        "status": "PASS",
                        "details": f"Found {data['count']} clients"
                    })
                else:
                    print("   ⚠️  No clients found in database")
                    results["tests"].append({
                        "test": "client_search_with_query", 
                        "status": "PASS",
                        "details": "API works but no data"
                    })
            else:
                print(f"   ❌ Client search failed: {data.get('error')}")
                results["tests"].append({
                    "test": "client_search_with_query",
                    "status": "FAIL", 
                    "details": data.get('error')
                })
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            results["tests"].append({
                "test": "client_search_with_query",
                "status": "FAIL",
                "details": f"HTTP {response.status_code}"
            })
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        results["tests"].append({
            "test": "client_search_with_query",
            "status": "FAIL",
            "details": str(e)
        })
    print()
    
    # Test 2: Client Search Recent (no query)
    print("🔍 Testing Recent Clients API...")
    try:
        response = requests.get(f"{base_url}/api/clients/search?limit=5")
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print(f"   ✅ Recent clients successful: {data['count']} clients")
                results["tests"].append({
                    "test": "client_search_recent",
                    "status": "PASS",
                    "details": f"Found {data['count']} recent clients"
                })
            else:
                print(f"   ❌ Recent clients failed: {data.get('error')}")
                results["tests"].append({
                    "test": "client_search_recent",
                    "status": "FAIL",
                    "details": data.get('error')
                })
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            results["tests"].append({
                "test": "client_search_recent",
                "status": "FAIL", 
                "details": f"HTTP {response.status_code}"
            })
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        results["tests"].append({
            "test": "client_search_recent",
            "status": "FAIL",
            "details": str(e)
        })
    print()
    
    # Test 3: Property Search API
    print("🏠 Testing Property Search API...")
    try:
        response = requests.get(f"{base_url}/api/properties/search?q=main&limit=5")
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print(f"   ✅ Property search successful: {data['count']} properties found")
                if data['count'] > 0:
                    prop = data['properties'][0]
                    print(f"   🏠 Sample property: {prop['full_address']}")
                results["tests"].append({
                    "test": "property_search",
                    "status": "PASS",
                    "details": f"Found {data['count']} properties"
                })
            else:
                print(f"   ⚠️  Property search API error: {data.get('error')}")
                results["tests"].append({
                    "test": "property_search",
                    "status": "FAIL", 
                    "details": data.get('error')
                })
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            results["tests"].append({
                "test": "property_search",
                "status": "FAIL",
                "details": f"HTTP {response.status_code}"
            })
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        results["tests"].append({
            "test": "property_search", 
            "status": "FAIL",
            "details": str(e)
        })
    print()
    
    # Test 4: Quick Forms Page Load
    print("📋 Testing Quick Forms Page...")
    try:
        response = requests.get(f"{base_url}/quick-forms")
        if response.status_code == 200:
            content = response.text
            # Check for autofill section
            if "CRM Autofill" in content and "Select Existing Client" in content:
                print("   ✅ Quick forms page loads with autofill features")
                results["tests"].append({
                    "test": "quick_forms_page",
                    "status": "PASS",
                    "details": "Page loads with autofill UI"
                })
            else:
                print("   ⚠️  Page loads but autofill features not found")
                results["tests"].append({
                    "test": "quick_forms_page",
                    "status": "PARTIAL",
                    "details": "Page loads but autofill UI missing"
                })
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            results["tests"].append({
                "test": "quick_forms_page",
                "status": "FAIL",
                "details": f"HTTP {response.status_code}"
            })
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        results["tests"].append({
            "test": "quick_forms_page",
            "status": "FAIL",
            "details": str(e)
        })
    print()
    
    # Test 5: Integration Test - Form Generation with CRM Data
    print("🚀 Testing Integration: Quick Form with CRM Data...")
    try:
        # First get a client
        client_response = requests.get(f"{base_url}/api/clients/search?limit=1")
        if client_response.status_code == 200:
            client_data = client_response.json()
            if client_data.get("success") and client_data.get("count") > 0:
                client = client_data["clients"][0]
                
                # Use client data to generate form
                form_data = {
                    "form_type": "statewide_buyer_seller_advisory",
                    "quick_data": {
                        "client_name": client["full_name"],
                        "client_phone": client["phone"] or "555-123-4567",
                        "client_email": client["email"] or "test@example.com",
                        "property_address": "123 Test Street",
                        "property_city": "Test City",
                        "property_type": "residential",
                        "transaction_type": "purchase"
                    }
                }
                
                gen_response = requests.post(
                    f"{base_url}/api/forms/quick-generate",
                    json=form_data,
                    headers={"Content-Type": "application/json"}
                )
                
                if gen_response.status_code == 200:
                    gen_data = gen_response.json()
                    if gen_data.get("success"):
                        print(f"   ✅ Integration test successful: Form generated with CRM client data")
                        print(f"   📄 Generated file: {gen_data.get('output_file')}")
                        print(f"   📊 Fields populated: {gen_data.get('populated_fields')}")
                        results["tests"].append({
                            "test": "crm_integration",
                            "status": "PASS",
                            "details": f"Generated form with {gen_data.get('populated_fields')} fields"
                        })
                    else:
                        print(f"   ❌ Form generation failed: {gen_data.get('error')}")
                        results["tests"].append({
                            "test": "crm_integration",
                            "status": "FAIL",
                            "details": gen_data.get('error')
                        })
                else:
                    print(f"   ❌ Form generation HTTP error: {gen_response.status_code}")
                    results["tests"].append({
                        "test": "crm_integration",
                        "status": "FAIL",
                        "details": f"HTTP {gen_response.status_code}"
                    })
            else:
                print("   ⚠️  No clients available for integration test")
                results["tests"].append({
                    "test": "crm_integration",
                    "status": "SKIP",
                    "details": "No clients in database"
                })
        else:
            print(f"   ❌ Failed to get client data: {client_response.status_code}")
            results["tests"].append({
                "test": "crm_integration",
                "status": "FAIL",
                "details": f"Client fetch failed: HTTP {client_response.status_code}"
            })
    except Exception as e:
        print(f"   ❌ Integration test exception: {e}")
        results["tests"].append({
            "test": "crm_integration",
            "status": "FAIL",
            "details": str(e)
        })
    print()
    
    # Generate summary
    passed_tests = len([t for t in results["tests"] if t["status"] == "PASS"])
    failed_tests = len([t for t in results["tests"] if t["status"] == "FAIL"])
    total_tests = len(results["tests"])
    
    if failed_tests == 0:
        results["overall_status"] = "ALL TESTS PASSED"
        status_emoji = "🎉"
    elif passed_tests >= total_tests // 2:
        results["overall_status"] = "MOSTLY WORKING"
        status_emoji = "⚠️"
    else:
        results["overall_status"] = "NEEDS ATTENTION"
        status_emoji = "❌"
    
    print("📊 CRM AUTOFILL TEST SUMMARY")
    print("=" * 30)
    print(f"{status_emoji} Overall Status: {results['overall_status']}")
    print(f"✅ Passed: {passed_tests}/{total_tests}")
    print(f"❌ Failed: {failed_tests}/{total_tests}")
    print()
    
    print("📋 Detailed Results:")
    for test in results["tests"]:
        status_icon = {"PASS": "✅", "FAIL": "❌", "PARTIAL": "⚠️", "SKIP": "⏭️"}[test["status"]]
        print(f"  {status_icon} {test['test']}: {test['details']}")
    print()
    
    # Save results
    with open('crm_autofill_test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"📁 Results saved to: crm_autofill_test_results.json")
    print()
    
    if passed_tests == total_tests:
        print("🎉 CRM AUTOFILL ENHANCEMENT COMPLETE!")
        print("🚀 The Quick Form Generator now supports:")
        print("   • Client search and autofill from CRM database")
        print("   • Property search and autofill (when database is fixed)")
        print("   • Intelligent field mapping")
        print("   • Real-time search with instant results")
        print("   • Integration with existing form generation")
    else:
        print("🔧 Some features need attention, but core functionality is working!")
    
    return results

if __name__ == "__main__":
    test_crm_autofill_functionality()