#!/usr/bin/env python3
"""
DataValidator Service - Legal Compliance and Cross-Field Validation

Based on Google AI Studio's architectural recommendations, this service:
1. Validates legal compliance for California real estate forms
2. Implements cross-field consistency checks
3. Enforces business rules and validation constraints
4. Provides detailed validation reports for error handling

Architecture: Enhanced CRPA mapping → DataValidator → Validation Report → Form Generation
"""

import logging
import re
from datetime import datetime, date, timedelta
from decimal import Decimal, InvalidOperation
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
import json
import os

@dataclass
class ValidationError:
    """Represents a single validation error"""
    field_name: str
    error_type: str
    message: str
    severity: str = "error"  # error, warning, info
    suggested_fix: str = ""

@dataclass
class ValidationReport:
    """Comprehensive validation report for form data"""
    is_valid: bool
    errors: List[ValidationError] = field(default_factory=list)
    warnings: List[ValidationError] = field(default_factory=list)
    field_completion_rate: float = 0.0
    legal_compliance_status: str = "unknown"
    business_rules_passed: bool = True
    
    def add_error(self, field_name: str, error_type: str, message: str, suggested_fix: str = ""):
        """Add a validation error"""
        self.errors.append(ValidationError(
            field_name=field_name,
            error_type=error_type,
            message=message,
            severity="error",
            suggested_fix=suggested_fix
        ))
        self.is_valid = False
    
    def add_warning(self, field_name: str, warning_type: str, message: str, suggested_fix: str = ""):
        """Add a validation warning"""
        self.warnings.append(ValidationError(
            field_name=field_name,
            error_type=warning_type,
            message=message,
            severity="warning",
            suggested_fix=suggested_fix
        ))
    
    def get_summary(self) -> str:
        """Get a human-readable validation summary"""
        if self.is_valid:
            return f"✅ Validation passed with {len(self.warnings)} warnings. Field completion: {self.field_completion_rate:.1%}"
        else:
            return f"❌ Validation failed with {len(self.errors)} errors, {len(self.warnings)} warnings. Field completion: {self.field_completion_rate:.1%}"

