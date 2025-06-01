#!/usr/bin/env python3
"""
MLS Data Integration for Real Estate CRM
Handles Nevada County MLS CSV data processing
"""

import pandas as pd
import os
from datetime import datetime
from typing import Dict, Optional, Any

# Global MLS data cache
_mls_data = None
_mls_last_loaded = None

def load_mls_data(csv_path: str) -> Dict[str, Any]:
    """
    Load Nevada County MLS data from CSV file.

    Args:
        csv_path (str): Path to MLS CSV file

    Returns:
        dict: {'success': bool, 'count': int, 'message': str, 'last_updated': str}
    """
    global _mls_data, _mls_last_loaded

    try:
        if not os.path.exists(csv_path):
            return {
                'success': False,
                'count': 0,
                'message': f'MLS file not found: {csv_path}',
                'last_updated': None
            }

        # Load CSV data with error handling for malformed lines
        df = pd.read_csv(csv_path, quotechar='"', skipinitialspace=True, on_bad_lines='skip')

        # Use "Listing Number" as the MLS identifier column
        mls_column = "Listing Number"

        if mls_column not in df.columns:
            return {
                'success': False,
                'count': 0,
                'message': f'Could not find "{mls_column}" column in CSV. Available columns: {list(df.columns)}',
                'last_updated': None
            }

        # Create lookup dictionary
        _mls_data = {}
        for _, row in df.iterrows():
            mls_num = str(row[mls_column]).strip()
            if mls_num and mls_num.lower() != 'nan':
                _mls_data[mls_num] = row.to_dict()

        _mls_last_loaded = datetime.now().isoformat()

        return {
            'success': True,
            'count': len(_mls_data),
            'message': f'Successfully loaded {len(_mls_data)} MLS listings',
            'last_updated': _mls_last_loaded
        }

    except Exception as e:
        return {
            'success': False,
            'count': 0,
            'message': f'Error loading MLS data: {str(e)}',
            'last_updated': None
        }

def find_mls_property(mls_number: str) -> Dict[str, Any]:
    """
    Find property by MLS number in loaded data.

    Args:
        mls_number (str): MLS listing number to search for

    Returns:
        dict: {'success': bool, 'property': dict, 'message': str}
    """
    global _mls_data

    if not _mls_data:
        return {
            'success': False,
            'property': None,
            'message': 'No MLS data loaded. Please load MLS CSV file first.'
        }

    mls_number = str(mls_number).strip()

    if mls_number in _mls_data:
        return {
            'success': True,
            'property': _mls_data[mls_number],
            'message': f'Found MLS #{mls_number}'
        }
    else:
        return {
            'success': False,
            'property': None,
            'message': f'MLS #{mls_number} not found in loaded data'
        }

def create_property_from_mls(mls_number: str) -> Dict[str, Any]:
    """
    Auto-create property record from MLS data.

    Args:
        mls_number (str): MLS number to create property from

    Returns:
        dict: {'success': bool, 'property_id': int, 'message': str, 'mls_data': dict}
    """
    # First find the MLS property
    mls_result = find_mls_property(mls_number)

    if not mls_result['success']:
        return {
            'success': False,
            'property_id': None,
            'message': mls_result['message'],
            'mls_data': None
        }

    mls_data = mls_result['property']

    try:
        # Import our CRM functions
        from real_estate_crm import create_property

        # Map Nevada County MLS data to our property fields (exact column names)
        property_data = {
            'address_line1': mls_data.get('Address - Street Complete', ''),
            'city': mls_data.get('Address - City', ''),
            'state': 'CA',  # Nevada County is in California
            'zip_code': str(mls_data.get('Address - Zip Code', '')),
            'mls_number': mls_number,
            'listing_price': _safe_float(mls_data.get('Current Listing Price', 0)),
            'bedrooms': _extract_bedrooms(mls_data.get('Bedrooms And Possible Bedrooms', '')),
            'bathrooms': _calculate_total_bathrooms(
                mls_data.get('Full Bathrooms', 0),
                mls_data.get('Partial Bathrooms', 0)
            ),
            'square_feet': _safe_int(mls_data.get('Square Footage', 0)),
            'lot_size': _safe_float(mls_data.get('Lot Size - Acres', 0)),
            'year_built': _safe_int(mls_data.get('Year Built Details', 0)),
            'property_type': _normalize_property_type(mls_data.get('Property Type', 'Residential')),
            'listing_type': 'sale',
            'property_description': mls_data.get('Public Remarks', ''),
            'public_remarks': mls_data.get('Public Remarks', ''),
            'private_remarks': f'''Auto-imported from Nevada County MLS #{mls_number} on {datetime.now().strftime("%Y-%m-%d")}

Additional MLS Details:
- Architectural Style: {mls_data.get('Architectural Style', 'N/A')}
- Heating: {mls_data.get('Heating', 'N/A')}
- Cooling: {mls_data.get('Cooling', 'N/A')}
- Fireplace Features: {mls_data.get('Fireplace Features', 'N/A')}
- Garage Spaces: {mls_data.get('Garage Spaces', 'N/A')}
- Parking Features: {mls_data.get('Parking Features', 'N/A')}
- Pool: {mls_data.get('Pool', 'N/A')}
- Subdivision: {mls_data.get('Subdivision', 'N/A')}
- DOM (Days on Market): {mls_data.get('DOM', 'N/A')}
- Original Price: {mls_data.get('Original Price', 'N/A')}
- Listing Date: {mls_data.get('Listing Date', 'N/A')}
- Status: {mls_data.get('Status', 'N/A')}'''
        }

        # Create property using our existing function
        result = create_property(**property_data)

        if result['success']:
            return {
                'success': True,
                'property_id': result['property_id'],
                'message': f'Successfully created property from MLS #{mls_number}',
                'mls_data': mls_data
            }
        else:
            return {
                'success': False,
                'property_id': None,
                'message': f'Failed to create property: {result["message"]}',
                'mls_data': mls_data
            }

    except Exception as e:
        return {
            'success': False,
            'property_id': None,
            'message': f'Error creating property from MLS data: {str(e)}',
            'mls_data': mls_data
        }

