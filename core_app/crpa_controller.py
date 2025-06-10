#!/usr/bin/env python3
"""
CRPA Controller - Main Integration Controller for Enhanced Architecture

This controller orchestrates the complete enhanced architecture:
1. CrmDataMapper for intelligent field mapping
2. DataValidator for legal compliance validation
3. Enhanced form generation with multiple output formats
4. Comprehensive error handling and user-friendly responses

Architecture: Flask Routes → CrpaController → CrmDataMapper → DataValidator → Form Generation
"""

import logging
import os
import sys
from datetime import datetime
from typing import Dict, Any, Optional, List
import json

# Add core_app to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from crm_data_mapper import CrmDataMapper
from data_validator import DataValidator, ValidationReport

class CrpaController:
    """
    Main controller for CRPA form generation using enhanced architecture
    
    Features:
    - Unified interface for CRM integration
    - Comprehensive error handling
    - Multiple output format support
    - Performance monitoring and logging
    - User-friendly response formatting for Flask endpoints
    """
    
    def __init__(self, database_path: str = "real_estate.db"):
        self.database_path = database_path
        self.logger = logging.getLogger(__name__)
        
        # Initialize enhanced architecture components
        try:
            self.crm_mapper = CrmDataMapper(database_path=database_path)
            self.validator = DataValidator()
            self.logger.info("CRPA Controller initialized with enhanced architecture")
        except Exception as e:
            self.logger.error(f"Failed to initialize CRPA Controller: {e}")
            raise
    
    def generate_crpa_form(self, transaction_id: int, include_html: bool = True, 
                          include_json: bool = True) -> Dict[str, Any]:
        """
        Main method: Generate complete CRPA form package from CRM transaction
        
        Args:
            transaction_id: ID of the transaction in CRM database
            include_html: Whether to generate HTML replica
            include_json: Whether to generate JSON data
            
        Returns:
            Dict containing complete form generation results for Flask endpoints
        """
        start_time = datetime.now()
        
        try:
            self.logger.info(f"Starting CRPA form generation for transaction {transaction_id}")
            
            # Step 1: Extract and map CRM data (177 → 33 fields)
            self.logger.info("Step 1: Extracting CRM data with enhanced transformations")
            crpa_data = self.crm_mapper.get_crpa_data(transaction_id)
            mapping_time = (datetime.now() - start_time).total_seconds()
            
            # Step 2: Validate data for legal compliance
            self.logger.info("Step 2: Validating legal compliance and cross-field consistency")
            validation_start = datetime.now()
            validation_report = self.validator.validate_crpa_data(crpa_data)
            validation_time = (datetime.now() - validation_start).total_seconds()
            
            # Step 3: Generate output formats
            self.logger.info("Step 3: Generating output formats")
            generation_start = datetime.now()
            
            outputs = {}
            
            # Generate HTML replica if requested
            if include_html:
                html_content = self._generate_html_content(crpa_data, validation_report, transaction_id)
                outputs['html_content'] = html_content
                
                # Save HTML file
                html_path = f"output/crpa_transaction_{transaction_id}.html"
                os.makedirs(os.path.dirname(html_path), exist_ok=True)
                with open(html_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                outputs['html_path'] = html_path
            
            # Generate JSON data if requested
            if include_json:
                json_data = self._generate_json_response(crpa_data, validation_report, transaction_id)
                outputs['json_data'] = json_data
                
                # Save JSON file
                json_path = f"output/crpa_transaction_{transaction_id}.json"
                os.makedirs(os.path.dirname(json_path), exist_ok=True)
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(json_data, f, indent=2, ensure_ascii=False)
                outputs['json_path'] = json_path
            
            generation_time = (datetime.now() - generation_start).total_seconds()
            total_time = (datetime.now() - start_time).total_seconds()
            
            # Compile Flask-friendly response
            response = {
                'success': True,
                'transaction_id': transaction_id,
                'timestamp': datetime.now().isoformat(),
                'processing_time': {
                    'data_mapping': round(mapping_time, 3),
                    'validation': round(validation_time, 3),
                    'generation': round(generation_time, 3),
                    'total': round(total_time, 3)
                },
                'crpa_data': crpa_data,
                'validation': {
                    'is_valid': validation_report.is_valid,
                    'completion_rate': round(validation_report.field_completion_rate, 3),
                    'legal_compliance': validation_report.legal_compliance_status,
                    'business_rules_passed': validation_report.business_rules_passed,
                    'summary': validation_report.get_summary(),
                    'errors': [
                        {
                            'field': error.field_name,
                            'type': error.error_type,
                            'message': error.message,
                            'suggested_fix': error.suggested_fix
                        } for error in validation_report.errors
                    ],
                    'warnings': [
                        {
                            'field': warning.field_name,
                            'type': warning.error_type,
                            'message': warning.message,
                            'suggested_fix': warning.suggested_fix
                        } for warning in validation_report.warnings
                    ]
                },
                'outputs': outputs,
                'field_count': len(crpa_data),
                'architecture': 'enhanced_google_ai_studio'
            }
            
            self.logger.info(f"✅ CRPA form generation completed successfully in {total_time:.3f} seconds")
            return response
            
        except Exception as e:
            self.logger.error(f"CRPA form generation failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'transaction_id': transaction_id,
                'timestamp': datetime.now().isoformat(),
                'processing_time': {'total': round((datetime.now() - start_time).total_seconds(), 3)}
            }
    
    def get_available_transactions(self) -> Dict[str, Any]:
        """Get list of available transactions for Flask endpoints"""
        try:
            transactions = self.crm_mapper.get_available_transactions()
            return {
                'success': True,
                'transactions': transactions,
                'count': len(transactions),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Failed to get available transactions: {e}")
            return {
                'success': False,
                'error': str(e),
                'transactions': [],
                'count': 0,
                'timestamp': datetime.now().isoformat()
            }
    
    def validate_transaction_data(self, transaction_id: int) -> Dict[str, Any]:
        """Validate transaction data without generating full form"""
        try:
            # Extract CRM data
            crpa_data = self.crm_mapper.get_crpa_data(transaction_id)
            
            # Validate data
            validation_report = self.validator.validate_crpa_data(crpa_data)
            
            return {
                'success': True,
                'transaction_id': transaction_id,
                'validation': {
                    'is_valid': validation_report.is_valid,
                    'completion_rate': round(validation_report.field_completion_rate, 3),
                    'legal_compliance': validation_report.legal_compliance_status,
                    'business_rules_passed': validation_report.business_rules_passed,
                    'summary': validation_report.get_summary(),
                    'error_count': len(validation_report.errors),
                    'warning_count': len(validation_report.warnings)
                },
                'field_count': len(crpa_data),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Transaction validation failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'transaction_id': transaction_id,
                'timestamp': datetime.now().isoformat()
            }
    
    def _generate_html_content(self, crpa_data: Dict[str, Any], validation_report: ValidationReport, 
                              transaction_id: int) -> str:
        """Generate complete HTML content for Flask templates"""
        
        # Load HTML template from enhanced mapping
        try:
            with open("form_templates/enhanced_crpa_mapping.json", 'r') as f:
                config = json.load(f)
                template_content = config.get('template_content', '')
        except:
            template_content = self._get_basic_html_template()
        
        # Replace template variables with actual data
        html_content = template_content
        for field_name, value in crpa_data.items():
            placeholder = f"{{{{{field_name}}}}}"
            html_content = html_content.replace(placeholder, str(value) if value else "")
        
        # Add validation information
        validation_html = self.validator.generate_validation_summary_html(validation_report)
        
        # Create complete HTML page
        full_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Enhanced CRPA Form - Transaction {transaction_id}</title>
    <style>
        body {{ 
            font-family: Arial, sans-serif; 
            line-height: 1.6; 
            margin: 20px; 
            background-color: #f8f9fa;
        }}
        .container {{ 
            max-width: 900px; 
            margin: 0 auto; 
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 30px;
            text-align: center;
        }}
        .header h1 {{ margin: 0; font-size: 28px; }}
        .metadata {{ 
            background: #e3f2fd; 
            padding: 15px; 
            border-radius: 8px; 
            margin-bottom: 25px; 
            border-left: 5px solid #2196f3;
        }}
        .form-content {{
            background: #fff;
            padding: 25px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            margin: 20px 0;
        }}
        h1, h2 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
        .section {{ margin: 25px 0; padding: 20px; border: 1px solid #ddd; border-radius: 8px; background: #fafafa; }}
        strong {{ color: #2c3e50; }}
        .copy-button {{ 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; 
            padding: 12px 25px; 
            border: none; 
            border-radius: 25px; 
            cursor: pointer; 
            margin: 15px 5px;
            font-weight: bold;
            transition: all 0.3s ease;
        }}
        .copy-button:hover {{ 
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }}
        .performance-metrics {{
            display: flex;
            justify-content: space-around;
            background: #f1f8e9;
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
        }}
        .metric {{
            text-align: center;
        }}
        .metric-value {{
            font-size: 24px;
            font-weight: bold;
            color: #4caf50;
        }}
        .metric-label {{
            font-size: 12px;
            color: #666;
            text-transform: uppercase;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏠 Enhanced CRPA Form</h1>
            <p>Google AI Studio Architecture | Transaction {transaction_id}</p>
        </div>
        
        <div class="metadata">
            <strong>📊 Form Generation Details:</strong><br>
            <strong>Generated:</strong> {datetime.now().strftime('%m/%d/%Y at %I:%M %p')} |
            <strong>Transaction ID:</strong> {transaction_id} |
            <strong>Architecture:</strong> CrmDataMapper + DataValidator + Enhanced Transformations
            <br><br>
            <button class="copy-button" onclick="copyFormContent()">📋 Copy Form Content</button>
            <button class="copy-button" onclick="copyValidationReport()">📊 Copy Validation Report</button>
        </div>
        
        <div class="performance-metrics">
            <div class="metric">
                <div class="metric-value">{len(crpa_data)}</div>
                <div class="metric-label">Fields Mapped</div>
            </div>
            <div class="metric">
                <div class="metric-value">{validation_report.field_completion_rate:.1%}</div>
                <div class="metric-label">Completion</div>
            </div>
            <div class="metric">
                <div class="metric-value">{validation_report.legal_compliance_status.title()}</div>
                <div class="metric-label">Legal Status</div>
            </div>
        </div>
        
        {validation_html}
        
        <div class="form-content" id="form-content">
{html_content}
        </div>
        
        <div style="text-align: center; margin-top: 30px; padding: 20px; background: #f8f9fa; border-radius: 8px;">
            <p><strong>🚀 Powered by Enhanced Professional Form Filler</strong></p>
            <p style="font-size: 12px; color: #666;">
                Google AI Studio Architecture | 177 CRM Fields → 33 CRPA Fields | 
                Legal Compliance Validation | Sub-second Processing
            </p>
        </div>
    </div>
    
    <div style="display: none;" id="validation-content">
{validation_html}
    </div>
    
    <script>
        function copyFormContent() {{
            const content = document.getElementById('form-content').innerText;
            navigator.clipboard.writeText(content).then(function() {{
                showSuccessMessage('✅ Form content copied to clipboard!');
            }}, function(err) {{
                console.error('Could not copy text: ', err);
                alert('❌ Copy failed. Please select and copy manually.');
            }});
        }}
        
        function copyValidationReport() {{
            const content = document.getElementById('validation-content').innerText;
            navigator.clipboard.writeText(content).then(function() {{
                showSuccessMessage('✅ Validation report copied to clipboard!');
            }}, function(err) {{
                console.error('Could not copy text: ', err);
                alert('❌ Copy failed. Please select and copy manually.');
            }});
        }}
        
        function showSuccessMessage(message) {{
            const div = document.createElement('div');
            div.innerHTML = message;
            div.style.cssText = `
                position: fixed; top: 20px; right: 20px; z-index: 1000;
                background: #4caf50; color: white; padding: 15px 25px;
                border-radius: 5px; font-weight: bold; box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            `;
            document.body.appendChild(div);
            setTimeout(() => div.remove(), 3000);
        }}
    </script>
</body>
</html>
"""
        
        return full_html
    
    def _generate_json_response(self, crpa_data: Dict[str, Any], validation_report: ValidationReport, 
                               transaction_id: int) -> Dict[str, Any]:
        """Generate JSON response for API endpoints"""
        return {
            'transaction_id': transaction_id,
            'generated_at': datetime.now().isoformat(),
            'crpa_fields': crpa_data,
            'field_count': len(crpa_data),
            'validation_summary': {
                'is_valid': validation_report.is_valid,
                'completion_rate': validation_report.field_completion_rate,
                'legal_compliance': validation_report.legal_compliance_status,
                'business_rules_passed': validation_report.business_rules_passed,
                'error_count': len(validation_report.errors),
                'warning_count': len(validation_report.warnings),
                'summary': validation_report.get_summary()
            },
            'architecture_info': {
                'system': 'Enhanced Professional Form Filler',
                'architecture': 'Google AI Studio Recommendations',
                'components': [
                    'CrmDataMapper (177→33 field mapping)',
                    'DataValidator (legal compliance)',
                    'Enhanced transformations (concatenate, format_currency, template)',
                    'Database view optimization',
                    'Connection pooling'
                ]
            }
        }
    
    def _get_basic_html_template(self) -> str:
        """Fallback HTML template if enhanced mapping unavailable"""
        return """
# CALIFORNIA RESIDENTIAL PURCHASE AGREEMENT
**Date:** {{offer_date}}

---

## PROPERTY INFORMATION
**Property Address:** {{property_address}}  
**City, State, ZIP:** {{city_state_zip}}  
**County:** {{county}}  
**Property Type:** {{property_type}}  

---

## BUYER INFORMATION
**Buyer Name(s):** {{buyer_name}}  
**Buyer Address:** {{buyer_address}}  
**Phone:** {{buyer_phone}}  
**Email:** {{buyer_email}}  
**Buyer's Agent:** {{buyer_agent}}  
**Brokerage:** {{buyer_brokerage}}  
**Agent License #:** {{buyer_agent_license}}  

---

## PURCHASE TERMS
**Purchase Price:** {{purchase_price}}  
**Initial Deposit:** {{initial_deposit}}  
**Down Payment:** {{down_payment}}  
**Closing Date:** {{closing_date}}  

---

*Generated by Enhanced Professional Form Filler with Google AI Studio Architecture*
"""

# Test function for development
def test_crpa_controller():
    """Test the CRPA controller functionality"""
    
    print("🎯 CRPA CONTROLLER TEST")
    print("=" * 50)
    print("Testing unified interface for enhanced architecture")
    print()
    
    try:
        # Initialize controller
        print("📦 Initializing CRPA Controller...")
        controller = CrpaController()
        print("✅ Controller initialized successfully")
        
        # Test available transactions
        print("\n📋 Testing transaction retrieval...")
        transactions_result = controller.get_available_transactions()
        
        if transactions_result['success']:
            print(f"✅ Found {transactions_result['count']} transactions")
        else:
            print(f"⚠️ No transactions found: {transactions_result['error']}")
        
        # Test validation
        print("\n🔍 Testing transaction validation...")
        validation_result = controller.validate_transaction_data(1)
        
        if validation_result['success']:
            print(f"✅ Validation completed")
            print(f"   Legal Compliance: {validation_result['validation']['legal_compliance']}")
        else:
            print(f"⚠️ Validation failed: {validation_result['error']}")
        
        # Test form generation (with mock data)
        print("\n🔄 Testing form generation...")
        form_result = controller.generate_crpa_form(1)
        
        if form_result['success']:
            print(f"✅ Form generation completed")
            print(f"   Processing time: {form_result['processing_time']['total']}s")
            print(f"   Fields mapped: {form_result['field_count']}")
        else:
            print(f"⚠️ Form generation failed: {form_result['error']}")
        
        print("\n🎉 CRPA Controller test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Controller test failed: {e}")
        return False

if __name__ == "__main__":
    # Configure logging for testing
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    test_crpa_controller()