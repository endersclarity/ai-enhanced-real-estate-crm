#!/usr/bin/env python3
"""
Property URL Generator
Automatically generates real estate portal URLs from property data
"""

import re
import sqlite3
from urllib.parse import quote

def clean_address_for_url(address, city, state, zip_code):
    """Clean and format address for URL generation"""
    # Combine full address
    full_address = f"{address} {city} {state} {zip_code}"
    
    # Clean and format for URL
    cleaned = re.sub(r'[^\w\s-]', '', full_address)  # Remove special chars except hyphens
    cleaned = re.sub(r'\s+', '-', cleaned.strip())   # Replace spaces with hyphens
    cleaned = cleaned.lower()                         # Lowercase
    
    return cleaned

def generate_property_urls(street_address, city, state, zip_code, mls_number=None):
    """Generate URLs for major real estate portals"""
    
    # Clean address for URL
    address_slug = clean_address_for_url(street_address, city, state, zip_code)
    
    # Generate URLs
    urls = {
        'zillow_url': f"https://www.zillow.com/homes/{address_slug}",
        'realtor_url': f"https://www.realtor.com/realestateandhomes-search/{city.replace(' ', '-').lower()}-{state.lower()}-{zip_code}",
        'mls_portal_url': f"https://www.mlslistings.com/property/{mls_number}" if mls_number else None
    }
    
    return urls

def update_all_property_urls():
    """Update all properties in database with generated URLs"""
    conn = sqlite3.connect('real_estate_crm.db')
    cursor = conn.cursor()
    
    # Get all properties
    cursor.execute("""
        SELECT id, street_address, city, state, zip_code, mls_number 
        FROM properties 
        WHERE zillow_url IS NULL OR realtor_url IS NULL
    """)
    
    properties = cursor.fetchall()
    updated_count = 0
    
    for prop in properties:
        prop_id, street_address, city, state, zip_code, mls_number = prop
        
        if not street_address or not city or not state:
            continue
            
        # Generate URLs
        urls = generate_property_urls(street_address, city, state, zip_code, mls_number)
        
        # Update database
        cursor.execute("""
            UPDATE properties 
            SET zillow_url = ?, realtor_url = ?, mls_portal_url = ?
            WHERE id = ?
        """, (urls['zillow_url'], urls['realtor_url'], urls['mls_portal_url'], prop_id))
        
        updated_count += 1
        print(f"✅ Updated URLs for: {street_address}, {city}")
    
    conn.commit()
    conn.close()
    
    print(f"🎯 Updated {updated_count} properties with real estate portal URLs")
    return updated_count

def test_url_generation():
    """Test URL generation with sample data"""
    test_data = [
        ("123 Main St", "Sacramento", "CA", "95814", "22472271"),
        ("456 Oak Ave", "Davis", "CA", "95616", "22412695"),
        ("789 Pine Dr", "Folsom", "CA", "95630", "22425097")
    ]
    
    print("🧪 Testing URL generation:")
    for address, city, state, zip_code, mls in test_data:
        urls = generate_property_urls(address, city, state, zip_code, mls)
        print(f"\n📍 {address}, {city}, {state} {zip_code}")
        print(f"   Zillow: {urls['zillow_url']}")
        print(f"   Realtor: {urls['realtor_url']}")
        print(f"   MLS: {urls['mls_portal_url']}")

if __name__ == "__main__":
    print("🏠 Property URL Generator")
    print("=" * 50)
    
    # Test first
    test_url_generation()
    
    print("\n" + "=" * 50)
    
    # Update all properties
    update_all_property_urls()