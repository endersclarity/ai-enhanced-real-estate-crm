# Bug Report: Missing Core Functionality

## Issue Summary
The Docker containers are running a stripped-down boilerplate Flask app instead of the feature-rich Real Estate CRM with AI, form generation, and MLS integration.

## Current State
- **Running**: Basic authentication boilerplate from `app/` directory
- **Not Running**: Original CRM from `core_app/real_estate_crm.py`

## Missing Features
1. AI Chatbot (`/chat`, `/debug_chat`)
2. Form Generation (`/generate_crpa`, `/api/generate_forms`)
3. CRPA Dashboard (`/crpa_dashboard`)
4. MLS Property Integration
5. Populated database with clients, properties, transactions
6. Professional form filling functionality

## Root Cause
`run_flask_app.py` imports from `app` (boilerplate) instead of `core_app` (original CRM)

## Fix in Progress
1. Created `run_original_crm.py` to load the full-featured app
2. Updated `docker-compose.two-stage.yml` to use original CRM
3. Created database initialization script
4. Need to restart containers with new configuration

## Next Steps
1. Restart dev container with original CRM
2. Initialize database with proper schema
3. Populate with dummy data
4. Test all features are restored

## Command to Fix
```bash
docker-compose -f docker-compose.two-stage.yml down
docker-compose -f docker-compose.two-stage.yml up -d
docker cp scripts/init-dev-database.py offer-creator-dev:/app/
docker-compose -f docker-compose.two-stage.yml exec dev python3 /app/init-dev-database.py
```