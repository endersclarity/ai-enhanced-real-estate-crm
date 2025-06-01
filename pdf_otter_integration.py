#!/usr/bin/env python3
"""
PDF Otter Integration - Professional form field detection
Uses PDF Otter's API for accurate coordinate mapping
"""

import requests
import os
import json

class PDFOtterIntegration:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://www.pdfotter.com/api/v1"
        
    def create_template(self, pdf_path, template_name="CRPA_Form"):
        """Upload PDF to PDF Otter and create template"""
        print(f"📤 Uploading {pdf_path} to PDF Otter...")
        
        url = f"{self.base_url}/pdf_templates"
        
        with open(pdf_path, 'rb') as f:
            files = {'file': f}
            data = {'name': template_name}
            
            response = requests.post(
                url,
                auth=(self.api_key, ''),
                files=files,
                data=data
            )
        
        if response.status_code == 200:
            template = response.json()
            print(f"✅ Template created: {template['id']}")
            return template
        else:
            print(f"❌ Upload failed: {response.text}")
            return None
    
    def check_template_status(self, template_id):
        """Check if template processing is complete"""
        url = f"{self.base_url}/pdf_templates/{template_id}"
        
        response = requests.get(url, auth=(self.api_key, ''))
        
        if response.status_code == 200:
            template = response.json()
            return template
        else:
            print(f"❌ Status check failed: {response.text}")
            return None
    
    def fill_template(self, template_id, data):
        """Fill template with data and get PDF"""
        url = f"{self.base_url}/pdf_templates/{template_id}/fill"
        
        response = requests.post(
            url,
            auth=(self.api_key, ''),
            data=data
        )
        
        if response.status_code == 200:
            return response.content  # PDF bytes
        else:
            print(f"❌ Fill failed: {response.text}")
            return None

def setup_pdf_otter():
    """Guide user through PDF Otter setup"""
    print("🦦 PDF OTTER SETUP")
    print("=" * 50)
    print("1. Go to https://www.pdfotter.com/")
    print("2. Sign up for free account")
    print("3. Get your API key from dashboard")
    print("4. Upload your CRPA form using their visual editor")
    print("5. Map fields using their point-and-click interface")
    print("6. Use the template ID for automated filling")
    print()
    print("💰 Cost: $0.01 per PDF (extremely affordable)")
    print("🎯 Benefit: Professional accuracy, zero manual coordinate mapping")
    print()
    
    api_key = input("Enter your PDF Otter API key (or 'skip' to continue): ")
    
    if api_key.lower() == 'skip':
        print("⏭️ Skipping PDF Otter setup")
        return None
    
    return api_key

def main():
    """Demo PDF Otter integration"""
    print("🦦 PDF OTTER INTEGRATION")
    print("=" * 60)
    print("Professional form field detection with visual template editor")
    print("✅ Point-and-click field mapping")
    print("✅ Accurate coordinate detection")
    print("✅ API integration for automated filling")
    print("✅ Only $0.01 per PDF")
    print("=" * 60)
    
    api_key = setup_pdf_otter()
    
    if api_key:
        pdf_otter = PDFOtterIntegration(api_key)
        
        # Example usage
        pdf_path = "documents/California_Residential_Purchase_Agreement_CLEAN_TEMPLATE.pdf"
        
        if os.path.exists(pdf_path):
            template = pdf_otter.create_template(pdf_path)
            
            if template:
                print(f"✅ Template ID: {template['id']}")
                print("📝 Now use PDF Otter's dashboard to map fields visually")
                print("🔗 https://www.pdfotter.com/dashboard")
        else:
            print(f"❌ PDF file not found: {pdf_path}")
    else:
        print("\n🤷 No API key provided.")
        print("📋 Alternative: Use PDF Otter's web interface manually")
        print("🔗 https://www.pdfotter.com/")
        print("💡 Upload your CRPA form and use their visual editor")

if __name__ == "__main__":
    main()