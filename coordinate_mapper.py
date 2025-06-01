#!/usr/bin/env python3
"""
Coordinate Mapper - Interactive tool to properly map form field positions
Shows the PDF as background and lets us click to place fields correctly
"""

import fitz  # pymupdf
import base64
import os

class CoordinateMapper:
    def __init__(self):
        self.pdf_path = "documents/California_Residential_Purchase_Agreement_CLEAN_TEMPLATE.pdf"
        
    def create_interactive_coordinate_mapper(self, output_path="html_templates/coordinate_mapper.html"):
        """Create interactive HTML tool to map coordinates correctly"""
        
        print("🎯 CREATING INTERACTIVE COORDINATE MAPPER")
        print("=" * 60)
        
        doc = fitz.open(self.pdf_path)
        
        # Get page 3 (main form page) - index 2
        page = doc[2]
        
        # Remove blue text first
        text_dict = page.get_text("dict")
        for block in text_dict["blocks"]:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        color = span.get("color", 0)
                        text = span.get("text", "").strip()
                        if text and color != 0:  # Remove colored text
                            bbox = span["bbox"]
                            rect = fitz.Rect(bbox)
                            page.draw_rect(rect, color=(1, 1, 1), fill=(1, 1, 1))
        
        # Convert page to image
        mat = fitz.Matrix(2.0, 2.0)  # High quality
        pix = page.get_pixmap(matrix=mat)
        img_data = pix.tobytes("png")
        img_base64 = base64.b64encode(img_data).decode()
        
        # Get actual page dimensions
        page_rect = page.rect
        pdf_width = page_rect.width
        pdf_height = page_rect.height
        
        print(f"📏 PDF page dimensions: {pdf_width} x {pdf_height} points")
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CRPA Coordinate Mapper</title>
    <style>
        body {{
            margin: 0;
            padding: 20px;
            font-family: Arial, sans-serif;
            background: #f0f0f0;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        .header {{
            background: #007cba;
            color: white;
            padding: 20px;
            text-align: center;
        }}
        
        .content {{
            display: flex;
            min-height: 800px;
        }}
        
        .form-container {{
            flex: 1;
            position: relative;
            background: white;
            border-right: 2px solid #eee;
        }}
        
        .form-image {{
            width: 100%;
            height: auto;
            display: block;
            cursor: crosshair;
        }}
        
        .controls {{
            width: 300px;
            padding: 20px;
            background: #f8f9fa;
            overflow-y: auto;
        }}
        
        .field-marker {{
            position: absolute;
            border: 2px solid red;
            background: rgba(255, 0, 0, 0.1);
            font-size: 10px;
            color: red;
            font-weight: bold;
            pointer-events: none;
            z-index: 10;
        }}
        
        .control-group {{
            margin-bottom: 15px;
            padding: 15px;
            border: 1px solid #ddd;
            border-radius: 4px;
            background: white;
        }}
        
        .control-group h3 {{
            margin: 0 0 10px 0;
            color: #333;
            font-size: 14px;
        }}
        
        input, select {{
            width: 100%;
            padding: 8px;
            margin: 5px 0;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 12px;
        }}
        
        button {{
            width: 100%;
            padding: 10px;
            margin: 5px 0;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
        }}
        
        .btn-primary {{
            background: #007cba;
            color: white;
        }}
        
        .btn-success {{
            background: #28a745;
            color: white;
        }}
        
        .btn-danger {{
            background: #dc3545;
            color: white;
        }}
        
        .btn-secondary {{
            background: #6c757d;
            color: white;
        }}
        
        .field-list {{
            max-height: 300px;
            overflow-y: auto;
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 10px;
            background: white;
        }}
        
        .field-item {{
            padding: 8px;
            margin: 5px 0;
            border: 1px solid #eee;
            border-radius: 4px;
            background: #f8f9fa;
            font-size: 11px;
        }}
        
        .coordinates {{
            background: #e9ecef;
            padding: 10px;
            border-radius: 4px;
            font-family: monospace;
            font-size: 11px;
            margin: 10px 0;
        }}
        
        #output-code {{
            width: 100%;
            height: 200px;
            font-family: monospace;
            font-size: 10px;
            background: #f8f9fa;
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 10px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>CRPA Form Coordinate Mapper</h1>
            <p>Click on the form to place fields exactly where they should go</p>
        </div>
        
        <div class="content">
            <div class="form-container">
                <img src="data:image/png;base64,{img_base64}" 
                     class="form-image" 
                     id="form-image"
                     onclick="addField(event)">
            </div>
            
            <div class="controls">
                <div class="control-group">
                    <h3>Current Field</h3>
                    <select id="field-type">
                        <option value="text">Text Field</option>
                        <option value="checkbox">Checkbox</option>
                    </select>
                    
                    <input type="text" id="field-name" placeholder="Field name (e.g., buyer_name)" />
                    <input type="text" id="field-placeholder" placeholder="Placeholder text" />
                    
                    <input type="number" id="field-width" placeholder="Width (px)" value="150" />
                    <input type="number" id="field-height" placeholder="Height (px)" value="20" />
                </div>
                
                <div class="control-group">
                    <h3>Quick Fields</h3>
                    <button class="btn-primary" onclick="setField('buyer_name', 'Buyer Name', 200, 20)">Buyer Name</button>
                    <button class="btn-primary" onclick="setField('property_address', 'Property Address', 250, 20)">Property Address</button>
                    <button class="btn-primary" onclick="setField('city', 'City', 120, 20)">City</button>
                    <button class="btn-primary" onclick="setField('state', 'State', 40, 20)">State</button>
                    <button class="btn-primary" onclick="setField('zip_code', 'ZIP Code', 80, 20)">ZIP Code</button>
                    <button class="btn-primary" onclick="setField('purchase_price', 'Purchase Price', 150, 20)">Purchase Price</button>
                    <button class="btn-primary" onclick="setField('form_date', 'Date', 100, 20)">Date</button>
                </div>
                
                <div class="control-group">
                    <h3>Actions</h3>
                    <button class="btn-success" onclick="generateHTML()">Generate HTML Code</button>
                    <button class="btn-danger" onclick="clearAllFields()">Clear All Fields</button>
                    <button class="btn-secondary" onclick="exportCoordinates()">Export Coordinates</button>
                </div>
                
                <div class="control-group">
                    <h3>Mouse Position</h3>
                    <div class="coordinates" id="mouse-coords">
                        Click on the form to see coordinates
                    </div>
                </div>
                
                <div class="control-group">
                    <h3>Placed Fields</h3>
                    <div class="field-list" id="field-list">
                        No fields placed yet
                    </div>
                </div>
                
                <div class="control-group">
                    <h3>Generated HTML</h3>
                    <textarea id="output-code" readonly placeholder="Click 'Generate HTML Code' to see the form HTML"></textarea>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        let fields = [];
        let fieldCounter = 0;
        
        // Track mouse position
        document.getElementById('form-image').addEventListener('mousemove', function(e) {{
            const rect = this.getBoundingClientRect();
            const x = Math.round(e.clientX - rect.left);
            const y = Math.round(e.clientY - rect.top);
            document.getElementById('mouse-coords').textContent = `X: ${{x}}, Y: ${{y}}`;
        }});
        
        function setField(name, placeholder, width, height) {{
            document.getElementById('field-name').value = name;
            document.getElementById('field-placeholder').value = placeholder;
            document.getElementById('field-width').value = width;
            document.getElementById('field-height').value = height;
        }}
        
        function addField(event) {{
            const rect = event.target.getBoundingClientRect();
            const x = Math.round(event.clientX - rect.left);
            const y = Math.round(event.clientY - rect.top);
            
            const fieldType = document.getElementById('field-type').value;
            const fieldName = document.getElementById('field-name').value || `field_${{fieldCounter++}}`;
            const placeholder = document.getElementById('field-placeholder').value || fieldName;
            const width = parseInt(document.getElementById('field-width').value) || 150;
            const height = parseInt(document.getElementById('field-height').value) || 20;
            
            // Create field object
            const field = {{
                id: `field_${{fields.length}}`,
                type: fieldType,
                name: fieldName,
                placeholder: placeholder,
                x: x,
                y: y,
                width: width,
                height: height
            }};
            
            fields.push(field);
            
            // Create visual marker
            const marker = document.createElement('div');
            marker.className = 'field-marker';
            marker.id = field.id;
            marker.style.left = x + 'px';
            marker.style.top = y + 'px';
            marker.style.width = width + 'px';
            marker.style.height = height + 'px';
            marker.textContent = fieldName;
            marker.title = `${{fieldName}} (${{x}}, ${{y}}) ${{width}}x${{height}}`;
            
            // Add click to remove
            marker.onclick = function(e) {{
                e.stopPropagation();
                removeField(field.id);
            }};
            marker.style.pointerEvents = 'auto';
            marker.style.cursor = 'pointer';
            
            document.querySelector('.form-container').appendChild(marker);
            
            updateFieldList();
        }}
        
        function removeField(fieldId) {{
            fields = fields.filter(f => f.id !== fieldId);
            const marker = document.getElementById(fieldId);
            if (marker) marker.remove();
            updateFieldList();
        }}
        
        function clearAllFields() {{
            fields = [];
            document.querySelectorAll('.field-marker').forEach(marker => marker.remove());
            updateFieldList();
        }}
        
        function updateFieldList() {{
            const list = document.getElementById('field-list');
            if (fields.length === 0) {{
                list.innerHTML = 'No fields placed yet';
                return;
            }}
            
            list.innerHTML = fields.map(field => 
                `<div class="field-item">
                    <strong>${{field.name}}</strong> (${{field.type}})<br>
                    Position: (${{field.x}}, ${{field.y}})<br>
                    Size: ${{field.width}} × ${{field.height}}
                    <button onclick="removeField('${{field.id}}')" style="float: right; padding: 2px 6px; font-size: 10px;">×</button>
                </div>`
            ).join('');
        }}
        
        function generateHTML() {{
            let html = `<!-- Form fields positioned exactly where they should be -->\\n`;
            
            fields.forEach(field => {{
                if (field.type === 'checkbox') {{
                    html += `        <input type="checkbox" name="${{field.name}}" class="form-field checkbox-field" 
               style="left: ${{field.x}}px; top: ${{field.y}}px; width: ${{field.width}}px; height: ${{field.height}}px;" 
               title="${{field.placeholder}}">\\n`;
                }} else {{
                    html += `        <input type="text" name="${{field.name}}" class="form-field text-field" 
               style="left: ${{field.x}}px; top: ${{field.y}}px; width: ${{field.width}}px; height: ${{field.height}}px;" 
               placeholder="${{field.placeholder}}" title="${{field.placeholder}}">\\n`;
                }}
            }});
            
            document.getElementById('output-code').value = html;
        }}
        
        function exportCoordinates() {{
            const coords = fields.map(field => ({{
                name: field.name,
                type: field.type,
                x: field.x,
                y: field.y,
                width: field.width,
                height: field.height
            }}));
            
            console.log('Field coordinates:', coords);
            alert('Coordinates exported to browser console (F12 to view)');
        }}
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
            print(f"✅ COORDINATE MAPPER CREATED!")
            print(f"📁 File: {output_path}")
            print(f"📊 Size: {file_size:,} bytes")
            print(f"🎯 Interactive tool to place fields correctly!")
            print(f"🌐 Windows: file:///C:/Users/ender/.claude/projects/offer-creator/{output_path}")
            print(f"")
            print(f"📋 HOW TO USE:")
            print(f"1. Open the file in your browser")
            print(f"2. Click 'Buyer Name' button, then click where buyer name should go")
            print(f"3. Click 'Property Address' button, then click where address should go")
            print(f"4. Continue for all fields")
            print(f"5. Click 'Generate HTML Code' to get perfect coordinates")
            print(f"6. Copy the generated HTML code for the final form!")
            
            return output_path
        else:
            print("❌ Failed to create coordinate mapper")
            return None

def main():
    """Create interactive coordinate mapping tool"""
    
    mapper = CoordinateMapper()
    
    print("🎯 INTERACTIVE COORDINATE MAPPER")
    print("=" * 70)
    print("Creating visual tool to map form field coordinates correctly!")
    print("✅ Shows actual form as background")
    print("✅ Click to place fields exactly where they should go")
    print("✅ Generates perfect HTML code with correct coordinates")
    print("=" * 70)
    
    result = mapper.create_interactive_coordinate_mapper()
    
    if result:
        print(f"\n🎉 SUCCESS!")
        print(f"✅ Interactive coordinate mapper created")
        print(f"✅ Use this tool to place fields exactly where they belong")
        print(f"✅ No more guessing coordinates!")

if __name__ == "__main__":
    main()