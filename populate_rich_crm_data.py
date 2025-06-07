#!/usr/bin/env python3
"""
Populate CRM with rich dummy data using real MLS data as inspiration
Creates realistic clients, properties, and transactions for comprehensive form testing
"""

import csv
import random
import sqlite3
import os
from datetime import datetime, timedelta

# Read real MLS data for inspiration
def load_mls_inspiration():
    """Load real MLS addresses and details for realistic dummy data"""
    mls_data = []
    try:
        with open('Listing.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                mls_data.append({
                    'address': row.get('Address - Street Complete', '').strip(),
                    'city': row.get('Address - City', '').strip(),
                    'zip_code': row.get('Address - Zip Code', '').strip(),
                    'price': float(row.get('List Price', 0) or 0),
                    'sqft': int(row.get('Square Footage', 0) or 0),
                    'bedrooms': row.get('Bedrooms And Possible Bedrooms', '').strip(),
                    'year_built': row.get('Year Built Details', '').strip()
                })
    except Exception as e:
        print(f"⚠️ Could not load MLS data: {e}")
    
    return [m for m in mls_data if m['address'] and m['city']][:100]  # Top 100 real properties

# Rich client data pools
FIRST_NAMES = [
    "Jennifer", "Michael", "Sarah", "David", "Lisa", "Robert", "Maria", "James",
    "Amanda", "Christopher", "Jessica", "Matthew", "Ashley", "Daniel", "Emily",
    "John", "Samantha", "Ryan", "Nicole", "Andrew", "Elizabeth", "Kevin",
    "Rachel", "Brandon", "Stephanie", "Justin", "Lauren", "William", "Heather",
    "Carlos", "Michelle", "Anthony", "Kimberly", "Mark", "Amy", "Steven",
    "Donna", "Kenneth", "Carol", "Paul", "Sharon", "Jason", "Deborah", "Frank",
    "Helen", "Gregory", "Angela", "Raymond", "Brenda", "Patrick", "Laura"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
    "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson",
    "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson",
    "Walker", "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen",
    "Hill", "Flores", "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera",
    "Campbell", "Mitchell", "Carter", "Roberts", "Gomez", "Phillips"
]

PROFESSIONS = [
    "Software Engineer", "Teacher", "Nurse", "Sales Manager", "Business Owner",
    "Real Estate Agent", "Contractor", "Accountant", "Doctor", "Attorney",
    "Consultant", "Marketing Manager", "Project Manager", "Retired",
    "Engineer", "Therapist", "Police Officer", "Firefighter", "Chef",
    "Designer", "Photographer", "Writer", "Mechanic", "Electrician"
]

CITIES = ["Nevada City", "Grass Valley", "Auburn", "Roseville", "Folsom", "Penn Valley"]

