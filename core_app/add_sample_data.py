#!/usr/bin/env python3
"""
Add sample data to test offer creation workflow
"""

import sqlite3
from datetime import datetime

DATABASE_PATH = '../real_estate_crm.db'

def add_sample_data():
    """Add sample clients, properties, and agents for testing"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        
        # Sample clients
        sample_clients = [
            ("John", "Smith", "john.smith@email.com", "555-123-4567", "buyer", 400000, 600000, "Sacramento", 3),
            ("Mary", "Johnson", "mary.johnson@email.com", "555-234-5678", "buyer", 300000, 500000, "Davis", 2),
            ("Robert", "Williams", "robert.williams@email.com", "555-345-6789", "seller", 0, 0, "Elk Grove", 4),
            ("Jennifer", "Brown", "jennifer.brown@email.com", "555-456-7890", "buyer", 500000, 800000, "Roseville", 3)
        ]
        
        for client in sample_clients:
            try:
                conn.execute("""
                    INSERT OR IGNORE INTO clients (
                        first_name, last_name, email, home_phone, client_type, 
                        budget_min, budget_max, area_preference, bedrooms, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, client + (datetime.now(),))
            except Exception as e:
                print(f"Error inserting client {client[0]} {client[1]}: {e}")
        
        # Sample properties  
        sample_properties = [
            ("123 Main Street", "Sacramento", "CA", "95814", 550000, 3, 2, 1500, "Residential", "ML123456"),
            ("456 Oak Avenue", "Davis", "CA", "95616", 450000, 2, 2, 1200, "Condo", "ML234567"),
            ("789 Pine Drive", "Elk Grove", "CA", "95758", 625000, 4, 3, 2000, "Residential", "ML345678"),
            ("321 Elm Street", "Roseville", "CA", "95661", 475000, 3, 2, 1400, "Townhouse", "ML456789")
        ]
        
        for prop in sample_properties:
            try:
                conn.execute("""
                    INSERT OR IGNORE INTO properties (
                        address_line1, city, state, zip_code, listing_price,
                        bedrooms, bathrooms, square_feet, property_type, mls_number, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, prop + (datetime.now(),))
            except Exception as e:
                print(f"Error inserting property {prop[0]}: {e}")
        
        # Sample agents
        sample_agents = [
            ("Narissa Realty", "123 Real Estate Blvd", "Sacramento", "CA", "95814", "916-555-1000", "DRE12345", 
             "Narissa Henderson", "916-555-1001", "916-555-1002", "916-555-1003", "narissa@realtyco.com", "DRE67890", "selling_agent"),
            ("Premier Properties", "456 Agent Street", "Davis", "CA", "95616", "530-555-2000", "DRE23456",
             "Mike Agent", "530-555-2001", "530-555-2002", "530-555-2003", "mike@premier.com", "DRE78901", "listing_agent"),
            ("Century 21", "789 Broker Lane", "Roseville", "CA", "95661", "916-555-3000", "DRE34567",
             "Sarah Broker", "916-555-3001", "916-555-3002", "916-555-3003", "sarah@c21.com", "DRE89012", "selling_agent")
        ]
        
        for agent in sample_agents:
            try:
                conn.execute("""
                    INSERT OR IGNORE INTO brokers_agents (
                        firm_name, firm_address, firm_city, firm_state, firm_zip_code, firm_phone, firm_dre_license,
                        agent_name, agent_phone, agent_cellular, agent_fax, agent_email, agent_dre_license, role, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, agent + (datetime.now(),))
            except Exception as e:
                print(f"Error inserting agent {agent[7]}: {e}")
        
        # Sample lenders
        sample_lenders = [
            ("Wells Fargo Home Mortgage", "100 Bank Street", "Sacramento", "CA", "95814", "800-555-9999", "800-555-9998",
             "John Banker", "916-555-4001", "john.banker@wellsfargo.com", "Conv", ""),
            ("Chase Home Lending", "200 Finance Blvd", "Davis", "CA", "95616", "800-555-8888", "800-555-8887", 
             "Mary Lender", "530-555-5001", "mary.lender@chase.com", "FHA", ""),
            ("Bank of America", "300 Mortgage Ave", "Roseville", "CA", "95661", "800-555-7777", "800-555-7776",
             "Robert Finance", "916-555-6001", "robert.finance@bofa.com", "VA", "")
        ]
        
        for lender in sample_lenders:
            try:
                conn.execute("""
                    INSERT OR IGNORE INTO lenders (
                        company_name, street_address, city, state, zip_code, phone, fax,
                        officer_name, officer_cell_phone, officer_email, mortgage_type, mortgage_type_other, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, lender + (datetime.now(),))
            except Exception as e:
                print(f"Error inserting lender {lender[0]}: {e}")
        
        conn.commit()
        conn.close()
        
        print("✅ Sample data added successfully!")
        
        # Show counts
        conn = sqlite3.connect(DATABASE_PATH)
        counts = {}
        for table in ['clients', 'properties', 'brokers_agents', 'lenders']:
            cursor = conn.execute(f'SELECT COUNT(*) FROM {table}')
            counts[table] = cursor.fetchone()[0]
        conn.close()
        
        print(f"📊 Database now contains:")
        for table, count in counts.items():
            print(f"  - {table}: {count} records")
        
        return True
        
    except Exception as e:
        print(f"❌ Error adding sample data: {e}")
        return False

if __name__ == "__main__":
    print("📝 Adding Sample Data for Offer Creation Testing")
    print("=" * 50)
    add_sample_data()