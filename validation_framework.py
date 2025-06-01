#!/usr/bin/env python3
"""
Form Validation Framework
Task #5: Comprehensive validation for populated forms

Ensures populated forms meet legal and business requirements
with detailed error reporting and correction suggestions.
"""

import json
import re
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
from typing import Dict, Any, List, Tuple, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FormValidationFramework:
    """Comprehensive validation framework for populated forms"""
    
    def __init__(self):
        self.validation_rules = self._load_validation_rules()
        self.business_rules = self._load_business_rules()
        self.legal_requirements = self._load_legal_requirements()
        
    def _load_validation_rules(self) -> Dict[str, callable]:
        """Load field-level validation rules"""
        return {
            # Basic format validations
            'non_empty': self._validate_non_empty,
            'email_format': self._validate_email,
            'phone_format': self._validate_phone,
            'currency_format': self._validate_currency,
            'date_format': self._validate_date,
            'zip_format': self._validate_zip,
            'state_code': self._validate_state_code,
            'license_format': self._validate_license,
            'apn_format': self._validate_apn,
            'address_format': self._validate_address,
            
            # Advanced validations
            'price_range': self._validate_price_range,
            'percentage_format': self._validate_percentage,
            'loan_to_value': self._validate_loan_to_value,
            'future_date': self._validate_future_date
        }
    
    def _load_business_rules(self) -> Dict[str, Dict]:
        """Load business logic validation rules"""
        return {
            'purchase_price_limits': {
                'min_value': 50000,
                'max_value': 50000000,
                'message': 'Purchase price must be between $50,000 and $50,000,000'
            },
            'earnest_money_percentage': {
                'min_percentage': 0.5,  # 0.5% of purchase price
                'max_percentage': 10.0,  # 10% of purchase price
                'message': 'Earnest money should be 0.5% to 10% of purchase price'
            },
            'down_payment_minimum': {
                'conventional_min': 3.0,  # 3% for conventional loans
                'fha_min': 3.5,          # 3.5% for FHA loans
                'va_min': 0.0,           # 0% for VA loans
                'message': 'Down payment percentage below recommended minimum'
            },
            'closing_timeline': {
                'min_days': 14,  # Minimum 14 days from contract to close
                'max_days': 60,  # Maximum 60 days typical
                'message': 'Closing timeline should be 14-60 days from contract date'
            },
            'commission_rates': {
                'min_rate': 1.0,  # 1% minimum
                'max_rate': 10.0, # 10% maximum
                'typical_range': (5.0, 7.0),
                'message': 'Commission rate outside typical range (5-7%)'
            }
        }
    
    def _load_legal_requirements(self) -> Dict[str, List[str]]:
        """Load legal requirements for California real estate forms"""
        return {
            'california_purchase_agreement': [
                'buyer_name',
                'seller_name', 
                'property_address',
                'purchase_price',
                'earnest_money',
                'closing_date',
                'possession_date',
                'listing_agent_license',
                'brokerage_name'
            ],
            'buyer_representation_agreement': [
                'buyer_name',
                'agent_name',
                'agent_license',
                'brokerage_name',
                'commission_rate',
                'agreement_date',
                'expiration_date'
            ],
            'disclosure_requirements': [
                'property_condition_disclosure',
                'lead_paint_disclosure',
                'natural_hazard_disclosure',
                'transfer_disclosure_statement'
            ]
        }
    
    # Basic validation methods
    def _validate_non_empty(self, value: Any) -> Tuple[bool, str]:
        """Validate field is not empty"""
        if not value or (isinstance(value, str) and not value.strip()):
            return False, "Field cannot be empty"
        return True, "Valid"
    
    def _validate_email(self, value: str) -> Tuple[bool, str]:
        """Validate email format"""
        if not value:
            return False, "Email is required"
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if re.match(email_pattern, value):
            return True, "Valid email format"
        return False, "Invalid email format (example: name@domain.com)"
    
    def _validate_phone(self, value: str) -> Tuple[bool, str]:
        """Validate phone number format"""
        if not value:
            return False, "Phone number is required"
        
        # Remove all non-digit characters
        digits = re.sub(r'\D', '', value)
        
        if len(digits) == 10:
            return True, "Valid phone number"
        elif len(digits) == 11 and digits[0] == '1':
            return True, "Valid phone number with country code"
        else:
            return False, "Phone number must be 10 digits (example: (555) 123-4567)"
    
    def _validate_currency(self, value: Any) -> Tuple[bool, str]:
        """Validate currency format and value"""
        try:
            if isinstance(value, str):
                # Remove currency symbols and commas
                clean_value = re.sub(r'[$,]', '', value)
                amount = Decimal(clean_value)
            else:
                amount = Decimal(str(value))
            
            if amount < 0:
                return False, "Amount cannot be negative"
            if amount > Decimal('999999999.99'):
                return False, "Amount exceeds maximum limit"
            
            return True, f"Valid currency amount: ${amount:,.2f}"
            
        except (InvalidOperation, ValueError):
            return False, "Invalid currency format (example: $123,456.78)"
    
    def _validate_date(self, value: Any) -> Tuple[bool, str]:
        """Validate date format"""
        if not value:
            return False, "Date is required"
        
        try:
            if isinstance(value, str):
                # Try multiple date formats
                formats = ['%Y-%m-%d', '%m/%d/%Y', '%m-%d-%Y', '%Y/%m/%d']
                for fmt in formats:
                    try:
                        parsed_date = datetime.strptime(value, fmt).date()
                        return True, f"Valid date: {parsed_date}"
                    except ValueError:
                        continue
                return False, "Invalid date format (use YYYY-MM-DD or MM/DD/YYYY)"
            elif isinstance(value, (date, datetime)):
                return True, f"Valid date: {value}"
            else:
                return False, "Invalid date type"
                
        except Exception as e:
            return False, f"Date validation error: {e}"
    
    def _validate_zip(self, value: str) -> Tuple[bool, str]:
        """Validate ZIP code format"""
        if not value:
            return False, "ZIP code is required"
        
        # Remove spaces and hyphens
        clean_zip = re.sub(r'[\s-]', '', value)
        
        if re.match(r'^\d{5}$', clean_zip):
            return True, "Valid 5-digit ZIP code"
        elif re.match(r'^\d{9}$', clean_zip):
            return True, "Valid 9-digit ZIP code"
        else:
            return False, "ZIP code must be 5 or 9 digits (example: 12345 or 12345-6789)"
    
    def _validate_state_code(self, value: str) -> Tuple[bool, str]:
        """Validate state code"""
        if not value:
            return False, "State code is required"
        
        if len(value) == 2 and value.upper().isalpha():
            return True, f"Valid state code: {value.upper()}"
        return False, "State code must be 2 letters (example: CA)"
    
    def _validate_license(self, value: str) -> Tuple[bool, str]:
        """Validate real estate license number"""
        if not value:
            return False, "License number is required"
        
        # California license format: 2 letters + 8 digits
        if re.match(r'^[A-Z]{2}\d{8}$', value.upper()):
            return True, f"Valid CA license format: {value.upper()}"
        elif len(value) >= 6:
            return True, f"Valid license number: {value}"
        else:
            return False, "License number must be at least 6 characters"
    
    def _validate_apn(self, value: str) -> Tuple[bool, str]:
        """Validate Assessor's Parcel Number"""
        if not value:
            return False, "APN is recommended for property identification"
        
        # Common APN formats: 123-456-789 or 1234-567-890
        if re.match(r'^\d{3,4}-\d{3}-\d{3}$', value):
            return True, f"Valid APN format: {value}"
        elif len(value) >= 8:
            return True, f"Valid APN: {value}"
        else:
            return False, "APN should be in format 123-456-789"
    
    def _validate_address(self, value: str) -> Tuple[bool, str]:
        """Validate address format"""
        if not value:
            return False, "Address is required"
        
        if len(value.strip()) < 10:
            return False, "Address appears incomplete"
        
        # Check for street number and name
        if re.search(r'\d+', value) and re.search(r'[A-Za-z]', value):
            return True, "Valid address format"
        
        return False, "Address should include street number and name"
    
    # Advanced validation methods
    def _validate_price_range(self, value: Any) -> Tuple[bool, str]:
        """Validate price is within reasonable range"""
        try:
            amount = float(value)
            rules = self.business_rules['purchase_price_limits']
            
            if amount < rules['min_value']:
                return False, f"Price below minimum: ${rules['min_value']:,}"
            if amount > rules['max_value']:
                return False, f"Price above maximum: ${rules['max_value']:,}"
            
            return True, f"Price within acceptable range: ${amount:,.2f}"
            
        except (ValueError, TypeError):
            return False, "Invalid price format"
    
    def _validate_percentage(self, value: Any) -> Tuple[bool, str]:
        """Validate percentage format"""
        try:
            pct = float(value)
            if 0 <= pct <= 100:
                return True, f"Valid percentage: {pct}%"
            else:
                return False, "Percentage must be between 0 and 100"
        except (ValueError, TypeError):
            return False, "Invalid percentage format"
    
    def _validate_loan_to_value(self, loan_amount: Any, property_value: Any) -> Tuple[bool, str]:
        """Validate loan-to-value ratio"""
        try:
            loan = float(loan_amount)
            value = float(property_value)
            
            if value <= 0:
                return False, "Property value must be greater than 0"
            
            ltv = (loan / value) * 100
            
            if ltv > 97:  # Most programs cap at 97% LTV
                return False, f"LTV ratio too high: {ltv:.1f}% (max typically 97%)"
            elif ltv > 80:
                return True, f"High LTV ratio: {ltv:.1f}% (may require PMI)"
            else:
                return True, f"Good LTV ratio: {ltv:.1f}%"
                
        except (ValueError, TypeError, ZeroDivisionError):
            return False, "Invalid loan or property value for LTV calculation"
    
    def _validate_future_date(self, value: Any) -> Tuple[bool, str]:
        """Validate date is in the future"""
        try:
            if isinstance(value, str):
                check_date = datetime.strptime(value, '%Y-%m-%d').date()
            else:
                check_date = value
            
            if check_date <= date.today():
                return False, f"Date must be in the future (after {date.today()})"
            
            return True, f"Valid future date: {check_date}"
            
        except (ValueError, TypeError):
            return False, "Invalid date for future date validation"
    
    def validate_form_data(self, form_name: str, field_data: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive validation of form data"""
        
        logger.info(f"🔍 Starting validation for form: {form_name}")
        
        validation_results = {
            'form_name': form_name,
            'overall_valid': True,
            'field_validations': {},
            'business_rule_violations': [],
            'legal_requirement_failures': [],
            'warnings': [],
            'validation_summary': {
                'total_fields': len(field_data),
                'valid_fields': 0,
                'invalid_fields': 0,
                'warning_fields': 0
            }
        }
        
        # Field-level validation
        for field_name, value in field_data.items():
            field_result = self._validate_field(field_name, value)
            validation_results['field_validations'][field_name] = field_result
            
            if field_result['valid']:
                validation_results['validation_summary']['valid_fields'] += 1
            else:
                validation_results['validation_summary']['invalid_fields'] += 1
                validation_results['overall_valid'] = False
            
            if field_result.get('warnings'):
                validation_results['validation_summary']['warning_fields'] += 1
        
        # Business rule validation
        business_violations = self._validate_business_rules(field_data)
        validation_results['business_rule_violations'] = business_violations
        
        if business_violations:
            validation_results['overall_valid'] = False
        
        # Legal requirement validation
        legal_failures = self._validate_legal_requirements(form_name, field_data)
        validation_results['legal_requirement_failures'] = legal_failures
        
        if legal_failures:
            validation_results['overall_valid'] = False
        
        logger.info(f"✅ Validation complete: {validation_results['overall_valid']}")
        logger.info(f"📊 Valid fields: {validation_results['validation_summary']['valid_fields']}/{validation_results['validation_summary']['total_fields']}")
        
        return validation_results
    
    def _validate_field(self, field_name: str, value: Any) -> Dict[str, Any]:
        """Validate individual field"""
        result = {
            'field_name': field_name,
            'value': value,
            'valid': True,
            'errors': [],
            'warnings': [],
            'suggestions': []
        }
        
        # Apply relevant validation rules based on field name patterns
        if 'email' in field_name.lower():
            is_valid, message = self._validate_email(str(value) if value else '')
            if not is_valid:
                result['valid'] = False
                result['errors'].append(message)
        
        elif 'phone' in field_name.lower():
            is_valid, message = self._validate_phone(str(value) if value else '')
            if not is_valid:
                result['valid'] = False
                result['errors'].append(message)
        
        elif 'price' in field_name.lower() or 'amount' in field_name.lower():
            is_valid, message = self._validate_currency(value)
            if not is_valid:
                result['valid'] = False
                result['errors'].append(message)
        
        elif 'date' in field_name.lower():
            is_valid, message = self._validate_date(value)
            if not is_valid:
                result['valid'] = False
                result['errors'].append(message)
        
        elif 'zip' in field_name.lower():
            is_valid, message = self._validate_zip(str(value) if value else '')
            if not is_valid:
                result['valid'] = False
                result['errors'].append(message)
        
        elif 'state' in field_name.lower():
            is_valid, message = self._validate_state_code(str(value) if value else '')
            if not is_valid:
                result['valid'] = False
                result['errors'].append(message)
        
        elif 'license' in field_name.lower():
            is_valid, message = self._validate_license(str(value) if value else '')
            if not is_valid:
                result['valid'] = False
                result['errors'].append(message)
        
        elif 'address' in field_name.lower():
            is_valid, message = self._validate_address(str(value) if value else '')
            if not is_valid:
                result['valid'] = False
                result['errors'].append(message)
        
        # Check for empty required fields
        if not value or (isinstance(value, str) and not value.strip()):
            result['warnings'].append("Field is empty - verify if this is acceptable")
        
        return result
    
    def _validate_business_rules(self, field_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """Validate business logic rules"""
        violations = []
        
        # Check earnest money percentage
        if 'purchase_price' in field_data and 'earnest_money' in field_data:
            try:
                purchase_price = float(field_data['purchase_price'])
                earnest_money = float(field_data['earnest_money'])
                
                if purchase_price > 0:
                    earnest_percentage = (earnest_money / purchase_price) * 100
                    rules = self.business_rules['earnest_money_percentage']
                    
                    if earnest_percentage < rules['min_percentage']:
                        violations.append({
                            'rule': 'earnest_money_percentage',
                            'message': f"Earnest money {earnest_percentage:.1f}% below minimum {rules['min_percentage']}%",
                            'severity': 'warning'
                        })
                    elif earnest_percentage > rules['max_percentage']:
                        violations.append({
                            'rule': 'earnest_money_percentage', 
                            'message': f"Earnest money {earnest_percentage:.1f}% above typical maximum {rules['max_percentage']}%",
                            'severity': 'warning'
                        })
            except (ValueError, TypeError, ZeroDivisionError):
                pass
        
        return violations
    
    def _validate_legal_requirements(self, form_name: str, field_data: Dict[str, Any]) -> List[str]:
        """Validate legal requirements are met"""
        failures = []
        
        if form_name in self.legal_requirements:
            required_fields = self.legal_requirements[form_name]
            
            for required_field in required_fields:
                if required_field not in field_data or not field_data[required_field]:
                    failures.append(f"Missing required field: {required_field}")
        
        return failures

def test_validation_framework():
    """Test the validation framework"""
    
    print("🧪 Testing Form Validation Framework")
    print("=" * 50)
    
    validator = FormValidationFramework()
    
    # Test data with some issues
    test_data = {
        'buyer_name': 'John Smith',
        'buyer_email': 'invalid-email',  # Invalid email
        'buyer_phone': '555-1234',       # Too short
        'purchase_price': 850000,
        'earnest_money': 500,            # Too low percentage
        'closing_date': '2025-07-15',
        'property_state': 'California',  # Should be 2-letter code
        'buyer_zip': '12345'
    }
    
    results = validator.validate_form_data('california_purchase_agreement', test_data)
    
    print(f"✅ Overall Valid: {results['overall_valid']}")
    print(f"📊 Summary: {results['validation_summary']}")
    
    print(f"\n❌ Field Validation Errors:")
    for field, validation in results['field_validations'].items():
        if not validation['valid']:
            print(f"   {field}: {', '.join(validation['errors'])}")
    
    print(f"\n⚠️ Business Rule Violations:")
    for violation in results['business_rule_violations']:
        print(f"   {violation['rule']}: {violation['message']}")
    
    print(f"\n⚖️ Legal Requirement Failures:")
    for failure in results['legal_requirement_failures']:
        print(f"   {failure}")
    
    return results

if __name__ == "__main__":
    test_validation_framework()