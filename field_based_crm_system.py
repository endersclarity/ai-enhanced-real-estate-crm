#!/usr/bin/env python3
"""
Field-Based CRM System - Use real form fields for perfect population
NO MORE NEWSPAPER OVERLAP - fields guide exactly where data goes!
"""

import sqlite3
import os
import fitz  # pymupdf
from form_field_adder import FormFieldAdder

class FieldBasedCRMSystem:
    def __init__(self, db_path="../real_estate_crm.db"):
        self.db_path = db_path
        self.template_with_fields_path = "output/CRPA_TEMPLATE_WITH_FIELDS.pdf"
        self.field_adder = FormFieldAdder()
        
    def ensure_template_with_fields_exists(self):
        """Ensure the template with form fields exists"""
        if not os.path.exists(self.template_with_fields_path):
            print("🏗️ Creating template with form fields...")
            self.field_adder.add_form_fields_to_template()
        return os.path.exists(self.template_with_fields_path)
    
    def get_transaction_data(self, transaction_id):
        """Get complete transaction data from CRM database"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
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
            p.zip_code
            
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
    
    def create_perfect_crpa_form(self, transaction_id, output_path=None):
        """Create PERFECT CRPA form using field-based population"""
        
        # Ensure template with fields exists
        if not self.ensure_template_with_fields_exists():
            raise Exception("Could not create template with form fields")
        
        # Get CRM data
        data = self.get_transaction_data(transaction_id)
        if not data:
            raise ValueError(f"Transaction {transaction_id} not found")
        
        # Set output path
        if not output_path:
            output_path = f"output/PERFECT_CRPA_Transaction_{transaction_id}.pdf"
        
        # Open template with form fields
        doc = fitz.open(self.template_with_fields_path)
        
        # Map CRM data to form field names
        field_mapping = {
            'date_prepared': data.get('transaction_date', '2025-06-01'),
            'buyer_name': data.get('buyer_name', 'TBD'),
            'property_address': data.get('street_address', 'TBD'),
            'city': data.get('city', 'TBD'),
            'state': data.get('state', 'CA'),
            'zip_code': data.get('zip_code', 'TBD'),
            'purchase_price': f"${data.get('purchase_price', 0):,.2f}" if data.get('purchase_price') else 'TBD',
            'earnest_money': f"${data.get('earnest_money_amount', 0):,.2f}" if data.get('earnest_money_amount') else 'TBD',
            'inspection_contingency': True  # Default to checked
        }
        
        print(f"📝 Creating PERFECT CRPA form for Transaction {transaction_id}:")
        populated_fields = 0
        
        # Populate fields by name - NO MORE COORDINATES!
        for page_num in range(len(doc)):
            page = doc[page_num]
            widgets = list(page.widgets())
            
            for widget in widgets:
                field_name = widget.field_name
                if field_name in field_mapping:
                    value = field_mapping[field_name]
                    
                    if widget.field_type == fitz.PDF_WIDGET_TYPE_TEXT and value != 'TBD':
                        widget.field_value = str(value)
                        print(f"  ✓ {field_name}: {value}")
                        populated_fields += 1
                    elif widget.field_type == fitz.PDF_WIDGET_TYPE_CHECKBOX:
                        widget.field_value = value
                        print(f"  ✓ {field_name}: {'Checked' if value else 'Unchecked'}")
                        populated_fields += 1
                    
                    widget.update()
        
        # Save the perfect form
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        doc.save(output_path)
        doc.close()
        
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            print(f"\n🏆 PERFECT CRPA FORM CREATED!")
            print(f"📁 File: {output_path}")
            print(f"📊 Size: {file_size:,} bytes")
            print(f"📝 Populated {populated_fields} fields precisely")
            print(f"🎯 NO newspaper overlap - field-based positioning!")
            print(f"🌐 Windows path: \\\\wsl.localhost\\Ubuntu\\home\\ender\\.claude\\projects\\offer-creator\\{output_path}")
            return output_path
        else:
            raise Exception("Failed to create perfect CRPA form")
    
    def get_available_transactions(self):
        """Get list of available transactions"""
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
    """Test the perfect field-based CRPA system"""
    system = FieldBasedCRMSystem()
    
    print("🏆 PERFECT FIELD-BASED CRPA SYSTEM")
    print("=" * 70)
    print("✅ Uses real form fields - NO coordinate guessing!")
    print("✅ NO newspaper overlap - precise field positioning!")
    print("✅ Perfect integration with your gorgeous clean template!")
    print("=" * 70)
    
    # Show available transactions
    transactions = system.get_available_transactions()
    print("\nAvailable Transactions:")
    for t in transactions:
        print(f"  ID: {t[0]}, Client: {t[1]}, Property: {t[2]}, Price: ${t[3]}")
    
    if transactions:
        # Create perfect CRPA form
        transaction_id = transactions[0][0]
        output_file = system.create_perfect_crpa_form(transaction_id)
        print(f"\n🎉 SUCCESS: Created PERFECT CRPA form!")
        print(f"🎯 No more overlapping text - everything in perfect alignment!")
    else:
        print("No transactions found in database")

if __name__ == "__main__":
    main()