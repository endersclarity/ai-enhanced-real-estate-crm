#!/usr/bin/env python3
"""
HTML Form Populator - Populate the exact replica HTML with real CRM data
Form fields positioned over the gorgeous PDF background
"""

import sqlite3
import os
from jinja2 import Template

class HTMLFormPopulator:
    def __init__(self, db_path="../real_estate_crm.db"):
        self.db_path = db_path
        self.template_path = "html_templates/crpa_exact_replica.html"
        
    def get_transaction_data(self, transaction_id):
        """Get transaction data from CRM database"""
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
    
    def create_populated_html_form(self, transaction_id, output_path=None):
        """Create populated HTML form using the exact replica template"""
        
        # Get CRM data
        data = self.get_transaction_data(transaction_id)
        if not data:
            raise ValueError(f"Transaction {transaction_id} not found")
        
        # Set output path
        if not output_path:
            output_path = f"html_templates/crpa_populated_transaction_{transaction_id}.html"
        
        # Read the exact replica template
        with open(self.template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        # Format the data for display
        formatted_data = {
            'date_prepared': data.get('transaction_date', '2025-06-01'),
            'buyer_name': data.get('buyer_name', 'TBD'),
            'property_address': data.get('street_address', 'TBD'),
            'city': data.get('city', 'TBD'),
            'state': data.get('state', 'CA'),
            'zip_code': data.get('zip_code', 'TBD'),
            'purchase_price': f"${data.get('purchase_price', 0):,.2f}" if data.get('purchase_price') else 'TBD',
            'earnest_money': f"${data.get('earnest_money_amount', 0):,.2f}" if data.get('earnest_money_amount') else 'TBD',
        }
        
        print(f"📝 Populating HTML form for Transaction {transaction_id}:")
        for field, value in formatted_data.items():
            if value != 'TBD':
                print(f"  ✓ {field}: {value}")
        
        # Replace the form field values in the HTML
        populated_html = template_content
        
        # Update form field values with actual data
        replacements = {
            'placeholder="Date"': f'value="{formatted_data["date_prepared"]}" placeholder="Date"',
            'placeholder="Buyer Name(s)"': f'value="{formatted_data["buyer_name"]}" placeholder="Buyer Name(s)"',
            'placeholder="Property Address"': f'value="{formatted_data["property_address"]}" placeholder="Property Address"',
            'placeholder="City"': f'value="{formatted_data["city"]}" placeholder="City"',
            'value="CA"': f'value="{formatted_data["state"]}"',
            'placeholder="ZIP"': f'value="{formatted_data["zip_code"]}" placeholder="ZIP"',
            'placeholder="Purchase Price"': f'value="{formatted_data["purchase_price"]}" placeholder="Purchase Price"',
        }
        
        # Apply replacements
        for old_text, new_text in replacements.items():
            populated_html = populated_html.replace(old_text, new_text)
        
        # Add default contingency selections (for demo)
        populated_html = populated_html.replace(
            'name="inspection_contingency"', 
            'name="inspection_contingency" checked'
        )
        populated_html = populated_html.replace(
            'name="loan_contingency"', 
            'name="loan_contingency" checked'
        )
        
        # Update title to show it's populated
        populated_html = populated_html.replace(
            'California Residential Purchase Agreement - Exact Replica',
            f'CRPA - Transaction {transaction_id} - {formatted_data["buyer_name"]}'
        )
        
        # Add populated data info
        info_section = f"""
        <div class="form-info">
            <strong>Populated with Transaction {transaction_id}</strong><br>
            Buyer: {formatted_data["buyer_name"]}<br>
            Property: {formatted_data["property_address"]}<br>
            Price: {formatted_data["purchase_price"]}
        </div>
        """
        
        populated_html = populated_html.replace(
            '<div class="form-info">',
            info_section.replace('<div class="form-info">', '<div class="form-info">')
        )
        
        # Save populated form
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(populated_html)
        
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            print(f"\n🏆 POPULATED HTML FORM CREATED!")
            print(f"📁 File: {output_path}")
            print(f"📊 Size: {file_size:,} bytes")
            print(f"🎨 Gorgeous PDF background with real CRM data!")
            print(f"🌐 Windows: file:///C:/Users/ender/.claude/projects/offer-creator/{output_path}")
            print(f"💻 WSL: file://{os.path.abspath(output_path)}")
            
            return output_path
        else:
            raise Exception("Failed to create populated HTML form")
    
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
    
    def create_test_populated_form(self):
        """Create test form with enhanced sample data"""
        
        # Override with premium sample data for testing
        sample_data = {
            'transaction_date': '2025-06-01',
            'buyer_name': 'Alexander & Victoria Rodriguez',
            'street_address': '8765 Sunset Boulevard',
            'city': 'West Hollywood',
            'state': 'CA',
            'zip_code': '90069',
            'purchase_price': 3750000,
            'earnest_money_amount': 75000
        }
        
        # Read template and populate manually for testing
        with open(self.template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        replacements = {
            'placeholder="Date"': f'value="{sample_data["transaction_date"]}" placeholder="Date"',
            'placeholder="Buyer Name(s)"': f'value="{sample_data["buyer_name"]}" placeholder="Buyer Name(s)"',
            'placeholder="Property Address"': f'value="{sample_data["street_address"]}" placeholder="Property Address"',
            'placeholder="City"': f'value="{sample_data["city"]}" placeholder="City"',
            'value="CA"': f'value="{sample_data["state"]}"',
            'placeholder="ZIP"': f'value="{sample_data["zip_code"]}" placeholder="ZIP"',
            'placeholder="Purchase Price"': f'value="${sample_data["purchase_price"]:,.2f}" placeholder="Purchase Price"',
        }
        
        populated_html = template_content
        for old_text, new_text in replacements.items():
            populated_html = populated_html.replace(old_text, new_text)
        
        # Check contingencies
        populated_html = populated_html.replace('name="inspection_contingency"', 'name="inspection_contingency" checked')
        populated_html = populated_html.replace('name="loan_contingency"', 'name="loan_contingency" checked')
        
        # Save test form
        test_output = "html_templates/crpa_test_populated.html"
        with open(test_output, 'w', encoding='utf-8') as f:
            f.write(populated_html)
        
        print(f"🧪 TEST POPULATED FORM CREATED!")
        print(f"📁 File: {test_output}")
        print(f"🎨 Sample data: {sample_data['buyer_name']} buying {sample_data['street_address']}")
        print(f"💰 Price: ${sample_data['purchase_price']:,.2f}")
        print(f"🌐 Windows: file:///C:/Users/ender/.claude/projects/offer-creator/{test_output}")
        
        return test_output

def main():
    """Populate the exact replica HTML with real CRM data"""
    
    populator = HTMLFormPopulator()
    
    print("🎨 HTML FORM POPULATOR - EXACT REPLICA")
    print("=" * 70)
    print("Populating gorgeous PDF background with real CRM data!")
    print("✅ Form fields positioned exactly over PDF layout")
    print("✅ Uses real transaction data from database")
    print("=" * 70)
    
    # Create test populated form first
    print("\n🧪 Creating test form with premium sample data...")
    test_form = populator.create_test_populated_form()
    
    # Show available transactions
    transactions = populator.get_available_transactions()
    print(f"\nAvailable Transactions:")
    for t in transactions:
        print(f"  ID: {t[0]}, Client: {t[1]}, Property: {t[2]}, Price: ${t[3]}")
    
    if transactions:
        # Create form with real CRM data
        print(f"\n📝 Creating form with real CRM data...")
        transaction_id = transactions[0][0]
        populated_form = populator.create_populated_html_form(transaction_id)
        
        print(f"\n🎉 SUCCESS!")
        print(f"✅ Test form: crpa_test_populated.html")
        print(f"✅ Real data form: crpa_populated_transaction_{transaction_id}.html")
        print(f"🎯 Both use your gorgeous PDF as background!")
        print(f"🌐 Open in browser - data should appear in EXACTLY the right places!")
    else:
        print("No transactions found in database")

if __name__ == "__main__":
    main()