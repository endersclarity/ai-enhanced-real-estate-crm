# Module: CRM Core

## Purpose & Responsibility
Manages comprehensive real estate customer relationship data with a 177-field schema covering clients, properties, and transactions. Provides secure database operations, AI-assisted data entry, and real-time dashboard statistics. Handles authentication, validation, and audit logging for all CRM operations.

## Interfaces
* `RealEstateCRM`: Main Flask application interface
  * `add_client()`: Create new client with validation
  * `add_property()`: Add property with MLS integration
  * `create_transaction()`: Track deal progression
  * `get_dashboard_stats()`: Real-time metrics
* Input: Client forms, property data, AI-extracted email content
* Output: JSON API responses, HTML templates, database confirmations

## Implementation Details
* Files:
  * `core_app/real_estate_crm.py` - Main Flask application and API endpoints
  * `core_app/database/real_estate_crm_schema.sql` - 177-field database schema
  * `core_app/init_database.py` - Database initialization and setup
  * `database_config.py` - Database connection configuration
  * `populate_rich_crm_data.py` - Sample data population utilities
* Important algorithms:
  * AI-assisted data validation with user confirmation workflow
  * Real-time dashboard statistics with auto-refresh capabilities
  * Property URL generation for Zillow, Realtor.com, MLS portals
* Data Models:
  * `clients` - Complete contact and financial information (buyers/sellers)
  * `properties` - Detailed listings with MLS integration and URL links
  * `transactions` - Full deal tracking from offer to closing
  * `ai_logs` - Conversation history and operation audit trail

## Current Implementation Status
* Completed: 177-field database schema, AI integration, property URL links, authentication system
* In Progress: **CRITICAL** - Database schema mismatch remediation between init_database.py and actual schema
* Pending: Enhanced architecture integration, user experience redesign for natural language input

## Implementation Plans & Tasks
* `implementation_plan_database_remediation.md`
  * [Schema Alignment]: Fix mismatches between init script and actual database structure
  * [Data Migration]: Ensure existing data integrity during schema corrections
* `implementation_plan_crm_enhancement.md`
  * [UX Redesign]: Replace memorized ID requirements with natural language/dropdown interfaces
  * [API Optimization]: Improve endpoint response times and error handling

## Mini Dependency Tracker
---mini_tracker_start---
Dependencies:
- ai_integration_module.md (for AI-assisted operations)
- form_processing_module.md (for CRM data mapping to forms)
- three_tier_diagnostics_module.md (for system health monitoring)

Dependents:
- All form generation workflows require CRM data
- AI chatbot operations depend on CRM database access
- Dashboard statistics rely on CRM data aggregation
---mini_tracker_end---
