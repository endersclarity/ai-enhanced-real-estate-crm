#!/usr/bin/env python3
"""
Intelligent PDF Form Filler
Analyzes the PDF structure and fills it properly without ugly overlays
"""

import os
import io
import json
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import pandas as pd
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import black, white
import pdfplumber


class IntelligentPDFFiller:
    """Smart PDF filling that respects the original form structure"""
    
    def __init__(self):
        self.output_dir = "smart_filled_forms"
        self.ensure_output_dir()
    
    def ensure_output_dir(self):
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def analyze_pdf_structure(self, pdf_path: str) -> Dict:
        """Analyze the PDF to find fillable areas and text patterns"""
        print(f"🔍 Analyzing PDF structure: {pdf_path}")
        
        analysis = {
            "has_form_fields": False,
            "fillable_fields": {},
            "text_patterns": [],
            "blank_areas": [],
            "pages": []
        }
        
        try:
            # Check for existing form fields
            with open(pdf_path, 'rb') as file:
                reader = PdfReader(file)
                
                # Check if PDF has AcroForm fields
                if reader.trailer.get("/Root") and reader.trailer["/Root"].get("/AcroForm"):
                    analysis["has_form_fields"] = True
                    print("✓ Found existing form fields")
                    
                    # Extract field information
                    form = reader.trailer["/Root"]["/AcroForm"]
                    if form.get("/Fields"):
                        for field in form["/Fields"]:
                            if hasattr(field, 'get_object'):
                                field_obj = field.get_object()
                                field_name = field_obj.get("/T")
                                if field_name:
                                    analysis["fillable_fields"][str(field_name)] = {
                                        "type": str(field_obj.get("/FT", "unknown")),
                                        "value": str(field_obj.get("/V", ""))
                                    }
            
            # Analyze text patterns with pdfplumber
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    page_analysis = self._analyze_page_structure(page)
                    analysis["pages"].append(page_analysis)
                    
        except Exception as e:
            print(f"❌ Analysis error: {e}")
        
        return analysis
    
    def _analyze_page_structure(self, page) -> Dict:
        """Analyze individual page structure"""
        page_info = {
            "width": page.width,
            "height": page.height,
            "text_elements": [],
            "potential_fields": [],
            "lines": []
        }
        
        # Extract text with positions
        chars = page.chars
        for char in chars:
            page_info["text_elements"].append({
                "text": char.get("text", ""),
                "x": char.get("x0", 0),
                "y": char.get("top", 0),
                "font": char.get("fontname", ""),
                "size": char.get("size", 10)
            })
        
        # Find potential form fields (blank lines, underscores, etc.)
        words = page.extract_words()
        for word in words:
            text = word["text"]
            if "_" in text or "___" in text or any(keyword in text.lower() for keyword in 
                ["buyer", "seller", "address", "price", "date", "name"]):
                page_info["potential_fields"].append({
                    "text": text,
                    "x": word["x0"],
                    "y": word["top"],
                    "width": word["x1"] - word["x0"],
                    "height": word["bottom"] - word["top"]
                })
        
        # Extract lines and rectangles
        try:
            lines = page.lines
            for line in lines:
                page_info["lines"].append({
                    "x0": line.get("x0", 0),
                    "y0": line.get("y0", 0),
                    "x1": line.get("x1", 0),
                    "y1": line.get("y1", 0)
                })
        except:
            pass
        
        return page_info
    
    def create_clean_fillable_pdf(self, original_pdf: str, csv_data: pd.DataFrame) -> List[str]:
        """Create clean, properly filled PDFs"""
        print(f"🎨 Creating clean filled PDFs from {original_pdf}")
        
        # Analyze the original PDF
        structure = self.analyze_pdf_structure(original_pdf)
        
        filled_pdfs = []
        
        for index, row in csv_data.iterrows():
            try:
                if structure["has_form_fields"]:
                    # PDF has actual form fields - fill them properly
                    output_path = self._fill_acroform_fields(original_pdf, row, index)
                else:
                    # No form fields - create intelligent placement
                    output_path = self._create_intelligent_fill(original_pdf, row, index, structure)
                
                if output_path:
                    filled_pdfs.append(output_path)
                    print(f"✅ Created: {os.path.basename(output_path)}")
                
            except Exception as e:
                print(f"❌ Error processing row {index}: {e}")
                continue
        
        return filled_pdfs
    
    def _fill_acroform_fields(self, pdf_path: str, data_row: pd.Series, index: int) -> str:
        """Fill actual PDF form fields properly"""
        buyer_name = str(data_row.get('buyer_name', f'Buyer_{index+1}')).replace(' ', '_')
        output_path = os.path.join(self.output_dir, f"{buyer_name}_CLEAN_FILLED.pdf")
        
        try:
            with open(pdf_path, 'rb') as file:
                reader = PdfReader(file)
                writer = PdfWriter()
                
                # Copy all pages
                for page in reader.pages:
                    writer.add_page(page)
                
                # Fill form fields
                if reader.trailer.get("/Root") and reader.trailer["/Root"].get("/AcroForm"):
                    # Update form fields
                    writer.update_page_form_field_values(
                        writer.pages[0], 
                        self._map_data_to_fields(data_row)
                    )
                
                # Write the filled PDF
                with open(output_path, 'wb') as output_file:
                    writer.write(output_file)
                    
            return output_path
            
        except Exception as e:
            print(f"AcroForm filling failed: {e}")
            return None
    
    def _create_intelligent_fill(self, pdf_path: str, data_row: pd.Series, index: int, structure: Dict) -> str:
        """Create intelligent filling based on PDF analysis"""
        buyer_name = str(data_row.get('buyer_name', f'Buyer_{index+1}')).replace(' ', '_')
        output_path = os.path.join(self.output_dir, f"{buyer_name}_SMART_FILLED.pdf")
        
        try:
            # Create a completely new PDF with proper field placement
            packet = io.BytesIO()
            can = canvas.Canvas(packet, pagesize=letter)
            
            # Analyze where to place fields based on text analysis
            field_positions = self._calculate_smart_positions(structure, data_row)
            
            # Fill fields with proper formatting
            for field_name, position in field_positions.items():
                if field_name in data_row and pd.notna(data_row[field_name]):
                    value = self._format_field_value(field_name, data_row[field_name])
                    
                    can.setFont("Helvetica", position.get("font_size", 10))
                    can.setFillColor(black)
                    can.drawString(position["x"], position["y"], value)
            
            can.save()
            
            # Merge with original PDF background
            packet.seek(0)
            overlay_pdf = PdfReader(packet)
            
            with open(pdf_path, 'rb') as file:
                background_pdf = PdfReader(file)
                writer = PdfWriter()
                
                for i, page in enumerate(background_pdf.pages):
                    if i < len(overlay_pdf.pages):
                        # Merge overlay cleanly
                        page.merge_page(overlay_pdf.pages[i])
                    writer.add_page(page)
                
                with open(output_path, 'wb') as output_file:
                    writer.write(output_file)
                    
            return output_path
            
        except Exception as e:
            print(f"Smart filling failed: {e}")
            return None
    
    def _calculate_smart_positions(self, structure: Dict, data_row: pd.Series) -> Dict:
        """Calculate intelligent field positions based on PDF analysis"""
        positions = {}
        
        # Look for text patterns that indicate where fields should go
        for page_num, page_info in enumerate(structure["pages"]):
            for field in page_info["potential_fields"]:
                text = field["text"].lower()
                
                # Match field patterns to data columns
                if "buyer" in text and "name" in text:
                    positions["buyer_name"] = {
                        "x": field["x"] + field["width"] + 10,
                        "y": page_info["height"] - field["y"],
                        "font_size": 10
                    }
                elif "address" in text and "property" in text:
                    positions["property_address"] = {
                        "x": field["x"] + field["width"] + 10,
                        "y": page_info["height"] - field["y"],
                        "font_size": 10
                    }
                elif "price" in text or "amount" in text:
                    positions["purchase_price"] = {
                        "x": field["x"] + field["width"] + 10,
                        "y": page_info["height"] - field["y"],
                        "font_size": 10
                    }
        
        return positions
    
    def _map_data_to_fields(self, data_row: pd.Series) -> Dict:
        """Map CSV data to PDF form field names"""
        field_mapping = {
            "BuyerName": data_row.get("buyer_name", ""),
            "PropertyAddress": data_row.get("property_address", ""),
            "PurchasePrice": self._format_field_value("purchase_price", data_row.get("purchase_price", "")),
            "SellerName": data_row.get("seller_name", ""),
            "Date": data_row.get("date_prepared", ""),
        }
        
        return {k: v for k, v in field_mapping.items() if v}
    
    def _format_field_value(self, field_name: str, value) -> str:
        """Format field values appropriately"""
        if pd.isna(value):
            return ""
        
        value_str = str(value)
        
        if "price" in field_name.lower() or "amount" in field_name.lower():
            try:
                num_value = float(value_str.replace(",", "").replace("$", ""))
                return f"${num_value:,.0f}"
            except:
                return value_str
        elif "date" in field_name.lower():
            try:
                dt = pd.to_datetime(value_str)
                return dt.strftime("%m/%d/%Y")
            except:
                return value_str
        else:
            return value_str


def main():
    """Demo the intelligent PDF filler"""
    filler = IntelligentPDFFiller()
    
    # Load sample data
    try:
        df = pd.read_csv("sample_zipform_data.csv")
        
        # Fill PDFs intelligently
        filled_files = filler.create_clean_fillable_pdf("template.pdf", df)
        
        print(f"\n🎉 Successfully created {len(filled_files)} clean filled PDFs")
        for file in filled_files:
            print(f"  ✓ {file}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure 'template.pdf' and 'sample_zipform_data.csv' exist")


if __name__ == "__main__":
    main()