#!/usr/bin/env python3
import sys
import os
from datetime import datetime

sys.path.append('/home/ender/.claude/projects/offer-creator')
sys.path.append('/home/ender/.claude/projects/offer-creator/core_app')

def create_simple_populated_form():
    print('🏠 SIMPLE FORM GENERATION TEST')
    print('=' * 50)
    
    try:
        from enhanced_professional_form_filler import EnhancedProfessionalFormFiller
        
        print('✅ Found enhanced form filler')
        
        dummy_data = {
            'buyer_name': 'John Michael Smith',
            'buyer_phone': '(555) 123-4567',
            'buyer_email': 'john.smith@email.com',
            'seller_name': 'Sarah Jane Wilson',
            'property_address': '123 Main Street',
            'city_state_zip': 'Sacramento, CA 95814',
            'purchase_price': ',000.00',
            'closing_date': '08/15/2025'
        }
        
        print('📋 Sample Data Created:')
        print(f'   Buyer: {dummy_data[" buyer_name\]}')
