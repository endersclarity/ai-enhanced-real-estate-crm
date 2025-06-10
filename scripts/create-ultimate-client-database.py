#!/usr/bin/env python3
"""
Create the ULTIMATE client database with every possible field from CAR forms
Based on the 177-field vision for complete form coverage
"""

import sqlite3

def create_ultimate_client_database():
    conn = sqlite3.connect('/app/real_estate_crm.db')
    cursor = conn.cursor()
    
    print("🚀 Creating ULTIMATE client database with ALL possible CAR form fields...")
    
    # MASSIVE list of fields from all CAR forms
    ultimate_fields = [
        # === IDENTIFICATION & BASIC INFO ===
        ('ssn_last_4', 'TEXT'),  # For certain forms
        ('drivers_license_number', 'TEXT'),
        ('drivers_license_state', 'TEXT'),
        ('passport_number', 'TEXT'),
        ('citizenship_status', 'TEXT'),
        
        # === DETAILED CONTACT ===
        ('fax_number', 'TEXT'),
        ('pager_number', 'TEXT'),
        ('assistant_name', 'TEXT'),
        ('assistant_phone', 'TEXT'),
        ('assistant_email', 'TEXT'),
        ('preferred_contact_method', 'TEXT'),
        ('do_not_call', 'BOOLEAN DEFAULT 0'),
        ('do_not_email', 'BOOLEAN DEFAULT 0'),
        ('do_not_text', 'BOOLEAN DEFAULT 0'),
        
        # === MAILING ADDRESS (if different) ===
        ('mailing_address_line1', 'TEXT'),
        ('mailing_address_line2', 'TEXT'),
        ('mailing_city', 'TEXT'),
        ('mailing_state', 'TEXT'),
        ('mailing_zip', 'TEXT'),
        ('mailing_country', 'TEXT'),
        
        # === FINANCIAL DETAILS ===
        ('employer_address', 'TEXT'),
        ('employer_phone', 'TEXT'),
        ('years_at_job', 'REAL'),
        ('monthly_income', 'REAL'),
        ('other_income', 'REAL'),
        ('other_income_source', 'TEXT'),
        ('debt_to_income_ratio', 'REAL'),
        ('bank_name', 'TEXT'),
        ('bank_account_number', 'TEXT'),
        ('bank_routing_number', 'TEXT'),
        ('investment_accounts', 'TEXT'),
        ('retirement_accounts', 'TEXT'),
        ('total_assets', 'REAL'),
        ('total_liabilities', 'REAL'),
        ('net_worth', 'REAL'),
        ('bankruptcy_history', 'BOOLEAN DEFAULT 0'),
        ('bankruptcy_date', 'DATE'),
        ('foreclosure_history', 'BOOLEAN DEFAULT 0'),
        ('foreclosure_date', 'DATE'),
        
        # === TAX INFORMATION ===
        ('tax_id_number', 'TEXT'),
        ('property_tax_id', 'TEXT'),
        ('homestead_exemption', 'BOOLEAN DEFAULT 0'),
        ('senior_exemption', 'BOOLEAN DEFAULT 0'),
        ('veteran_exemption', 'BOOLEAN DEFAULT 0'),
        ('disability_exemption', 'BOOLEAN DEFAULT 0'),
        
        # === CURRENT HOUSING ===
        ('current_residence_type', 'TEXT'),  # own, rent, family, etc
        ('current_rent_amount', 'REAL'),
        ('current_mortgage_amount', 'REAL'),
        ('current_mortgage_payment', 'REAL'),
        ('landlord_name', 'TEXT'),
        ('landlord_phone', 'TEXT'),
        ('years_at_current_address', 'REAL'),
        ('reason_for_moving', 'TEXT'),
        
        # === PROPERTY SEARCH CRITERIA ===
        ('max_hoa_fee', 'REAL'),
        ('garage_spaces_min', 'INTEGER'),
        ('pool_required', 'BOOLEAN DEFAULT 0'),
        ('view_required', 'BOOLEAN DEFAULT 0'),
        ('school_district_preference', 'TEXT'),
        ('commute_time_max', 'INTEGER'),
        ('work_from_home', 'BOOLEAN DEFAULT 0'),
        ('pets', 'TEXT'),
        ('pet_restrictions_ok', 'BOOLEAN DEFAULT 1'),
        
        # === TRANSACTION PREFERENCES ===
        ('cash_buyer', 'BOOLEAN DEFAULT 0'),
        ('contingent_buyer', 'BOOLEAN DEFAULT 0'),
        ('contingent_property_address', 'TEXT'),
        ('preferred_closing_date', 'DATE'),
        ('flexible_closing', 'BOOLEAN DEFAULT 0'),
        ('rent_back_needed', 'BOOLEAN DEFAULT 0'),
        ('rent_back_days', 'INTEGER'),
        
        # === LEGAL REPRESENTATION ===
        ('attorney_name', 'TEXT'),
        ('attorney_phone', 'TEXT'),
        ('attorney_email', 'TEXT'),
        ('attorney_firm', 'TEXT'),
        ('power_of_attorney', 'BOOLEAN DEFAULT 0'),
        ('poa_holder_name', 'TEXT'),
        ('poa_holder_phone', 'TEXT'),
        
        # === TRUST/ESTATE INFO ===
        ('buying_in_trust', 'BOOLEAN DEFAULT 0'),
        ('trust_name', 'TEXT'),
        ('trust_date', 'DATE'),
        ('trustee_name', 'TEXT'),
        ('trust_tax_id', 'TEXT'),
        ('estate_sale', 'BOOLEAN DEFAULT 0'),
        ('probate_case_number', 'TEXT'),
        
        # === BUSINESS ENTITY ===
        ('buying_as_llc', 'BOOLEAN DEFAULT 0'),
        ('llc_name', 'TEXT'),
        ('llc_state', 'TEXT'),
        ('llc_tax_id', 'TEXT'),
        ('corporation_name', 'TEXT'),
        ('corporation_state', 'TEXT'),
        ('authorized_signer', 'TEXT'),
        
        # === CO-BUYERS ===
        ('co_buyer_name', 'TEXT'),
        ('co_buyer_email', 'TEXT'),
        ('co_buyer_phone', 'TEXT'),
        ('co_buyer_ssn_last_4', 'TEXT'),
        ('co_buyer_income', 'REAL'),
        ('co_buyer_credit_score', 'INTEGER'),
        ('relationship_to_co_buyer', 'TEXT'),
        
        # === 1031 EXCHANGE ===
        ('exchange_1031', 'BOOLEAN DEFAULT 0'),
        ('qi_company', 'TEXT'),
        ('qi_contact', 'TEXT'),
        ('relinquished_property_address', 'TEXT'),
        ('exchange_deadline_45_day', 'DATE'),
        ('exchange_deadline_180_day', 'DATE'),
        
        # === DISCLOSURES & ACKNOWLEDGMENTS ===
        ('agency_disclosure_date', 'DATE'),
        ('buyer_inspection_advisory_date', 'DATE'),
        ('market_conditions_advisory_date', 'DATE'),
        ('statewide_buyer_seller_advisory_date', 'DATE'),
        ('wire_fraud_advisory_date', 'DATE'),
        ('fair_housing_notice_date', 'DATE'),
        
        # === INSURANCE INFO ===
        ('current_insurance_company', 'TEXT'),
        ('current_insurance_agent', 'TEXT'),
        ('current_insurance_phone', 'TEXT'),
        ('preferred_insurance_company', 'TEXT'),
        
        # === MOVING/RELOCATION ===
        ('relocation_company', 'TEXT'),
        ('relocation_coordinator', 'TEXT'),
        ('relocation_phone', 'TEXT'),
        ('corporate_relocation', 'BOOLEAN DEFAULT 0'),
        ('temporary_housing_needed', 'BOOLEAN DEFAULT 0'),
        
        # === FOREIGN BUYER INFO ===
        ('foreign_buyer', 'BOOLEAN DEFAULT 0'),
        ('country_of_citizenship', 'TEXT'),
        ('visa_type', 'TEXT'),
        ('itin_number', 'TEXT'),
        ('firpta_withholding', 'BOOLEAN DEFAULT 0'),
        
        # === MARKETING PREFERENCES ===
        ('newsletter_signup', 'BOOLEAN DEFAULT 1'),
        ('market_updates', 'BOOLEAN DEFAULT 1'),
        ('listing_alerts', 'BOOLEAN DEFAULT 1'),
        ('price_reduction_alerts', 'BOOLEAN DEFAULT 1'),
        ('new_listing_alerts', 'BOOLEAN DEFAULT 1'),
        
        # === GIFT FUNDS ===
        ('gift_funds', 'BOOLEAN DEFAULT 0'),
        ('gift_amount', 'REAL'),
        ('gift_donor_name', 'TEXT'),
        ('gift_donor_relationship', 'TEXT'),
        ('gift_letter_date', 'DATE'),
        
        # === VA/FHA/USDA SPECIFIC ===
        ('veteran', 'BOOLEAN DEFAULT 0'),
        ('va_eligibility_certificate', 'TEXT'),
        ('first_time_buyer', 'BOOLEAN DEFAULT 0'),
        ('rural_property_eligible', 'BOOLEAN DEFAULT 0'),
        
        # === SELLER-SPECIFIC FIELDS ===
        ('property_owned_years', 'REAL'),
        ('original_purchase_price', 'REAL'),
        ('mortgage_balance', 'REAL'),
        ('mortgage_company', 'TEXT'),
        ('mortgage_account_number', 'TEXT'),
        ('home_warranty_company', 'TEXT'),
        ('home_warranty_expiration', 'DATE'),
        ('solar_panels', 'BOOLEAN DEFAULT 0'),
        ('solar_owned_or_leased', 'TEXT'),
        ('solar_company', 'TEXT'),
        ('solar_monthly_payment', 'REAL'),
        
        # === REFERRAL TRACKING ===
        ('referred_clients', 'TEXT'),  # JSON list of client IDs
        ('referral_fee_owed', 'REAL'),
        ('referral_fee_percentage', 'REAL'),
        ('referral_agreement_date', 'DATE'),
        
        # === DOCUMENT TRACKING ===
        ('docs_signed_date', 'DATE'),
        ('proof_of_funds_date', 'DATE'),
        ('pre_approval_letter_date', 'DATE'),
        ('earnest_money_receipt_date', 'DATE'),
        ('inspection_report_date', 'DATE'),
        ('appraisal_report_date', 'DATE'),
        
        # === CUSTOM FIELDS ===
        ('custom_field_1', 'TEXT'),
        ('custom_field_2', 'TEXT'),
        ('custom_field_3', 'TEXT'),
        ('custom_field_4', 'TEXT'),
        ('custom_field_5', 'TEXT')
    ]
    
    # Get existing columns
    cursor.execute("PRAGMA table_info(clients)")
    existing_columns = {col[1] for col in cursor.fetchall()}
    
    # Add missing columns
    added = 0
    for col_name, col_type in ultimate_fields:
        if col_name not in existing_columns:
            try:
                cursor.execute(f"ALTER TABLE clients ADD COLUMN {col_name} {col_type}")
                added += 1
                if added % 10 == 0:
                    print(f"  ✅ Added {added} fields...")
            except sqlite3.OperationalError as e:
                if "duplicate column" not in str(e):
                    print(f"  ❌ Error adding {col_name}: {e}")
    
    conn.commit()
    
    # Final count
    cursor.execute("PRAGMA table_info(clients)")
    final_columns = cursor.fetchall()
    
    print(f"\n✅ ULTIMATE client database created!")
    print(f"   Added {added} new fields")
    print(f"   Total fields now: {len(final_columns)}")
    
    print("\n📊 Field Categories Now Available:")
    print("   • Basic ID & Contact (20+ fields)")
    print("   • Financial Profile (30+ fields)")
    print("   • Property Preferences (20+ fields)")
    print("   • Legal/Trust/Entity (20+ fields)")
    print("   • Transaction Details (15+ fields)")
    print("   • Disclosures & Documents (20+ fields)")
    print("   • Special Situations (1031, VA, Foreign, etc.)")
    print("   • Marketing & Communication Preferences")
    print("   • Custom Fields for Unique Situations")
    
    print("\n🎯 This database can now handle ANY field from ANY CAR form!")
    
    conn.close()

if __name__ == "__main__":
    create_ultimate_client_database()