def create_realistic_client(mls_property=None):
    """Create a comprehensive client with realistic financial and personal details"""
    first_name = random.choice(FIRST_NAMES)
    last_name = random.choice(LAST_NAMES)
    profession = random.choice(PROFESSIONS)
    
    # Generate realistic income based on profession
    income_ranges = {
        "Doctor": (200000, 600000),
        "Attorney": (150000, 400000), 
        "Software Engineer": (100000, 200000),
        "Business Owner": (80000, 300000),
        "Sales Manager": (70000, 150000),
        "Real Estate Agent": (60000, 180000),
        "Engineer": (80000, 140000),
        "Accountant": (55000, 120000),
        "Nurse": (65000, 110000),
        "Teacher": (45000, 85000),
        "Retired": (40000, 90000)
    }
    
    income_range = income_ranges.get(profession, (45000, 120000))
    annual_income = random.randint(*income_range)
    
    # Calculate realistic budget based on income
    budget_multiplier = random.uniform(3.5, 5.5)
    max_budget = int(annual_income * budget_multiplier)
    min_budget = int(max_budget * 0.7)
    
    # Use real MLS property data if provided
    if mls_property:
        city = mls_property['city']
        # Adjust budget to be realistic for the property
        if mls_property['price'] > 0:
            max_budget = int(mls_property['price'] * random.uniform(1.1, 1.4))
            min_budget = int(max_budget * 0.8)
    else:
        city = random.choice(CITIES)
    
    # Generate comprehensive client data
    return {
        'first_name': first_name,
        'last_name': last_name,
        'email': f"{first_name.lower()}.{last_name.lower()}@{random.choice(['gmail.com', 'yahoo.com', 'outlook.com', 'icloud.com'])}",
        'phone': f"({random.randint(530, 916)}) {random.randint(200, 999)}-{random.randint(1000, 9999)}",
        'client_type': random.choice(['Buyer', 'Seller', 'Both']),
        'preferred_contact': random.choice(['Email', 'Phone', 'Text']),
        
        # Financial details
        'annual_income': annual_income,
        'employment_status': 'Employed' if profession != 'Retired' else 'Retired',
        'job_title': profession,
        'employer_name': f"{random.choice(['Tech Solutions', 'Healthcare Group', 'Education District', 'Construction Co', 'Consulting LLC', 'Manufacturing Inc', 'Services Corp'])}",
        'additional_income': random.randint(0, 30000) if random.random() > 0.6 else 0,
        'credit_score': random.randint(650, 850),
        'debt_to_income_ratio': round(random.uniform(0.1, 0.4), 2),
        
        # Property preferences  
        'budget_min': min_budget,
        'budget_max': max_budget,
        'bedrooms_min': random.randint(2, 3),
        'bedrooms_max': random.randint(3, 5),
        'bathrooms_min': random.randint(1, 2),
        'bathrooms_max': random.randint(2, 4),
        'square_feet_min': random.randint(1200, 2000),
        'square_feet_max': random.randint(2200, 4000),
        'area_preference': f"{city} and surrounding areas",
        'property_type_preference': random.choice(['Single Family', 'Townhome', 'Condo']),
        
        # Financing
        'financing_type': random.choice(['Conventional', 'FHA', 'VA', 'Cash', 'USDA']),
        'down_payment_amount': int(max_budget * random.uniform(0.1, 0.25)),
        'pre_approval_amount': int(max_budget * random.uniform(1.05, 1.2)),
        'pre_approval_status': random.choice(['Pre-approved', 'Pre-qualified', 'In Process']),
        'lender_name': random.choice(['Wells Fargo', 'Bank of America', 'Chase', 'Local Credit Union', 'Rocket Mortgage', 'Quicken Loans']),
        
        # Personal details
        'notes': f"Client seeking {random.choice(['starter home', 'family home', 'upgrade', 'retirement home', 'investment property'])} in {city}. {random.choice(['First-time buyer', 'Repeat buyer', 'Relocating for work', 'Growing family', 'Empty nesters'])}.",
        'created_at': (datetime.now() - timedelta(days=random.randint(1, 365))).isoformat(),
        'updated_at': (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat()
    }

def create_client_property(client_data, mls_inspiration=None):
    """Create a property that a client currently owns (separate from MLS listings)"""
    
    # Use MLS data as inspiration but modify for owned properties
    if mls_inspiration:
        base_address = mls_inspiration['address']
        city = mls_inspiration['city']
        zip_code = mls_inspiration['zip_code']
        # Reduce price for owned vs listed properties
        market_value = int(mls_inspiration['price'] * random.uniform(0.8, 0.95)) if mls_inspiration['price'] else random.randint(300000, 800000)
        sqft = mls_inspiration['sqft'] if mls_inspiration['sqft'] else random.randint(1200, 3000)
    else:
        base_address = f"{random.randint(1000, 9999)} {random.choice(['Oak', 'Pine', 'Main', 'Cedar', 'Maple', 'Hill', 'Valley', 'Ridge'])} {random.choice(['St', 'Ave', 'Dr', 'Ln', 'Ct', 'Way'])}"
        city = random.choice(CITIES)
        zip_code = random.choice([95945, 95949, 95959, 95603, 95602])
        market_value = random.randint(350000, 750000)
        sqft = random.randint(1200, 3000)
    
    # Generate different address for owned property
    address_parts = base_address.split()
    if len(address_parts) >= 2:
        # Change street number
        new_number = random.randint(1000, 9999)
        address = f"{new_number} {' '.join(address_parts[1:])}"
    else:
        address = f"{random.randint(1000, 9999)} {base_address}"
    
    purchase_price = int(market_value * random.uniform(0.7, 0.9))
    
    return {
        'address': address,
        'city': city,
        'state': 'CA',
        'zip_code': zip_code,
        'property_type': random.choice(['Single Family', 'Townhome', 'Condo', 'Multi-Family']),
        'bedrooms': random.randint(2, 5),
        'bathrooms': round(random.uniform(1.5, 4.0), 1),
        'square_feet': sqft,
        'lot_size': round(random.uniform(0.1, 1.5), 2),
        'year_built': random.randint(1970, 2020),
        'purchase_price': purchase_price,
        'current_value': market_value,
        'property_tax': int(market_value * 0.012),  # 1.2% property tax
        'hoa_fees': random.randint(0, 250) if random.random() > 0.6 else 0,
        'listing_status': 'Not Listed',  # These are owned properties, not for sale
        'created_at': (datetime.now() - timedelta(days=random.randint(30, 1000))).isoformat()
    }

def populate_database_comprehensively():
    """Populate CRM with realistic, comprehensive data"""
    
    print("🔍 Loading MLS data for inspiration...")
    mls_inspiration = load_mls_inspiration()
    print(f"📊 Loaded {len(mls_inspiration)} MLS properties for inspiration")
    
    # Find database
    db_paths = ['real_estate_crm.db', 'real_estate.db', 'core_app/real_estate_crm.db']
    db_path = None
    
    for path in db_paths:
        if os.path.exists(path):
            db_path = path
            break
    
    if not db_path:
        print("❌ Could not find CRM database")
        return
    
    print(f"📊 Using database: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Clear existing dummy data but keep any real client data
        cursor.execute("DELETE FROM properties WHERE address LIKE '%Main St%' OR city = 'Sacramento'")
        cursor.execute("DELETE FROM clients WHERE email LIKE '%@gmail.com' OR email LIKE '%@yahoo.com' OR first_name IN ('John', 'Jane')")
        
        print("🚀 Creating 60 comprehensive client records...")
        
        client_ids = []
        for i in range(60):
            # Use MLS property as inspiration for some clients
            mls_prop = random.choice(mls_inspiration) if mls_inspiration and random.random() > 0.3 else None
            client = create_realistic_client(mls_prop)
            
            # Insert client with comprehensive data
            cursor.execute("""
                INSERT INTO clients (
                    first_name, last_name, email, phone, client_type, preferred_contact,
                    annual_income, employment_status, job_title, employer_name, additional_income,
                    credit_score, debt_to_income_ratio, budget_min, budget_max,
                    bedrooms_min, bedrooms_max, bathrooms_min, bathrooms_max,
                    square_feet_min, square_feet_max, area_preference, property_type_preference,
                    financing_type, down_payment_amount, pre_approval_amount, pre_approval_status,
                    lender_name, notes, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                client['first_name'], client['last_name'], client['email'], client['phone'],
                client['client_type'], client['preferred_contact'], client['annual_income'],
                client['employment_status'], client['job_title'], client['employer_name'],
                client['additional_income'], client['credit_score'], client['debt_to_income_ratio'],
                client['budget_min'], client['budget_max'], client['bedrooms_min'], client['bedrooms_max'],
                client['bathrooms_min'], client['bathrooms_max'], client['square_feet_min'],
                client['square_feet_max'], client['area_preference'], client['property_type_preference'],
                client['financing_type'], client['down_payment_amount'], client['pre_approval_amount'],
                client['pre_approval_status'], client['lender_name'], client['notes'],
                client['created_at'], client['updated_at']
            ))
            
            client_ids.append(cursor.lastrowid)
            if (i + 1) % 10 == 0:
                print(f"   ✅ Created {i + 1} clients...")
        
        print("🏠 Creating 40 client-owned properties...")
        
        # Create properties for 40 clients (some clients don't own property yet)
        property_clients = random.sample(client_ids, 40)
        for i, client_id in enumerate(property_clients):
            # Use MLS data as inspiration
            mls_prop = random.choice(mls_inspiration) if mls_inspiration else None
            property_data = create_client_property({}, mls_prop)
            
            cursor.execute("""
                INSERT INTO properties (
                    address, city, state, zip_code, property_type, bedrooms, bathrooms,
                    square_feet, lot_size, year_built, purchase_price, current_value,
                    property_tax, hoa_fees, listing_status, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                property_data['address'], property_data['city'], property_data['state'],
                property_data['zip_code'], property_data['property_type'], property_data['bedrooms'],
                property_data['bathrooms'], property_data['square_feet'], property_data['lot_size'],
                property_data['year_built'], property_data['purchase_price'], property_data['current_value'],
                property_data['property_tax'], property_data['hoa_fees'], property_data['listing_status'],
                property_data['created_at']
            ))
            
            if (i + 1) % 10 == 0:
                print(f"   ✅ Created {i + 1} properties...")
        
        conn.commit()
        
        # Verify comprehensive data
        cursor.execute("SELECT COUNT(*) FROM clients")
        client_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM properties")
        property_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT AVG(annual_income), MIN(annual_income), MAX(annual_income) FROM clients WHERE annual_income > 0")
        income_stats = cursor.fetchone()
        
        cursor.execute("SELECT AVG(budget_max), MIN(budget_max), MAX(budget_max) FROM clients WHERE budget_max > 0")
        budget_stats = cursor.fetchone()
        
        print(f"\n🎉 CRM COMPREHENSIVELY POPULATED!")
        print(f"📊 Total Clients: {client_count}")
        print(f"🏠 Total Properties: {property_count}")
        print(f"💰 Income Range: ${income_stats[1]:,.0f} - ${income_stats[2]:,.0f} (avg: ${income_stats[0]:,.0f})")
        print(f"🏡 Budget Range: ${budget_stats[1]:,.0f} - ${budget_stats[2]:,.0f} (avg: ${budget_stats[0]:,.0f})")
        print(f"📍 Cities: {', '.join(CITIES)}")
        print(f"💼 Professions: {len(PROFESSIONS)} different job types")
        print(f"🎯 Credit Scores: 650-850 range")
        print(f"🏦 Financing: Multiple loan types and lenders")
        print(f"\n✅ Ready for comprehensive form population testing!")
        
    except Exception as e:
        print(f"❌ Error populating database: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    populate_database_comprehensively()