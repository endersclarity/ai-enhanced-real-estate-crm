# PDF Password Removal Tasks
*Quick tactical plan to remove PDF passwords and extract field IDs*

## Objective
Remove password protection from sister's official PDF forms to enable field ID extraction for template mapping and CRM data population.

## Tasks

### 1. Try Online PDF Password Removers (15 minutes)
- **Tools to try**: SmallPDF, iLovePDF, PDF24, Sejda
- **Method**: Upload 2-3 sample PDFs to test effectiveness
- **Success criteria**: Get back unprotected PDFs that open in Adobe Acrobat Pro for editing
- **Risk**: File upload security (use non-sensitive test files first)

### 2. Use Python PDF Password Removal (30 minutes)
- **Method**: Extract PDFs with empty password using PyPDF2/pypdf, then save as new unprotected files
- **Script**: Create `remove_pdf_passwords.py` to batch process all attachments.zip files
- **Success criteria**: Generate clean PDFs that Adobe can edit
- **Advantage**: No file uploads, local processing

### 3. Try Alternative PDF Editors (20 minutes)
- **Tools**: PDFtk, QPDF command line tools, LibreOffice Draw
- **Method**: Open password-protected PDFs and save as new files
- **Success criteria**: Get editable versions without password protection
- **Fallback**: If Adobe still won't work

### 4. Extract Field IDs Programmatically (45 minutes)
- **Method**: Use PyPDF2 to read form fields directly from protected PDFs
- **Script**: Create `extract_field_ids.py` to scan all form fields and generate mapping JSON
- **Success criteria**: Complete field mapping without needing Adobe editing
- **Advantage**: Bypass Adobe entirely, get what we actually need

### 5. Test Field Mapping with CRM Data (30 minutes)
- **Method**: Use extracted field IDs to populate test data into PDFs
- **Validation**: Generate test PDFs with real estate data to verify field mapping accuracy
- **Success criteria**: Working PDF population from CRM data structure

## Priority Order
1. **Try #4 first** - Extract field IDs programmatically (may not need password removal at all)
2. **Try #2** - Python password removal if #4 fails
3. **Try #1** - Online tools as backup
4. **Try #3** - Alternative editors as last resort

## Expected Outcome
Complete field ID mapping that enables CRM → PDF population without needing to edit the original forms in Adobe Acrobat Pro.

## Time Investment
Total: ~2.5 hours maximum to solve the field mapping problem completely.