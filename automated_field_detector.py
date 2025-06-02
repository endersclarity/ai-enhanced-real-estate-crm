#!/usr/bin/env python3
"""
Automated Field Detector - Use image analysis to automatically detect form field positions
No manual mapping required - analyzes the form visually to find input areas
"""

import fitz  # pymupdf
import base64
import os
import re
from PIL import Image, ImageDraw, ImageFilter
import io
import numpy as np

class AutomatedFieldDetector:
    def __init__(self):
        self.pdf_path = "documents/California_Residential_Purchase_Agreement_CLEAN_TEMPLATE.pdf"
        
    def detect_form_fields_automatically(self):
        """Automatically detect form field positions using image analysis"""
        print("🤖 AUTOMATED FIELD DETECTION")
        print("=" * 60)
        
        doc = fitz.open(self.pdf_path)
        page = doc[2]  # Main form page
        
        # Remove colored text first
        print("🧹 Cleaning form background...")
        text_dict = page.get_text("dict")
        for block in text_dict["blocks"]:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        color = span.get("color", 0)
                        text = span.get("text", "").strip()
                        if text and color != 0:
                            bbox = span["bbox"]
                            rect = fitz.Rect(bbox)
                            page.draw_rect(rect, color=(1, 1, 1), fill=(1, 1, 1))
        
        # Convert to high-res image for analysis
        mat = fitz.Matrix(3.0, 3.0)  # 3x scaling for better analysis
        pix = page.get_pixmap(matrix=mat)
        img_data = pix.tobytes("png")
        
        # Open with PIL for analysis
        image = Image.open(io.BytesIO(img_data))
        width, height = image.size
        
        print(f"📏 Analyzing image: {width} x {height} pixels")
        
        # Convert to grayscale for line detection
        gray = image.convert('L')
        
        # Find horizontal lines (likely form fields)
        horizontal_lines = self._detect_horizontal_lines(gray)
        print(f"📏 Found {len(horizontal_lines)} horizontal lines")
        
        # Find text labels near lines
        labeled_fields = self._match_labels_to_lines(page, horizontal_lines, mat)
        print(f"🏷️ Matched {len(labeled_fields)} labeled fields")
        
        # Generate form fields
        form_fields = self._generate_form_fields(labeled_fields, width, height, mat)
        print(f"📝 Generated {len(form_fields)} form fields")
        
        doc.close()
        return form_fields, img_data
    
    def _detect_horizontal_lines(self, gray_image):
        """Detect horizontal lines in the image that likely represent form fields"""
        # Convert to numpy array
        img_array = np.array(gray_image)
        
        # Find horizontal edges
        horizontal_lines = []
        
        # Look for sequences of underscores or lines
        for y in range(50, img_array.shape[0] - 50):  # Skip edges
            row = img_array[y]
            
            # Find dark horizontal segments (potential underlines)
            dark_pixels = row < 200  # Threshold for "dark" pixels
            
            # Find continuous dark segments
            in_segment = False
            segment_start = 0
            
            for x in range(len(dark_pixels)):
                if dark_pixels[x] and not in_segment:
                    in_segment = True
                    segment_start = x
                elif not dark_pixels[x] and in_segment:
                    in_segment = False
                    segment_length = x - segment_start
                    
                    # If segment is long enough, it's likely a form line
                    if segment_length > 50:  # Minimum line length
                        horizontal_lines.append({
                            'y': y,
                            'x_start': segment_start,
                            'x_end': x,
                            'length': segment_length
                        })
        
        # Remove duplicate lines (keep longest in each y-range)
        filtered_lines = []
        horizontal_lines.sort(key=lambda x: x['y'])
        
        for line in horizontal_lines:
            # Check if there's already a line within 10 pixels
            nearby = [l for l in filtered_lines if abs(l['y'] - line['y']) < 10]
            if not nearby:
                filtered_lines.append(line)
            else:
                # Keep the longer line
                longest = max(nearby + [line], key=lambda x: x['length'])
                # Remove shorter lines
                filtered_lines = [l for l in filtered_lines if l not in nearby]
                filtered_lines.append(longest)
        
        return filtered_lines
    
    def _match_labels_to_lines(self, page, horizontal_lines, matrix):
        """Match text labels to horizontal lines to identify field purposes"""
        # Get all text with positions
        text_dict = page.get_text("dict")
        
        labeled_fields = []
        
        for line in horizontal_lines:
            # Convert line coordinates back to PDF coordinates
            line_y_pdf = (line['y'] / matrix.a)  # Reverse scaling
            line_x_start_pdf = (line['x_start'] / matrix.a)
            line_x_end_pdf = (line['x_end'] / matrix.a)
            
            # Look for text near this line
            nearby_text = []
            
            for block in text_dict["blocks"]:
                if "lines" in block:
                    for text_line in block["lines"]:
                        for span in text_line["spans"]:
                            text = span.get("text", "").strip()
                            if text and span.get("color", 0) == 0:  # Only black text
                                bbox = span["bbox"]
                                text_y = bbox[1]  # Top of text
                                text_x = bbox[0]  # Left of text
                                
                                # Check if text is near this line (above it)
                                y_distance = abs(text_y - line_y_pdf)
                                if y_distance < 30:  # Within 30 points
                                    nearby_text.append({
                                        'text': text,
                                        'distance': y_distance,
                                        'x': text_x,
                                        'y': text_y
                                    })
            
            # Find the best label for this line
            if nearby_text:
                # Sort by distance and relevance
                nearby_text.sort(key=lambda x: x['distance'])
                best_label = nearby_text[0]['text']
                
                # Determine field type and name from label
                field_info = self._classify_field(best_label, line_x_start_pdf, line_y_pdf)
                
                labeled_fields.append({
                    'line': line,
                    'label': best_label,
                    'field_name': field_info['name'],
                    'field_type': field_info['type'],
                    'width': field_info['width'],
                    'height': field_info['height']
                })
        
        return labeled_fields
    
    def _classify_field(self, label_text, x, y):
        """Classify field type and generate appropriate name based on label text"""
        label_lower = label_text.lower()
        
        # Common field patterns
        if any(word in label_lower for word in ['buyer', 'purchaser', 'name']):
            return {'name': 'buyer_name', 'type': 'text', 'width': 200, 'height': 20}
        elif any(word in label_lower for word in ['seller', 'vendor']):
            return {'name': 'seller_name', 'type': 'text', 'width': 200, 'height': 20}
        elif any(word in label_lower for word in ['property', 'address', 'street']):
            return {'name': 'property_address', 'type': 'text', 'width': 300, 'height': 20}
        elif any(word in label_lower for word in ['city']):
            return {'name': 'city', 'type': 'text', 'width': 150, 'height': 20}
        elif any(word in label_lower for word in ['state']):
            return {'name': 'state', 'type': 'text', 'width': 50, 'height': 20}
        elif any(word in label_lower for word in ['zip', 'postal']):
            return {'name': 'zip_code', 'type': 'text', 'width': 80, 'height': 20}
        elif any(word in label_lower for word in ['price', 'amount', '$']):
            return {'name': 'purchase_price', 'type': 'text', 'width': 150, 'height': 20}
        elif any(word in label_lower for word in ['date']):
            return {'name': 'date', 'type': 'text', 'width': 120, 'height': 20}
        elif any(word in label_lower for word in ['phone', 'tel']):
            return {'name': 'phone', 'type': 'text', 'width': 130, 'height': 20}
        elif any(word in label_lower for word in ['email']):
            return {'name': 'email', 'type': 'text', 'width': 200, 'height': 20}
        else:
            # Generic field
            field_name = re.sub(r'[^a-zA-Z0-9_]', '_', label_text[:20]).lower()
            return {'name': field_name, 'type': 'text', 'width': 150, 'height': 20}
    
    def _generate_form_fields(self, labeled_fields, img_width, img_height, matrix):
        """Generate final form field definitions with correct coordinates"""
        form_fields = []
        
        for field_data in labeled_fields:
            line = field_data['line']
            
            # Convert coordinates back to HTML scale (scale down from 3x)
            html_x = line['x_start'] // 3
            html_y = line['y'] // 3
            html_width = field_data['width']
            html_height = field_data['height']
            
            # Adjust position to be on the line (not above it)
            html_y -= 5  # Move up slightly to center on line
            
            form_fields.append({
                'name': field_data['field_name'],
                'type': field_data['field_type'],
                'x': html_x,
                'y': html_y,
                'width': html_width,
                'height': html_height,
                'label': field_data['label']
            })
        
        return form_fields
    
    def create_auto_detected_form(self, output_path="html_templates/auto_detected_form.html"):
        """Create HTML form with automatically detected field positions"""
        print("\n🎯 CREATING AUTO-DETECTED FORM")
        print("=" * 60)
        
        # Detect fields automatically
        form_fields, img_data = self.detect_form_fields_automatically()
        
        if not form_fields:
            print("❌ No fields detected")
            return None
        
        # Convert image to base64
        img_base64 = base64.b64encode(img_data).decode()
        
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Auto-Detected CRPA Form</title>
    <style>
        body {{
            margin: 0;
            padding: 20px;
            font-family: Arial, sans-serif;
            background: #f0f0f0;
        }}
        
        .container {{
            max-width: 1000px;
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
        
        .form-container {{
            position: relative;
            background: white;
        }}
        
        .form-image {{
            width: 100%;
            height: auto;
            display: block;
        }}
        
        .form-field {{
            position: absolute;
            border: 2px solid rgba(0, 123, 255, 0.5);
            background: rgba(255, 255, 255, 0.9);
            font-size: 10px;
            font-family: Arial, sans-serif;
            z-index: 10;
            padding: 2px 4px;
            border-radius: 2px;
        }}
        
        .field-highlight {{
            border-color: rgba(255, 0, 0, 0.7);
            background: rgba(255, 255, 0, 0.2);
        }}
        
        .controls {{
            padding: 20px;
            background: #f8f9fa;
        }}
        
        button {{
            padding: 10px 20px;
            margin: 5px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
        }}
        
        .btn-primary {{ background: #007cba; color: white; }}
        .btn-success {{ background: #28a745; color: white; }}
        .btn-danger {{ background: #dc3545; color: white; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Auto-Detected CRPA Form</h1>
            <p>Fields automatically detected using image analysis</p>
            <p><strong>{len(form_fields)} fields detected</strong></p>
        </div>
        
        <div class="form-container">
            <img src="data:image/png;base64,{img_base64}" class="form-image" id="form-image">
"""

        # Add form fields
        for field in form_fields:
            html_content += f"""
            <input type="{field['type']}" name="{field['name']}" class="form-field" 
                   style="left: {field['x']}px; top: {field['y']}px; width: {field['width']}px; height: {field['height']}px;" 
                   placeholder="{field['label'][:30]}" title="{field['label']}">"""

        html_content += f"""
        </div>
        
        <div class="controls">
            <h3>Auto-Detected Fields ({len(form_fields)} total)</h3>
            <button class="btn-primary" onclick="populateWithSampleData()">Fill Sample Data</button>
            <button class="btn-danger" onclick="clearAllFields()">Clear All</button>
            <button class="btn-success" onclick="toggleFieldVisibility()">Toggle Borders</button>
            
            <h4>Field List:</h4>
            <ul>"""

        for field in form_fields:
            html_content += f"<li><strong>{field['name']}</strong>: {field['label']} at ({field['x']}, {field['y']})</li>"

        html_content += """
            </ul>
        </div>
    </div>
    
    <script>
        function populateWithSampleData() {
            const sampleData = {
                'buyer_name': 'John & Jane Smith',
                'seller_name': 'Bob & Alice Johnson',
                'property_address': '1234 Main Street',
                'city': 'Beverly Hills',
                'state': 'CA',
                'zip_code': '90210',
                'purchase_price': '$2,500,000.00',
                'date': '2025-06-01',
                'phone': '(555) 123-4567',
                'email': 'buyer@example.com'
            };
            
            for (const [fieldName, value] of Object.entries(sampleData)) {
                const field = document.querySelector(`[name="${fieldName}"]`);
                if (field) field.value = value;
            }
        }
        
        function clearAllFields() {
            document.querySelectorAll('.form-field').forEach(field => {
                field.value = '';
            });
        }
        
        let fieldsVisible = true;
        function toggleFieldVisibility() {
            const fields = document.querySelectorAll('.form-field');
            fieldsVisible = !fieldsVisible;
            
            fields.forEach(field => {
                field.style.border = fieldsVisible ? '2px solid rgba(0, 123, 255, 0.5)' : 'none';
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
    </script>
</body>
</html>"""
        
        # Save HTML file
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            print(f"✅ AUTO-DETECTED FORM CREATED!")
            print(f"📁 File: {output_path}")
            print(f"📊 Size: {file_size:,} bytes")
            print(f"🤖 {len(form_fields)} fields automatically detected!")
            print(f"🌐 Windows: file:///C:/Users/ender/.claude/projects/offer-creator/{output_path}")
            
            return output_path
        else:
            print("❌ Failed to create auto-detected form")
            return None

def main():
    """Run automated field detection"""
    detector = AutomatedFieldDetector()
    
    print("🤖 AUTOMATED FIELD DETECTION")
    print("=" * 70)
    print("Using image analysis to automatically detect form field positions")
    print("✅ No manual mapping required!")
    print("✅ Analyzes horizontal lines and nearby text labels")
    print("✅ Intelligently classifies field types")
    print("=" * 70)
    
    result = detector.create_auto_detected_form()
    
    if result:
        print(f"\n🎉 SUCCESS!")
        print(f"✅ Form fields automatically detected and positioned")
        print(f"✅ No manual coordinate mapping needed")
        print(f"✅ Open in browser to see the results")

if __name__ == "__main__":
    main()