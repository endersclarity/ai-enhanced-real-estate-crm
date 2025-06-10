#!/usr/bin/env python3
"""
CrmDataMapper Service - Enterprise-grade CRM to Form Data Integration

Based on Google AI Studio's architectural recommendations, this service:
1. Decouples form generation from CRM complexity
2. Implements optimized database queries with connection pooling
3. Handles sophisticated field transformations and mapping
4. Provides clean 33-field output ready for form generation

Architecture: CRM Database → CrmDataMapper → Clean Dict → ProfessionalFormFiller
"""

import json
import logging
import os
from decimal import Decimal
from datetime import datetime, date
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import sqlite3
from contextlib import contextmanager

# Database connection pooling (will be enhanced with SQLAlchemy in production)
import threading
import queue

@dataclass
class TransformRule:
    """Represents a field transformation rule from enhanced mapping configuration"""
    method: str
    sources: List[str] = None
    source: str = None
    separator: str = " "
    template_string: str = None
    symbol: str = "$"
    format_type: str = None

class CrmDataMapper:
    """
    Enterprise-grade service for mapping 177 CRM fields to 33 form fields
    
    Features:
    - Database connection pooling for performance
    - Sophisticated field transformations (concatenate, format_currency, template)
    - Optimized database view queries
    - Error handling for missing/invalid data
    - UTF-8 encoding support for international names
    """
    
    def __init__(self, database_path: str = "real_estate.db", pool_size: int = 5):
        self.database_path = database_path
        self.pool_size = pool_size
        self.connection_pool = queue.Queue(maxsize=pool_size)
        self.pool_lock = threading.Lock()
        self.logger = logging.getLogger(__name__)
        
        # Initialize connection pool
        self._initialize_connection_pool()
        
        # Load field mapping configuration
        self.field_mappings = self._load_field_mappings()
        
        # Ensure database view exists
        self._ensure_database_view()
    
    def _initialize_connection_pool(self):
        """Initialize database connection pool for performance"""
        try:
            for _ in range(self.pool_size):
                conn = sqlite3.connect(
                    self.database_path,
                    check_same_thread=False,
                    isolation_level=None  # Autocommit mode for read operations
                )
                conn.row_factory = sqlite3.Row  # Enable dict-like access
                self.connection_pool.put(conn)
            self.logger.info(f"Initialized connection pool with {self.pool_size} connections")
        except Exception as e:
            self.logger.error(f"Failed to initialize connection pool: {e}")
            raise
    
    @contextmanager
    def _get_connection(self):
        """Context manager for connection pool management"""
        conn = None
        try:
            conn = self.connection_pool.get(timeout=5)
            yield conn
        except queue.Empty:
            self.logger.error("Connection pool exhausted")
            raise Exception("Database connection pool exhausted")
        finally:
            if conn:
                self.connection_pool.put(conn)
    
    def _load_field_mappings(self) -> Dict[str, Any]:
        """Load enhanced field mapping configuration with transformation rules"""
        try:
            # Try enhanced mapping first
            enhanced_path = "form_templates/enhanced_crpa_mapping.json"
            if os.path.exists(enhanced_path):
                with open(enhanced_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.logger.info("Loaded enhanced field mapping configuration")
                    return config.get('field_mappings', {})
            
            # Fallback to original mapping
            mapping_path = "form_templates/california_residential_purchase_agreement_template.json"
            if not os.path.exists(mapping_path):
                # Fallback to current directory
                mapping_path = "california_residential_purchase_agreement_template.json"
            
            with open(mapping_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                self.logger.info("Loaded basic field mapping configuration")
                return config.get('field_mappings', {})
        except Exception as e:
            self.logger.error(f"Failed to load field mappings: {e}")
            # Return basic mappings as fallback
            return self._get_fallback_mappings()
    
    def _get_fallback_mappings(self) -> Dict[str, Any]:
        """Fallback field mappings if configuration file is unavailable"""
        return {
            "buyer_name": {"crm_source": "client.full_name", "required": True},
            "property_address": {"crm_source": "property.property_address", "required": True},
            "purchase_price": {"crm_source": "transaction.purchase_price", "required": True, "type": "currency"}
        }
    
    def _ensure_database_view(self):
        """Create optimized database view for CRPA data as recommended by Google AI Studio"""
        create_view_sql = """
        CREATE VIEW IF NOT EXISTS v_crpa_data AS
        SELECT 
            -- Transaction data
            t.id as transaction_id,
            t.purchase_price,
            t.earnest_money_amount as earnest_money,
            t.down_payment_amount as down_payment,
            t.loan_amount,
            t.closing_date,
            t.possession_date,
            17 as financing_contingency_days,
            17 as inspection_contingency_days,
            t.offer_date,
            date(t.offer_date, '+3 days') as offer_expiration,
            t.contract_date,
            t.escrow_company,
            t.title_company,
            t.notes as additional_terms,
            
            -- Client data (buyer)
            c.id as client_id,
            c.first_name,
            c.last_name,
            (c.first_name || ' ' || c.last_name) as full_name,
            c.email,
            c.home_phone as phone,
            c.address_line1,
            c.address_line2,
            c.city,
            c.state,
            c.zip_code,
            (c.address_line1 || CASE WHEN c.address_line2 IS NOT NULL AND c.address_line2 != '' 
                THEN ', ' || c.address_line2 ELSE '' END) as full_address,
            
            -- Property data
            p.id as property_id,
            p.street_address as property_address,
            p.city as property_city,
            p.state as property_state,
            p.zip_code as property_zip,
            (p.city || ', ' || p.state || ' ' || p.zip_code) as city_state_zip,
            p.property_type,
            '' as apn,
            '' as legal_description,
            
            -- Computed fields
            datetime('now') as form_date
            
        FROM transactions t
        LEFT JOIN clients c ON t.buyer_client_id = c.id
        LEFT JOIN properties p ON t.property_id = p.id
        """
        
        try:
            with self._get_connection() as conn:
                conn.execute(create_view_sql)
                self.logger.info("Database view v_crpa_data created/verified successfully")
        except Exception as e:
            self.logger.error(f"Failed to create database view: {e}")
            # Continue without view - will use manual joins
    
    def get_crpa_data(self, transaction_id: int) -> Dict[str, Any]:
        """
        Main method: Get clean 33-field dictionary for CRPA form generation
        
        Args:
            transaction_id: ID of the transaction to generate form for
            
        Returns:
            Dict with 33 clean fields ready for ProfessionalFormFiller
            
        Raises:
            ValueError: If transaction not found or data validation fails
        """
        try:
            # Step 1: Query optimized database view
            raw_data = self._query_transaction_data(transaction_id)
            if not raw_data:
                raise ValueError(f"Transaction {transaction_id} not found")
            
            # Step 2: Apply field transformations
            mapped_data = self._apply_field_transformations(raw_data)
            
            # Step 3: Add default values and agent information
            complete_data = self._add_defaults_and_constants(mapped_data)
            
            self.logger.info(f"Successfully mapped data for transaction {transaction_id}")
            return complete_data
            
        except Exception as e:
            self.logger.error(f"Failed to get CRPA data for transaction {transaction_id}: {e}")
            raise
    
    def _query_transaction_data(self, transaction_id: int) -> Optional[sqlite3.Row]:
        """Query the optimized database view for transaction data"""
        try:
            with self._get_connection() as conn:
                # Try optimized view first
                cursor = conn.execute(
                    "SELECT * FROM v_crpa_data WHERE transaction_id = ?",
                    (transaction_id,)
                )
                row = cursor.fetchone()
                
                if row:
                    return row
                
                # Fallback to manual join if view doesn't exist
                return self._query_manual_join(conn, transaction_id)
                
        except Exception as e:
            self.logger.warning(f"View query failed, trying manual join: {e}")
            with self._get_connection() as conn:
                return self._query_manual_join(conn, transaction_id)
    
    def _query_manual_join(self, conn: sqlite3.Connection, transaction_id: int) -> Optional[sqlite3.Row]:
        """Fallback manual join query if database view is unavailable"""
        manual_query = """
        SELECT 
            t.*, c.*, p.*,
            (c.first_name || ' ' || c.last_name) as full_name,
            (p.city || ', ' || p.state || ' ' || p.zip_code) as city_state_zip
        FROM transactions t
        LEFT JOIN clients c ON t.buyer_client_id = c.id
        LEFT JOIN properties p ON t.property_id = p.id
        WHERE t.id = ?
        """
        cursor = conn.execute(manual_query, (transaction_id,))
        return cursor.fetchone()
    
    def _apply_field_transformations(self, raw_data: sqlite3.Row) -> Dict[str, Any]:
        """Apply sophisticated field transformations based on mapping configuration"""
        transformed = {}
        
        for field_name, field_config in self.field_mappings.items():
            try:
                # Handle enhanced transformation rules
                if 'transform' in field_config:
                    transform_rule = TransformRule(**field_config['transform'])
                    value = self._apply_transform_rule(raw_data, transform_rule)
                else:
                    # Simple CRM source mapping
                    crm_source = field_config.get('crm_source', '')
                    value = self._get_nested_value(raw_data, crm_source)
                
                # Apply type formatting
                field_type = field_config.get('type', 'text')
                value = self._format_by_type(value, field_type)
                
                # Handle required fields
                if field_config.get('required', False) and not value:
                    value = field_config.get('default', f"[MISSING: {field_name}]")
                
                transformed[field_name] = value
                
            except Exception as e:
                self.logger.warning(f"Failed to transform field {field_name}: {e}")
                transformed[field_name] = field_config.get('default', '')
        
        return transformed
    
    def _apply_transform_rule(self, raw_data: sqlite3.Row, rule: TransformRule) -> str:
        """Apply specific transformation rule (concatenate, format_currency, template)"""
        if rule.method == "concatenate":
            values = [self._get_nested_value(raw_data, source) for source in rule.sources]
            values = [str(v) for v in values if v]  # Filter out None/empty values
            return rule.separator.join(values)
        
        elif rule.method == "format_currency":
            amount = self._get_nested_value(raw_data, rule.source)
            if amount:
                try:
                    # Handle string amounts like "$2,500,000.00"
                    if isinstance(amount, str):
                        amount = amount.replace('$', '').replace(',', '')
                    amount = Decimal(str(amount))
                    return f"{rule.symbol}{amount:,.2f}"
                except (ValueError, TypeError):
                    return f"{rule.symbol}0.00"
            return f"{rule.symbol}0.00"
        
        elif rule.method == "template":
            values = [self._get_nested_value(raw_data, source) for source in rule.sources]
            try:
                return rule.template_string.format(*values)
            except (IndexError, ValueError):
                return " ".join(str(v) for v in values if v)
        
        else:
            # Unknown transformation method
            self.logger.warning(f"Unknown transformation method: {rule.method}")
            return ""
    
    def _get_nested_value(self, data: sqlite3.Row, path: str) -> Any:
        """Get value from data using dot notation (e.g., 'client.first_name')"""
        if not path:
            return None
        
        # Handle simple field names (no dot notation)
        if '.' not in path:
            try:
                return data[path]
            except (KeyError, IndexError):
                return None
        
        # Handle dot notation
        parts = path.split('.')
        if len(parts) == 2:
            table, field = parts
            # Map table prefixes to actual field names
            field_mappings = {
                'client': {'first_name': 'first_name', 'last_name': 'last_name', 'full_name': 'full_name',
                          'email': 'email', 'phone': 'phone', 'address': 'full_address'},
                'property': {'address': 'property_address', 'city_state_zip': 'city_state_zip', 
                           'apn': 'apn', 'property_type': 'property_type'},
                'transaction': {'purchase_price': 'purchase_price', 'earnest_money': 'earnest_money_amount',
                              'down_payment': 'down_payment', 'closing_date': 'closing_date'}
            }
            
            actual_field = field_mappings.get(table, {}).get(field, field)
            try:
                return data[actual_field]
            except (KeyError, IndexError):
                return None
        
        try:
            return data[path]
        except (KeyError, IndexError):
            return None
    
    def _format_by_type(self, value: Any, field_type: str) -> str:
        """Format value according to field type specification"""
        if not value:
            return ""
        
        if field_type == "currency":
            try:
                if isinstance(value, str):
                    value = value.replace('$', '').replace(',', '')
                amount = Decimal(str(value))
                return f"${amount:,.2f}"
            except (ValueError, TypeError):
                return "$0.00"
        
        elif field_type == "date":
            try:
                if isinstance(value, str):
                    # Parse various date formats
                    for fmt in ["%Y-%m-%d", "%m/%d/%Y", "%m-%d-%Y"]:
                        try:
                            date_obj = datetime.strptime(value, fmt).date()
                            return date_obj.strftime("%m/%d/%Y")
                        except ValueError:
                            continue
                elif isinstance(value, (date, datetime)):
                    return value.strftime("%m/%d/%Y")
                return str(value)
            except Exception:
                return str(value)
        
        elif field_type == "tel":
            # Format phone numbers
            phone = ''.join(filter(str.isdigit, str(value)))
            if len(phone) == 10:
                return f"({phone[:3]}) {phone[3:6]}-{phone[6:]}"
            return str(value)
        
        else:
            return str(value) if value is not None else ""
    
    def _add_defaults_and_constants(self, mapped_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add default values and agent constants (Narissa Realty information)"""
        # Agent defaults for Narissa Realty
        agent_defaults = {
            "buyer_agent": "Narissa Jennings",
            "buyer_brokerage": "Coldwell Banker Grass Roots Realty", 
            "buyer_agent_license": "02129287",
            "buyer_agent_phone": "(530) 276-5970",
            "escrow_company": "Nevada County Escrow",
            "financing_contingency_days": "21",
            "inspection_contingency_days": "17",
            "possession_date": "Close of escrow"
        }
        
        # Add defaults for missing fields
        for key, default_value in agent_defaults.items():
            if not mapped_data.get(key):
                mapped_data[key] = default_value
        
        # Add current date as form_date if not present
        if not mapped_data.get('form_date'):
            mapped_data['form_date'] = datetime.now().strftime("%m/%d/%Y")
        
        # Add offer_date as today if not present
        if not mapped_data.get('offer_date'):
            mapped_data['offer_date'] = datetime.now().strftime("%m/%d/%Y")
        
        return mapped_data
    
    def get_available_transactions(self) -> List[Dict[str, Any]]:
        """Get list of available transactions for form generation"""
        try:
            with self._get_connection() as conn:
                cursor = conn.execute("""
                    SELECT t.id, t.purchase_price, t.closing_date,
                           c.first_name, c.last_name,
                           p.street_address as property_address
                    FROM transactions t
                    LEFT JOIN clients c ON t.client_id = c.id
                    LEFT JOIN properties p ON t.property_id = p.id
                    ORDER BY t.created_at DESC
                """)
                
                transactions = []
                for row in cursor.fetchall():
                    transactions.append({
                        'id': row['id'],
                        'client_name': f"{row['first_name']} {row['last_name']}" if row['first_name'] else "Unknown",
                        'property_address': row['property_address'] or "Unknown Property",
                        'purchase_price': row['purchase_price'],
                        'closing_date': row['closing_date']
                    })
                
                return transactions
                
        except Exception as e:
            self.logger.error(f"Failed to get available transactions: {e}")
            return []
    
    def __del__(self):
        """Clean up connection pool on object destruction"""
        try:
            while not self.connection_pool.empty():
                conn = self.connection_pool.get_nowait()
                conn.close()
        except:
            pass

# Test function for development
def test_crm_data_mapper():
    """Test function to validate CrmDataMapper functionality"""
    mapper = CrmDataMapper()
    
    # Test getting available transactions
    transactions = mapper.get_available_transactions()
    print(f"Found {len(transactions)} transactions")
    
    if transactions:
        # Test mapping first transaction
        transaction_id = transactions[0]['id']
        print(f"Testing transaction {transaction_id}")
        
        try:
            crpa_data = mapper.get_crpa_data(transaction_id)
            print("✅ Successfully mapped CRPA data")
            print(f"Mapped {len(crpa_data)} fields")
            
            # Show sample fields
            sample_fields = ['buyer_name', 'property_address', 'purchase_price']
            for field in sample_fields:
                print(f"  {field}: {crpa_data.get(field, 'N/A')}")
                
        except Exception as e:
            print(f"❌ Failed to map data: {e}")

if __name__ == "__main__":
    test_crm_data_mapper()