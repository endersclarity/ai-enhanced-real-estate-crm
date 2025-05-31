#!/usr/bin/env python3
"""
Data Migration Tools for Narissa Realty CRM
Implements CSV import/export, database migration scripts, data validation and cleaning
"""

import os
import csv
import json
import sqlite3
import pandas as pd
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataMigrationTools:
    """Comprehensive data migration and transformation tools"""
    
    def __init__(self, db_path="real_estate_crm.db"):
        self.db_path = db_path
        self.validation_rules = self._load_validation_rules()
        self.field_mappings = self._load_field_mappings()
    
    def _load_validation_rules(self) -> Dict:
        """Load data validation rules"""
        return {
            'users': {
                'username': {'required': True, 'type': 'string', 'max_length': 50},
                'email': {'required': True, 'type': 'email', 'unique': True},
                'role': {'required': True, 'choices': ['admin', 'manager', 'agent']},
                'phone': {'type': 'phone', 'format': r'^\d{3}-\d{3}-\d{4}$'}
            },
            'clients': {
                'name': {'required': True, 'type': 'string', 'max_length': 100},
                'email': {'type': 'email'},
                'phone': {'type': 'phone'},
                'budget_max': {'type': 'decimal', 'min_value': 0},
                'agent_id': {'required': True, 'type': 'foreign_key', 'references': 'users.id'}
            },
            'properties': {
                'address': {'required': True, 'type': 'string'},
                'price': {'required': True, 'type': 'decimal', 'min_value': 0},
                'bedrooms': {'type': 'integer', 'min_value': 0, 'max_value': 20},
                'bathrooms': {'type': 'decimal', 'min_value': 0, 'max_value': 20},
                'square_feet': {'type': 'integer', 'min_value': 0}
            }
        }
    
    def _load_field_mappings(self) -> Dict:
        """Load field mapping configurations for different import formats"""
        return {
            'zipform_clients': {
                'Client Name': 'name',
                'Client Email': 'email',
                'Client Phone': 'phone',
                'Max Budget': 'budget_max',
                'Agent': 'agent_id',
                'Notes': 'notes'
            },
            'mls_properties': {
                'Property Address': 'address',
                'List Price': 'price',
                'Bedrooms': 'bedrooms',
                'Bathrooms': 'bathrooms',
                'Square Footage': 'square_feet',
                'Property Type': 'property_type',
                'MLS Number': 'mls_number'
            },
            'legacy_users': {
                'User Name': 'username',
                'Email Address': 'email',
                'Full Name': 'display_name',
                'Role': 'role',
                'Phone Number': 'phone'
            }
        }
    
    def import_csv_data(self, csv_file_path: str, table_name: str, 
                       mapping_type: str = None, validate: bool = True) -> Dict:
        """Import data from CSV file"""
        logger.info(f"Starting CSV import: {csv_file_path} -> {table_name}")
        
        results = {
            'success': False,
            'total_rows': 0,
            'imported_rows': 0,
            'failed_rows': 0,
            'errors': [],
            'warnings': []
        }
        
        try:
            # Read CSV file
            df = pd.read_csv(csv_file_path)
            results['total_rows'] = len(df)
            
            # Apply field mapping if specified
            if mapping_type and mapping_type in self.field_mappings:
                df = self._apply_field_mapping(df, self.field_mappings[mapping_type])
            
            # Validate data if enabled
            if validate:
                validation_results = self._validate_dataframe(df, table_name)
                results['warnings'].extend(validation_results['warnings'])
                if validation_results['errors']:
                    results['errors'].extend(validation_results['errors'])
                    return results
            
            # Clean and transform data
            df_cleaned = self._clean_dataframe(df, table_name)
            
            # Import to database
            import_results = self._import_dataframe_to_db(df_cleaned, table_name)
            results.update(import_results)
            
            results['success'] = True
            logger.info(f"CSV import completed: {results['imported_rows']}/{results['total_rows']} rows imported")
            
        except Exception as e:
            results['errors'].append(f"Import failed: {str(e)}")
            logger.error(f"CSV import failed: {e}")
        
        return results
    
    def export_csv_data(self, table_name: str, output_path: str, 
                       filters: Dict = None, columns: List[str] = None) -> Dict:
        """Export data to CSV file"""
        logger.info(f"Starting CSV export: {table_name} -> {output_path}")
        
        results = {
            'success': False,
            'exported_rows': 0,
            'file_size_mb': 0,
            'errors': []
        }
        
        try:
            # Build query
            if columns:
                column_str = ', '.join(columns)
            else:
                column_str = '*'
            
            query = f"SELECT {column_str} FROM {table_name}"
            params = []
            
            # Apply filters
            if filters:
                where_conditions = []
                for column, value in filters.items():
                    where_conditions.append(f"{column} = ?")
                    params.append(value)
                
                if where_conditions:
                    query += " WHERE " + " AND ".join(where_conditions)
            
            # Execute query and export
            with sqlite3.connect(self.db_path) as conn:
                df = pd.read_sql_query(query, conn, params=params)
            
            # Export to CSV
            df.to_csv(output_path, index=False)
            
            # Get file statistics
            file_size = Path(output_path).stat().st_size
            
            results.update({
                'success': True,
                'exported_rows': len(df),
                'file_size_mb': file_size / (1024 * 1024),
                'columns_exported': list(df.columns)
            })
            
            logger.info(f"CSV export completed: {len(df)} rows exported to {output_path}")
            
        except Exception as e:
            results['errors'].append(f"Export failed: {str(e)}")
            logger.error(f"CSV export failed: {e}")
        
        return results
    
    def bulk_import_operation(self, import_config: Dict) -> Dict:
        """Perform bulk import operation with multiple files"""
        logger.info("Starting bulk import operation")
        
        results = {
            'success': False,
            'imports': {},
            'total_imported': 0,
            'total_failed': 0,
            'errors': []
        }
        
        try:
            for import_name, config in import_config.items():
                logger.info(f"Processing import: {import_name}")
                
                import_result = self.import_csv_data(
                    csv_file_path=config['file_path'],
                    table_name=config['table'],
                    mapping_type=config.get('mapping_type'),
                    validate=config.get('validate', True)
                )
                
                results['imports'][import_name] = import_result
                results['total_imported'] += import_result['imported_rows']
                results['total_failed'] += import_result['failed_rows']
                
                if import_result['errors']:
                    results['errors'].extend([f"{import_name}: {error}" for error in import_result['errors']])
            
            results['success'] = len(results['errors']) == 0
            logger.info(f"Bulk import completed: {results['total_imported']} total rows imported")
            
        except Exception as e:
            results['errors'].append(f"Bulk import failed: {str(e)}")
            logger.error(f"Bulk import failed: {e}")
        
        return results
    
    def validate_data_integrity(self, table_name: str = None) -> Dict:
        """Validate data integrity across tables"""
        logger.info("Starting data integrity validation")
        
        validation_results = {
            'success': True,
            'issues': [],
            'statistics': {}
        }
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get list of tables to validate
            if table_name:
                tables = [table_name]
            else:
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
            
            for table in tables:
                if table.startswith('sqlite_'):
                    continue
                
                logger.info(f"Validating table: {table}")
                table_issues = []
                
                # Check for duplicate records
                duplicates = self._check_duplicates(cursor, table)
                if duplicates:
                    table_issues.extend(duplicates)
                
                # Check foreign key constraints
                fk_issues = self._check_foreign_keys(cursor, table)
                if fk_issues:
                    table_issues.extend(fk_issues)
                
                # Check data format compliance
                format_issues = self._check_data_formats(cursor, table)
                if format_issues:
                    table_issues.extend(format_issues)
                
                # Get table statistics
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                row_count = cursor.fetchone()[0]
                
                validation_results['statistics'][table] = {
                    'total_rows': row_count,
                    'issues_found': len(table_issues)
                }
                
                if table_issues:
                    validation_results['issues'].extend([f"{table}: {issue}" for issue in table_issues])
                    validation_results['success'] = False
        
        logger.info(f"Data integrity validation completed: {len(validation_results['issues'])} issues found")
        return validation_results
    
    def clean_and_standardize_data(self, table_name: str, rules: Dict = None) -> Dict:
        """Clean and standardize data in specified table"""
        logger.info(f"Starting data cleaning for table: {table_name}")
        
        results = {
            'success': False,
            'rows_processed': 0,
            'changes_made': 0,
            'errors': []
        }
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get all data from table
                cursor.execute(f"SELECT * FROM {table_name}")
                rows = cursor.fetchall()
                
                # Get column names
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = [col[1] for col in cursor.fetchall()]
                
                # Convert to DataFrame for easier manipulation
                df = pd.DataFrame(rows, columns=columns)
                results['rows_processed'] = len(df)
                
                # Apply cleaning rules
                original_df = df.copy()
                
                if table_name == 'users':
                    df = self._clean_user_data(df)
                elif table_name == 'clients':
                    df = self._clean_client_data(df)
                elif table_name == 'properties':
                    df = self._clean_property_data(df)
                
                # Apply custom rules if provided
                if rules:
                    df = self._apply_custom_cleaning_rules(df, rules)
                
                # Count changes
                changes = 0
                for col in df.columns:
                    if col in original_df.columns:
                        changes += (df[col] != original_df[col]).sum()
                
                results['changes_made'] = changes
                
                # Update database if changes were made
                if changes > 0:
                    # Clear table and re-insert cleaned data
                    cursor.execute(f"DELETE FROM {table_name}")
                    
                    # Insert cleaned data
                    placeholders = ', '.join(['?' for _ in columns])
                    for _, row in df.iterrows():
                        cursor.execute(f"INSERT INTO {table_name} VALUES ({placeholders})", row.tolist())
                    
                    conn.commit()
                
                results['success'] = True
                logger.info(f"Data cleaning completed: {changes} changes made to {len(df)} rows")
                
        except Exception as e:
            results['errors'].append(f"Data cleaning failed: {str(e)}")
            logger.error(f"Data cleaning failed: {e}")
        
        return results
    
    def migrate_database_schema(self, migration_scripts: List[str]) -> Dict:
        """Execute database schema migration scripts"""
        logger.info("Starting database schema migration")
        
        results = {
            'success': False,
            'migrations_applied': 0,
            'errors': []
        }
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create migration tracking table if it doesn't exist
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS schema_migrations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        migration_name TEXT UNIQUE NOT NULL,
                        applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                for script_path in migration_scripts:
                    script_name = Path(script_path).name
                    
                    # Check if migration already applied
                    cursor.execute('SELECT id FROM schema_migrations WHERE migration_name = ?', (script_name,))
                    if cursor.fetchone():
                        logger.info(f"Migration already applied: {script_name}")
                        continue
                    
                    # Read and execute migration script
                    with open(script_path, 'r') as f:
                        migration_sql = f.read()
                    
                    # Execute migration (can contain multiple statements)
                    cursor.executescript(migration_sql)
                    
                    # Record migration
                    cursor.execute('INSERT INTO schema_migrations (migration_name) VALUES (?)', (script_name,))
                    
                    results['migrations_applied'] += 1
                    logger.info(f"Migration applied: {script_name}")
                
                conn.commit()
                results['success'] = True
                
        except Exception as e:
            results['errors'].append(f"Schema migration failed: {str(e)}")
            logger.error(f"Schema migration failed: {e}")
        
        return results
    
    # Helper methods for data validation and cleaning
    def _apply_field_mapping(self, df: pd.DataFrame, mapping: Dict) -> pd.DataFrame:
        """Apply field mapping to DataFrame"""
        return df.rename(columns=mapping)
    
    def _validate_dataframe(self, df: pd.DataFrame, table_name: str) -> Dict:
        """Validate DataFrame against table rules"""
        validation_results = {'errors': [], 'warnings': []}
        
        if table_name not in self.validation_rules:
            return validation_results
        
        rules = self.validation_rules[table_name]
        
        for column, rule in rules.items():
            if column not in df.columns:
                if rule.get('required'):
                    validation_results['errors'].append(f"Required column missing: {column}")
                continue
            
            # Check required fields
            if rule.get('required') and df[column].isnull().any():
                validation_results['errors'].append(f"Required field {column} has null values")
            
            # Check data types and formats
            if rule.get('type') == 'email':
                invalid_emails = df[df[column].notna() & ~df[column].str.match(r'^[^@]+@[^@]+\.[^@]+$')]
                if not invalid_emails.empty:
                    validation_results['warnings'].append(f"Invalid email formats found in {column}")
            
            if rule.get('type') == 'phone' and rule.get('format'):
                pattern = rule['format']
                invalid_phones = df[df[column].notna() & ~df[column].str.match(pattern)]
                if not invalid_phones.empty:
                    validation_results['warnings'].append(f"Invalid phone formats found in {column}")
        
        return validation_results
    
    def _clean_dataframe(self, df: pd.DataFrame, table_name: str) -> pd.DataFrame:
        """Clean and standardize DataFrame data"""
        # Remove leading/trailing whitespace
        for col in df.select_dtypes(include=['object']).columns:
            df[col] = df[col].astype(str).str.strip()
        
        # Convert empty strings to None
        df = df.replace('', None)
        
        # Table-specific cleaning
        if table_name == 'users':
            df = self._clean_user_data(df)
        elif table_name == 'clients':
            df = self._clean_client_data(df)
        elif table_name == 'properties':
            df = self._clean_property_data(df)
        
        return df
    
    def _clean_user_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean user-specific data"""
        if 'email' in df.columns:
            df['email'] = df['email'].str.lower()
        
        if 'username' in df.columns:
            df['username'] = df['username'].str.lower()
        
        if 'phone' in df.columns:
            # Standardize phone numbers to XXX-XXX-XXXX format
            df['phone'] = df['phone'].str.replace(r'[^\d]', '', regex=True)
            df['phone'] = df['phone'].str.replace(r'(\d{3})(\d{3})(\d{4})', r'\1-\2-\3', regex=True)
        
        return df
    
    def _clean_client_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean client-specific data"""
        if 'name' in df.columns:
            df['name'] = df['name'].str.title()
        
        if 'email' in df.columns:
            df['email'] = df['email'].str.lower()
        
        if 'budget_max' in df.columns:
            # Remove currency symbols and convert to float
            df['budget_max'] = df['budget_max'].astype(str).str.replace(r'[$,]', '', regex=True)
            df['budget_max'] = pd.to_numeric(df['budget_max'], errors='coerce')
        
        return df
    
    def _clean_property_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean property-specific data"""
        if 'price' in df.columns:
            # Clean price data
            df['price'] = df['price'].astype(str).str.replace(r'[$,]', '', regex=True)
            df['price'] = pd.to_numeric(df['price'], errors='coerce')
        
        if 'address' in df.columns:
            df['address'] = df['address'].str.title()
        
        if 'square_feet' in df.columns:
            df['square_feet'] = pd.to_numeric(df['square_feet'], errors='coerce')
        
        return df

def create_sample_migration_data():
    """Create sample data files for testing migration tools"""
    
    # Create sample users CSV
    users_data = [
        ['john_doe', 'john@example.com', 'John Doe', 'agent', '555-123-4567'],
        ['jane_smith', 'jane@example.com', 'Jane Smith', 'manager', '555-234-5678'],
        ['bob_wilson', 'bob@example.com', 'Bob Wilson', 'agent', '555-345-6789']
    ]
    
    with open('sample_users.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['username', 'email', 'display_name', 'role', 'phone'])
        writer.writerows(users_data)
    
    # Create sample clients CSV
    clients_data = [
        ['John Client', 'client1@example.com', '555-111-2222', 500000, 'Looking for family home'],
        ['Jane Buyer', 'client2@example.com', '555-222-3333', 750000, 'First time buyer'],
        ['Bob Customer', 'client3@example.com', '555-333-4444', 300000, 'Investment property']
    ]
    
    with open('sample_clients.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['name', 'email', 'phone', 'budget_max', 'notes'])
        writer.writerows(clients_data)
    
    print("Sample migration data files created:")
    print("- sample_users.csv")
    print("- sample_clients.csv")

def main():
    """Test the data migration tools"""
    migration_tools = DataMigrationTools()
    
    print("Data Migration Tools Test")
    print("=" * 40)
    
    # Create sample data
    create_sample_migration_data()
    
    # Test CSV import
    print("1. Testing CSV import...")
    import_result = migration_tools.import_csv_data(
        csv_file_path='sample_users.csv',
        table_name='users',
        validate=True
    )
    print(f"Import result: {import_result}")
    
    # Test data validation
    print("\n2. Testing data integrity validation...")
    validation_result = migration_tools.validate_data_integrity('users')
    print(f"Validation result: {validation_result}")
    
    # Test CSV export
    print("\n3. Testing CSV export...")
    export_result = migration_tools.export_csv_data(
        table_name='users',
        output_path='exported_users.csv'
    )
    print(f"Export result: {export_result}")
    
    print("\nData migration tools test completed!")

if __name__ == "__main__":
    main()