def get_mls_status() -> Dict[str, Any]:
    """
    Get current MLS data status.

    Returns:
        dict: Status information about loaded MLS data
    """
    global _mls_data, _mls_last_loaded

    return {
        'loaded': _mls_data is not None,
        'count': len(_mls_data) if _mls_data else 0,
        'last_updated': _mls_last_loaded,
        'sample_mls_numbers': list(_mls_data.keys())[:5] if _mls_data else []
    }

def _safe_float(value) -> Optional[float]:
    """Safely convert value to float"""
    try:
        if value is None or value == '':
            return None
        return float(str(value).replace(',', '').replace('$', ''))
    except:
        return None

def _safe_int(value) -> Optional[int]:
    """Safely convert value to int"""
    try:
        if value is None or value == '':
            return None
        return int(float(str(value).replace(',', '')))
    except:
        return None

def _extract_bedrooms(bedroom_string: str) -> Optional[float]:
    """Extract bedroom count from Nevada County format like '4 (5)' """
    try:
        if not bedroom_string:
            return None
        # Extract first number from string like "4 (5)"
        import re
        match = re.search(r'(\d+)', str(bedroom_string))
        return float(match.group(1)) if match else None
    except:
        return None

def _calculate_total_bathrooms(full_baths, partial_baths) -> Optional[float]:
    """Calculate total bathrooms from full and partial"""
    try:
        full = _safe_float(full_baths) or 0
        partial = _safe_float(partial_baths) or 0
        total = full + (partial * 0.5)  # Partial baths count as 0.5
        return total if total > 0 else None
    except:
        return None

def _normalize_property_type(prop_type: str) -> str:
    """Convert Nevada County property type to our standard format"""
    if not prop_type:
        return 'single_family'

    prop_type_lower = str(prop_type).lower()

    if 'residential' in prop_type_lower or 'single' in prop_type_lower:
        return 'single_family'
    elif 'condo' in prop_type_lower:
        return 'condo'
    elif 'town' in prop_type_lower:
        return 'townhouse'
    elif 'land' in prop_type_lower or 'lot' in prop_type_lower:
        return 'land'
    else:
        return 'single_family'  # Default fallback

# MLS functions registry for AI discovery
MLS_FUNCTIONS = {
    'load_mls_data': {
        'function': load_mls_data,
        'description': 'Load Nevada County MLS data from CSV file',
        'required_params': ['csv_path'],
        'optional_params': [],
        'example': 'load_mls_data("/path/to/nevada_county_listings.csv")'
    },
    'find_mls_property': {
        'function': find_mls_property,
        'description': 'Find property details by MLS number',
        'required_params': ['mls_number'],
        'optional_params': [],
        'example': 'find_mls_property("12345")'
    },
    'create_property_from_mls': {
        'function': create_property_from_mls,
        'description': 'Auto-create property record from MLS data',
        'required_params': ['mls_number'],
        'optional_params': [],
        'example': 'create_property_from_mls("12345")'
    },
    'get_mls_status': {
        'function': get_mls_status,
        'description': 'Check status of loaded MLS data',
        'required_params': [],
        'optional_params': [],
        'example': 'get_mls_status()'
    }
}

if __name__ == "__main__":
    # Test with sample data structure
    print("🏠 MLS Integration System Ready")
    print("=" * 50)
    print("Available functions:")
    for func_name, info in MLS_FUNCTIONS.items():
        print(f"  {func_name}: {info['description']}")

    status = get_mls_status()
    print(f"\nCurrent status: {status}")
