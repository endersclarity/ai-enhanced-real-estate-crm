#!/usr/bin/env python3
"""
CRM Form Integrator - Connect PDF forms with CRM database
Populates forms with real client/property data from CRM
"""

import sqlite3
from pdf_form_creator import PDFFormCreator
from fdfgen import forge_fdf
import os

class CRMFormIntegrator:
    def __init__(self, db_path="../real_estate_crm.db"):
        self.db_path = db_path
        self.form_creator = PDFFormCreator()
        
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
            t.closing_date as possession_date,
            'Conventional' as financing_type,
            t.earnest_money_amount,
            CASE WHEN t.inspection_contingency_date IS NOT NULL THEN 1 ELSE 0 END as inspection_contingency,
            CASE WHEN t.financing_contingency_date IS NOT NULL THEN 1 ELSE 0 END as loan_contingency,
            CASE WHEN t.appraisal_contingency_date IS NOT NULL THEN 1 ELSE 0 END as appraisal_contingency,
            
            -- Client (Buyer) Information
            c.first_name || ' ' || c.last_name as buyer_name,
            c.home_phone as buyer_phone,
            c.email as buyer_email,
            
            -- Property Information
            p.street_address,
            p.city,
            p.state,
            p.zip_code,
            
            -- Seller Information (placeholder)
            'TBD' as seller_name,
            '' as seller_phone,
            '' as seller_email,
            
            -- Agent Information (placeholder)
            'Narissa Agent' as listing_agent_name,
            'CA-12345' as listing_agent_license,
            'Narissa Realty' as listing_brokerage
            
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
    
    def create_populated_form(self, transaction_id, output_path=None):
        """Create and populate form with CRM data"""
        # Get data from CRM
        data = self.get_transaction_data(transaction_id)
        if not data:
            raise ValueError(f"Transaction {transaction_id} not found")
        
        # Create base form
        if not output_path:
            output_path = f"california_purchase_agreement_transaction_{transaction_id}.pdf"
            
        base_form = self.form_creator.create_california_purchase_agreement(output_path)
        
        # Populate form with CRM data
        self.populate_form_fields(base_form, data, output_path)
        
        return output_path
    
    def populate_form_fields(self, form_path, data, output_path):
        """Populate PDF form fields with data using FDF"""
        try:
            # Map CRM data to form fields
            field_mapping = self.form_creator.get_form_field_mapping()
            
            form_data = []
            for form_field, crm_field in field_mapping.items():
                if crm_field in data and data[crm_field] is not None:
                    value = data[crm_field]
                    # Handle boolean fields (checkboxes)
                    if isinstance(value, bool):
                        form_data.append((form_field, 'Yes' if value else 'Off'))
                    else:
                        form_data.append((form_field, str(value)))
            
            # Generate FDF file for population
            fdf_data = forge_fdf("", form_data, [], [], [])
            fdf_path = output_path.replace('.pdf', '.fdf')
            
            with open(fdf_path, 'wb') as f:
                f.write(fdf_data)
                
            # Use pdftk to merge FDF with PDF (if available)
            try:
                import subprocess
                cmd = f"pdftk {form_path} fill_form {fdf_path} output {output_path}"
                subprocess.run(cmd, shell=True, check=True)
                # Clean up FDF file
                os.remove(fdf_path)
            except:
                # Fallback: just return the base form
                print("Warning: pdftk not available, returning base form")
                
        except Exception as e:
            print(f"Error populating form: {e}")
            # Return base form if population fails
            pass
    
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
    """Test the CRM form integration"""
    integrator = CRMFormIntegrator()
    
    # Show available transactions
    transactions = integrator.get_available_transactions()
    print("Available Transactions:")
    for t in transactions:
        print(f"ID: {t[0]}, Client: {t[1]}, Property: {t[2]}, Price: ${t[3]}")
    
    if transactions:
        # Create form for first transaction
        transaction_id = transactions[0][0]
        output_file = integrator.create_populated_form(transaction_id)
        print(f"\nCreated populated form: {output_file}")
    else:
        print("No transactions found in database")

if __name__ == "__main__":
    main()