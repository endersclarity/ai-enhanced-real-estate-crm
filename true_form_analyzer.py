#!/usr/bin/env python3
"""
True Form Analyzer - Convert the original CLEAN_TEMPLATE.pdf to HTML
Remove blue text and position form fields exactly where the real form lines are
"""

import fitz  # pymupdf
import base64
import os

class TrueFormAnalyzer:
    def __init__(self):
        self.original_pdf = "documents/California_Residential_Purchase_Agreement_CLEAN_TEMPLATE.pdf"
        
    def analyze_form_structure(self):
        """Analyze where the actual form lines and data entry areas are"""
        print("🔍 ANALYZING ORIGINAL FORM STRUCTURE")
        print("=" * 60)
        
        doc = fitz.open(self.original_pdf)
        
        form_data_positions = []
        
        for page_num in range(min(3, len(doc))):  # First 3 pages
            page = doc[page_num]
            
            print(f"📄 Analyzing page {page_num + 1}...")
            
            # Get all text blocks with positions and colors
            text_dict = page.get_text("dict")
            
            for block in text_dict["blocks"]:
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            color = span.get("color", 0)
                            text = span.get("text", "").strip()
                            bbox = span["bbox"]
                            
                            # If this is colored text (blue text = previous client data)
                            if text and color != 0:  # color=128 is the blue text
                                form_data_positions.append({
                                    'page': page_num,
                                    'text': text,
                                    'color': color,
                                    'bbox': bbox,
                                    'x': bbox[0],
                                    'y': bbox[1],
                                    'width': bbox[2] - bbox[0],
                                    'height': bbox[3] - bbox[1]
                                })
                                
                                if page_num == 2:  # Main form page
                                    print(f"  📍 Found data at ({bbox[0]:.0f}, {bbox[1]:.0f}): '{text}'")
        
        doc.close()
        
        print(f"\n📊 Found {len(form_data_positions)} data positions")
        return form_data_positions
    
    def create_true_html_form(self, form_data_positions, output_path="html_templates/true_crpa_form.html"):
        """Create HTML form with fields positioned exactly where the original data was"""
        
        print(f"\n🎨 CREATING TRUE HTML FORM")
        print("=" * 60)
        
        doc = fitz.open(self.original_pdf)
        
        # Start HTML
        html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>California Residential Purchase Agreement - True Form</title>
    <style>
        @page {
            size: 8.5in 11in;
            margin: 0;
        }
        
        body {
            margin: 0;
            padding: 0;
            font-family: Arial, sans-serif;
            background: white;
        }
        
        .page {
            width: 8.5in;
            height: 11in;
            position: relative;
            margin: 0 auto 20px auto;
            background-size: 100% 100%;
            background-repeat: no-repeat;
            background-position: center;
            border: 1px solid #ccc;
        }
        
        .form-field {
            position: absolute;
            border: 1px solid rgba(0, 123, 255, 0.3);
            background: rgba(255, 255, 255, 0.9);
            font-size: 10px;
            font-family: Arial, sans-serif;
            z-index: 10;
            padding: 1px 3px;
        }
        
        .text-field {
            border-radius: 2px;
        }
        
        .checkbox-field {
            width: 12px;
            height: 12px;
            padding: 0;
        }
        
        .field-highlight {
            border-color: rgba(255, 0, 0, 0.7);
            background: rgba(255, 255, 255, 1);
        }
        
        .control-buttons {
            position: fixed;
            top: 10px;
            right: 10px;
            z-index: 1000;
        }
        
        .control-buttons button {
            display: block;
            margin-bottom: 5px;
            padding: 8px 12px;
            background: #007cba;
            color: white;
            border: none;
            cursor: pointer;
            border-radius: 4px;
            font-size: 12px;
        }
        
        .control-buttons button:hover {
            background: #005a87;
        }
        
        .form-info {
            position: fixed;
            top: 10px;
            left: 10px;
            background: rgba(0, 0, 0, 0.8);
            color: white;
            padding: 10px;
            border-radius: 4px;
            font-size: 12px;
            z-index: 1000;
            max-width: 250px;
        }
        
        @media print {
            .control-buttons, .form-info { display: none; }
            .page { border: none; margin: 0; }
            .form-field { border: 1px solid #666; background: white; }
        }
    </style>
</head>
<body>
    <div class="form-info">
        <strong>True Form Layout</strong><br>
        Fields positioned exactly where original data was<br>
        Blue borders show editable areas<br>
        <span id="field-count">0 fields</span>
    </div>
    
    <div class="control-buttons">
        <button onclick="populateWithSampleData()">Fill Sample Data</button>
        <button onclick="clearAllFields()">Clear All</button>
        <button onclick="toggleFieldVisibility()">Toggle Field Borders</button>
        <button onclick="window.print()">Print/Save PDF</button>
    </div>
"""
        
        # Convert each page to image, removing blue text
        for page_num in range(min(3, len(doc))):
            page = doc[page_num]
            
            print(f"📄 Processing page {page_num + 1}...")
            
            # Create a copy of the page for editing
            page_copy = page
            
            # Remove blue text by drawing white rectangles over it
            removed_count = 0
            for data_pos in form_data_positions:
                if data_pos['page'] == page_num and data_pos['color'] != 0:
                    bbox = data_pos['bbox']
                    rect = fitz.Rect(bbox)
                    # Draw white rectangle to hide the blue text
                    page_copy.draw_rect(rect, color=(1, 1, 1), fill=(1, 1, 1))
                    removed_count += 1
            
            print(f"  🧹 Removed {removed_count} blue text items")
            
            # Render page as high-quality image
            mat = fitz.Matrix(2.0, 2.0)  # 2x scaling for quality
            pix = page_copy.get_pixmap(matrix=mat)
            img_data = pix.tobytes("png")
            img_base64 = base64.b64encode(img_data).decode()
            
            # Add page with clean background
            html_content += f"""
    <div class="page" id="page-{page_num + 1}" style="background-image: url(data:image/png;base64,{img_base64});">
"""
            
            # Add form fields exactly where the blue text was
            field_count = 0
            for data_pos in form_data_positions:
                if data_pos['page'] == page_num:
                    x = data_pos['x']
                    y = data_pos['y'] 
                    width = max(data_pos['width'], 50)  # Minimum width
                    height = max(data_pos['height'], 16)  # Minimum height
                    text = data_pos['text']
                    
                    # Determine field type and name based on content
                    field_name = f"field_{page_num}_{field_count}"
                    field_type = "text"
                    placeholder = text[:20] + "..." if len(text) > 20 else text
                    
                    # Smart field naming based on content
                    text_lower = text.lower()
                    if any(name in text_lower for name in ['benjamin', 'brown', 'hicks', 'buyer']):
                        field_name = "buyer_name"
                        placeholder = "Buyer Name"
                    elif 'slate creek' in text_lower or '13190' in text:
                        field_name = "property_address"
                        placeholder = "Property Address"
                    elif text_lower in ['nevada city', 'beverly hills', 'san diego']:
                        field_name = "city"
                        placeholder = "City"
                    elif text in ['Nevada', 'CA', 'California']:
                        field_name = "state"
                        placeholder = "State"
                    elif text.isdigit() and len(text) == 5:
                        field_name = "zip_code"
                        placeholder = "ZIP Code"
                    elif '930,000' in text or '750,000' in text or '$' in text:
                        field_name = "purchase_price"
                        placeholder = "Purchase Price"
                    elif 'april' in text_lower and '2025' in text:
                        field_name = "form_date"
                        placeholder = "Date"
                    elif text == 'X':
                        field_type = "checkbox"
                        field_name = f"checkbox_{field_count}"
                    
                    if field_type == "checkbox":
                        html_content += f"""
        <input type="checkbox" name="{field_name}" class="form-field checkbox-field" 
               style="left: {x}px; top: {y}px;" 
               title="{placeholder}">
"""
                    else:
                        html_content += f"""
        <input type="text" name="{field_name}" class="form-field text-field" 
               style="left: {x}px; top: {y}px; width: {width}px; height: {height}px;" 
               placeholder="{placeholder}" title="{placeholder}">
"""
                    
                    field_count += 1
                    
                    if page_num == 2:  # Main form page
                        print(f"  ✓ Added {field_type} field '{field_name}' at ({x:.0f}, {y:.0f})")
            
            html_content += """
    </div>
"""
        
        # Add JavaScript for functionality
        html_content += """
    <script>
        let fieldsVisible = true;
        
        function updateFieldCount() {
            const fields = document.querySelectorAll('.form-field');
            document.getElementById('field-count').textContent = fields.length + ' fields';
        }
        
        function populateWithSampleData() {
            // Populate with sample data based on field names
            const sampleData = {
                'buyer_name': 'John & Jane Smith',
                'property_address': '1234 Luxury Lane',
                'city': 'Beverly Hills',
                'state': 'CA',
                'zip_code': '90210',
                'purchase_price': '$2,500,000.00',
                'form_date': '2025-06-01'
            };
            
            for (const [fieldName, value] of Object.entries(sampleData)) {
                const field = document.querySelector(`[name="${fieldName}"]`);
                if (field && field.type !== 'checkbox') {
                    field.value = value;
                }
            }
            
            // Check some checkboxes
            const checkboxes = document.querySelectorAll('input[type="checkbox"]');
            checkboxes.forEach((cb, index) => {
                if (index < 3) cb.checked = true;
            });
        }
        
        function clearAllFields() {
            document.querySelectorAll('.form-field').forEach(field => {
                if (field.type === 'checkbox') {
                    field.checked = false;
                } else {
                    field.value = '';
                }
            });
        }
        
        function toggleFieldVisibility() {
            const fields = document.querySelectorAll('.form-field');
            fieldsVisible = !fieldsVisible;
            
            fields.forEach(field => {
                field.style.border = fieldsVisible ? '1px solid rgba(0, 123, 255, 0.3)' : 'none';
                field.style.background = fieldsVisible ? 'rgba(255, 255, 255, 0.9)' : 'transparent';
            });
        }
        
        // Highlight fields on focus
        document.querySelectorAll('.form-field').forEach(field => {
            field.addEventListener('focus', function() {
                this.classList.add('field-highlight');
            });
            field.addEventListener('blur', function() {
                this.classList.remove('field-highlight');
            });
        });
        
        // Initialize
        updateFieldCount();
    </script>
</body>
</html>
"""
        
        doc.close()
        
        # Save HTML file
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            print(f"\n✅ TRUE FORM HTML CREATED!")
            print(f"📁 File: {output_path}")
            print(f"📊 Size: {file_size:,} bytes")
            print(f"🎯 Fields positioned exactly where original data was!")
            print(f"🧹 Blue text removed from background")
            print(f"🌐 Windows: file:///C:/Users/ender/.claude/projects/offer-creator/{output_path}")
            print(f"💻 WSL: file://{os.path.abspath(output_path)}")
            
            return output_path
        else:
            print("❌ Failed to create true form HTML")
            return None

def main():
    """Create true HTML form positioned exactly where original form lines are"""
    
    analyzer = TrueFormAnalyzer()
    
    print("🎯 TRUE FORM ANALYZER")
    print("=" * 70)
    print("Converting original PDF to HTML with fields positioned EXACTLY")
    print("where the real form lines and data areas are!")
    print("✅ Analyzes where blue text (previous client data) appears")
    print("✅ Removes blue text from background")
    print("✅ Positions form fields in those exact locations")
    print("=" * 70)
    
    # Analyze the form structure
    form_positions = analyzer.analyze_form_structure()
    
    if form_positions:
        # Create true HTML form
        result = analyzer.create_true_html_form(form_positions)
        
        if result:
            print(f"\n🎉 SUCCESS!")
            print(f"✅ Created HTML form with fields positioned exactly where data should go")
            print(f"✅ No more guessing - fields are where the original form expects them")
            print(f"✅ Blue text removed, gorgeous layout preserved")
            print(f"🌐 Open in browser to see the true form layout!")

if __name__ == "__main__":
    main()