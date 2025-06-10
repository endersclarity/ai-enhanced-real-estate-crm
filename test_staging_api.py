#!/usr/bin/env python3
"""
API-specific tests for Real Estate CRM Staging
Tests API responses without modifying data
"""

import requests
import json
from datetime import datetime

STAGING_URL = "http://localhost:5002"

def test_api_responses():
    """Test all API endpoints"""
    print("\n🔌 API Endpoint Tests")
    print("=" * 50)
    
    # Test health endpoint
    try:
        resp = requests.get(f"{STAGING_URL}/api/health")
        health_data = resp.json()
        print(f"✓ Health Check: {health_data.get('status', 'unknown')}")
        print(f"  Database: {'✓ Connected' if health_data.get('database_connected') else '✗ Not connected'}")
        print(f"  Environment: {health_data.get('environment', 'unknown')}")
    except Exception as e:
        print(f"✗ Health Check Failed: {e}")
    
    # Test stats endpoint
    try:
        resp = requests.get(f"{STAGING_URL}/api/stats")
        stats = resp.json()
        print(f"\n✓ Stats API:")
        print(f"  Clients: {stats.get('clients', 0)}")
        print(f"  Properties: {stats.get('properties', 0)}")
        print(f"  Transactions: {stats.get('transactions', 0)}")
        if 'recent_activity' in stats:
            print(f"  Recent Activity: {len(stats['recent_activity'])} items")
    except Exception as e:
        print(f"✗ Stats API Failed: {e}")
    
    # Test form validation (GET request should fail properly)
    try:
        resp = requests.get(f"{STAGING_URL}/api/validate/client")
        if resp.status_code == 405:
            print(f"\n✓ Form Validation: Correctly rejects GET requests")
        else:
            print(f"\n⚠ Form Validation: Unexpected response code {resp.status_code}")
    except Exception as e:
        print(f"✗ Form Validation Check Failed: {e}")
    
    # Test CRPA endpoints
    try:
        resp = requests.get(f"{STAGING_URL}/api/crpa/templates")
        if resp.status_code == 200:
            templates = resp.json()
            print(f"\n✓ CRPA Templates: {len(templates) if isinstance(templates, list) else 'Available'}")
        else:
            print(f"\n⚠ CRPA Templates: Status {resp.status_code}")
    except Exception as e:
        print(f"✗ CRPA Templates Failed: {e}")

if __name__ == "__main__":
    test_api_responses()