#!/usr/bin/env python3
"""
Simple CRM population script matching existing schema
"""

import requests
import random
from datetime import datetime

# Realistic dummy data
NAMES = [
    ("Jennifer", "Smith"), ("Michael", "Johnson"), ("Sarah", "Williams"), ("David", "Brown"),
    ("Lisa", "Jones"), ("Robert", "Garcia"), ("Maria", "Miller"), ("James", "Davis"),
    ("Amanda", "Rodriguez"), ("Christopher", "Martinez"), ("Jessica", "Hernandez"), ("Matthew", "Lopez"),
    ("Ashley", "Gonzalez"), ("Daniel", "Wilson"), ("Emily", "Anderson"), ("John", "Thomas"),
    ("Samantha", "Taylor"), ("Ryan", "Moore"), ("Nicole", "Jackson"), ("Andrew", "Martin"),
    ("Elizabeth", "Lee"), ("Kevin", "Perez"), ("Rachel", "Thompson"), ("Brandon", "White"),
    ("Stephanie", "Harris"), ("Justin", "Sanchez"), ("Lauren", "Clark"), ("William", "Ramirez"),
    ("Heather", "Lewis"), ("Carlos", "Robinson"), ("Michelle", "Walker"), ("Anthony", "Young"),
    ("Kimberly", "Allen"), ("Mark", "King"), ("Amy", "Wright"), ("Steven", "Scott"),
    ("Donna", "Torres"), ("Kenneth", "Nguyen"), ("Carol", "Hill"), ("Paul", "Flores"),
    ("Sharon", "Green"), ("Jason", "Adams"), ("Deborah", "Nelson"), ("Frank", "Baker"),
    ("Helen", "Hall"), ("Gregory", "Rivera"), ("Angela", "Campbell"), ("Raymond", "Mitchell"),
    ("Brenda", "Carter"), ("Patrick", "Roberts")
]

CITIES = ["Nevada City", "Grass Valley", "Auburn", "Roseville", "Sacramento", "Folsom"]

def create_clients():
    """Create realistic clients via API"""
    base_url = "http://172.22.206.209:3001"
    
    created_count = 0
    for first_name, last_name in NAMES:
        client_data = {
            'first_name': first_name,
            'last_name': last_name,
            'email': f"{first_name.lower()}.{last_name.lower()}@{'gmail.com' if random.random() > 0.3 else random.choice(['yahoo.com', 'outlook.com'])}",
            'phone': f"({random.randint(530,916)}) {random.randint(200,999)}-{random.randint(1000,9999)}",
            'client_type': random.choice(['Buyer', 'Seller', 'Both']),
            'area_preference': f"{random.choice(CITIES)} area"
        }
        
        try:
            # Create client via API
            response = requests.post(f"{base_url}/api/clients", json=client_data, timeout=5)
            if response.status_code in [200, 201]:
                created_count += 1
                print(f"✅ Created client: {first_name} {last_name}")
            else:
                print(f"⚠️ Failed to create {first_name} {last_name}: {response.status_code}")
        except Exception as e:
            print(f"❌ Error creating {first_name} {last_name}: {e}")
    
    print(f"\n📊 Created {created_count} clients successfully")

def create_properties():
    """Create realistic properties via API"""
    base_url = "http://172.22.206.209:3001"
    
    street_names = ["Oak St", "Pine Ave", "Main St", "Cedar Dr", "Maple Ln", "Hill Way", "Valley Ct"]
    property_types = ["Single Family", "Townhome", "Condo", "Multi-Family"]
    
    created_count = 0
    for i in range(30):
        property_data = {
            'address': f"{random.randint(100,9999)} {random.choice(street_names)}",
            'city': random.choice(CITIES),
            'state': 'CA',
            'zip_code': random.choice([95945, 95949, 95959, 95603]),
            'property_type': random.choice(property_types),
            'bedrooms': random.randint(2, 5),
            'bathrooms': random.randint(1, 4),
            'square_feet': random.randint(1200, 4000),
            'listing_price': random.randint(350000, 800000),
        }
        
        try:
            # Create property via API  
            response = requests.post(f"{base_url}/api/properties", json=property_data, timeout=5)
            if response.status_code in [200, 201]:
                created_count += 1
                print(f"✅ Created property: {property_data['address']}, {property_data['city']}")
            else:
                print(f"⚠️ Failed to create property: {response.status_code}")
        except Exception as e:
            print(f"❌ Error creating property: {e}")
    
    print(f"\n🏠 Created {created_count} properties successfully")

if __name__ == "__main__":
    print("🚀 Populating CRM with dummy data...")
    create_clients()
    create_properties()
    print("\n✅ CRM population complete!")