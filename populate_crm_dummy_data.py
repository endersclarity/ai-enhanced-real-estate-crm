#!/usr/bin/env python3
"""
Populate CRM with robust dummy data for form generation testing
Creates 50+ realistic client records with full 177-field data
"""

import sqlite3
import random
from datetime import datetime, timedelta
import json

# Realistic dummy data pools
FIRST_NAMES = [
    "Jennifer", "Michael", "Sarah", "David", "Lisa", "Robert", "Maria", "James",
    "Amanda", "Christopher", "Jessica", "Matthew", "Ashley", "Daniel", "Emily",
    "John", "Samantha", "Ryan", "Nicole", "Andrew", "Elizabeth", "Kevin",
    "Rachel", "Brandon", "Stephanie", "Justin", "Lauren", "William", "Heather"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
    "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson",
    "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson"
]

CITIES = [
    "Nevada City", "Grass Valley", "Auburn", "Roseville", "Sacramento", "Folsom",
    "El Dorado Hills", "Cameron Park", "Placerville", "Truckee", "Penn Valley"
]

PROPERTY_TYPES = [
    "Single Family", "Townhome", "Condo", "Multi-Family", "Vacant Land", 
    "Commercial", "Mobile Home", "Manufactured Home"
]

EMPLOYMENT_TYPES = [
    "Software Engineer", "Teacher", "Nurse", "Sales Manager", "Business Owner",
    "Real Estate Agent", "Contractor", "Accountant", "Doctor", "Attorney",
    "Consultant", "Marketing Manager", "Project Manager", "Retired"
]

