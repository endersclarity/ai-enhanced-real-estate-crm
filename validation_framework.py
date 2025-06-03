#!/usr/bin/env python3
"""
Form Population Validation Framework - ENGINE002
Comprehensive validation for populated CAR forms ensuring legal and business compliance
"""

from datetime import datetime, date
from typing import Dict, List, Any, Optional
import re

class FormValidationFramework:
    """Comprehensive validation framework for populated forms"""
    
    def __init__(self):
        self.required_fields = {
            "california_residential_purchase_agreement": [
                "buyer_name", "seller_name", "property_address",
                "purchase_price", "closing_date", "contract_date"
            ]
        }
    
    def validate_populated_form(self, form_data: Dict[str, Any], 
                               form_type: str = "california_residential_purchase_agreement") -> Dict[str, Any]:
        """Main validation entry point"""
        results = []
        fields = form_data.get("fields", {})
        
        # Required field validation
        required = self.required_fields.get(form_type, [])
        for field in required:
            if field not in fields or not fields[field]:
                results.append({
                    "field": field,
                    "level": "error", 
                    "message": f"Required field '{field}' is missing or empty"
                })
        
        # Financial validation
        if "purchase_price" in fields:
            price_str = str(fields["purchase_price"]).replace("$", "").replace(",", "")
            try:
                price = float(price_str)
                if price <= 0:
                    results.append({
                        "field": "purchase_price",
                        "level": "error",
                        "message": "Purchase price must be greater than zero"
                    })
            except ValueError:
                results.append({
                    "field": "purchase_price", 
                    "level": "error",
                    "message": "Invalid purchase price format"
                })
        
        # Date validation  
        date_fields = ["contract_date", "closing_date"]
        for field in date_fields:
            if field in fields and fields[field]:
                if not self._validate_date_format(fields[field]):
                    results.append({
                        "field": field,
                        "level": "error", 
                        "message": f"Invalid date format in {field}"
                    })
        
        # Generate summary
        error_count = sum(1 for r in results if r["level"] == "error")
        
        return {
            "validation_passed": error_count == 0,
            "can_generate": error_count == 0,
            "summary": {
                "total_validations": len(results),
                "error_count": error_count,
                "validation_score": max(0, 100 - (error_count * 25))
            },
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
    
    def _validate_date_format(self, date_str: str) -> bool:
        """Validate date format"""
        patterns = ["%m/%d/%Y", "%Y-%m-%d", "%B %d, %Y"]
        for pattern in patterns:
            try:
                datetime.strptime(str(date_str), pattern)
                return True
            except ValueError:
                continue
        return False