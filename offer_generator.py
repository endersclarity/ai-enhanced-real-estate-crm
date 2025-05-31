#!/usr/bin/env python3
import json
import os
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
import pdfplumber

class OfferGenerator:
    def __init__(self):
        self.load_form_mapping()
        self.output_dir = "output"
        os.makedirs(self.output_dir, exist_ok=True)
        
    def load_form_mapping(self):
        """Load form data mapping from JSON file"""
        try:
            with open('form_data_mapping.json', 'r') as f:
                self.mapping = json.load(f)
        except FileNotFoundError:
            self.mapping = {"common_fields": {}, "form_mappings": {}}
    
    def generate_offer_package(self, client_data):
        """Generate complete offer package with all required forms"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        package_name = f"offer_package_{timestamp}"
        
        generated_files = []
        
        # Generate each form based on priority
        form_priorities = sorted(
            self.mapping["form_mappings"].items(), 
            key=lambda x: x[1].get("priority", 999)
        )
        
        for form_name, form_config in form_priorities:
            try:
                output_file = self.generate_form(form_name, client_data, package_name)
                if output_file:
                    generated_files.append(output_file)
            except Exception as e:
                print(f"Error generating {form_name}: {e}")
                
        return generated_files
    
    def generate_form(self, form_name, client_data, package_name):
        """Generate individual form with client data"""
        output_filename = f"{package_name}_{form_name}.pdf"
        output_path = os.path.join(self.output_dir, output_filename)
        
        # For now, create a simple document with client data
        # In a full implementation, this would overlay text on the original forms
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Add title
        title = Paragraph(f"<b>{form_name.replace('_', ' ')}</b>", styles['Title'])
        story.append(title)
        story.append(Spacer(1, 20))
        
        # Add client data
        story.append(Paragraph("<b>Property Information:</b>", styles['Heading2']))
        property_data = client_data.get('property', {})
        for key, value in property_data.items():
            if value:
                story.append(Paragraph(f"{key.replace('_', ' ').title()}: {value}", styles['Normal']))
        
        story.append(Spacer(1, 12))
        story.append(Paragraph("<b>Buyer Information:</b>", styles['Heading2']))
        buyer_data = client_data.get('buyer', {})
        for key, value in buyer_data.items():
            if value:
                story.append(Paragraph(f"{key.replace('_', ' ').title()}: {value}", styles['Normal']))
        
        doc.build(story)
        return output_filename