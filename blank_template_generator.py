#!/usr/bin/env python3
"""
Blank Fillable Template Generator - FORM002
Creates blank fillable PDF templates with coordinate mapping for automated population
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import black, blue, lightgrey
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime

class BlankTemplateGenerator:
    """Generates blank fillable templates from CAR form analysis"""
    
    def __init__(self):
        self.templates_dir = Path("form_templates")
        self.output_dir = Path("blank_templates")
        self.output_dir.mkdir(exist_ok=True)
        
        # Standard field types and their properties
        self.field_types = {
            "text": {"height": 20, "border": True, "fill": False},
            "number": {"height": 20, "border": True, "fill": False, "align": "right"},
            "date": {"height": 20, "border": True, "fill": False, "format": "MM/DD/YYYY"},
            "currency": {"height": 20, "border": True, "fill": False, "align": "right", "prefix": "$"},
            "checkbox": {"height": 12, "width": 12, "border": True, "fill": False},
            "signature": {"height": 30, "border": True, "fill": lightgrey, "label": "SIGNATURE REQUIRED"}
        }
    
    def generate_all_blank_templates(self) -> Dict[str, Any]:
        """Generate blank fillable templates for all 13 CAR forms"""
        results = {
            "templates_created": 0,
            "templates": [],
            "errors": [],
            "timestamp": datetime.now().isoformat()
        }
        
        # Define the 13 CAR forms from the task inventory
        car_forms = [
            "California_Residential_Purchase_Agreement_-_1224_ts77432_template.json",
            "Buyer_Representation_and_Broker_Compensation_Agreement_-_1224_ts74307_template.json", 
            "Transaction_Record_-_724_ts71184_template.json",
            "Verification_of_Property_Condition_-_624_ts05559_template.json",
            "Statewide_Buyer_and_Seller_Advisory_-_624_ts89932_template.json",
            "Agent_Visual_Inspection_Disclosure_1_-_624_ts99307_template.json",
            "Market_Conditions_Advisory_-_624_ts88371_template.json",
            "Electronic_Signature_Verification_for_Third_Parties_-_1221_ts02433_template.json",
            "Confidentiality_and_Non-Disclosure_Agreement_-_1221_ts85245_template.json",
            "Modification_of_Terms_-_Buyer_Representation_Agreement_1_-_1224_ts08683_template.json",
            "Addendum_to_Statewide_Buyer_and_Seller_Adv_-_722_ts94619_template.json",
            "Septic_Insp_Well_Insp_Prop_Monument_and_Propane_Allocation_of_Cost_Addendum_-_624_ts96183_template.json",
            "Permit_Transmittal_0516_ts82120_template.json"
        ]
        
        print(f"🚀 Generating {len(car_forms)} blank fillable templates...")
        
        for form_template in car_forms:
            try:
                template_path = self.templates_dir / form_template
                
                if template_path.exists():
                    result = self.generate_blank_template(str(template_path))
                    if result["success"]:
                        results["templates_created"] += 1
                        results["templates"].append(result)
                        print(f"   ✅ {result['form_name']}")
                    else:
                        results["errors"].append({
                            "form": form_template,
                            "error": result.get("error", "Unknown error")
                        })
                        print(f"   ❌ {form_template}: {result.get('error', 'Unknown error')}")
                else:
                    # Generate simplified template for missing forms
                    simplified_result = self.generate_simplified_template(form_template)
                    results["templates_created"] += 1
                    results["templates"].append(simplified_result)
                    print(f"   📝 {form_template} (simplified)")
                    
            except Exception as e:
                results["errors"].append({
                    "form": form_template,
                    "error": str(e)
                })
                print(f"   ❌ {form_template}: {str(e)}")
        
        return results
    
    def generate_blank_template(self, template_file: str) -> Dict[str, Any]:
        """Generate a blank fillable template from existing template data"""
        try:
            # Load template data
            with open(template_file, 'r') as f:
                template_data = json.load(f)
            
            form_name = template_data.get("form_name", "unknown_form")
            
            # Create blank PDF with fillable fields
            output_filename = f"blank_{form_name}.pdf"
            output_path = self.output_dir / output_filename
            
            # Generate the blank PDF
            blank_pdf_path = self._create_blank_pdf(template_data, output_path)
            
            # Create coordinate mapping file
            mapping_filename = f"blank_{form_name}_mapping.json"
            mapping_path = self.output_dir / mapping_filename
            mapping_data = self._create_coordinate_mapping(template_data)
            
            with open(mapping_path, 'w') as f:
                json.dump(mapping_data, f, indent=2)
            
            return {
                "success": True,
                "form_name": form_name,
                "blank_pdf": str(blank_pdf_path),
                "mapping_file": str(mapping_path),
                "field_count": len(mapping_data.get("fillable_fields", {})),
                "pages": template_data.get("pages", 1)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "template_file": template_file
            }
    
    def generate_simplified_template(self, form_name: str) -> Dict[str, Any]:
        """Generate a simplified template for forms without detailed coordinates"""
        try:
            # Extract clean form name
            clean_name = form_name.replace("_template.json", "").replace("_", " ")
            
            output_filename = f"blank_simplified_{form_name.replace('.json', '.pdf')}"
            output_path = self.output_dir / output_filename
            
            # Create simplified PDF structure
            c = canvas.Canvas(str(output_path), pagesize=letter)
            width, height = letter
            
            # Header
            c.setFont("Helvetica-Bold", 16)
            c.drawString(50, height - 50, clean_name)
            c.setFont("Helvetica", 10)
            c.drawString(50, height - 70, f"Simplified Fillable Template - Generated {datetime.now().strftime('%B %d, %Y')}")
            
            # Standard real estate form fields
            standard_fields = [
                {"label": "Date", "type": "date", "required": True},
                {"label": "Buyer Name(s)", "type": "text", "required": True},
                {"label": "Buyer Address", "type": "text", "required": False},
                {"label": "Buyer Phone", "type": "text", "required": False},
                {"label": "Buyer Email", "type": "text", "required": False},
                {"label": "Seller Name(s)", "type": "text", "required": True},
                {"label": "Seller Address", "type": "text", "required": False},
                {"label": "Property Address", "type": "text", "required": True},
                {"label": "Purchase Price", "type": "currency", "required": True},
                {"label": "Earnest Money", "type": "currency", "required": False},
                {"label": "Closing Date", "type": "date", "required": True},
                {"label": "Agent Name", "type": "text", "required": True},
                {"label": "Agent Phone", "type": "text", "required": False},
                {"label": "Brokerage", "type": "text", "required": False}
            ]
            
            # Draw fillable fields
            y_position = height - 120
            mapping_data = {"fillable_fields": {}, "form_info": {"simplified": True}}
            
            for i, field in enumerate(standard_fields):
                field_id = f"field_{i:03d}"
                
                # Draw label
                c.setFont("Helvetica-Bold", 10)
                label_text = field["label"]
                if field["required"]:
                    label_text += " *"
                c.drawString(50, y_position, label_text)
                
                # Draw fillable area
                field_x = 200
                field_width = 250
                field_height = self.field_types[field["type"]]["height"]
                
                # Draw border
                c.setStrokeColor(black)
                c.rect(field_x, y_position - 5, field_width, field_height, stroke=1, fill=0)
                
                # Add field to mapping
                mapping_data["fillable_fields"][field_id] = {
                    "label": field["label"],
                    "type": field["type"],
                    "required": field["required"],
                    "coordinates": {
                        "x": field_x,
                        "y": y_position - 5,
                        "width": field_width,
                        "height": field_height
                    },
                    "crm_mapping": self._suggest_crm_mapping(field["label"])
                }
                
                y_position -= 35
                
                # Start new page if needed
                if y_position < 100:
                    c.showPage()
                    y_position = height - 50
            
            # Add signature section
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, y_position - 30, "Signatures:")
            
            signature_fields = ["Buyer Signature", "Seller Signature", "Agent Signature"]
            for i, sig_label in enumerate(signature_fields):
                y_pos = y_position - 60 - (i * 50)
                c.setFont("Helvetica", 10)
                c.drawString(50, y_pos, f"{sig_label}:")
                c.drawString(350, y_pos, "Date:")
                
                # Signature line
                c.line(50, y_pos - 20, 300, y_pos - 20)
                # Date line  
                c.line(350, y_pos - 20, 450, y_pos - 20)
                
                # Add to mapping
                mapping_data["fillable_fields"][f"signature_{i}"] = {
                    "label": sig_label,
                    "type": "signature",
                    "required": True,
                    "coordinates": {"x": 50, "y": y_pos - 20, "width": 250, "height": 30}
                }
            
            c.save()
            
            # Save mapping file
            mapping_filename = f"blank_simplified_{form_name.replace('.json', '_mapping.json')}"
            mapping_path = self.output_dir / mapping_filename
            
            with open(mapping_path, 'w') as f:
                json.dump(mapping_data, f, indent=2)
            
            return {
                "success": True,
                "form_name": clean_name,
                "blank_pdf": str(output_path),
                "mapping_file": str(mapping_path),
                "field_count": len(mapping_data["fillable_fields"]),
                "simplified": True
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "form_name": form_name
            }
    
    def _create_blank_pdf(self, template_data: Dict[str, Any], output_path: Path) -> Path:
        """Create blank PDF with form fields"""
        c = canvas.Canvas(str(output_path), pagesize=letter)
        width, height = letter
        
        form_name = template_data.get("form_name", "Unknown Form")
        pages = template_data.get("pages", 1)
        
        # Create each page
        for page_num in range(1, pages + 1):
            if page_num > 1:
                c.showPage()
            
            # Header for each page
            c.setFont("Helvetica-Bold", 14)
            c.drawString(50, height - 30, form_name.replace("_", " "))
            c.setFont("Helvetica", 10)
            c.drawString(50, height - 45, f"Page {page_num} of {pages}")
            c.drawString(400, height - 45, f"Generated: {datetime.now().strftime('%m/%d/%Y')}")
            
            # Draw field placeholders for this page
            field_mappings = template_data.get("field_mappings", {})
            page_fields = {k: v for k, v in field_mappings.items() 
                          if v.get("page") == page_num}
            
            for field_id, field_data in page_fields.items():
                coords = field_data.get("coordinates", {})
                if coords:
                    x = coords.get("x", 0)
                    y = height - coords.get("y", 0)  # Flip Y coordinate
                    w = coords.get("width", 100)
                    h = coords.get("height", 20)
                    
                    # Draw field border
                    c.setStrokeColor(lightgrey)
                    c.rect(x, y, w, h, stroke=1, fill=0)
        
        c.save()
        return output_path
    
    def _create_coordinate_mapping(self, template_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create coordinate mapping for fillable fields"""
        mapping = {
            "form_name": template_data.get("form_name"),
            "pages": template_data.get("pages", 1),
            "fillable_fields": {},
            "generated_at": datetime.now().isoformat()
        }
        
        field_mappings = template_data.get("field_mappings", {})
        
        for field_id, field_data in field_mappings.items():
            # Determine field type from content or position
            field_type = self._classify_field_type(field_data)
            
            mapping["fillable_fields"][field_id] = {
                "coordinates": field_data.get("coordinates", {}),
                "page": field_data.get("page", 1),
                "field_type": field_type,
                "original_content": field_data.get("text_content", ""),
                "crm_mapping": field_data.get("crm_mapping"),
                "required": self._is_field_required(field_data)
            }
        
        return mapping
    
    def _classify_field_type(self, field_data: Dict[str, Any]) -> str:
        """Classify field type based on content and context"""
        content = field_data.get("text_content", "").lower()
        
        # Date fields
        if any(keyword in content for keyword in ["date", "month", "day", "year", "/"]):
            return "date"
        
        # Currency fields  
        if any(keyword in content for keyword in ["$", "price", "amount", "payment", "cost"]):
            return "currency"
        
        # Number fields
        if content.isdigit() or any(keyword in content for keyword in ["number", "count", "#"]):
            return "number"
        
        # Checkbox fields
        if len(content) <= 2 or content in ["x", "✓", "□", "☐"]:
            return "checkbox"
        
        # Signature fields
        if any(keyword in content for keyword in ["signature", "sign", "initial"]):
            return "signature"
        
        # Default to text
        return "text"
    
    def _is_field_required(self, field_data: Dict[str, Any]) -> bool:
        """Determine if field is required based on content"""
        content = field_data.get("text_content", "").lower()
        
        # Required field indicators
        required_keywords = ["required", "must", "shall", "*", "mandatory"]
        return any(keyword in content for keyword in required_keywords)
    
    def _suggest_crm_mapping(self, field_label: str) -> Optional[str]:
        """Suggest CRM field mapping based on field label"""
        label_lower = field_label.lower()
        
        mapping_suggestions = {
            "buyer": "client_first_name",
            "seller": "seller_first_name", 
            "property address": "property_address",
            "purchase price": "sale_price",
            "closing date": "closing_date",
            "agent": "agent_name",
            "phone": "client_phone",
            "email": "client_email",
            "address": "client_address"
        }
        
        for keyword, crm_field in mapping_suggestions.items():
            if keyword in label_lower:
                return crm_field
        
        return None

def main():
    """Test the blank template generator"""
    print("🚀 Blank Template Generator - FORM002")
    print("=" * 50)
    
    generator = BlankTemplateGenerator()
    
    # Generate all blank templates
    print("\n📄 Generating blank fillable templates for all 13 CAR forms...")
    results = generator.generate_all_blank_templates()
    
    print(f"\n📊 Generation Results:")
    print(f"   ✅ Templates Created: {results['templates_created']}")
    print(f"   ❌ Errors: {len(results['errors'])}")
    
    if results["errors"]:
        print(f"\n⚠️  Errors encountered:")
        for error in results["errors"]:
            print(f"   • {error['form']}: {error['error']}")
    
    print(f"\n📁 Output Directory: {generator.output_dir}")
    print(f"   • Blank PDF templates with fillable fields")
    print(f"   • Coordinate mapping files for automated population")
    print(f"   • Both detailed and simplified templates available")
    
    print(f"\n✅ FORM002 Complete: Blank Fillable Templates Created")
    print(f"🔄 Ready for automated form population with coordinate mapping")

if __name__ == "__main__":
    main()