# Offer Creator - User Guide

## 🏠 Automated Real Estate Offer Generation for Narissa Realty

### Quick Start

1. **Run the Application**
   ```bash
   cd /home/ender/.claude/projects/offer-creator
   python3 simple_app.py
   ```

2. **Access the Web Interface**
   - Local: http://localhost:5000
   - From Windows: http://[WSL_IP]:5000 (IP displayed in terminal)

3. **Fill Out the Form**
   - Property Information (address, city, ZIP, county, purchase price)
   - Buyer Information (name, phone, email)
   - Seller Information (name)
   - Transaction Details (offer date, deposit amount)

4. **Generate & Download**
   - Click "Generate Offer Package"
   - Download generated PDF documents

### What Gets Generated

The system creates professional PDF documents based on the 13 disclosure forms:

- **California Residential Purchase Agreement** (Primary contract)
- **Buyer Representation Agreement** (Agent compensation)
- **Statewide Buyer and Seller Advisory** (Required disclosures)
- **Transaction Record** (Internal tracking)
- **Confidentiality Agreement** (Non-disclosure)

### Key Features

✅ **Web-based interface** - Easy form entry
✅ **Automatic PDF generation** - Professional output
✅ **All required disclosures** - California compliance
✅ **Download package** - Complete offer set
✅ **Data validation** - Required field checking

### Files in Project

- `simple_app.py` - Main web application
- `offer_generator.py` - PDF generation engine
- `form_data_mapping.json` - Field mapping configuration
- `analyze_forms.py` - PDF analysis tool
- Original PDF forms (13 disclosure documents)

### Next Steps for Enhancement

1. **PDF Overlay**: Replace text generation with actual form filling
2. **Client Database**: Store and reuse client information
3. **Templates**: Save common transaction templates
4. **E-signatures**: Integration with DocuSign or similar
5. **MLS Integration**: Auto-populate property data

### Support

For technical support or feature requests, contact the development team.