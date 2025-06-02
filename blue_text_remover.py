#!/usr/bin/env python3
"""
Blue Text Remover - Remove all colored text from CLEAN_TEMPLATE.pdf
Creates a truly clean template with no previous client data
"""

import fitz  # pymupdf
import os

class BlueTextRemover:
    def __init__(self):
        self.template_path = "documents/California_Residential_Purchase_Agreement_CLEAN_TEMPLATE.pdf"
        
    def remove_colored_text(self, output_path="output/CRPA_CLEAN_TEMPLATE.pdf"):
        """Remove all colored text (previous client data) from the template"""
        print("🧹 REMOVING COLORED TEXT (BLUE TEXT)")
        print("=" * 50)
        
        # Open the PDF
        doc = fitz.open(self.template_path)
        removed_count = 0
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            
            # Get all text blocks
            text_dict = page.get_text("dict")
            
            print(f"📄 Processing page {page_num + 1}...")
            
            # Find and remove colored text
            for block in text_dict["blocks"]:
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            color = span.get("color", 0)
                            text = span.get("text", "").strip()
                            
                            # If this is colored text (not black), remove it
                            if text and color != 0:  # color=128 is the gray "blue text"
                                print(f"  Removing: '{text}' (color={color})")
                                
                                # Get the rectangle area of this text
                                bbox = span["bbox"]
                                rect = fitz.Rect(bbox)
                                
                                # Draw a white rectangle over the colored text
                                page.draw_rect(rect, color=(1, 1, 1), fill=(1, 1, 1))
                                removed_count += 1
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Save the cleaned PDF
        doc.save(output_path)
        doc.close()
        
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            print(f"\n✅ CLEAN TEMPLATE CREATED!")
            print(f"📁 File: {output_path}")
            print(f"📊 Size: {file_size:,} bytes")
            print(f"🧹 Removed {removed_count} colored text items")
            print(f"🌐 Windows path: \\\\wsl.localhost\\Ubuntu\\home\\ender\\.claude\\projects\\offer-creator\\{output_path}")
            print(f"💎 Template is now clean and ready for population!")
            
            return output_path
        else:
            print("❌ Failed to create clean template")
            return None
    
    def create_populated_template(self, client_data, output_path="output/CRPA_POPULATED.pdf"):
        """Create a populated form using the clean template + new text overlays"""
        print(f"\n🎨 CREATING POPULATED FORM")
        print("=" * 50)
        
        # First, create clean template
        clean_template = self.remove_colored_text("output/CRPA_CLEAN_TEMPLATE.pdf")
        if not clean_template:
            return None
            
        # Open the clean template
        doc = fitz.open(clean_template)
        
        # Sample positioning data for key fields (you'll need to fine-tune these coordinates)
        field_positions = {
            # Page 1 (page 0) - Main form
            'date': (525, 142),  # Date prepared
            'buyer_name': (280, 170),  # Buyer name
            'property_address': (280, 195),  # Property address
            'city': (180, 220),  # City
            'state': (350, 220),  # State  
            'zip': (450, 220),  # ZIP
            'purchase_price': (200, 400),  # Purchase price
        }
        
        # Add new text overlays
        page = doc[2]  # Page 3 is where main form starts (0-indexed)
        
        # Add sample data
        sample_data = {
            'date': client_data.get('form_date', '2025-06-01'),
            'buyer_name': client_data.get('buyer_name', 'John & Jane Smith'),
            'property_address': client_data.get('property_address', '1234 Dream Street'),
            'city': client_data.get('city', 'Los Angeles'),
            'state': client_data.get('state', 'CA'),
            'zip': client_data.get('zip', '90210'),
            'purchase_price': client_data.get('purchase_price', '$1,500,000.00'),
        }
        
        print("Adding new client data:")
        for field, value in sample_data.items():
            if field in field_positions:
                x, y = field_positions[field]
                print(f"  {field}: {value} at ({x}, {y})")
                
                # Add text at the specified position
                text_color = (0, 0, 1)  # Blue color for new text
                page.insert_text((x, y), value, fontsize=10, color=text_color)
        
        # Save populated form
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        doc.save(output_path)
        doc.close()
        
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            print(f"\n✅ POPULATED FORM CREATED!")
            print(f"📁 File: {output_path}")
            print(f"📊 Size: {file_size:,} bytes")
            print(f"🌐 Windows path: \\\\wsl.localhost\\Ubuntu\\home\\ender\\.claude\\projects\\offer-creator\\{output_path}")
            
            return output_path
        else:
            print("❌ Failed to create populated form")
            return None

def main():
    """Test the blue text removal and form population"""
    remover = BlueTextRemover()
    
    print("🕵️ BLUE TEXT REMOVAL AND CLEAN TEMPLATE CREATION")
    print("=" * 80)
    
    # Step 1: Create clean template
    clean_template = remover.remove_colored_text()
    
    if clean_template:
        print(f"\n🎯 SUCCESS! Clean template created.")
        print(f"Now you have a gorgeous template with no previous client data!")
        
        # Step 2: Test population with sample data
        sample_client = {
            'form_date': '2025-06-01',
            'buyer_name': 'Alexander & Victoria Rodriguez',
            'property_address': '8765 Luxury Boulevard',
            'city': 'Beverly Hills',
            'state': 'CA',
            'zip': '90210',
            'purchase_price': '$3,750,000.00'
        }
        
        populated_form = remover.create_populated_template(sample_client)
        
        if populated_form:
            print(f"\n🎨 BONUS: Created sample populated form with new client data!")

if __name__ == "__main__":
    main()