#!/usr/bin/env python3
"""
Multi-Form Support Backend API
Task #6: Build Multi-Form Support Backend

REST API endpoints for form selection, population, and management.
Integrates with the Form Population Engine and Validation Framework.
"""

import os
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

from flask import Blueprint, request, jsonify, send_file
from werkzeug.exceptions import BadRequest, NotFound, InternalServerError
import logging

from form_population_engine import FormPopulationEngine
from validation_framework import FormValidationFramework
from coordinate_based_form_filler import CoordinateBasedFormFiller

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask Blueprint for form API
form_api = Blueprint('form_api', __name__, url_prefix='/api/forms')

class FormBackendService:
    """Service layer for form backend operations"""
    
    def __init__(self):
        self.population_engine = FormPopulationEngine()
        self.validation_framework = FormValidationFramework()
        self.form_filler = CoordinateBasedFormFiller()
        self.supported_forms = self._load_supported_forms()
        
    def _load_supported_forms(self) -> Dict[str, Dict]:
        """Load list of supported forms with metadata"""
        return {
            'california_purchase_agreement': {
                'name': 'California Residential Purchase Agreement',
                'description': 'Primary transaction form for California real estate purchases',
                'pages': 27,
                'category': 'purchase_contracts',
                'required_data': ['client', 'property', 'transaction'],
                'estimated_time': '5-10 minutes',
                'legal_requirements': ['buyer_name', 'seller_name', 'property_address', 'purchase_price']
            },
            'buyer_representation_agreement': {
                'name': 'Buyer Representation and Broker Compensation Agreement',
                'description': 'Agreement between buyer and real estate agent',
                'pages': 13,
                'category': 'representation_agreements',
                'required_data': ['client', 'agent'],
                'estimated_time': '3-5 minutes',
                'legal_requirements': ['buyer_name', 'agent_name', 'commission_rate']
            },
            'transaction_record': {
                'name': 'Transaction Record',
                'description': 'Complete transaction documentation and timeline',
                'pages': 3,
                'category': 'transaction_documentation',
                'required_data': ['client', 'property', 'transaction'],
                'estimated_time': '2-3 minutes',
                'legal_requirements': ['transaction_id', 'parties', 'property_details']
            },
            'verification_property_condition': {
                'name': 'Verification of Property Condition',
                'description': 'Property condition disclosure and verification',
                'pages': 1,
                'category': 'disclosures',
                'required_data': ['property'],
                'estimated_time': '1-2 minutes',
                'legal_requirements': ['property_address', 'condition_details']
            },
            'statewide_buyer_seller_advisory': {
                'name': 'Statewide Buyer and Seller Advisory',
                'description': 'Required advisory for California real estate transactions',
                'pages': 15,
                'category': 'advisories',
                'required_data': ['client'],
                'estimated_time': '2-3 minutes',
                'legal_requirements': ['parties', 'acknowledgment']
            }
        }
    
    def get_forms_list(self, category: Optional[str] = None) -> List[Dict]:
        """Get list of available forms with metadata"""
        forms_list = []
        
        for form_id, form_info in self.supported_forms.items():
            if category and form_info['category'] != category:
                continue
                
            forms_list.append({
                'id': form_id,
                'name': form_info['name'],
                'description': form_info['description'],
                'pages': form_info['pages'],
                'category': form_info['category'],
                'estimated_time': form_info['estimated_time'],
                'required_data': form_info['required_data']
            })
        
        return forms_list
    
    def get_form_details(self, form_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific form"""
        if form_id not in self.supported_forms:
            raise NotFound(f"Form not found: {form_id}")
        
        form_info = self.supported_forms[form_id]
        
        # Get field mapping information
        mapping_config = self.population_engine.mapping_config
        form_mappings = mapping_config['form_mappings'].get(form_id, {})
        
        return {
            'id': form_id,
            'metadata': form_info,
            'field_count': len(form_mappings.get('mappings', {})),
            'required_fields': form_info['legal_requirements'],
            'sample_fields': list(form_mappings.get('mappings', {}).keys())[:10],
            'validation_rules': list(form_mappings.get('validation_rules', {}).keys()),
            'supported_data_sources': form_mappings.get('mappings', {})
        }
    
    def populate_form_request(self, form_id: str, client_id: str, property_id: str, 
                            transaction_id: str = None, options: Dict = None) -> Dict[str, Any]:
        """Handle form population request"""
        
        logger.info(f"🚀 Processing form population request: {form_id}")
        
        # Validate form exists
        if form_id not in self.supported_forms:
            raise NotFound(f"Unsupported form: {form_id}")
        
        # Validate required parameters
        if not client_id:
            raise BadRequest("client_id is required")
        if not property_id and 'property' in self.supported_forms[form_id]['required_data']:
            raise BadRequest("property_id is required for this form")
        
        try:
            # Use population engine to generate form
            result = self.population_engine.populate_form(
                form_name=form_id,
                client_id=client_id,
                property_id=property_id,
                transaction_id=transaction_id
            )
            
            # Add backend metadata
            result.update({
                'api_version': '1.0',
                'backend_timestamp': datetime.now().isoformat(),
                'form_metadata': self.supported_forms[form_id],
                'request_parameters': {
                    'client_id': client_id,
                    'property_id': property_id,
                    'transaction_id': transaction_id,
                    'options': options or {}
                }
            })
            
            logger.info(f"✅ Form population completed: {result['success']}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Form population failed: {e}")
            raise InternalServerError(f"Form population failed: {str(e)}")
    
    def validate_form_request(self, form_id: str, field_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle form validation request"""
        
        logger.info(f"🔍 Processing form validation request: {form_id}")
        
        if form_id not in self.supported_forms:
            raise NotFound(f"Unsupported form: {form_id}")
        
        try:
            # Use validation framework
            validation_result = self.validation_framework.validate_form_data(form_id, field_data)
            
            # Add backend metadata
            validation_result.update({
                'api_version': '1.0',
                'validation_timestamp': datetime.now().isoformat(),
                'form_metadata': self.supported_forms[form_id]
            })
            
            logger.info(f"✅ Form validation completed: {validation_result['overall_valid']}")
            return validation_result
            
        except Exception as e:
            logger.error(f"❌ Form validation failed: {e}")
            raise InternalServerError(f"Form validation failed: {str(e)}")

# Initialize service
form_service = FormBackendService()

# API Routes
@form_api.route('/list', methods=['GET'])
def list_forms():
    """Get list of available forms"""
    try:
        category = request.args.get('category')
        forms = form_service.get_forms_list(category)
        
        return jsonify({
            'success': True,
            'forms': forms,
            'total_count': len(forms),
            'categories': list(set(form['category'] for form in forms)),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ List forms error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@form_api.route('/<form_id>/details', methods=['GET'])
def get_form_details(form_id: str):
    """Get detailed information about a specific form"""
    try:
        details = form_service.get_form_details(form_id)
        
        return jsonify({
            'success': True,
            'form_details': details,
            'timestamp': datetime.now().isoformat()
        })
        
    except NotFound as e:
        return jsonify({'success': False, 'error': str(e)}), 404
    except Exception as e:
        logger.error(f"❌ Get form details error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@form_api.route('/populate', methods=['POST'])
def populate_form():
    """Populate a form with CRM data"""
    try:
        data = request.get_json()
        
        if not data:
            raise BadRequest("JSON data required")
        
        form_id = data.get('form_id')
        client_id = data.get('client_id')
        property_id = data.get('property_id')
        transaction_id = data.get('transaction_id')
        options = data.get('options', {})
        
        result = form_service.populate_form_request(
            form_id=form_id,
            client_id=client_id,
            property_id=property_id,
            transaction_id=transaction_id,
            options=options
        )
        
        return jsonify({
            'success': True,
            'population_result': result,
            'timestamp': datetime.now().isoformat()
        })
        
    except (BadRequest, NotFound) as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except InternalServerError as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    except Exception as e:
        logger.error(f"❌ Populate form error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@form_api.route('/validate', methods=['POST'])
def validate_form():
    """Validate form field data"""
    try:
        data = request.get_json()
        
        if not data:
            raise BadRequest("JSON data required")
        
        form_id = data.get('form_id')
        field_data = data.get('field_data', {})
        
        if not form_id:
            raise BadRequest("form_id is required")
        
        result = form_service.validate_form_request(form_id, field_data)
        
        return jsonify({
            'success': True,
            'validation_result': result,
            'timestamp': datetime.now().isoformat()
        })
        
    except (BadRequest, NotFound) as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except InternalServerError as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    except Exception as e:
        logger.error(f"❌ Validate form error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@form_api.route('/download/<form_id>/<file_name>', methods=['GET'])
def download_form(form_id: str, file_name: str):
    """Download a generated form file"""
    try:
        # Security: validate form_id and file_name
        if form_id not in form_service.supported_forms:
            raise NotFound("Form not found")
        
        # Construct safe file path
        output_dir = Path('output')
        file_path = output_dir / file_name
        
        # Security: ensure file exists and is in output directory
        if not file_path.exists() or not str(file_path).startswith(str(output_dir.absolute())):
            raise NotFound("File not found")
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=file_name,
            mimetype='application/pdf'
        )
        
    except NotFound as e:
        return jsonify({'success': False, 'error': str(e)}), 404
    except Exception as e:
        logger.error(f"❌ Download form error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@form_api.route('/status', methods=['GET'])
def api_status():
    """Get API status and configuration"""
    try:
        return jsonify({
            'success': True,
            'api_status': 'operational',
            'version': '1.0',
            'supported_forms_count': len(form_service.supported_forms),
            'endpoints': [
                '/api/forms/list',
                '/api/forms/<form_id>/details',
                '/api/forms/populate',
                '/api/forms/validate',
                '/api/forms/download/<form_id>/<file_name>',
                '/api/forms/status'
            ],
            'population_engine_status': 'loaded',
            'validation_framework_status': 'loaded',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ API status error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

def test_form_api():
    """Test the form API functionality"""
    
    print("🧪 Testing Form API Backend")
    print("=" * 50)
    
    try:
        # Test 1: Get forms list
        forms = form_service.get_forms_list()
        print(f"✅ Available forms: {len(forms)}")
        for form in forms[:3]:
            print(f"   - {form['name']} ({form['pages']} pages)")
        
        # Test 2: Get form details
        details = form_service.get_form_details('california_purchase_agreement')
        print(f"✅ Form details loaded: {details['field_count']} fields")
        
        # Test 3: Test form population
        result = form_service.populate_form_request(
            form_id='california_purchase_agreement',
            client_id='test_client_001',
            property_id='test_property_001',
            transaction_id='test_transaction_001'
        )
        print(f"✅ Form population test: {result['success']}")
        print(f"📄 Output file: {result.get('output_path', 'Not created')}")
        
        # Test 4: Test validation
        test_data = {
            'buyer_name': 'John Smith',
            'purchase_price': 850000,
            'buyer_email': 'john@example.com'
        }
        
        validation = form_service.validate_form_request('california_purchase_agreement', test_data)
        print(f"✅ Form validation test: {validation['overall_valid']}")
        print(f"📊 Valid fields: {validation['validation_summary']['valid_fields']}")
        
        print(f"\n🎯 API Backend Ready for Integration")
        return True
        
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

if __name__ == "__main__":
    test_form_api()