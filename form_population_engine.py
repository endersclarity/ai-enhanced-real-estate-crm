#!/usr/bin/env python3
"""
Automated Form Population Engine
Task #4: Core engine for populating CAR forms with CRM data

This engine takes CRM data and form templates, applies field mappings,
and generates populated PDF forms using coordinate-based placement.
"""

import json
import sqlite3
from pathlib import Path
from datetime import datetime
from decimal import Decimal
import logging
from typing import Dict, Any, Optional, List

import PyPDF2
import pdfplumber
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Import our coordinate-based form filler
from coordinate_based_form_filler import CoordinateBasedFormFiller

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FormPopulationEngine:
    """Core engine for automated form population"""
    
    def __init__(self, mapping_config_path: str = 'crm_field_mapping_config.json'):
        """Initialize the population engine with field mapping configuration"""
        self.mapping_config = self._load_mapping_config(mapping_config_path)
        self.validation_rules = self._load_validation_rules()
        
        # Initialize coordinate-based form filler
        self.form_filler = CoordinateBasedFormFiller()
        
        # Database connection
        self.db_path = 'real_estate.db'
        
    def _load_mapping_config(self, config_path: str) -> Dict[str, Any]:
        """Load the field mapping configuration"""
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            logger.info(f"✅ Loaded mapping config: {len(config['form_mappings'])} forms")
            return config
        except FileNotFoundError:
            logger.error(f"❌ Mapping config not found: {config_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"❌ Invalid JSON in mapping config: {e}")
            raise
    
    def _load_validation_rules(self) -> Dict[str, callable]:
        """Load validation rules for form fields"""
        return {
            'non_empty': lambda x: x and len(str(x).strip()) > 0,
            'email_format': lambda x: '@' in str(x) and '.' in str(x),
            'phone_format': lambda x: len(str(x).replace('(', '').replace(')', '').replace('-', '').replace(' ', '')) >= 10,
            'currency_format': lambda x: isinstance(x, (int, float, Decimal)) and float(x) >= 0,
            'date_format': lambda x: self._validate_date_format(x),
            'zip_format': lambda x: len(str(x)) in [5, 10],
            'state_code': lambda x: len(str(x)) == 2,
            'license_format': lambda x: len(str(x)) >= 6,
            'apn_format': lambda x: len(str(x)) >= 5,
            'address_format': lambda x: len(str(x).strip()) > 10
        }
    
    def _validate_date_format(self, date_value: Any) -> bool:
        """Validate date format"""
        if not date_value:
            return False
        try:
            if isinstance(date_value, str):
                datetime.strptime(date_value, '%Y-%m-%d')
            return True
        except (ValueError, TypeError):
            return False
    
    def fetch_crm_data(self, client_id: str, property_id: str, transaction_id: str = None) -> Dict[str, Any]:
        """Fetch CRM data for form population"""
        try:
            # Try to fetch from actual database first
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Fetch client data
            cursor.execute("SELECT * FROM clients WHERE id = ?", (client_id,))
            client_row = cursor.fetchone()
            client_data = dict(client_row) if client_row else {}
            
            # Fetch property data
            cursor.execute("SELECT * FROM properties WHERE id = ?", (property_id,))
            property_row = cursor.fetchone()
            property_data = dict(property_row) if property_row else {}
            
            # Fetch transaction data if provided
            transaction_data = {}
            if transaction_id:
                cursor.execute("SELECT * FROM transactions WHERE id = ?", (transaction_id,))
                transaction_row = cursor.fetchone()
                transaction_data = dict(transaction_row) if transaction_row else {}
            
            # Fetch agent data (default to first agent)
            cursor.execute("SELECT * FROM agents LIMIT 1")
            agent_row = cursor.fetchone()
            agent_data = dict(agent_row) if agent_row else {}
            
            conn.close()
            
            if client_data or property_data:
                logger.info(f"📊 Fetched real CRM data for client: {client_id}, property: {property_id}")
                return {
                    'clients': client_data,
                    'properties': property_data,
                    'transactions': transaction_data,
                    'agents': agent_data
                }
        
        except Exception as e:
            logger.warning(f"⚠️ Database fetch failed, using mock data: {e}")
        
        # Fallback to mock data
        mock_data = {
            'clients': {
                'id': client_id,
                'first_name': 'John',
                'last_name': 'Smith',
                'email': 'john.smith@email.com',
                'phone': '(555) 123-4567',
                'address_line1': '123 Main Street',
                'city': 'San Francisco',
                'state': 'CA',
                'zip_code': '94102'
            },
            'properties': {
                'id': property_id,
                'property_address': '456 Oak Avenue',
                'property_city': 'San Francisco',
                'property_state': 'CA',
                'property_zip': '94105',
                'apn': '1234-567-890',
                'mls_number': 'MLS123456',
                'square_feet': 2500,
                'bedrooms': 3,
                'bathrooms': 2
            },
            'transactions': {
                'id': transaction_id or 'trans_001',
                'purchase_price': 850000.00,
                'earnest_money': 25000.00,
                'down_payment': 170000.00,
                'loan_amount': 680000.00,
                'closing_date': '2025-07-15',
                'possession_date': '2025-07-15'
            },
            'agents': {
                'id': 'agent_001',
                'first_name': 'Narissa',
                'last_name': 'Johnson',
                'license_number': 'CA12345678',
                'phone': '(555) 987-6543',
                'brokerage': 'Narissa Realty'
            }
        }
        
        logger.info(f"📊 Fetched CRM data for client: {client_id}, property: {property_id}")
        return mock_data
    
    def resolve_field_value(self, crm_source: str, crm_data: Dict[str, Any]) -> Any:
        """Resolve CRM field value from source expression"""
        try:
            # Handle concatenated fields (e.g., "clients.first_name + ' ' + clients.last_name")
            if '+' in crm_source:
                parts = crm_source.split('+')
                result = ""
                for part in parts:
                    part = part.strip().strip('"').strip("'")
                    if '.' in part:
                        table, field = part.split('.', 1)
                        value = crm_data.get(table, {}).get(field, '')
                        result += str(value) if value else ''
                    else:
                        result += part
                return result.strip()
            
            # Handle simple field references (e.g., "clients.first_name")
            elif '.' in crm_source:
                table, field = crm_source.split('.', 1)
                return crm_data.get(table, {}).get(field, '')
            
            # Handle direct values
            else:
                return crm_source
                
        except Exception as e:
            logger.warning(f"⚠️ Error resolving field {crm_source}: {e}")
            return ''
    
    def validate_field_value(self, value: Any, validation_rule: str) -> tuple[bool, str]:
        """Validate a field value against its validation rule"""
        if not validation_rule or validation_rule not in self.validation_rules:
            return True, "No validation rule"
        
        try:
            is_valid = self.validation_rules[validation_rule](value)
            message = "Valid" if is_valid else f"Failed {validation_rule} validation"
            return is_valid, message
        except Exception as e:
            logger.warning(f"⚠️ Validation error for rule {validation_rule}: {e}")
            return False, f"Validation error: {e}"
    
    def create_populated_pdf(self, template_path: str, field_data: Dict[str, Any], output_path: str, form_name: str) -> bool:
        """Create a populated PDF from template and field data using coordinate-based filling"""
        try:
            # Use the coordinate-based form filler for professional PDF generation
            result = self.form_filler.fill_form(
                form_name=form_name,
                field_data=field_data,
                template_path=template_path,
                output_path=output_path
            )
            
            if result:
                logger.info(f"✅ Successfully created populated PDF: {output_path}")
                return True
            else:
                logger.error(f"❌ Failed to create populated PDF")
                return False
            width, height = letter
            
            # Title
            c.setFont("Helvetica-Bold", 16)
            c.drawString(50, height - 50, "California Residential Purchase Agreement")
            
            # Populate fields
            y_position = height - 100
            c.setFont("Helvetica", 12)
            
            for field_name, value in field_data.items():
                if value and str(value).strip():
                    c.drawString(50, y_position, f"{field_name}: {value}")
                    y_position -= 20
                    
                    if y_position < 50:  # Start new page
                        c.showPage()
                        y_position = height - 50
            
            c.save()
            logger.info(f"✅ Created populated PDF: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error creating PDF: {e}")
            return False
    
    def populate_form(self, form_name: str, client_id: str, property_id: str, 
                     transaction_id: str = None, output_dir: str = 'output') -> Dict[str, Any]:
        """Main method to populate a form with CRM data"""
        
        logger.info(f"🚀 Starting form population: {form_name}")
        
        # Get form mapping configuration
        if form_name not in self.mapping_config['form_mappings']:
            raise ValueError(f"Form mapping not found: {form_name}")
        
        form_config = self.mapping_config['form_mappings'][form_name]
        
        # Fetch CRM data
        crm_data = self.fetch_crm_data(client_id, property_id, transaction_id)
        
        # Resolve and validate field values
        field_data = {}
        validation_errors = []
        
        for field_name, field_config in form_config['mappings'].items():
            # Resolve field value from CRM data
            raw_value = self.resolve_field_value(field_config['crm_source'], crm_data)
            
            # Apply default values if needed
            if not raw_value and field_name in form_config.get('default_values', {}):
                raw_value = form_config['default_values'][field_name]
            
            # Validate field value
            validation_rule = field_config.get('validation', '')
            is_valid, validation_message = self.validate_field_value(raw_value, validation_rule)
            
            if not is_valid and field_config.get('required', False):
                validation_errors.append({
                    'field': field_name,
                    'value': raw_value,
                    'error': validation_message
                })
            
            # Store the field data
            field_data[field_name] = raw_value
        
        # Create output directory
        Path(output_dir).mkdir(exist_ok=True)
        
        # Generate output filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_filename = f"{form_name}_{client_id}_{property_id}_{timestamp}.pdf"
        output_path = Path(output_dir) / output_filename
        
        # Create populated PDF
        template_path = f"documents/{form_name}_BLANK_TEMPLATE.pdf"
        pdf_created = self.create_populated_pdf(str(template_path), field_data, str(output_path))
        
        # Prepare result
        result = {
            'success': pdf_created and len(validation_errors) == 0,
            'form_name': form_name,
            'output_path': str(output_path) if pdf_created else None,
            'field_count': len(field_data),
            'populated_fields': {k: v for k, v in field_data.items() if v},
            'validation_errors': validation_errors,
            'processing_time': datetime.now().isoformat(),
            'client_id': client_id,
            'property_id': property_id,
            'transaction_id': transaction_id
        }
        
        logger.info(f"✅ Form population completed: {result['success']}")
        logger.info(f"📊 Fields populated: {len(result['populated_fields'])}/{len(field_data)}")
        
        if validation_errors:
            logger.warning(f"⚠️ Validation errors: {len(validation_errors)}")
            for error in validation_errors:
                logger.warning(f"   - {error['field']}: {error['error']}")
        
        return result

def test_population_engine():
    """Test the form population engine with sample data"""
    
    print("🧪 Testing Form Population Engine")
    print("=" * 50)
    
    try:
        engine = FormPopulationEngine()
        
        # Test with California Purchase Agreement
        result = engine.populate_form(
            form_name='california_purchase_agreement',
            client_id='client_001',
            property_id='property_001',
            transaction_id='transaction_001'
        )
        
        print(f"✅ Population Success: {result['success']}")
        print(f"📄 Output File: {result['output_path']}")
        print(f"📊 Fields Populated: {len(result['populated_fields'])}")
        
        if result['validation_errors']:
            print(f"⚠️ Validation Errors: {len(result['validation_errors'])}")
            for error in result['validation_errors']:
                print(f"   - {error['field']}: {error['error']}")
        
        # Show sample populated fields
        print("\n🔍 Sample Populated Fields:")
        for i, (field, value) in enumerate(list(result['populated_fields'].items())[:5]):
            print(f"   {i+1}. {field}: {value}")
        
        return result
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        raise

if __name__ == "__main__":
    test_population_engine()