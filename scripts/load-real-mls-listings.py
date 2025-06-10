#!/usr/bin/env python3
"""
Load real MLS listings from canonicalListing.csv into the database
"""

import sqlite3
import csv
import os
from datetime import datetime

def load_mls_listings():
    """Load real Nevada County MLS listings into the database"""
    
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
        
        for row in reader:
            try:
                # Extract and clean data
                street_address = row.get('Address - Street Complete', '')
                city = row.get('Address - City', '')
                zip_code = row.get('Address - Zip Code', '')
                list_price = float(row.get('List Price', '0').replace(',', '') or 0)
                bedrooms = int(row.get('Bedrooms And Possible Bedrooms', '0') or 0)
                bathrooms = float(row.get('Full Bathrooms', '0') or 0)
                square_feet = int(row.get('Square Footage', '0').replace(',', '') or 0)
                property_type = row.get('Property Type', 'Residential')
                mls_number = row.get('Listing Number', '')
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
                    
            except Exception as e:
                print(f"  ⚠️  Error loading {row.get('Listing Number', 'unknown')}: {e}")
                continue
    
    conn.commit()
    print(f"\n✅ Successfully loaded {count} real MLS listings!")
    
    # Show sample of loaded properties
    cursor.execute('''
        SELECT street_address, city, listing_price, bedrooms, bathrooms, mls_number
        FROM properties 
        WHERE mls_number NOT LIKE 'MLS%'
        ORDER BY created_at DESC
        LIMIT 5
    ''')
    
    print("\n📋 Sample of loaded properties:")
    for prop in cursor.fetchall():
        print(f"  • {prop[0]}, {prop[1]} - ${prop[2]:,.0f} - {prop[3]}BR/{prop[4]}BA - MLS#{prop[5]}")
    
    conn.close()

if __name__ == "__main__":
    load_mls_listings()