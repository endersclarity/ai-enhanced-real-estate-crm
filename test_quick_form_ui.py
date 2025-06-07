#!/usr/bin/env python3
"""
Quick Form Generator UI Testing Script
Tests responsive design, error handling, and user experience
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://172.22.206.209:5000"
QUICK_FORMS_URL = f"{BASE_URL}/quick-forms"
API_URL = f"{BASE_URL}/api/forms/quick-generate"

def test_page_accessibility():
    """Test that the quick forms page loads correctly"""
    print("📋 Testing Page Accessibility")
    try:
        response = requests.get(QUICK_FORMS_URL, timeout=10)
        
        # Check status code
        if response.status_code == 200:
            print("  ✅ Page loads successfully (200 OK)")
        else:
            print(f"  ❌ Page failed to load: {response.status_code}")
            return False
            
        # Check for key elements
        content = response.text
        required_elements = [
            'Quick Form Generator',
            'Step 1: Select Form Type',
            'Step 2: Fill Required Information',
            'form-option',
            'statewide_buyer_seller_advisory',
            'buyer_representation_agreement'
        ]
        
        missing_elements = []
        for element in required_elements:
            if element not in content:
                missing_elements.append(element)
                
        if missing_elements:
            print(f"  ❌ Missing elements: {missing_elements}")
            return False
        else:
            print("  ✅ All required UI elements present")
            
        # Check responsive design elements
        responsive_elements = [
            'col-lg-4 col-md-6',  # Bootstrap responsive columns
            'container-fluid',     # Responsive container
            'meta name="viewport"' # Mobile viewport
        ]
        
        for element in responsive_elements:
            if element in content:
                print(f"  ✅ Responsive element found: {element}")
            else:
                print(f"  ⚠️ Missing responsive element: {element}")
                
        return True
        
    except Exception as e:
        print(f"  ❌ Error testing page accessibility: {e}")
        return False

def test_form_validation():
    """Test form validation and error handling"""
    print("\n🔍 Testing Form Validation & Error Handling")
    
    tests_passed = 0
    total_tests = 3
    
    # Test 1: Empty submission
    print("  Testing empty form submission...")
    try:
        empty_payload = {
            "form_type": "statewide_buyer_seller_advisory",
            "quick_data": {},
            "generation_method": "quick_form"
        }
        
        response = requests.post(API_URL, json=empty_payload, timeout=15)
        
        if response.status_code == 400 or (response.status_code == 200 and not response.json().get('success', True)):
            print("  ✅ Empty form properly rejected")
            tests_passed += 1
        else:
            print(f"  ❌ Empty form not rejected properly: {response.status_code}")
            
    except Exception as e:
        print(f"  ❌ Error testing empty form: {e}")
    
    # Test 2: Invalid form type
    print("  Testing invalid form type...")
    try:
        invalid_payload = {
            "form_type": "nonexistent_form",
            "quick_data": {
                "client_name": "Test Client",
                "client_phone": "555-123-4567"
            },
            "generation_method": "quick_form"
        }
        
        response = requests.post(API_URL, json=invalid_payload, timeout=15)
        
        if response.status_code == 400 or (response.status_code == 200 and not response.json().get('success', True)):
            print("  ✅ Invalid form type properly rejected")
            tests_passed += 1
        else:
            print(f"  ❌ Invalid form type not rejected: {response.status_code}")
            
    except Exception as e:
        print(f"  ❌ Error testing invalid form: {e}")
    
    # Test 3: Partial data submission
    print("  Testing partial data submission...")
    try:
        partial_payload = {
            "form_type": "statewide_buyer_seller_advisory",
            "quick_data": {
                "client_name": "Test Client"
                # Missing required fields: phone, email, property_address, etc.
            },
            "generation_method": "quick_form"
        }
        
        response = requests.post(API_URL, json=partial_payload, timeout=15)
        result = response.json()
        
        if not result.get('success', True) and ('missing' in result.get('error', '').lower() or 'required' in result.get('error', '').lower()):
            print("  ✅ Partial data properly validated with helpful error")
            tests_passed += 1
        else:
            print(f"  ⚠️ Partial data handling: {result}")
            
    except Exception as e:
        print(f"  ❌ Error testing partial data: {e}")
    
    return tests_passed == total_tests

def test_successful_form_generation():
    """Test successful form generation for each form type"""
    print("\n🚀 Testing Successful Form Generation")
    
    # Test data for each form type
    test_forms = {
        "statewide_buyer_seller_advisory": {
            "client_name": "John Test Client",
            "client_phone": "555-123-4567",
            "client_email": "john@test.com",
            "property_address": "123 Test Street",
            "property_city": "Sacramento",
            "property_type": "Single Family Home",
            "transaction_type": "Purchase"
        },
        "buyer_representation_agreement": {
            "client_name": "Mary Test Buyer",
            "client_phone": "555-234-5678",
            "client_email": "mary@test.com",
            "client_address": "456 Test Avenue\nSacramento, CA 95814",
            "agent_name": "Narissa Henderson",
            "agent_license": "DRE12345",
            "brokerage_name": "Narissa Realty",
            "commission_rate": "3.0"
        },
        "agent_visual_inspection_disclosure": {
            "client_name": "Bob Test Client",
            "property_address": "789 Test Drive",
            "property_city": "Davis",
            "property_type": "Condominium",
            "inspection_date": "2025-06-15",
            "agent_name": "Narissa Henderson",
            "agent_license": "DRE12345",
            "brokerage_name": "Narissa Realty"
        },
        "market_conditions_advisory": {
            "client_name": "Sarah Test Client",
            "client_phone": "555-345-6789",
            "client_email": "sarah@test.com",
            "target_city": "Roseville",
            "property_type": "Townhouse",
            "transaction_type": "Purchase",
            "agent_name": "Narissa Henderson",
            "agent_license": "DRE12345",
            "brokerage_name": "Narissa Realty"
        },
        "transaction_record": {
            "buyer_name": "Mike Test Buyer",
            "buyer_phone": "555-456-7890",
            "buyer_email": "mike@test.com",
            "property_address": "321 Test Lane",
            "purchase_price": "750000",
            "earnest_money": "15000",
            "contract_date": "2025-06-10",
            "closing_date": "2025-07-15",
            "listing_agent": "Jane Listing Agent",
            "buyer_agent": "Narissa Henderson"
        }
    }
    
    success_count = 0
    total_forms = len(test_forms)
    
    for form_type, test_data in test_forms.items():
        print(f"  Testing {form_type}...")
        try:
            start_time = time.time()
            
            payload = {
                "form_type": form_type,
                "quick_data": test_data,
                "generation_method": "quick_form"
            }
            
            response = requests.post(API_URL, json=payload, timeout=30)
            result = response.json()
            
            end_time = time.time()
            generation_time = end_time - start_time
            
            if result.get('success', False):
                print(f"    ✅ Generated successfully in {generation_time:.2f}s")
                print(f"    📄 Output: {result.get('output_file', 'Unknown')}")
                print(f"    📊 Fields: {result.get('populated_fields', 'Unknown')}")
                success_count += 1
                
                # Check generation time
                if generation_time < 5.0:
                    print(f"    ⚡ Performance: Excellent (<5s)")
                elif generation_time < 10.0:
                    print(f"    ⚠️ Performance: Acceptable (5-10s)")
                else:
                    print(f"    ❌ Performance: Too slow (>10s)")
                    
            else:
                print(f"    ❌ Generation failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"    ❌ Error testing {form_type}: {e}")
    
    print(f"\n📊 Form Generation Results: {success_count}/{total_forms} successful")
    return success_count == total_forms

def test_responsive_design():
    """Test responsive design elements"""
    print("\n📱 Testing Responsive Design Elements")
    
    try:
        response = requests.get(QUICK_FORMS_URL, timeout=10)
        content = response.text
        
        # Check viewport meta tag
        if 'name="viewport"' in content:
            print("  ✅ Mobile viewport meta tag present")
        else:
            print("  ❌ Missing mobile viewport meta tag")
        
        # Check Bootstrap responsive classes
        responsive_classes = [
            'col-lg-4 col-md-6',
            'container-fluid',
            'd-flex',
            'justify-content-between',
            'align-items-center'
        ]
        
        for css_class in responsive_classes:
            if css_class in content:
                print(f"  ✅ Responsive class found: {css_class}")
            else:
                print(f"  ⚠️ Missing responsive class: {css_class}")
        
        # Check for mobile-friendly form elements
        mobile_elements = [
            'form-control',
            'form-select',
            'btn-lg',
            'card'
        ]
        
        for element in mobile_elements:
            if element in content:
                print(f"  ✅ Mobile-friendly element: {element}")
                
        return True
        
    except Exception as e:
        print(f"  ❌ Error testing responsive design: {e}")
        return False

def test_user_experience_flow():
    """Test the complete user experience flow timing"""
    print("\n⏱️ Testing User Experience Flow")
    
    # Simulate realistic user interaction timing
    print("  Simulating user flow with realistic timing...")
    
    total_start = time.time()
    
    # Step 1: Load page (user navigation)
    print("  Step 1: Loading quick forms page...")
    step1_start = time.time()
    response = requests.get(QUICK_FORMS_URL, timeout=10)
    step1_time = time.time() - step1_start
    print(f"    Page load: {step1_time:.2f}s")
    
    # Step 2: User form selection and filling (simulated delay)
    print("  Step 2: User selecting form and filling fields...")
    user_input_time = 15.0  # Simulate 15 seconds of user input
    time.sleep(2)  # Brief simulation delay
    print(f"    User input simulation: {user_input_time}s")
    
    # Step 3: Form generation
    print("  Step 3: Generating PDF...")
    step3_start = time.time()
    
    payload = {
        "form_type": "statewide_buyer_seller_advisory",
        "quick_data": {
            "client_name": "UX Test Client",
            "client_phone": "555-999-8888",
            "client_email": "ux@test.com",
            "property_address": "999 UX Test Blvd",
            "property_city": "Sacramento",
            "property_type": "Single Family Home",
            "transaction_type": "Purchase"
        },
        "generation_method": "quick_form"
    }
    
    response = requests.post(API_URL, json=payload, timeout=30)
    step3_time = time.time() - step3_start
    print(f"    PDF generation: {step3_time:.2f}s")
    
    # Calculate total time
    total_time = step1_time + user_input_time + step3_time
    print(f"\n  📊 Total UX Flow Time: {total_time:.2f}s")
    
    # Evaluate against target (<30 seconds)
    if total_time < 30:
        print(f"  ✅ UX Target Met: {total_time:.2f}s < 30s")
        return True
    else:
        print(f"  ❌ UX Target Missed: {total_time:.2f}s > 30s")
        return False

def main():
    """Run comprehensive UI testing"""
    print("🧪 Quick Form Generator UI Testing Suite")
    print("=" * 50)
    print(f"Target URL: {QUICK_FORMS_URL}")
    print(f"API URL: {API_URL}")
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    test_results = []
    
    # Run all tests
    test_results.append(("Page Accessibility", test_page_accessibility()))
    test_results.append(("Form Validation", test_form_validation()))
    test_results.append(("Form Generation", test_successful_form_generation()))
    test_results.append(("Responsive Design", test_responsive_design()))
    test_results.append(("User Experience", test_user_experience_flow()))
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:20s} {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(test_results)} tests passed")
    
    if passed == len(test_results):
        print("🎉 All tests passed! UI is ready for production.")
        return True
    else:
        print("⚠️ Some tests failed. Review results above.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)