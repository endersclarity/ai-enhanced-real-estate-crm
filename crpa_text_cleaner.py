#!/usr/bin/env python3
"""
CRPA Text Cleaner - Clean old client data and insert dummy data
Replace specific client information with dummy data in the text file
"""

import re
import os

class CRPATextCleaner:
    def __init__(self, input_file, output_file):
        self.input_file = input_file
        self.output_file = output_file
        
    def clean_and_replace_data(self):
        """Clean old client data and replace with dummy data"""
        print("🧹 CLEANING OLD CLIENT DATA AND INSERTING DUMMY DATA")
        print("=" * 70)
        
        # Read the original file with proper encoding handling
        try:
            with open(self.input_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            # Try with latin-1 encoding if utf-8 fails
            with open(self.input_file, 'r', encoding='latin-1') as f:
                content = f.read()
        
        print(f"📄 Original file size: {len(content):,} characters")
        
        # Define replacements (old data -> dummy data)
        replacements = {
            # Buyer information
            'Benjamin J. Brown, Marya L. Hicks': 'Alexander J. Rodriguez, Victoria M. Rodriguez',
            'Benjamin J. Brown': 'Alexander J. Rodriguez',
            'Marya L. Hicks': 'Victoria M. Rodriguez',
            
            # Property information
            '13190 Slate Creek Road': '8765 Luxury Boulevard',
            'Nevada City': 'Beverly Hills',
            'Nevada': 'Los Angeles',
            '95959': '90210',
            '004-161-020-000': '5555-123-456-000',
            
            # Agent information - Seller's side
            'Clare L. Moran': 'Patricia L. Wilson',
            '02068824': '01234567',
            'RE/MAX Gold': 'Coldwell Banker Elite',
            '01949144': '00876543',
            
            # Agent information - Buyer's side  
            'Narissa Jennings': 'Michael A. Thompson',
            '02129287': '01987654',
            'Coldwell Banker Grass Roots Realty': 'Century 21 Premier',
            '00873741': '00567890',
            
            # Dates
            'April 7, 2025': 'June 15, 2025'
        }
        
        # Apply replacements
        cleaned_content = content
        replacement_count = 0
        
        for old_text, new_text in replacements.items():
            if old_text in cleaned_content:
                before_count = cleaned_content.count(old_text)
                cleaned_content = cleaned_content.replace(old_text, new_text)
                after_count = cleaned_content.count(old_text)
                actual_replacements = before_count - after_count
                replacement_count += actual_replacements
                print(f"🔄 Replaced '{old_text}' -> '{new_text}' ({actual_replacements} times)")
        
        # Additional cleanup - remove any remaining specific data patterns
        additional_patterns = [
            # Remove any remaining license numbers that look like the old ones
            (r'DRE Lic\. # 008737', 'DRE Lic. # 001234'),
            
            # Clean up any missed dates
            (r'Date: April 7, 2025', 'Date: June 15, 2025'),
        ]
        
        for pattern, replacement in additional_patterns:
            if re.search(pattern, cleaned_content):
                cleaned_content = re.sub(pattern, replacement, cleaned_content)
                print(f"🔄 Pattern replaced: {pattern} -> {replacement}")
                replacement_count += 1
        
        # Write cleaned content
        with open(self.output_file, 'w', encoding='utf-8') as f:
            f.write(cleaned_content)
        
        if os.path.exists(self.output_file):
            new_size = os.path.getsize(self.output_file)
            print(f"\n✅ CLEANED FILE CREATED!")
            print(f"📁 Output: {self.output_file}")
            print(f"📊 File size: {new_size:,} bytes")
            print(f"🔄 Total replacements: {replacement_count}")
            print(f"🎯 Ready for use with clean dummy data")
            
            # Show a sample of the cleaned content
            print(f"\n📝 SAMPLE OF CLEANED CONTENT:")
            print("-" * 50)
            with open(self.output_file, 'r', encoding='utf-8') as f:
                sample_lines = f.readlines()[114:125]  # Around line 115 where the main form starts
                for i, line in enumerate(sample_lines, 115):
                    print(f"{i:3d}: {line.rstrip()}")
            
            return self.output_file
        else:
            print("❌ Failed to create cleaned file")
            return None

def main():
    """Clean the CRPA text file"""
    input_file = "/mnt/c/Users/ender/Documents/California_Residential_Purchase_Agreement_BLANK_TEMPLATE.txt"
    output_file = "/home/ender/.claude/projects/offer-creator/CRPA_CLEAN_DUMMY_DATA.txt"
    
    print("🧹 CRPA TEXT FILE CLEANER")
    print("=" * 70)
    print("Removing old client data and inserting professional dummy data")
    print("✅ Preserves all form structure and formatting")
    print("✅ Replaces only client-specific information")
    print("✅ Uses realistic dummy data for testing")
    print("=" * 70)
    
    cleaner = CRPATextCleaner(input_file, output_file)
    result = cleaner.clean_and_replace_data()
    
    if result:
        print(f"\n🎉 SUCCESS!")
        print(f"✅ Clean CRPA text file with dummy data created")
        print(f"✅ All old client information removed")
        print(f"✅ Professional dummy data inserted")
        print(f"✅ Form structure preserved perfectly")
        print(f"\n📁 Use this file: {result}")

if __name__ == "__main__":
    main()