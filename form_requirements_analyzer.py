#!/usr/bin/env python3
"""
Form Requirements Analyzer
Tells you exactly what CRM information is needed to fill out any CAR form
"""

import json
from typing import Dict, List, Any

class FormRequirementsAnalyzer:
    def __init__(self, config_path: str = "crm_field_mapping_config.json"):
        """Initialize with the CRM field mapping configuration"""
        with open(config_path, 'r') as f:
            self.config = json.load(f)
    
    def get_form_requirements(self, form_type: str) -> Dict[str, Any]:
        """
        Get all required and optional information for a specific form
        
        Args:
            form_type: Form identifier (e.g., 'california_purchase_agreement')
            
        Returns:
            Dictionary with organized requirements by CRM table
        """
        if form_type not in self.config['form_mappings']:
            available_forms = list(self.config['form_mappings'].keys())
            return {
                "error": f"Form type '{form_type}' not found",
                "available_forms": available_forms
            }
        
        mappings = self.config['form_mappings'][form_type]['mappings']
        
        # Organize by CRM table
        requirements = {
            "client_info": {"required": [], "optional": []},
            "property_info": {"required": [], "optional": []},
            "transaction_info": {"required": [], "optional": []},
            "agent_info": {"required": [], "optional": []},
            "summary": {"total_required": 0, "total_optional": 0}
        }
        
        for field_name, field_config in mappings.items():
            crm_source = field_config['crm_source']
            required = field_config['required']
            field_type = field_config['field_type']
            
            field_info = {
                "form_field": field_name,
                "crm_source": crm_source,
                "type": field_type,
                "description": self._get_field_description(field_name, crm_source)
            }
            
            # Determine CRM table and add to appropriate section
            if 'clients.' in crm_source:
                category = "client_info"
            elif 'properties.' in crm_source:
                category = "property_info"
            elif 'transactions.' in crm_source:
                category = "transaction_info"
            elif 'agents.' in crm_source:
                category = "agent_info"
            else:
                category = "other_info"
                if category not in requirements:
                    requirements[category] = {"required": [], "optional": []}
            
            if required:
                requirements[category]["required"].append(field_info)
                requirements["summary"]["total_required"] += 1
            else:
                requirements[category]["optional"].append(field_info)
                requirements["summary"]["total_optional"] += 1
        
        return requirements
    
    def _get_field_description(self, field_name: str, crm_source: str) -> str:
        """Generate human-readable description of what the field represents"""
        descriptions = {
            "buyer_name": "Full name of the property buyer",
            "buyer_address": "Buyer's mailing address",
            "buyer_phone": "Buyer's primary phone number",
            "buyer_email": "Buyer's email address",
            "property_address": "Street address of the property being purchased",
            "property_city": "City where the property is located",
            "property_state": "State where the property is located",
            "property_zip": "ZIP code of the property",
            "apn": "Assessor's Parcel Number (property tax ID)",
            "purchase_price": "Agreed purchase price for the property",
            "earnest_money": "Good faith deposit amount",
            "down_payment": "Buyer's down payment amount",
            "loan_amount": "Mortgage loan amount (if financing)",
            "closing_date": "Date when the sale closes",
            "possession_date": "Date when buyer takes possession",
            "listing_agent_name": "Name of the listing agent",
            "listing_agent_license": "Listing agent's license number",
            "listing_agent_phone": "Listing agent's phone number",
            "brokerage_name": "Name of the listing brokerage"
        }
        return descriptions.get(field_name, f"Data from {crm_source}")
    
    def print_requirements(self, form_type: str) -> None:
        """Print a formatted report of form requirements"""
        reqs = self.get_form_requirements(form_type)
        
        if "error" in reqs:
            print(f"❌ Error: {reqs['error']}")
            print(f"📋 Available forms: {', '.join(reqs['available_forms'])}")
            return
        
        print(f"📋 FORM REQUIREMENTS: {form_type.replace('_', ' ').title()}")
        print("=" * 60)
        
        sections = [
            ("👤 CLIENT INFORMATION", "client_info"),
            ("🏠 PROPERTY INFORMATION", "property_info"), 
            ("💰 TRANSACTION DETAILS", "transaction_info"),
            ("🏢 AGENT INFORMATION", "agent_info")
        ]
        
        for title, key in sections:
            if key in reqs and (reqs[key]["required"] or reqs[key]["optional"]):
                print(f"\n{title}:")
                
                if reqs[key]["required"]:
                    print("  ✅ REQUIRED:")
                    for field in reqs[key]["required"]:
                        print(f"    • {field['description']}")
                        print(f"      ({field['type']}) → {field['crm_source']}")
                
                if reqs[key]["optional"]:
                    print("  ⭕ OPTIONAL:")
                    for field in reqs[key]["optional"]:
                        print(f"    • {field['description']}")
                        print(f"      ({field['type']}) → {field['crm_source']}")
        
        summary = reqs["summary"]
        print(f"\n📊 SUMMARY:")
        print(f"   • {summary['total_required']} required fields")
        print(f"   • {summary['total_optional']} optional fields")
        print(f"   • {summary['total_required'] + summary['total_optional']} total fields")
    
    def get_available_forms(self) -> List[str]:
        """Get list of all available form types"""
        return list(self.config['form_mappings'].keys())
    
    def check_data_completeness(self, form_type: str, client_data: Dict, property_data: Dict, transaction_data: Dict, agent_data: Dict) -> Dict[str, Any]:
        """
        Check if provided data is sufficient to fill out the form
        
        Returns:
            Analysis of missing required fields and available optional fields
        """
        reqs = self.get_form_requirements(form_type)
        if "error" in reqs:
            return reqs
        
        missing_required = []
        available_optional = []
        
        # Check each category
        data_sources = {
            "client_info": client_data,
            "property_info": property_data,
            "transaction_info": transaction_data,
            "agent_info": agent_data
        }
        
        for category, data in data_sources.items():
            if category in reqs:
                # Check required fields
                for field in reqs[category]["required"]:
                    if not self._has_required_data(field["crm_source"], data):
                        missing_required.append({
                            "field": field["form_field"],
                            "description": field["description"],
                            "crm_source": field["crm_source"]
                        })
                
                # Check optional fields
                for field in reqs[category]["optional"]:
                    if self._has_required_data(field["crm_source"], data):
                        available_optional.append({
                            "field": field["form_field"],
                            "description": field["description"]
                        })
        
        return {
            "can_generate": len(missing_required) == 0,
            "missing_required": missing_required,
            "available_optional": available_optional,
            "completeness_score": round((reqs["summary"]["total_required"] - len(missing_required)) / reqs["summary"]["total_required"] * 100, 1) if reqs["summary"]["total_required"] > 0 else 100
        }
    
    def _has_required_data(self, crm_source: str, data: Dict) -> bool:
        """Check if the required data is available in the provided data dictionary"""
        # Handle composite fields like "first_name + \" \" + last_name"
        if " + " in crm_source:
            # For composite fields, check if all components are available
            parts = crm_source.replace('"', '').split(" + ")
            for part in parts:
                if "." in part:
                    field_name = part.split(".")[-1]
                    if field_name not in data or not data[field_name]:
                        return False
            return True
        else:
            # Single field
            field_name = crm_source.split(".")[-1] if "." in crm_source else crm_source
            return field_name in data and data[field_name]


def main():
    """Command line interface for the requirements analyzer"""
    import sys
    
    analyzer = FormRequirementsAnalyzer()
    
    if len(sys.argv) < 2:
        print("📋 Available Forms:")
        for form in analyzer.get_available_forms():
            print(f"  • {form}")
        print(f"\nUsage: python {sys.argv[0]} <form_type>")
        return
    
    form_type = sys.argv[1]
    analyzer.print_requirements(form_type)


if __name__ == "__main__":
    main()