#!/usr/bin/env python3
"""
Fix schema and load real MLS listings
"""

import sqlite3
import csv
import os
import re

def fix_schema():
    """Add missing status column"""
    conn = sqlite3.connect('/app/real_estate_crm.db')
    cursor = conn.cursor()
    
    print("🔧 Adding status column to properties table...")
    
    try:
        cursor.execute("ALTER TABLE properties ADD COLUMN status TEXT DEFAULT 'Active'")
        print("✅ Added status column")
    except sqlite3.OperationalError as e:
        if "duplicate column" in str(e):
            print("✅ Status column already exists")
        else:
            print(f"⚠️  Error: {e}")
    
    conn.commit()
    conn.close()

def parse_bedrooms(bedroom_str):
    """Parse bedroom count from strings like '3', '4 (5)', etc."""
    if not bedroom_str:
        return 0
    
    # Extract first number from string
    match = re.search(r'(\d+)', str(bedroom_str))
    if match:
        return int(match.group(1))
    return 0

def load_mls_listings():
    """Load real Nevada County MLS listings"""
    
    csv_path = '/app/documents/canonicalListing.csv'
    db_path = '/app/real_estate_crm.db'
    
    if not os.path.exists(csv_path):
        print(f"❌ CSV file not found: {csv_path}")
        return
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("🏠 Loading real MLS listings from Nevada County...")
    
    # Clear existing dummy properties
    cursor.execute("DELETE FROM properties WHERE mls_number LIKE 'MLS%'")
    print("✅ Cleared dummy properties")
    
    # Read CSV and insert listings
    with open(csv_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        count = 0
        errors = 0
        
        for row in reader:
            try:
                # Extract and clean data
                street_address = row.get('Address - Street Complete', '').strip()
                city = row.get('Address - City', '').strip()
                zip_code = row.get('Address - Zip Code', '').strip()
                list_price = float(row.get('List Price', '0').replace(',', '') or 0)
                bedrooms = parse_bedrooms(row.get('Bedrooms And Possible Bedrooms', '0'))
                bathrooms = float(row.get('Full Bathrooms', '0') or 0)
                
                # Parse square footage - handle bad data
                sq_ft_str = row.get('Square Footage', '0').replace(',', '')
                try:
                    square_feet = int(sq_ft_str) if sq_ft_str.isdigit() else 0
                except:
                    square_feet = 0
                
                property_type = row.get('Property Type', 'Residential')
                mls_number = row.get('Listing Number', '').strip()
                year_built = row.get('Year Built Details', '')
                status = row.get('Status', 'Active')
                
                # Skip if missing critical data
                if not street_address or not city or not mls_number:
                    continue
                
                # Insert into database
                cursor.execute('''
                    INSERT INTO properties 
                    (street_address, city, state, zip_code, listing_price, listed_price,
                     bedrooms, bathrooms, square_feet, property_type, mls_number,
                     created_at, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), ?)
                ''', (
                    street_address, city, 'CA', zip_code, list_price, list_price,
                    bedrooms, bathrooms, square_feet, property_type, mls_number,
                    status
                ))
                
                count += 1
                
                # Show progress every 100 records
                if count % 100 == 0:
                    print(f"  Loaded {count} properties...")
                    conn.commit()  # Commit in batches
                    
            except Exception as e:
                errors += 1
                if errors < 5:  # Only show first few errors
                    print(f"  ⚠️  Error loading {row.get('Listing Number', 'unknown')}: {e}")
                continue
    
    conn.commit()
    print(f"\n✅ Successfully loaded {count} real MLS listings!")
    print(f"   ({errors} records skipped due to errors)")
    
    # Show sample of loaded properties
    cursor.execute('''
        SELECT street_address, city, listing_price, bedrooms, bathrooms, mls_number, status
        FROM properties 
        WHERE mls_number NOT LIKE 'MLS%'
        ORDER BY created_at DESC
        LIMIT 5
    ''')
    
    print("\n📋 Sample of loaded properties:")
    for prop in cursor.fetchall():
        print(f"  • {prop[0]}, {prop[1]} - ${prop[2]:,.0f} - {prop[3]}BR/{prop[4]}BA - MLS#{prop[5]} ({prop[6]})")
    
    # Show summary by city
    cursor.execute('''
        SELECT city, COUNT(*) as count, AVG(listing_price) as avg_price
        FROM properties 
        WHERE mls_number NOT LIKE 'MLS%'
        GROUP BY city
        ORDER BY count DESC
        LIMIT 10
    ''')
    
    print("\n📊 Properties by city:")
    for city_data in cursor.fetchall():
        print(f"  • {city_data[0]}: {city_data[1]} properties (avg ${city_data[2]:,.0f})")
    
    conn.close()

if __name__ == "__main__":
    fix_schema()
    load_mls_listings()