#!/usr/bin/env python3
"""
CRPA CRM Integration System - Use the gorgeous clean template and populate with CRM data
This is the final solution that creates beautiful, populated forms
"""

import sqlite3
import os
import fitz  # pymupdf
from blue_text_remover import BlueTextRemover

class CRPACRMSystem:
    def __init__(self, db_path="../real_estate_crm.db"):
        self.db_path = db_path
        self.clean_template_path = "output/CRPA_CLEAN_TEMPLATE.pdf"
        self.remover = BlueTextRemover()
        
    def get_transaction_data(self, transaction_id):
        """Get complete transaction data from CRM database"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get transaction with related client and property data
        query = """
        SELECT 
            t.id as transaction_id,
            t.offer_date as transaction_date,
            t.purchase_price,
            t.closing_date,
            t.earnest_money_amount,
            
            -- Client (Buyer) Information
            c.first_name || ' ' || c.last_name as buyer_name,
            c.home_phone as buyer_phone,
            c.email as buyer_email,
            
            -- Property Information
            p.street_address,
            p.city,
            p.state,
            p.zip_code,
            
            -- Agent Information (placeholder)
            'Narissa Thompson' as listing_agent_name,
            'CA-DRE-02145678' as listing_agent_license,
            'Narissa Realty Group' as listing_brokerage
            
        FROM transactions t
        LEFT JOIN clients c ON t.buyer_client_id = c.id
        LEFT JOIN properties p ON t.property_id = p.id
        WHERE t.id = ?
        """
        
        cursor.execute(query, (transaction_id,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return dict(result)
        return None
    
    def ensure_clean_template_exists(self):
        """Ensure the clean template exists, create it if needed"""
        if not os.path.exists(self.clean_template_path):
            print("🧹 Creating clean template...")
            self.remover.remove_colored_text(self.clean_template_path)
        return os.path.exists(self.clean_template_path)
    
    def create_crpa_form(self, transaction_id, output_path=None):
        """Create a populated CRPA form using CRM data"""
        
        # Ensure clean template exists
        if not self.ensure_clean_template_exists():
            raise Exception("Could not create clean template")
        
        # Get CRM data
        data = self.get_transaction_data(transaction_id)
        if not data:
            raise ValueError(f"Transaction {transaction_id} not found")
        
        # Set output path
        if not output_path:
            output_path = f"output/CRPA_Transaction_{transaction_id}.pdf"
        
        # Open clean template
        doc = fitz.open(self.clean_template_path)
        
        # Format data for display
        formatted_data = {
            'form_date': data.get('transaction_date', '2025-06-01'),
            'buyer_name': data.get('buyer_name', 'TBD'),
            'property_address': data.get('street_address', 'TBD'),
            'city': data.get('city', 'TBD'),
            'state': data.get('state', 'CA'),
            'zip': data.get('zip_code', 'TBD'),
            'purchase_price': f"${data.get('purchase_price', 0):,.2f}" if data.get('purchase_price') else 'TBD',
            'earnest_money': f"${data.get('earnest_money_amount', 0):,.2f}" if data.get('earnest_money_amount') else 'TBD',
            'closing_date': data.get('closing_date', 'TBD'),
            'listing_agent': data.get('listing_agent_name', 'Narissa Thompson'),
            'agent_license': data.get('listing_agent_license', 'CA-DRE-02145678'),
            'brokerage': data.get('listing_brokerage', 'Narissa Realty Group')
        }
        
        # Position mappings for the main form fields (page 3, 0-indexed as page 2)
        field_positions = {
            # Page 3 - Main purchase agreement form
            'form_date': (500, 142),      # Date prepared field
            'buyer_name': (350, 170),     # Buyer name field  
            'property_address': (350, 195), # Property address
            'city': (200, 220),           # City
            'state': (380, 220),          # State
            'zip': (480, 220),            # ZIP code
            'purchase_price': (200, 280), # Purchase price (need to find exact position)
            'earnest_money': (150, 320),  # Earnest money amount
            'closing_date': (200, 360),   # Closing date
        }
        
        # Add text to Page 3 (main form page)
        page = doc[2]  # Page 3 is 0-indexed as page 2
        
        print(f"📝 Populating CRPA form for Transaction {transaction_id}:")
        for field, value in formatted_data.items():
            if field in field_positions and value != 'TBD':
                x, y = field_positions[field]
                print(f"  {field}: {value}")
                
                # Add blue text for new data
                page.insert_text((x, y), str(value), fontsize=10, color=(0, 0, 0.8))
        
        # Save the populated form
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        doc.save(output_path)
        doc.close()
        
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            print(f"\n✅ CRPA FORM CREATED!")
            print(f"📁 File: {output_path}")
            print(f"📊 Size: {file_size:,} bytes")
            print(f"🌐 Windows path: \\\\wsl.localhost\\Ubuntu\\home\\ender\\.claude\\projects\\offer-creator\\{output_path}")
            return output_path
        else:
            raise Exception("Failed to create CRPA form")
    
    def get_available_transactions(self):
        """Get list of available transactions for form creation"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = """
        SELECT 
            t.id,
            c.first_name || ' ' || c.last_name as client_name,
            p.street_address,
            t.purchase_price,
            t.offer_date
        FROM transactions t
        LEFT JOIN clients c ON t.buyer_client_id = c.id  
        LEFT JOIN properties p ON t.property_id = p.id
        ORDER BY t.offer_date DESC
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        conn.close()
        
        return results

def main():
    """Test the CRPA CRM system"""
    system = CRPACRMSystem()
    
    print("🏠 CRPA CRM INTEGRATION SYSTEM")
    print("=" * 60)
    
    # Show available transactions
    transactions = system.get_available_transactions()
    print("Available Transactions:")
    for t in transactions:
        print(f"  ID: {t[0]}, Client: {t[1]}, Property: {t[2]}, Price: ${t[3]}")
    
    if transactions:
        # Create CRPA form for first transaction
        transaction_id = transactions[0][0]
        output_file = system.create_crpa_form(transaction_id)
        print(f"\n🎉 SUCCESS: Created gorgeous CRPA form using your clean template!")
    else:
        print("No transactions found in database")

if __name__ == "__main__":
    main()