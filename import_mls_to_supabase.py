#!/usr/bin/env python3
"""
Import MLS Listings from CSV to Supabase
Real Estate CRM - Cloud Migration Script
"""

import csv
import requests
import json
from decimal import Decimal

# Supabase Configuration
SUPABASE_URL = "https://pfcdqrxnjyarhueofrsn.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBmY2Rxcnhuanlhcmh1ZW9mcnNuIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0ODgxNTIzMSwiZXhwIjoyMDY0MzkxMjMxfQ.V2xwZbGrxqFIanYl_ZN84xS8BzlSpZ36pIRV3y1s-4Q"
CSV_FILE = "Listing.csv"

def import_mls_listings():
    """Import MLS listings from CSV to Supabase properties table"""
    
    print("🏠 Starting MLS Import to Supabase...")
    
    # Read CSV file
    with open(CSV_FILE, 'r') as file:
        csv_reader = csv.DictReader(file)
        listings = list(csv_reader)
    
    print(f"📊 Found {len(listings)} listings to import")
    
    # Import each listing
    imported_count = 0
    for listing in listings:
        try:
            # Map CSV fields to Supabase schema
            property_data = {
                "mls_number": listing["Listing Number"],
                "street_address": listing["Property_Address"],
                "city": listing["City"],
                "state": listing["State"],
                "zip_code": listing["Zip"],
                "listed_price": float(listing["Price"]),
                "bedrooms": int(listing["Bedrooms"]),
                "bathrooms": float(listing["Bathrooms"]),
                "square_feet": int(listing["Square_Feet"]),
                "property_type": listing["Property_Type"],
                "status": listing["Status"].lower()
            }
            
            # Insert into Supabase
            response = requests.post(
                f"{SUPABASE_URL}/rest/v1/properties",
                headers={
                    "apikey": SUPABASE_KEY,
                    "Authorization": f"Bearer {SUPABASE_KEY}",
                    "Content-Type": "application/json",
                    "Prefer": "return=minimal"
                },
                json=property_data
            )
            
            if response.status_code == 201:
                print(f"✅ Imported: {listing['Property_Address']} - ${listing['Price']}")
                imported_count += 1
            else:
                print(f"❌ Failed to import {listing['Property_Address']}: {response.text}")
                
        except Exception as e:
            print(f"❌ Error importing {listing.get('Property_Address', 'Unknown')}: {str(e)}")
    
    print(f"\n🎉 Import completed! {imported_count}/{len(listings)} listings imported successfully")
    
    # Verify import
    print("\n📋 Verifying import...")
    response = requests.get(
        f"{SUPABASE_URL}/rest/v1/properties?select=mls_number,street_address,city,listed_price",
        headers={
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}"
        }
    )
    
    if response.status_code == 200:
        properties = response.json()
        print(f"✅ Total properties in database: {len(properties)}")
        for prop in properties:
            if prop.get('mls_number'):
                print(f"   MLS #{prop['mls_number']}: {prop['street_address']}, {prop['city']} - ${prop['listed_price']}")
    else:
        print(f"❌ Failed to verify: {response.text}")

if __name__ == "__main__":
    import_mls_listings()