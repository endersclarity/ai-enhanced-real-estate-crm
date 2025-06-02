#!/usr/bin/env python3
"""
Clean Bespoke Creator - Start with BLANK template and build perfect HTML form
Use the cleanest possible starting point and recreate only the form structure
"""

import fitz  # PyMuPDF
import pdfplumber
import os
from typing import List, Dict

class CleanBespokeCreator:
    def __init__(self):
        # Use the BLANK template, not the messy one with data
        self.blank_pdf = "documents/California_Residential_Purchase_Agreement_BLANK_TEMPLATE.pdf"
        self.final_blank_pdf = "documents/California_Residential_Purchase_Agreement_FINAL_BLANK.pdf"
        
    def analyze_blank_template(self):
        """Analyze the blank template to understand clean form structure"""
        print("🔍 ANALYZING BLANK CAR FORM TEMPLATE")
        print("=" * 60)
        
        # Try both blank templates to find the cleanest one
        templates_to_try = [self.blank_pdf, self.final_blank_pdf]
        
        for template_path in templates_to_try:
            if os.path.exists(template_path):
                print(f"📄 Analyzing: {template_path}")
                
                with pdfplumber.open(template_path) as pdf:
                    print(f"📖 Total pages: {len(pdf.pages)}")
                    
                    # Check each page for content
                    for page_num, page in enumerate(pdf.pages):
                        chars = page.chars
                        lines = page.lines
                        
                        print(f"📄 Page {page_num + 1}: {len(chars)} chars, {len(lines)} lines")
                        
                        # Show some sample text to see what we're working with
                        if chars:
                            sample_text = ' '.join([c['text'] for c in chars[:50]])
                            print(f"   Sample text: {sample_text[:100]}...")
                        
                        # Page 3 (index 2) is usually the main form
                        if page_num == 2:
                            return self._analyze_main_form_page(page, template_path)
        
        print("❌ No suitable blank template found")
        return None
    
    def _analyze_main_form_page(self, page, template_path):
        """Analyze the main form page structure"""
        print(f"\n🎯 ANALYZING MAIN FORM PAGE")
        print("=" * 50)
        
        # Get page dimensions
        width, height = page.width, page.height
        print(f"📏 Page size: {width} x {height} points ({width/72:.1f}\" x {height/72:.1f}\")")
        
        # Get all elements
        chars = page.chars
        lines = page.lines
        rects = page.rects
        
        print(f"📝 Elements: {len(chars)} chars, {len(lines)} lines, {len(rects)} rects")
        
        # Group text into meaningful blocks
        text_blocks = self._group_clean_text(chars)
        print(f"📄 Text blocks: {len(text_blocks)}")
        
        # Find form field indicators (lines, underscores, boxes)
        field_indicators = self._find_form_field_indicators(lines, text_blocks)
        print(f"📝 Form field indicators: {len(field_indicators)}")
        
        # Classify form sections
        form_sections = self._identify_form_sections(text_blocks)
        print(f"📋 Form sections: {len(form_sections)}")
        
        return {
            'template_path': template_path,
            'page_size': (width, height),
            'text_blocks': text_blocks,
            'field_indicators': field_indicators,
            'form_sections': form_sections,
            'lines': lines,
            'rects': rects
        }
    
    def _group_clean_text(self, chars):
        """Group characters into clean text blocks without old data"""
        if not chars:
            return []
        
        # Sort characters by position
        sorted_chars = sorted(chars, key=lambda c: (round(c['top'], 1), c['x0']))
        
        blocks = []
        current_block = []
        
        for char in sorted_chars:
            # Skip very small text (likely form field data we don't want)
            if char.get('size', 10) < 6:
                continue
                
            if current_block and (
                abs(char['top'] - current_block[-1]['top']) > 5 or  # Different line
                char['x0'] - current_block[-1]['x1'] > 20  # Large gap
            ):
                # Finish current block
                if current_block:
                    block_text = ''.join(c['text'] for c in current_block).strip()
                    if block_text and len(block_text) > 2:  # Skip tiny fragments
                        blocks.append(self._create_clean_text_block(current_block))
                current_block = [char]
            else:
                current_block.append(char)
        
        # Add last block
        if current_block:
            block_text = ''.join(c['text'] for c in current_block).strip()
            if block_text and len(block_text) > 2:
                blocks.append(self._create_clean_text_block(current_block))
        
        return blocks
    
    def _create_clean_text_block(self, chars):
        """Create a clean text block"""
        text = ''.join(c['text'] for c in chars).strip()
        x0 = min(c['x0'] for c in chars)
        x1 = max(c['x1'] for c in chars)
        top = min(c['top'] for c in chars)
        bottom = max(c['bottom'] for c in chars)
        font_size = chars[0].get('size', 10) if chars else 10
        
        return {
            'text': text,
            'x': x0,
            'y': top,
            'width': x1 - x0,
            'height': bottom - top,
            'font_size': font_size,
            'type': self._classify_text_block(text)
        }
    
    def _classify_text_block(self, text):
        """Classify what type of text block this is"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['california', 'residential', 'purchase', 'agreement']):
            return 'title'
        elif text.endswith(':') or 'name' in text_lower or 'address' in text_lower:
            return 'label'
        elif len(text) > 100:
            return 'instructions'
        elif text.isupper() and len(text) > 10:
            return 'section_header'
        else:
            return 'content'
    
    def _find_form_field_indicators(self, lines, text_blocks):
        """Find lines and patterns that indicate where form fields should go"""
        indicators = []
        
        # Look for horizontal lines that could be form fields
        for line in lines:
            if (line['width'] > 50 and  # Minimum length
                abs(line['top'] - line['bottom']) < 3 and  # Horizontal
                line['width'] < 400):  # Not too long (border)
                
                indicators.append({
                    'type': 'line',
                    'x': line['x0'],
                    'y': line['top'],
                    'width': line['width'],
                    'height': 1,
                    'purpose': 'form_field'
                })
        
        # Look for text patterns that indicate form fields
        for block in text_blocks:
            text = block['text']
            
            # Labels that typically have form fields after them
            if (block['type'] == 'label' or 
                text.endswith(':') or
                any(word in text.lower() for word in ['name', 'address', 'date', 'price', 'city', 'state'])):
                
                indicators.append({
                    'type': 'label_field',
                    'x': block['x'] + block['width'] + 10,
                    'y': block['y'] - 2,
                    'width': 150,
                    'height': 18,
                    'purpose': 'text_input',
                    'label': text
                })
        
        return indicators
    
    def _identify_form_sections(self, text_blocks):
        """Identify major sections of the form"""
        sections = []
        current_section = None
        
        for block in text_blocks:
            if block['type'] == 'section_header' or block['type'] == 'title':
                if current_section:
                    sections.append(current_section)
                
                current_section = {
                    'title': block['text'],
                    'x': block['x'],
                    'y': block['y'],
                    'blocks': []
                }
            elif current_section:
                current_section['blocks'].append(block)
        
        if current_section:
            sections.append(current_section)
        
        return sections
    
    def create_clean_html_form(self, output_path="html_templates/clean_bespoke_crpa.html"):
        """Create a clean HTML form from blank template analysis"""
        print("\n🎨 CREATING CLEAN BESPOKE HTML FORM")
        print("=" * 60)
        
        # Analyze blank template
        analysis = self.analyze_blank_template()
        
        if not analysis:
            print("❌ Could not analyze blank template")
            return None
        
        page_width, page_height = analysis['page_size']
        text_blocks = analysis['text_blocks']
        field_indicators = analysis['field_indicators']
        form_sections = analysis['form_sections']
        
        print(f"🎨 Building clean form from {analysis['template_path']}")
        
        # Create HTML content
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>✨ Clean CRPA Form - Built from Blank Template</title>
    <style>
        @page {{
            size: {page_width/72:.1f}in {page_height/72:.1f}in;
            margin: 0.5in;
        }}
        
        * {{
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Times New Roman', serif;
            font-size: 11px;
            line-height: 1.3;
            color: #000;
            background: #fff;
            margin: 0;
            padding: 20px;
        }}
        
        .form-page {{
            width: {page_width}px;
            height: {page_height}px;
            position: relative;
            margin: 0 auto;
            background: white;
            border: 1px solid #ddd;
            padding: 36px;
        }}
        
        /* Clean text elements */
        .form-title {{
            font-size: 14px;
            font-weight: bold;
            text-align: center;
            margin-bottom: 20px;
        }}
        
        .section-header {{
            font-size: 12px;
            font-weight: bold;
            text-transform: uppercase;
            margin: 15px 0 10px 0;
            border-bottom: 1px solid #000;
            padding-bottom: 2px;
        }}
        
        .form-label {{
            font-size: 10px;
            font-weight: normal;
            position: absolute;
        }}
        
        .instructions {{
            font-size: 9px;
            color: #666;
            margin: 10px 0;
            line-height: 1.2;
        }}
        
        /* Clean form fields */
        .form-field {{
            position: absolute;
            border: none;
            border-bottom: 1px solid #000;
            background: transparent;
            font-family: 'Times New Roman', serif;
            font-size: 10px;
            color: #000;
            padding: 0 2px;
            outline: none;
        }}
        
        .form-field:focus {{
            background: rgba(173, 216, 230, 0.2);
            border-bottom: 2px solid #0066cc;
        }}
        
        .checkbox-field {{
            width: 12px;
            height: 12px;
            position: absolute;
        }}
        
        /* Print optimized */
        @media print {{
            body {{ padding: 0; }}
            .form-page {{ 
                border: none; 
                margin: 0;
                padding: 36px;
            }}
            .form-field {{
                border-bottom: 1px solid #000 !important;
                background: transparent !important;
            }}
            .control-panel {{ display: none; }}
        }}
        
        /* Control panel */
        .control-panel {{
            position: fixed;
            top: 20px;
            right: 20px;
            background: rgba(0, 0, 0, 0.9);
            color: white;
            padding: 15px;
            border-radius: 8px;
            z-index: 1000;
            font-size: 12px;
        }}
        
        .control-panel button {{
            display: block;
            width: 100%;
            margin: 5px 0;
            padding: 8px 12px;
            background: #28a745;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 11px;
        }}
        
        .control-panel button:hover {{
            background: #1e7e34;
        }}
    </style>
</head>
<body>
    <div class="control-panel">
        <h4>✨ Clean Form Controls</h4>
        <button onclick="fillSampleData()">📝 Fill Sample</button>
        <button onclick="clearAllFields()">🗑️ Clear All</button>
        <button onclick="window.print()">🖨️ Print</button>
        <div style="margin-top: 10px; font-size: 10px; color: #ccc;">
            Built from: {os.path.basename(analysis['template_path'])}<br>
            {len(text_blocks)} elements<br>
            {len(field_indicators)} fields
        </div>
    </div>
    
    <div class="form-page">"""
        
        # Add clean text elements (structure only)
        for block in text_blocks:
            if block['type'] == 'title':
                html_content += f"""
        <div class="form-title">{block['text']}</div>"""
            elif block['type'] == 'section_header':
                html_content += f"""
        <div class="section-header">{block['text']}</div>"""
            elif block['type'] == 'label':
                html_content += f"""
        <div class="form-label" style="left: {block['x']}px; top: {block['y']}px;">{block['text']}</div>"""
            elif block['type'] == 'instructions' and len(block['text']) > 20:
                html_content += f"""
        <div class="instructions">{block['text']}</div>"""
        
        # Add clean form fields
        field_count = 0
        for indicator in field_indicators:
            if indicator['type'] in ['line', 'label_field']:
                field_name = f"field_{field_count}"
                
                # Try to generate meaningful field names
                if 'label' in indicator:
                    label_text = indicator['label'].lower()
                    if 'buyer' in label_text:
                        field_name = 'buyer_name'
                    elif 'seller' in label_text:
                        field_name = 'seller_name'
                    elif 'address' in label_text:
                        field_name = 'property_address'
                    elif 'city' in label_text:
                        field_name = 'city'
                    elif 'state' in label_text:
                        field_name = 'state'
                    elif 'date' in label_text:
                        field_name = 'date'
                    elif 'price' in label_text:
                        field_name = 'purchase_price'
                
                html_content += f"""
        <input type="text" 
               name="{field_name}" 
               class="form-field"
               style="left: {indicator['x']}px; top: {indicator['y']}px; width: {indicator['width']}px; height: {indicator['height']}px;"
               placeholder="{field_name.replace('_', ' ').title()}">"""
                
                field_count += 1
        
        html_content += """
    </div>
    
    <script>
        function fillSampleData() {
            const cleanSampleData = {
                'buyer_name': 'John & Jane Smith',
                'seller_name': 'Robert & Patricia Wilson',
                'property_address': '123 Main Street',
                'city': 'Los Angeles',
                'state': 'CA',
                'purchase_price': '$750,000.00',
                'date': '2025-06-01'
            };
            
            for (const [fieldName, value] of Object.entries(cleanSampleData)) {
                const field = document.querySelector(`[name="${fieldName}"]`);
                if (field) field.value = value;
            }
        }
        
        function clearAllFields() {
            document.querySelectorAll('.form-field').forEach(field => {
                field.value = '';
            });
        }
        
        console.log('✨ Clean CRPA form loaded - built from blank template');
    </script>
</body>
</html>"""
        
        # Save HTML file
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            print(f"✅ CLEAN BESPOKE FORM CREATED!")
            print(f"📁 File: {output_path}")
            print(f"📊 Size: {file_size:,} bytes")
            print(f"✨ Built from: {os.path.basename(analysis['template_path'])}")
            print(f"📄 {len(text_blocks)} clean text elements")
            print(f"📝 {len(field_indicators)} form fields")
            print(f"🌐 Windows: file:///C:/Users/ender/.claude/projects/offer-creator/{output_path}")
            
            return output_path
        else:
            print("❌ Failed to create clean form")
            return None

def main():
    """Create clean bespoke form from blank template"""
    creator = CleanBespokeCreator()
    
    print("✨ CLEAN BESPOKE FORM CREATOR")
    print("=" * 70)
    print("Building from BLANK template - no old data, no mess")
    print("✅ Uses blank CAR form template as starting point")
    print("✅ Extracts only clean structure and labels")
    print("✅ Creates native HTML form fields")
    print("✅ Picture-perfect layout without any old client data")
    print("=" * 70)
    
    result = creator.create_clean_html_form()
    
    if result:
        print(f"\n🎉 SUCCESS!")
        print(f"✅ Clean bespoke form created from blank template")
        print(f"✅ No old data, no mess - just clean form structure")
        print(f"✅ Ready for professional use")

if __name__ == "__main__":
    main()