class DataValidator:
    """
    Enterprise-grade validation service for California real estate forms
    
    Features:
    - Legal compliance validation for California DRE requirements
    - Cross-field consistency checks (dates, financial calculations)
    - Business rule enforcement (contingency periods, price validations)
    - UTF-8 encoding support for international names
    - Configurable validation rules from enhanced mapping JSON
    """
    
    def __init__(self, config_path: str = "form_templates/enhanced_crpa_mapping.json"):
        self.config_path = config_path
        self.logger = logging.getLogger(__name__)
        
        # Load validation configuration
        self.validation_config = self._load_validation_config()
        
        # California-specific validation patterns
        self.ca_license_pattern = re.compile(r'^(\d{8}|[A-Z]{2}-\d{7})$')
        self.phone_pattern = re.compile(r'^\(\d{3}\)\s+\d{3}-\d{4}$')
        self.email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        self.currency_pattern = re.compile(r'^\$[\d,]+\.?\d{0,2}$')
        self.apn_pattern = re.compile(r'^(\d{3}-\d{3}-\d{3}|\d{8,12})$')
        
        # Legal compliance requirements
        self.required_legal_fields = [
            'buyer_agent_license', 'property_address', 'purchase_price', 
            'buyer_name', 'closing_date'
        ]
        
    def _load_validation_config(self) -> Dict[str, Any]:
        """Load enhanced validation configuration from mapping JSON"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config.get('validation_rules', {})
        except Exception as e:
            self.logger.warning(f"Could not load validation config: {e}")
            return {}
    
    def validate_crpa_data(self, form_data: Dict[str, Any]) -> ValidationReport:
        """
        Main validation method: Comprehensive validation of CRPA form data
        
        Args:
            form_data: Dictionary with 33 CRPA fields
            
        Returns:
            ValidationReport with detailed validation results
        """
        report = ValidationReport(is_valid=True)
        
        try:
            # Step 1: Field-level validation
            self._validate_individual_fields(form_data, report)
            
            # Step 2: Cross-field validation
            self._validate_cross_field_constraints(form_data, report)
            
            # Step 3: Business rules validation
            self._validate_business_rules(form_data, report)
            
            # Step 4: Legal compliance validation
            self._validate_legal_compliance(form_data, report)
            
            # Step 5: Calculate completion rate
            report.field_completion_rate = self._calculate_completion_rate(form_data)
            
            # Step 6: Set overall status
            report.legal_compliance_status = "compliant" if len(report.errors) == 0 else "non-compliant"
            report.business_rules_passed = len([e for e in report.errors if e.error_type == "business_rule"]) == 0
            
            self.logger.info(f"Validation completed: {report.get_summary()}")
            return report
            
        except Exception as e:
            self.logger.error(f"Validation failed with exception: {e}")
            report.add_error("system", "validation_error", f"Validation system error: {e}")
            return report
    
    def _validate_individual_fields(self, form_data: Dict[str, Any], report: ValidationReport):
        """Validate individual field formats and requirements"""
        
        # Required field validation
        required_fields = [
            'property_address', 'buyer_name', 'purchase_price', 'closing_date',
            'buyer_agent', 'buyer_agent_license'
        ]
        
        for field in required_fields:
            value = form_data.get(field, "")
            if not value or str(value).strip() == "":
                report.add_error(
                    field, "required_field", 
                    f"Required field '{field}' is missing or empty",
                    f"Provide a valid value for {field}"
                )
        
        # Email validation
        email_fields = ['buyer_email', 'seller_email']
        for field in email_fields:
            value = form_data.get(field, "")
            if value and not self.email_pattern.match(str(value)):
                report.add_error(
                    field, "format_error",
                    f"Invalid email format: {value}",
                    "Use format: user@domain.com"
                )
        
        # Phone validation
        phone_fields = ['buyer_phone', 'seller_phone', 'buyer_agent_phone']
        for field in phone_fields:
            value = form_data.get(field, "")
            if value and not self.phone_pattern.match(str(value)):
                report.add_error(
                    field, "format_error",
                    f"Invalid phone format: {value}",
                    "Use format: (555) 123-4567"
                )
        
        # California license validation
        license_fields = ['buyer_agent_license', 'seller_agent_license']
        for field in license_fields:
            value = form_data.get(field, "")
            if value and not self.ca_license_pattern.match(str(value)):
                report.add_error(
                    field, "legal_compliance",
                    f"Invalid CA DRE license format: {value}",
                    "Use 8-digit format (12345678) or state format (CA-1234567)"
                )
        
        # Currency validation
        currency_fields = ['purchase_price', 'initial_deposit', 'down_payment', 'loan_amount']
        for field in currency_fields:
            value = form_data.get(field, "")
            if value:
                try:
                    # Clean and validate currency
                    cleaned = str(value).replace('$', '').replace(',', '')
                    amount = Decimal(cleaned)
                    
                    if field == 'purchase_price' and (amount < 1000 or amount > 50000000):
                        report.add_error(
                            field, "business_rule",
                            f"Purchase price ${amount:,} is outside reasonable range ($1,000 - $50,000,000)",
                            "Verify purchase price amount"
                        )
                        
                except (ValueError, InvalidOperation):
                    report.add_error(
                        field, "format_error",
                        f"Invalid currency format: {value}",
                        "Use format: $123,456.78"
                    )
        
        # Date validation
        date_fields = ['offer_date', 'closing_date', 'offer_expiration', 'contract_date']
        for field in date_fields:
            value = form_data.get(field, "")
            if value and not self._is_valid_date(str(value)):
                report.add_error(
                    field, "format_error",
                    f"Invalid date format: {value}",
                    "Use format: MM/DD/YYYY"
                )
        
        # APN validation
        apn = form_data.get('apn', "")
        if apn and not self.apn_pattern.match(str(apn)):
            report.add_warning(
                'apn', "format_warning",
                f"APN format may be incorrect: {apn}",
                "Verify APN format with county records"
            )
    
    def _validate_cross_field_constraints(self, form_data: Dict[str, Any], report: ValidationReport):
        """Validate relationships between fields"""
        
        # Date consistency checks
        offer_date = self._parse_date(form_data.get('offer_date', ''))
        closing_date = self._parse_date(form_data.get('closing_date', ''))
        offer_expiration = self._parse_date(form_data.get('offer_expiration', ''))
        
        if offer_date and closing_date:
            if closing_date <= offer_date:
                report.add_error(
                    'closing_date', "cross_field_error",
                    "Closing date must be after offer date",
                    "Set closing date to at least 7 days after offer date"
                )
            
            # Check minimum closing period (7 days)
            min_closing = offer_date + timedelta(days=7)
            if closing_date < min_closing:
                report.add_warning(
                    'closing_date', "business_warning",
                    "Closing date is very soon after offer date",
                    "Consider allowing more time for processing"
                )
        
        if offer_date and offer_expiration:
            if offer_expiration <= offer_date:
                report.add_error(
                    'offer_expiration', "cross_field_error",
                    "Offer expiration must be after offer date",
                    "Set expiration to reasonable time after offer"
                )
        
        # Financial consistency checks
        try:
            purchase_price = self._parse_currency(form_data.get('purchase_price', '0'))
            initial_deposit = self._parse_currency(form_data.get('initial_deposit', '0'))
            down_payment = self._parse_currency(form_data.get('down_payment', '0'))
            loan_amount = self._parse_currency(form_data.get('loan_amount', '0'))
            
            if purchase_price > 0:
                # Initial deposit should be less than purchase price
                if initial_deposit >= purchase_price:
                    report.add_error(
                        'initial_deposit', "cross_field_error",
                        "Initial deposit cannot equal or exceed purchase price",
                        "Set initial deposit to reasonable percentage of purchase price"
                    )
                
                # Down payment should not exceed purchase price
                if down_payment > purchase_price:
                    report.add_error(
                        'down_payment', "cross_field_error",
                        "Down payment cannot exceed purchase price",
                        "Verify down payment amount"
                    )
                
                # Financial calculation check
                if loan_amount > 0 and down_payment > 0:
                    expected_loan = purchase_price - down_payment
                    if abs(loan_amount - expected_loan) > 1000:  # Allow $1000 tolerance
                        report.add_warning(
                            'loan_amount', "calculation_warning",
                            f"Loan amount ${loan_amount:,} doesn't match purchase price - down payment (${expected_loan:,})",
                            "Verify loan amount calculation"
                        )
        
        except Exception as e:
            report.add_warning("financial", "calculation_error", f"Could not validate financial calculations: {e}")
    
    def _validate_business_rules(self, form_data: Dict[str, Any], report: ValidationReport):
        """Validate real estate business rules"""
        
        # Contingency period validation
        financing_days = self._parse_number(form_data.get('financing_contingency_days', '0'))
        inspection_days = self._parse_number(form_data.get('inspection_contingency_days', '0'))
        
        if financing_days < 0 or financing_days > 60:
            report.add_error(
                'financing_contingency_days', "business_rule",
                f"Financing contingency period ({financing_days} days) must be 0-60 days",
                "Set contingency period within legal limits"
            )
        
        if inspection_days < 0 or inspection_days > 30:
            report.add_error(
                'inspection_contingency_days', "business_rule", 
                f"Inspection contingency period ({inspection_days} days) must be 0-30 days",
                "Set inspection period within standard limits"
            )
        
        # Property type validation
        valid_property_types = [
            "Single Family Residence", "Condominium", "Townhouse", 
            "Multi-Unit", "Vacant Land", ""
        ]
        property_type = form_data.get('property_type', '')
        if property_type and property_type not in valid_property_types:
            report.add_warning(
                'property_type', "business_warning",
                f"Unusual property type: {property_type}",
                "Verify property type classification"
            )
        
        # Address completeness check
        property_address = form_data.get('property_address', '')
        if property_address and not re.search(r'\d+', property_address):
            report.add_warning(
                'property_address', "completeness_warning",
                "Property address may be missing street number",
                "Include complete street address with number"
            )
    
    def _validate_legal_compliance(self, form_data: Dict[str, Any], report: ValidationReport):
        """Validate California real estate legal compliance requirements"""
        
        # California DRE requirements
        buyer_agent_license = form_data.get('buyer_agent_license', '')
        if not buyer_agent_license:
            report.add_error(
                'buyer_agent_license', "legal_compliance",
                "Buyer agent license number is required for California transactions",
                "Provide valid CA DRE license number"
            )
        
        # Required disclosures check (business logic)
        purchase_price = self._parse_currency(form_data.get('purchase_price', '0'))
        if purchase_price > 1000000:  # $1M+ requires additional disclosures
            report.add_warning(
                'purchase_price', "legal_warning",
                "High-value transaction may require additional disclosures",
                "Consult with legal counsel for $1M+ transactions"
            )
        
        # Title company recommendation for high-value transactions
        title_company = form_data.get('title_company', '')
        if purchase_price > 500000 and not title_company:
            report.add_warning(
                'title_company', "business_recommendation",
                "Title company recommended for transactions over $500,000",
                "Consider specifying title company for enhanced protection"
            )
    
    def _calculate_completion_rate(self, form_data: Dict[str, Any]) -> float:
        """Calculate percentage of fields completed"""
        total_fields = 33  # Total CRPA fields
        completed_fields = 0
        
        for field_name in form_data:
            value = form_data.get(field_name, "")
            if value and str(value).strip():
                completed_fields += 1
        
        return completed_fields / total_fields if total_fields > 0 else 0.0
    
    def _is_valid_date(self, date_string: str) -> bool:
        """Check if string is a valid date"""
        try:
            self._parse_date(date_string)
            return True
        except:
            return False
    
    def _parse_date(self, date_string: str) -> Optional[date]:
        """Parse date string into date object"""
        if not date_string:
            return None
        
        # Try various date formats
        formats = ['%m/%d/%Y', '%Y-%m-%d', '%m-%d-%Y', '%B %d, %Y']
        
        for fmt in formats:
            try:
                return datetime.strptime(str(date_string), fmt).date()
            except ValueError:
                continue
        
        return None
    
    def _parse_currency(self, currency_string: str) -> Decimal:
        """Parse currency string into Decimal"""
        if not currency_string:
            return Decimal('0')
        
        try:
            cleaned = str(currency_string).replace('$', '').replace(',', '')
            return Decimal(cleaned)
        except (ValueError, InvalidOperation):
            return Decimal('0')
    
    def _parse_number(self, number_string: str) -> int:
        """Parse number string into integer"""
        try:
            return int(str(number_string))
        except (ValueError, TypeError):
            return 0
    
    def generate_validation_summary_html(self, report: ValidationReport) -> str:
        """Generate HTML summary of validation results for UI display"""
        
        status_color = "green" if report.is_valid else "red"
        status_icon = "✅" if report.is_valid else "❌"
        
        html = f"""
        <div class="validation-summary" style="border: 2px solid {status_color}; padding: 15px; margin: 10px; border-radius: 5px;">
            <h3>{status_icon} Validation Summary</h3>
            <p><strong>Status:</strong> {report.get_summary()}</p>
            <p><strong>Legal Compliance:</strong> {report.legal_compliance_status.title()}</p>
            <p><strong>Field Completion:</strong> {report.field_completion_rate:.1%}</p>
        """
        
        if report.errors:
            html += "<h4 style='color: red;'>Errors:</h4><ul>"
            for error in report.errors:
                html += f"<li><strong>{error.field_name}:</strong> {error.message}"
                if error.suggested_fix:
                    html += f" <em>({error.suggested_fix})</em>"
                html += "</li>"
            html += "</ul>"
        
        if report.warnings:
            html += "<h4 style='color: orange;'>Warnings:</h4><ul>"
            for warning in report.warnings:
                html += f"<li><strong>{warning.field_name}:</strong> {warning.message}"
                if warning.suggested_fix:
                    html += f" <em>({warning.suggested_fix})</em>"
                html += "</li>"
            html += "</ul>"
        
        html += "</div>"
        return html

# Test function for development
def test_data_validator():
    """Test function to validate DataValidator functionality"""
    
    # Sample form data for testing
    test_data = {
        'property_address': '123 Main Street',
        'city_state_zip': 'Sacramento, CA 95814',
        'buyer_name': 'John Smith',
        'buyer_email': 'john.smith@email.com',
        'buyer_phone': '(555) 123-4567',
        'buyer_agent': 'Narissa Jennings',
        'buyer_agent_license': '02129287',
        'purchase_price': '$450,000.00',
        'initial_deposit': '$15,000.00',
        'down_payment': '$90,000.00',
        'loan_amount': '$360,000.00',
        'offer_date': '06/01/2025',
        'closing_date': '07/15/2025',
        'financing_contingency_days': '21',
        'inspection_contingency_days': '17'
    }
    
    validator = DataValidator()
    
    print("🔍 Testing DataValidator with sample CRPA data...")
    report = validator.validate_crpa_data(test_data)
    
    print(f"\n{report.get_summary()}")
    print(f"Legal Compliance: {report.legal_compliance_status}")
    print(f"Field Completion: {report.field_completion_rate:.1%}")
    
    if report.errors:
        print(f"\n❌ Errors ({len(report.errors)}):")
        for error in report.errors:
            print(f"  • {error.field_name}: {error.message}")
    
    if report.warnings:
        print(f"\n⚠️ Warnings ({len(report.warnings)}):")
        for warning in report.warnings:
            print(f"  • {warning.field_name}: {warning.message}")
    
    # Test HTML generation
    html_summary = validator.generate_validation_summary_html(report)
    print(f"\n📄 Generated HTML validation summary ({len(html_summary)} characters)")
    
    return report

if __name__ == "__main__":
    test_data_validator()