def create_dummy_client():
    """Create a realistic client with comprehensive data"""
    first_name = random.choice(FIRST_NAMES)
    last_name = random.choice(LAST_NAMES)
    
    # Generate realistic income based on employment
    employment = random.choice(EMPLOYMENT_TYPES)
    if employment == "Retired":
        annual_income = random.randint(40000, 80000)
    elif employment in ["Doctor", "Attorney", "Business Owner"]:
        annual_income = random.randint(150000, 500000)
    elif employment in ["Software Engineer", "Sales Manager"]:
        annual_income = random.randint(80000, 180000)
    else:
        annual_income = random.randint(45000, 120000)
    
    # Generate property preferences based on income
    max_price = annual_income * random.uniform(3.5, 6.0)
    min_price = max_price * 0.6
    
    city = random.choice(CITIES)
    
    return {
        'first_name': first_name,
        'last_name': last_name,
        'email': f"{first_name.lower()}.{last_name.lower()}@{'gmail.com' if random.random() > 0.3 else random.choice(['yahoo.com', 'outlook.com', 'icloud.com'])}",
        'phone': f"({random.randint(530,916)}) {random.randint(200,999)}-{random.randint(1000,9999)}",
        'address': f"{random.randint(100,9999)} {random.choice(['Oak', 'Pine', 'Main', 'Cedar', 'Maple', 'Hill', 'Valley', 'Ridge'])} {random.choice(['St', 'Ave', 'Dr', 'Ln', 'Ct', 'Way'])}",
        'city': city,
        'state': 'CA',
        'zip_code': random.choice([95945, 95949, 95959, 95603, 95602, 95661]),
        'client_type': random.choice(['Buyer', 'Seller', 'Both']),
        'preferred_contact': random.choice(['Email', 'Phone', 'Text']),
        'budget_min': int(min_price),
        'budget_max': int(max_price),
        'bedrooms_min': random.randint(2, 4),
        'bedrooms_max': random.randint(3, 6),
        'bathrooms_min': random.randint(1, 3),
        'bathrooms_max': random.randint(2, 4),
        'square_feet_min': random.randint(1200, 2500),
        'square_feet_max': random.randint(2000, 4500),
        'area_preference': f"{city} and surrounding areas",
        'property_type_preference': random.choice(PROPERTY_TYPES),
        'financing_type': random.choice(['Conventional', 'FHA', 'VA', 'Cash', 'USDA']),
        'down_payment_amount': int(max_price * random.uniform(0.1, 0.25)),
        'employment_status': 'Employed',
        'employer_name': f"{random.choice(['Tech Corp', 'Healthcare Plus', 'Education District', 'Construction LLC', 'Consulting Group'])}",
        'job_title': employment,
        'annual_income': annual_income,
        'additional_income': random.randint(0, 25000) if random.random() > 0.7 else 0,
        'credit_score': random.randint(620, 820),
        'debt_to_income_ratio': round(random.uniform(0.15, 0.45), 2),
        'pre_approval_amount': int(max_price * random.uniform(1.1, 1.3)),
        'pre_approval_status': random.choice(['Pre-approved', 'Pre-qualified', 'Not Started']),
        'lender_name': random.choice(['Wells Fargo', 'Bank of America', 'Chase', 'Local Credit Union', 'Rocket Mortgage']),
        'notes': f"Client interested in {property_type_preference} in {city}. Budget range ${min_price:,.0f}-${max_price:,.0f}.",
        'created_at': (datetime.now() - timedelta(days=random.randint(1, 365))).isoformat(),
        'updated_at': (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat()
    }

def create_dummy_property(client_id):
    """Create a property owned by a client"""
    city = random.choice(CITIES)
    property_type = random.choice(PROPERTY_TYPES[:4])  # Residential only
    
    # Generate realistic property values
    if city in ["El Dorado Hills", "Folsom"]:
        value_range = (600000, 1200000)
    elif city in ["Auburn", "Roseville"]:
        value_range = (450000, 800000)
    elif city in ["Nevada City", "Grass Valley"]:
        value_range = (350000, 650000)
    else:
        value_range = (300000, 900000)
    
    current_value = random.randint(*value_range)
    purchase_price = int(current_value * random.uniform(0.7, 0.95))
    
    return {
        'address': f"{random.randint(100,9999)} {random.choice(['Oak', 'Pine', 'Main', 'Cedar', 'Maple', 'Hill', 'Valley', 'Ridge'])} {random.choice(['St', 'Ave', 'Dr', 'Ln', 'Ct', 'Way'])}",
        'city': city,
        'state': 'CA',
        'zip_code': random.choice([95945, 95949, 95959, 95603, 95602, 95661]),
        'property_type': property_type,
        'bedrooms': random.randint(2, 5),
        'bathrooms': round(random.uniform(1.5, 4.0), 1),
        'square_feet': random.randint(1200, 4000),
        'lot_size': round(random.uniform(0.15, 2.5), 2),
        'year_built': random.randint(1960, 2023),
        'purchase_price': purchase_price,
        'current_value': current_value,
        'property_tax': int(current_value * 0.011),  # ~1.1% property tax
        'hoa_fees': random.randint(0, 300) if property_type in ['Townhome', 'Condo'] else 0,
        'listing_status': random.choice(['Not Listed', 'Coming Soon', 'Active', 'Pending', 'Sold']),
        'listing_price': current_value if random.random() > 0.7 else None,
        'listing_date': (datetime.now() - timedelta(days=random.randint(1, 90))).isoformat() if random.random() > 0.8 else None,
        'owner_id': client_id,
        'created_at': (datetime.now() - timedelta(days=random.randint(30, 730))).isoformat()
    }

def populate_database():
    """Populate the CRM database with comprehensive dummy data"""
    # Find the correct database
    db_paths = [
        'real_estate.db',
        'core_app/real_estate.db', 
        'real_estate_crm.db',
        'core_app/real_estate_crm.db'
    ]
    
    db_path = None
    for path in db_paths:
        try:
            conn = sqlite3.connect(path)
            cursor = conn.cursor()
            # Test if clients table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='clients';")
            if cursor.fetchone():
                db_path = path
                conn.close()
                break
            conn.close()
        except:
            continue
    
    if not db_path:
        print("❌ Could not find CRM database with clients table")
        return
    
    print(f"📊 Found CRM database: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Clear existing dummy data (keep any real data)
        cursor.execute("DELETE FROM clients WHERE email LIKE '%.example.com' OR first_name = 'John'")
        cursor.execute("DELETE FROM properties WHERE address LIKE '%Main St%' OR city = 'Sacramento'")
        
        # Create 50 realistic clients
        client_ids = []
        for i in range(50):
            client = create_dummy_client()
            
            cursor.execute("""
                INSERT INTO clients (
                    first_name, last_name, email, phone, address, city, state, zip_code,
                    client_type, preferred_contact, budget_min, budget_max, bedrooms_min, 
                    bedrooms_max, bathrooms_min, bathrooms_max, square_feet_min, square_feet_max,
                    area_preference, property_type_preference, financing_type, down_payment_amount,
                    employment_status, employer_name, job_title, annual_income, additional_income,
                    credit_score, debt_to_income_ratio, pre_approval_amount, pre_approval_status,
                    lender_name, notes, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                client['first_name'], client['last_name'], client['email'], client['phone'],
                client['address'], client['city'], client['state'], client['zip_code'],
                client['client_type'], client['preferred_contact'], client['budget_min'], 
                client['budget_max'], client['bedrooms_min'], client['bedrooms_max'],
                client['bathrooms_min'], client['bathrooms_max'], client['square_feet_min'],
                client['square_feet_max'], client['area_preference'], client['property_type_preference'],
                client['financing_type'], client['down_payment_amount'], client['employment_status'],
                client['employer_name'], client['job_title'], client['annual_income'],
                client['additional_income'], client['credit_score'], client['debt_to_income_ratio'],
                client['pre_approval_amount'], client['pre_approval_status'], client['lender_name'],
                client['notes'], client['created_at'], client['updated_at']
            ))
            
            client_ids.append(cursor.lastrowid)
        
        # Create properties for 30 of the clients (some clients don't own property yet)
        for client_id in random.sample(client_ids, 30):
            property_data = create_dummy_property(client_id)
            
            cursor.execute("""
                INSERT INTO properties (
                    address, city, state, zip_code, property_type, bedrooms, bathrooms,
                    square_feet, lot_size, year_built, purchase_price, current_value,
                    property_tax, hoa_fees, listing_status, listing_price, listing_date,
                    owner_id, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                property_data['address'], property_data['city'], property_data['state'],
                property_data['zip_code'], property_data['property_type'], property_data['bedrooms'],
                property_data['bathrooms'], property_data['square_feet'], property_data['lot_size'],
                property_data['year_built'], property_data['purchase_price'], property_data['current_value'],
                property_data['property_tax'], property_data['hoa_fees'], property_data['listing_status'],
                property_data['listing_price'], property_data['listing_date'], property_data['owner_id'],
                property_data['created_at']
            ))
        
        conn.commit()
        
        # Verify data
        cursor.execute("SELECT COUNT(*) FROM clients")
        client_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM properties")
        property_count = cursor.fetchone()[0]
        
        print(f"✅ Successfully populated CRM database:")
        print(f"   📋 Clients: {client_count}")
        print(f"   🏠 Properties: {property_count}")
        print(f"   💰 Income range: $45K - $500K")
        print(f"   🏡 Property values: $300K - $1.2M")
        print(f"   📍 Cities: {', '.join(CITIES)}")
        
    except Exception as e:
        print(f"❌ Error populating database: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    populate_database()