#!/usr/bin/env python3
"""
Enhance the client database with all the missing fields to make it truly robust
"""

import sqlite3

def enhance_client_database():
    conn = sqlite3.connect('/app/real_estate_crm.db')
    cursor = conn.cursor()
    
    print("🚀 Enhancing client database to be truly robust...")
    
    # List of columns to add (from the original 177-field schema)
    columns_to_add = [
        # Contact Information
        ('mobile_phone', 'TEXT'),
        ('work_phone', 'TEXT'),
        ('preferred_contact', 'TEXT DEFAULT "email"'),
        ('address_line1', 'TEXT'),
        ('address_line2', 'TEXT'),
        ('state', 'TEXT DEFAULT "CA"'),
        ('zip_code', 'TEXT'),
        ('country', 'TEXT DEFAULT "USA"'),
        
        # Personal Information
        ('date_of_birth', 'DATE'),
        ('occupation', 'TEXT'),
        ('employer', 'TEXT'),
        ('annual_income', 'REAL'),
        ('credit_score', 'INTEGER'),
        
        # Pre-Approval Information
        ('pre_approval_amount', 'REAL'),
        ('pre_approval_date', 'DATE'),
        ('pre_approval_lender', 'TEXT'),
        
        # Lead Tracking
        ('lead_source', 'TEXT'),
        ('referral_source', 'TEXT'),
        ('first_contact_date', 'DATE'),
        ('lead_status', 'TEXT'),
        
        # Spouse/Partner Information
        ('spouse_name', 'TEXT'),
        ('spouse_email', 'TEXT'),
        ('spouse_phone', 'TEXT'),
        ('spouse_occupation', 'TEXT'),
        
        # Emergency Contact
        ('emergency_contact_name', 'TEXT'),
        ('emergency_contact_phone', 'TEXT'),
        ('emergency_contact_relationship', 'TEXT'),
        
        # Preferences
        ('budget_min', 'REAL'),
        ('budget_max', 'REAL'),
        ('preferred_locations', 'TEXT'),
        ('property_type_preference', 'TEXT'),
        ('bedrooms_min', 'INTEGER'),
        ('bathrooms_min', 'REAL'),
        ('square_feet_min', 'INTEGER'),
        ('lot_size_preference', 'TEXT'),
        ('must_have_features', 'TEXT'),
        ('deal_breakers', 'TEXT'),
        
        # Timeline
        ('looking_to_buy_date', 'DATE'),
        ('lease_end_date', 'DATE'),
        ('motivation_level', 'TEXT'),
        ('pre_qualified', 'BOOLEAN DEFAULT 0'),
        
        # Communication History
        ('notes', 'TEXT'),
        ('last_contact_date', 'DATE'),
        ('next_followup_date', 'DATE'),
        ('preferred_communication_time', 'TEXT'),
        
        # Social Media
        ('facebook', 'TEXT'),
        ('instagram', 'TEXT'),
        ('linkedin', 'TEXT'),
        
        # Additional Professional Info
        ('realtor_in_other_state', 'BOOLEAN DEFAULT 0'),
        ('previous_agent', 'TEXT'),
        ('how_heard_about_us', 'TEXT'),
        
        # Timestamps
        ('updated_at', 'TIMESTAMP'),
        ('last_activity_date', 'TIMESTAMP')
    ]
    
    # Get existing columns
    cursor.execute("PRAGMA table_info(clients)")
    existing_columns = {col[1] for col in cursor.fetchall()}
    
    # Add missing columns
    added = 0
    for col_name, col_type in columns_to_add:
        if col_name not in existing_columns:
            try:
                cursor.execute(f"ALTER TABLE clients ADD COLUMN {col_name} {col_type}")
                added += 1
                print(f"  ✅ Added {col_name}")
            except sqlite3.OperationalError as e:
                if "duplicate column" not in str(e):
                    print(f"  ❌ Error adding {col_name}: {e}")
    
    conn.commit()
    
    # Verify final column count
    cursor.execute("PRAGMA table_info(clients)")
    final_columns = cursor.fetchall()
    
    print(f"\n✅ Client database enhanced!")
    print(f"   Added {added} new columns")
    print(f"   Total columns now: {len(final_columns)}")
    
    # Show categories of information we now track
    print("\n📊 Client Information Categories:")
    print("   • Basic Info (name, email, phones)")
    print("   • Full Address Details")
    print("   • Financial Profile (income, credit, pre-approval)")
    print("   • Personal Details (DOB, occupation, employer)")
    print("   • Family Info (spouse, emergency contact)")
    print("   • Property Preferences (budget, location, features)")
    print("   • Lead Tracking (source, status, timeline)")
    print("   • Communication History")
    print("   • Social Media Profiles")
    
    conn.close()

if __name__ == "__main__":
    enhance_client_database()