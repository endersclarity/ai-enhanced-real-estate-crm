#!/usr/bin/env python3
"""
Production Documentation Generator for Narissa Realty CRM
Creates comprehensive system documentation, API docs, and troubleshooting guides
"""

import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ProductionDocumentationGenerator:
    """Generates comprehensive production documentation"""
    
    def __init__(self, docs_dir="docs/production"):
        self.docs_dir = Path(docs_dir)
        self.docs_dir.mkdir(parents=True, exist_ok=True)
        
        # Documentation structure
        self.doc_sections = {
            'system_admin': 'System Administrator Guide',
            'user_guide': 'User Documentation',
            'api_docs': 'API Documentation',
            'troubleshooting': 'Troubleshooting Guide',
            'deployment': 'Deployment Guide',
            'security': 'Security Documentation'
        }
    
    def generate_all_documentation(self) -> Dict:
        """Generate all production documentation"""
        logger.info("Starting complete documentation generation")
        
        results = {
            'generated_docs': [],
            'success': True,
            'errors': []
        }
        
        try:
            # Generate each documentation section
            for section_key, section_title in self.doc_sections.items():
                logger.info(f"Generating {section_title}")
                
                if section_key == 'system_admin':
                    content = self._generate_system_admin_guide()
                elif section_key == 'user_guide':
                    content = self._generate_user_guide()
                elif section_key == 'api_docs':
                    content = self._generate_api_documentation()
                elif section_key == 'troubleshooting':
                    content = self._generate_troubleshooting_guide()
                elif section_key == 'deployment':
                    content = self._generate_deployment_guide()
                elif section_key == 'security':
                    content = self._generate_security_documentation()
                else:
                    continue
                
                # Save documentation
                doc_path = self.docs_dir / f"{section_key}.md"
                with open(doc_path, 'w') as f:
                    f.write(content)
                
                results['generated_docs'].append({
                    'section': section_title,
                    'file_path': str(doc_path),
                    'size_kb': len(content) / 1024
                })
            
            # Generate main index
            index_content = self._generate_documentation_index()
            index_path = self.docs_dir / "README.md"
            with open(index_path, 'w') as f:
                f.write(index_content)
            
            results['generated_docs'].append({
                'section': 'Documentation Index',
                'file_path': str(index_path),
                'size_kb': len(index_content) / 1024
            })
            
            logger.info(f"Documentation generation completed: {len(results['generated_docs'])} files created")
            
        except Exception as e:
            results['success'] = False
            results['errors'].append(str(e))
            logger.error(f"Documentation generation failed: {e}")
        
        return results
    
    def _generate_documentation_index(self) -> str:
        """Generate main documentation index"""
        return f"""# Narissa Realty CRM - Production Documentation

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Documentation Sections

### 📋 [System Administrator Guide](system_admin.md)
Complete guide for system administrators covering installation, configuration, maintenance, and monitoring.

### 👥 [User Documentation](user_guide.md)
End-user guide covering all CRM features, workflows, and best practices.

### 🔌 [API Documentation](api_docs.md)
Complete API reference with endpoints, authentication, and examples.

### 🔧 [Troubleshooting Guide](troubleshooting.md)
Common issues, solutions, and diagnostic procedures.

### 🚀 [Deployment Guide](deployment.md)
Step-by-step deployment instructions for production environments.

### 🔒 [Security Documentation](security.md)
Security features, configurations, and compliance guidelines.

## Quick Links

- [Health Check Endpoint](http://localhost:8000/health)
- [Monitoring Dashboard](http://localhost:8000/api/monitoring/dashboard)
- [User Management Interface](http://localhost:8000/api/users/management-interface)

## System Overview

The Narissa Realty CRM is a comprehensive real estate management system built with:
- **Backend**: Python Flask with SQLite/PostgreSQL
- **Authentication**: JWT with role-based access control
- **Monitoring**: Sentry integration with custom metrics
- **Deployment**: Docker-ready with cloud hosting support

## Support

For technical support, contact: admin@narissarealty.com

---
*Generated by Narissa Realty CRM Documentation System*
"""
    
    def _generate_system_admin_guide(self) -> str:
        """Generate system administrator guide"""
        return f"""# System Administrator Guide

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Database Management](#database-management)
5. [User Management](#user-management)
6. [Monitoring and Alerts](#monitoring-and-alerts)
7. [Backup and Recovery](#backup-and-recovery)
8. [Performance Optimization](#performance-optimization)
9. [Security Management](#security-management)
10. [Troubleshooting](#troubleshooting)

## System Requirements

### Minimum Requirements
- **CPU**: 2 cores, 2.4GHz
- **RAM**: 4GB
- **Storage**: 20GB available space
- **OS**: Ubuntu 20.04 LTS or later

### Recommended Production Requirements
- **CPU**: 4 cores, 3.0GHz
- **RAM**: 8GB
- **Storage**: 100GB SSD
- **Network**: 1Gbps connection

### Dependencies
- Python 3.8+
- PostgreSQL 12+ (production) or SQLite (development)
- Redis 6.0+ (session management)
- Nginx (reverse proxy)

## Installation

### 1. System Preparation
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install python3-pip python3-venv nginx redis-server postgresql postgresql-contrib

# Create application user
sudo useradd -m -s /bin/bash crm
sudo usermod -aG sudo crm
```

### 2. Application Setup
```bash
# Switch to CRM user
sudo su - crm

# Clone repository
git clone <repository-url> /opt/narissa-crm
cd /opt/narissa-crm

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Database Setup
```bash
# Create PostgreSQL database
sudo -u postgres createdb narissa_crm
sudo -u postgres createuser crm_user
sudo -u postgres psql -c "ALTER USER crm_user WITH PASSWORD 'secure_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE narissa_crm TO crm_user;"

# Initialize database schema
python deployment/postgresql_setup.py
```

## Configuration

### Environment Variables
Create `/opt/narissa-crm/.env`:
```bash
# Database Configuration
DATABASE_URL=postgresql://crm_user:secure_password@localhost/narissa_crm

# Security
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-here

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@domain.com
SMTP_PASSWORD=your-app-password

# Monitoring
SENTRY_DSN=your-sentry-dsn-here

# Application
ENVIRONMENT=production
DEBUG=False
```

### Nginx Configuration
Create `/etc/nginx/sites-available/narissa-crm`:
```nginx
server {{
    listen 80;
    server_name your-domain.com;
    
    # SSL configuration (handled by domain_ssl_setup.py)
    
    location / {{
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
    
    location /static/ {{
        alias /opt/narissa-crm/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }}
}}
```

### Systemd Service
Create `/etc/systemd/system/narissa-crm.service`:
```ini
[Unit]
Description=Narissa Realty CRM
After=network.target postgresql.service redis.service

[Service]
Type=exec
User=crm
Group=crm
WorkingDirectory=/opt/narissa-crm
Environment=PATH=/opt/narissa-crm/venv/bin
ExecStart=/opt/narissa-crm/venv/bin/gunicorn --config deployment/gunicorn_config.py deployment.production_app:app
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always

[Install]
WantedBy=multi-user.target
```

## Database Management

### Daily Operations
```bash
# Check database status
sudo systemctl status postgresql
psql -h localhost -U crm_user -d narissa_crm -c "SELECT COUNT(*) FROM users;"

# Monitor database size
psql -h localhost -U crm_user -d narissa_crm -c "SELECT pg_size_pretty(pg_database_size('narissa_crm'));"

# Check active connections
psql -h localhost -U crm_user -d narissa_crm -c "SELECT count(*) FROM pg_stat_activity;"
```

### Backup Operations
```bash
# Manual backup
python deployment/backup_restore_system.py

# Restore from backup
python -c "
from deployment.backup_restore_system import BackupRestoreSystem
backup_system = BackupRestoreSystem()
result = backup_system.restore_from_backup('/path/to/backup.db.gz')
print(result)
"
```

## User Management

### Creating Admin User
```bash
# Access Python shell
python -c "
from deployment.auth_system import UserManager
user_mgr = UserManager()
user = user_mgr.create_user('admin', 'admin@narissarealty.com', 'SecurePassword123!', 'admin')
print(f'Admin user created: {{user.username}}')
"
```

### Managing Roles and Permissions
```bash
# Assign role to user
python -c "
from deployment.user_management_system import UserManagementSystem
user_mgmt = UserManagementSystem()
result = user_mgmt.assign_role(user_id=1, new_role='manager', assigned_by=1)
print(result)
"
```

## Monitoring and Alerts

### Health Checks
```bash
# Application health
curl http://localhost:8000/health

# Database connectivity
curl http://localhost:8000/api/monitoring/metrics

# System metrics
curl http://localhost:8000/api/monitoring/dashboard
```

### Log Monitoring
```bash
# Application logs
tail -f /var/log/narissa-crm/app.log

# System service logs
journalctl -u narissa-crm -f

# Nginx logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

### Performance Monitoring
```bash
# Run performance optimization
python deployment/performance_optimization.py

# Check system resources
htop
df -h
free -h
```

## Backup and Recovery

### Automated Backups
The system includes automated backup scheduling:
- **Full backups**: Daily at 2:00 AM
- **Incremental backups**: Every 4 hours
- **Retention**: 30 days

### Manual Operations
```bash
# Create full backup
python -c "
from deployment.backup_restore_system import BackupRestoreSystem
backup_system = BackupRestoreSystem()
result = backup_system.create_full_backup()
print(result)
"

# Verify backup
python -c "
from deployment.backup_restore_system import BackupRestoreSystem
backup_system = BackupRestoreSystem()
result = backup_system.verify_backup('/path/to/backup.db.gz')
print(result)
"
```

## Security Management

### SSL Certificate Management
```bash
# Setup SSL certificates
python deployment/domain_ssl_setup.py your-domain.com admin@your-domain.com

# Check certificate status
openssl x509 -in /etc/letsencrypt/live/your-domain.com/fullchain.pem -text -noout
```

### User Authentication
- Passwords must meet complexity requirements (8+ chars, mixed case, numbers, symbols)
- Account lockout after 5 failed attempts
- Session timeout after 1 hour of inactivity
- Two-factor authentication available

### Security Auditing
```bash
# Review access logs
python -c "
from deployment.rbac_system import RBACManager
rbac = RBACManager()
# Check recent access attempts
"

# Monitor failed login attempts
grep "authentication failed" /var/log/narissa-crm/app.log
```

## Troubleshooting

### Common Issues

#### Application Won't Start
```bash
# Check service status
sudo systemctl status narissa-crm

# Check logs
journalctl -u narissa-crm --no-pager

# Verify configuration
python -c "import os; print(os.environ.get('DATABASE_URL'))"
```

#### Database Connection Issues
```bash
# Test database connection
psql -h localhost -U crm_user -d narissa_crm -c "SELECT 1;"

# Check PostgreSQL status
sudo systemctl status postgresql

# Review PostgreSQL logs
sudo tail -f /var/log/postgresql/postgresql-12-main.log
```

#### Performance Issues
```bash
# Check system resources
top
iotop
netstat -tulpn

# Run performance analysis
python deployment/performance_optimization.py

# Check database performance
psql -h localhost -U crm_user -d narissa_crm -c "SELECT * FROM pg_stat_activity WHERE state = 'active';"
```

### Emergency Procedures

#### Service Recovery
```bash
# Stop all services
sudo systemctl stop narissa-crm nginx

# Start services in order
sudo systemctl start postgresql redis-server
sudo systemctl start narissa-crm
sudo systemctl start nginx

# Verify all services
sudo systemctl status narissa-crm nginx postgresql redis-server
```

#### Data Recovery
```bash
# Restore from latest backup
python -c "
from deployment.backup_restore_system import BackupRestoreSystem
backup_system = BackupRestoreSystem()
# Get latest backup
status = backup_system.get_backup_status()
latest = status['recent_backups'][0]
result = backup_system.restore_from_backup(latest['path'])
print(result)
"
```

## Maintenance Tasks

### Daily
- Monitor system health via `/health` endpoint
- Check disk space usage
- Review error logs

### Weekly
- Verify backup integrity
- Update system packages
- Review security logs
- Performance metrics analysis

### Monthly
- SSL certificate renewal check
- Database maintenance (VACUUM, ANALYZE)
- Security audit
- Capacity planning review

---

For additional support, contact: admin@narissarealty.com
"""
    
    def _generate_user_guide(self) -> str:
        """Generate user documentation"""
        return f"""# User Guide - Narissa Realty CRM

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Table of Contents

1. [Getting Started](#getting-started)
2. [Client Management](#client-management)
3. [Property Management](#property-management)
4. [Transaction Tracking](#transaction-tracking)
5. [Document Management](#document-management)
6. [Reporting and Analytics](#reporting-and-analytics)
7. [Team Collaboration](#team-collaboration)
8. [User Settings](#user-settings)

## Getting Started

### Logging In
1. Navigate to the CRM login page
2. Enter your username and password
3. Click "Login"
4. If enabled, complete two-factor authentication

### Dashboard Overview
The main dashboard provides:
- Recent client interactions
- Upcoming appointments
- Transaction pipeline
- Performance metrics
- Quick action buttons

### Navigation
- **Clients**: Manage your client database
- **Properties**: Browse and manage property listings
- **Transactions**: Track deals in progress
- **Documents**: Upload and organize files
- **Reports**: Generate performance reports
- **Settings**: Configure your preferences

## Client Management

### Adding New Clients
1. Click "Add Client" button
2. Fill in required information:
   - Name (required)
   - Email
   - Phone number
   - Budget range
   - Property preferences
3. Save the client record

### Client Communication
- Log all interactions in the activity timeline
- Set follow-up reminders
- Track communication preferences
- Monitor response rates

### Client Search and Filtering
Use the search bar to find clients by:
- Name
- Email
- Phone number
- Budget range
- Location preferences

## Property Management

### Property Listings
- Browse available properties
- Filter by price, location, features
- Save favorites for clients
- Track property status changes

### Property Details
Each property record includes:
- Address and location details
- Price and financial information
- Property features and amenities
- Photos and virtual tours
- Market analysis data

### Matching Clients to Properties
1. Select a client from your database
2. Use the property matching tool
3. Review suggested properties
4. Share recommendations with client
5. Schedule viewings

## Transaction Tracking

### Transaction Pipeline
Track deals through stages:
1. **Lead** - Initial client interest
2. **Showing** - Property viewings scheduled
3. **Offer** - Offer submitted
4. **Under Contract** - Offer accepted
5. **Closing** - Final steps and completion

### Managing Transactions
- Update transaction status
- Track important dates and deadlines
- Monitor contingencies
- Generate transaction reports

### Commission Tracking
- Record commission details
- Track payment status
- Generate commission reports
- Monitor team performance

## Document Management

### Uploading Documents
1. Navigate to client or property record
2. Click "Upload Document"
3. Select file type category
4. Add description and tags
5. Upload file

### Document Organization
- Organize by client, property, or transaction
- Use tags for easy searching
- Set access permissions
- Track document versions

### Document Templates
Access pre-built templates for:
- Purchase agreements
- Listing agreements
- Disclosure forms
- Marketing materials

## Reporting and Analytics

### Available Reports
- **Sales Performance**: Individual and team metrics
- **Client Activity**: Interaction summaries
- **Property Analytics**: Market trends and pricing
- **Commission Reports**: Earnings tracking
- **Pipeline Reports**: Deal flow analysis

### Custom Reports
1. Select report type
2. Choose date range
3. Apply filters
4. Generate and download report

### Dashboard Widgets
Customize your dashboard with:
- Goal tracking widgets
- Performance charts
- Activity feeds
- Calendar integration

## Team Collaboration

### Team Communication
- Internal messaging system
- Client assignment notifications
- Deal update alerts
- Team announcements

### Lead Distribution
- Automatic lead assignment
- Round-robin distribution
- Skills-based routing
- Manual assignment options

### Collaboration Tools
- Shared client notes
- Team calendars
- Joint client meetings
- Cross-referral tracking

## User Settings

### Profile Management
- Update personal information
- Change password
- Set notification preferences
- Configure dashboard layout

### Privacy Settings
- Control data sharing
- Set profile visibility
- Manage contact preferences
- Configure security options

### Integration Settings
- Email account sync
- Calendar integration
- Third-party app connections
- API access tokens

## Best Practices

### Client Management
- Update client records regularly
- Log all interactions promptly
- Set follow-up reminders
- Maintain professional communication

### Data Security
- Use strong passwords
- Log out when finished
- Don't share login credentials
- Report security concerns immediately

### Performance Optimization
- Complete data entry fields
- Use standardized formats
- Regular data cleanup
- Monitor system performance

## Support and Training

### Getting Help
- In-app help system
- Video tutorials
- User community forums
- Direct support contact

### Training Resources
- New user onboarding
- Feature update training
- Best practices workshops
- Certification programs

---

For technical support: support@narissarealty.com
For training: training@narissarealty.com
"""
    
    def _generate_api_documentation(self) -> str:
        """Generate API documentation"""
        return f"""# API Documentation - Narissa Realty CRM

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Base URL
```
Production: https://crm.narissarealty.com/api
Development: http://localhost:8000/api
```

## Authentication

### JWT Token Authentication
All API requests require authentication via JWT tokens.

#### Login
```http
POST /auth/login
Content-Type: application/json

{{
    "username": "your_username",
    "password": "your_password"
}}
```

**Response:**
```json
{{
    "success": true,
    "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user": {{
        "id": 1,
        "username": "agent1",
        "role": "agent"
    }}
}}
```

#### Using the Token
Include the token in the Authorization header:
```http
Authorization: Bearer <your-jwt-token>
```

## User Management

### Get Current User
```http
GET /auth/profile
Authorization: Bearer <token>
```

### List Users
```http
GET /users?page=1&limit=50
Authorization: Bearer <token>
```

**Query Parameters:**
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 50)
- `role`: Filter by role (admin, manager, agent)
- `search`: Search by name or email

### Create User
```http
POST /users
Authorization: Bearer <token>
Content-Type: application/json

{{
    "username": "newuser",
    "email": "user@example.com",
    "password": "SecurePass123!",
    "first_name": "John",
    "last_name": "Doe",
    "role": "agent"
}}
```

### Update User
```http
PUT /users/{{user_id}}
Authorization: Bearer <token>
Content-Type: application/json

{{
    "first_name": "Updated Name",
    "phone": "555-123-4567"
}}
```

## Client Management

### List Clients
```http
GET /clients?page=1&limit=50
Authorization: Bearer <token>
```

**Query Parameters:**
- `page`: Page number
- `limit`: Items per page
- `agent_id`: Filter by agent
- `search`: Search by name or email

### Get Client Details
```http
GET /clients/{{client_id}}
Authorization: Bearer <token>
```

### Create Client
```http
POST /clients
Authorization: Bearer <token>
Content-Type: application/json

{{
    "name": "John Client",
    "email": "client@example.com",
    "phone": "555-123-4567",
    "budget_min": 300000,
    "budget_max": 500000,
    "notes": "Looking for family home"
}}
```

### Update Client
```http
PUT /clients/{{client_id}}
Authorization: Bearer <token>
Content-Type: application/json

{{
    "budget_max": 600000,
    "notes": "Updated budget requirements"
}}
```

## Property Management

### List Properties
```http
GET /properties?page=1&limit=50
Authorization: Bearer <token>
```

**Query Parameters:**
- `min_price`: Minimum price filter
- `max_price`: Maximum price filter
- `bedrooms`: Number of bedrooms
- `property_type`: Type of property
- `location`: Location filter

### Get Property Details
```http
GET /properties/{{property_id}}
Authorization: Bearer <token>
```

### Create Property
```http
POST /properties
Authorization: Bearer <token>
Content-Type: application/json

{{
    "address": "123 Main St, City, State 12345",
    "price": 450000,
    "bedrooms": 3,
    "bathrooms": 2.5,
    "square_feet": 1800,
    "property_type": "single_family",
    "description": "Beautiful family home"
}}
```

## Transaction Management

### List Transactions
```http
GET /transactions?page=1&limit=50
Authorization: Bearer <token>
```

### Get Transaction Details
```http
GET /transactions/{{transaction_id}}
Authorization: Bearer <token>
```

### Create Transaction
```http
POST /transactions
Authorization: Bearer <token>
Content-Type: application/json

{{
    "client_id": 1,
    "property_id": 1,
    "offer_amount": 425000,
    "status": "offer_submitted",
    "closing_date": "2024-03-15"
}}
```

### Update Transaction Status
```http
PUT /transactions/{{transaction_id}}
Authorization: Bearer <token>
Content-Type: application/json

{{
    "status": "under_contract",
    "contract_date": "2024-02-15"
}}
```

## Monitoring and Health

### Health Check
```http
GET /health
```

**Response:**
```json
{{
    "timestamp": "2024-01-15T10:30:00Z",
    "overall_status": "healthy",
    "checks": {{
        "database": {{"status": "healthy"}},
        "cpu": {{"status": "healthy", "value": 25.5}},
        "memory": {{"status": "healthy", "value": 45.2}}
    }}
}}
```

### System Metrics
```http
GET /monitoring/metrics
Authorization: Bearer <token>
```

### Monitoring Dashboard
```http
GET /monitoring/dashboard
Authorization: Bearer <token>
```

## Error Handling

### Standard Error Response
```json
{{
    "error": "Error description",
    "code": "ERROR_CODE",
    "details": {{
        "field": "Additional error details"
    }}
}}
```

### HTTP Status Codes
- `200`: Success
- `201`: Created
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `422`: Validation Error
- `500`: Internal Server Error

## Rate Limiting

API requests are limited to:
- **Authenticated users**: 1000 requests per hour
- **Public endpoints**: 100 requests per hour

Rate limit headers:
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1642234800
```

## Pagination

List endpoints support pagination:

**Request:**
```http
GET /clients?page=2&limit=25
```

**Response:**
```json
{{
    "data": [...],
    "pagination": {{
        "page": 2,
        "limit": 25,
        "total": 150,
        "pages": 6
    }}
}}
```

## Filtering and Searching

Most list endpoints support filtering:

**Date Ranges:**
```http
GET /transactions?start_date=2024-01-01&end_date=2024-12-31
```

**Search:**
```http
GET /clients?search=john
```

**Multiple Filters:**
```http
GET /properties?min_price=300000&max_price=500000&bedrooms=3
```

## SDK Examples

### Python
```python
import requests

class NarissaCRMClient:
    def __init__(self, base_url, token):
        self.base_url = base_url
        self.headers = {{'Authorization': f'Bearer {{token}}'}}
    
    def get_clients(self, page=1, limit=50):
        response = requests.get(
            f'{{self.base_url}}/clients',
            params={{'page': page, 'limit': limit}},
            headers=self.headers
        )
        return response.json()
    
    def create_client(self, client_data):
        response = requests.post(
            f'{{self.base_url}}/clients',
            json=client_data,
            headers=self.headers
        )
        return response.json()

# Usage
client = NarissaCRMClient('https://crm.narissarealty.com/api', 'your-token')
clients = client.get_clients()
```

### JavaScript
```javascript
class NarissaCRMClient {{
    constructor(baseUrl, token) {{
        this.baseUrl = baseUrl;
        this.headers = {{
            'Authorization': `Bearer ${{token}}`,
            'Content-Type': 'application/json'
        }};
    }}
    
    async getClients(page = 1, limit = 50) {{
        const response = await fetch(
            `${{this.baseUrl}}/clients?page=${{page}}&limit=${{limit}}`,
            {{ headers: this.headers }}
        );
        return response.json();
    }}
    
    async createClient(clientData) {{
        const response = await fetch(
            `${{this.baseUrl}}/clients`,
            {{
                method: 'POST',
                headers: this.headers,
                body: JSON.stringify(clientData)
            }}
        );
        return response.json();
    }}
}}

// Usage
const client = new NarissaCRMClient('https://crm.narissarealty.com/api', 'your-token');
const clients = await client.getClients();
```

## Webhooks

### Configuring Webhooks
```http
POST /webhooks
Authorization: Bearer <token>
Content-Type: application/json

{{
    "url": "https://your-app.com/webhook",
    "events": ["client.created", "transaction.updated"],
    "secret": "your-webhook-secret"
}}
```

### Webhook Events
- `client.created`
- `client.updated`
- `property.created`
- `transaction.created`
- `transaction.updated`
- `user.created`

### Webhook Payload
```json
{{
    "event": "client.created",
    "timestamp": "2024-01-15T10:30:00Z",
    "data": {{
        "id": 123,
        "name": "John Client",
        "email": "client@example.com"
    }}
}}
```

---

For API support: api-support@narissarealty.com
"""
    
    def _generate_troubleshooting_guide(self) -> str:
        """Generate troubleshooting guide"""
        return f"""# Troubleshooting Guide - Narissa Realty CRM

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Quick Diagnostic Commands

### System Health Check
```bash
# Application health
curl http://localhost:8000/health

# Service status
sudo systemctl status narissa-crm nginx postgresql redis-server

# Disk space
df -h

# Memory usage
free -h

# CPU usage
top
```

## Common Issues

### 1. Application Won't Start

**Symptoms:**
- Service fails to start
- "Connection refused" errors
- 502 Bad Gateway from Nginx

**Diagnostic Steps:**
```bash
# Check service status
sudo systemctl status narissa-crm

# View service logs
journalctl -u narissa-crm --no-pager -n 50

# Check if port is in use
sudo netstat -tulpn | grep :8000

# Verify Python environment
/opt/narissa-crm/venv/bin/python --version
```

**Common Causes & Solutions:**

#### Missing Environment Variables
```bash
# Check environment file
cat /opt/narissa-crm/.env

# Verify required variables
grep -E "DATABASE_URL|SECRET_KEY" /opt/narissa-crm/.env
```

#### Database Connection Issues
```bash
# Test database connection
psql -h localhost -U crm_user -d narissa_crm -c "SELECT 1;"

# Check PostgreSQL service
sudo systemctl status postgresql

# View PostgreSQL logs
sudo tail -f /var/log/postgresql/postgresql-12-main.log
```

#### Permission Issues
```bash
# Check file ownership
ls -la /opt/narissa-crm/

# Fix ownership if needed
sudo chown -R crm:crm /opt/narissa-crm/

# Check service file permissions
ls -la /etc/systemd/system/narissa-crm.service
```

### 2. Database Connection Errors

**Symptoms:**
- "Connection to database failed"
- Authentication errors
- Timeout errors

**Diagnostic Steps:**
```bash
# Test database connectivity
pg_isready -h localhost -p 5432

# Check database exists
sudo -u postgres psql -l | grep narissa_crm

# Verify user permissions
sudo -u postgres psql -c "\\du crm_user"

# Check active connections
sudo -u postgres psql -d narissa_crm -c "SELECT count(*) FROM pg_stat_activity;"
```

**Solutions:**

#### Reset Database Password
```bash
sudo -u postgres psql -c "ALTER USER crm_user PASSWORD 'new_password';"
# Update .env file with new password
```

#### Fix Connection Limits
```bash
# Check max connections
sudo -u postgres psql -c "SHOW max_connections;"

# If too low, edit postgresql.conf
sudo nano /etc/postgresql/12/main/postgresql.conf
# max_connections = 200
sudo systemctl restart postgresql
```

### 3. Authentication Issues

**Symptoms:**
- Users can't log in
- "Invalid credentials" errors
- Session timeouts

**Diagnostic Steps:**
```bash
# Check Redis service (sessions)
sudo systemctl status redis-server
redis-cli ping

# View authentication logs
grep -i "authentication" /var/log/narissa-crm/app.log

# Check user account status
python3 -c "
from deployment.auth_system import UserManager
user_mgr = UserManager()
user = user_mgr.get_user_by_username('username')
print(f'User active: {{user.is_active if user else \"Not found\"}}')
print(f'Account locked: {{user.is_account_locked() if user else \"N/A\"}}')
"
```

**Solutions:**

#### Reset User Password
```bash
python3 -c "
from deployment.auth_system import UserManager
user_mgr = UserManager()
user_mgr.change_password(user_id, '', 'NewPassword123!')
print('Password reset completed')
"
```

#### Unlock User Account
```bash
python3 -c "
from deployment.auth_system import UserManager
user_mgr = UserManager()
user_mgr.reset_failed_login_attempts(user_id)
print('Account unlocked')
"
```

### 4. Performance Issues

**Symptoms:**
- Slow page loads
- High CPU/memory usage
- Database query timeouts

**Diagnostic Steps:**
```bash
# Check system resources
htop
iotop
vmstat 1 5

# Database performance
sudo -u postgres psql -d narissa_crm -c "
SELECT query, calls, total_time, mean_time 
FROM pg_stat_statements 
ORDER BY total_time DESC 
LIMIT 10;"

# Application performance
python3 deployment/performance_optimization.py
```

**Solutions:**

#### Database Optimization
```bash
# Run database optimization
python3 -c "
from deployment.performance_optimization import DatabaseOptimizer
optimizer = DatabaseOptimizer()
result = optimizer.optimize_database_schema()
print(result)
"

# Manual database maintenance
sudo -u postgres psql -d narissa_crm -c "VACUUM ANALYZE;"
```

#### Clear Cache and Restart
```bash
# Clear Redis cache
redis-cli FLUSHALL

# Restart services
sudo systemctl restart narissa-crm nginx
```

### 5. SSL Certificate Issues

**Symptoms:**
- "Certificate expired" warnings
- HTTPS not working
- Mixed content errors

**Diagnostic Steps:**
```bash
# Check certificate status
openssl x509 -in /etc/letsencrypt/live/your-domain.com/fullchain.pem -text -noout | grep -A 2 "Validity"

# Test HTTPS connection
curl -I https://your-domain.com

# Check Nginx configuration
sudo nginx -t
```

**Solutions:**

#### Renew SSL Certificate
```bash
# Manual renewal
sudo certbot renew --dry-run
sudo certbot renew

# Restart Nginx
sudo systemctl restart nginx
```

#### Fix Certificate Permissions
```bash
sudo chmod 644 /etc/letsencrypt/live/your-domain.com/fullchain.pem
sudo chmod 600 /etc/letsencrypt/live/your-domain.com/privkey.pem
```

### 6. Backup and Restore Issues

**Symptoms:**
- Backup files corrupted
- Restore operations failing
- Missing backup files

**Diagnostic Steps:**
```bash
# Check backup status
python3 -c "
from deployment.backup_restore_system import BackupRestoreSystem
backup_system = BackupRestoreSystem()
status = backup_system.get_backup_status()
print(f'Total backups: {{status[\"total_backups\"]}}')
print(f'Last backup: {{status[\"last_full_backup\"]}}')
"

# Verify backup integrity
python3 -c "
from deployment.backup_restore_system import BackupRestoreSystem
backup_system = BackupRestoreSystem()
result = backup_system.verify_backup('/path/to/backup.db.gz')
print(result)
"
```

**Solutions:**

#### Create Manual Backup
```bash
python3 -c "
from deployment.backup_restore_system import BackupRestoreSystem
backup_system = BackupRestoreSystem()
result = backup_system.create_full_backup()
print(result)
"
```

#### Emergency Data Recovery
```bash
# Stop application
sudo systemctl stop narissa-crm

# Restore from backup
python3 -c "
from deployment.backup_restore_system import BackupRestoreSystem
backup_system = BackupRestoreSystem()
result = backup_system.restore_from_backup('/path/to/backup.db.gz')
print(result)
"

# Start application
sudo systemctl start narissa-crm
```

## Monitoring and Alerting

### Log Locations
```bash
# Application logs
/var/log/narissa-crm/app.log
/var/log/narissa-crm/error.log

# System logs
journalctl -u narissa-crm
journalctl -u nginx
journalctl -u postgresql

# Nginx logs
/var/log/nginx/access.log
/var/log/nginx/error.log
```

### Key Metrics to Monitor
- **Response time**: < 1 second target
- **Error rate**: < 5% target
- **CPU usage**: < 80% sustained
- **Memory usage**: < 85% sustained
- **Disk usage**: < 90% total
- **Database connections**: < 80% of max

### Setting Up Alerts
```bash
# Email alerts for critical issues
python3 -c "
from deployment.monitoring_system import AlertSystem
alert_system = AlertSystem()
alert_system.send_email_alert(
    'Test Alert', 
    'System is functioning normally', 
    'info'
)
"
```

## Emergency Procedures

### Complete System Recovery
```bash
# 1. Stop all services
sudo systemctl stop narissa-crm nginx

# 2. Check system integrity
sudo fsck /dev/sda1  # Adjust device as needed

# 3. Start core services
sudo systemctl start postgresql redis-server

# 4. Restore from backup if needed
# (See backup procedures above)

# 5. Start application services
sudo systemctl start narissa-crm nginx

# 6. Verify system health
curl http://localhost:8000/health
```

### Data Corruption Recovery
```bash
# 1. Stop application immediately
sudo systemctl stop narissa-crm

# 2. Create emergency backup of current state
cp /opt/narissa-crm/real_estate_crm.db /tmp/corrupted_backup_$(date +%Y%m%d_%H%M%S).db

# 3. Restore from last known good backup
python3 -c "
from deployment.backup_restore_system import BackupRestoreSystem
backup_system = BackupRestoreSystem()
status = backup_system.get_backup_status()
latest_backup = status['recent_backups'][0]['path']
result = backup_system.restore_from_backup(latest_backup)
print(result)
"

# 4. Restart application
sudo systemctl start narissa-crm

# 5. Verify data integrity
python3 -c "
from deployment.data_migration_tools import DataMigrationTools
migration_tools = DataMigrationTools()
result = migration_tools.validate_data_integrity()
print(result)
"
```

## Getting Help

### Self-Service Resources
1. Check this troubleshooting guide
2. Review system logs
3. Run diagnostic scripts
4. Check monitoring dashboard

### Escalation Procedures
1. **Level 1**: Basic troubleshooting (this guide)
2. **Level 2**: System administrator intervention
3. **Level 3**: Development team support
4. **Level 4**: Emergency vendor support

### Contact Information
- **System Admin**: admin@narissarealty.com
- **Technical Support**: support@narissarealty.com
- **Emergency Hotline**: +1-555-CRM-HELP

### Information to Include in Support Requests
- Error messages (exact text)
- Time of occurrence
- Affected users/features
- Steps taken so far
- System logs (relevant portions)
- Current system status

---

*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
    
    def _generate_deployment_guide(self) -> str:
        """Generate deployment guide"""
        return f"""# Deployment Guide - Narissa Realty CRM

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Overview

This guide covers the complete deployment process for the Narissa Realty CRM system, from initial setup to production monitoring.

## Prerequisites

### System Requirements
- Ubuntu 20.04 LTS or later
- 4GB RAM minimum (8GB recommended)
- 50GB disk space minimum
- Domain name with DNS access
- SSL certificate (Let's Encrypt supported)

### Required Services
- Python 3.8+
- PostgreSQL 12+
- Redis 6.0+
- Nginx
- Certbot (for SSL)

## Deployment Methods

### Method 1: Automated Deployment (Recommended)

Run the complete deployment automation:

```bash
# Clone repository
git clone <repository-url> /opt/narissa-crm
cd /opt/narissa-crm

# Run automated deployment
chmod +x deployment/deploy.sh
sudo ./deployment/deploy.sh
```

### Method 2: Manual Step-by-Step Deployment

#### Step 1: System Preparation
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3-pip python3-venv nginx postgresql postgresql-contrib redis-server git

# Create application user
sudo useradd -m -s /bin/bash crm
sudo usermod -aG sudo crm
```

#### Step 2: Database Setup
```bash
# Switch to postgres user
sudo -u postgres psql

-- Create database and user
CREATE DATABASE narissa_crm;
CREATE USER crm_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE narissa_crm TO crm_user;
\\q

# Test connection
psql -h localhost -U crm_user -d narissa_crm -c "SELECT 1;"
```

#### Step 3: Application Setup
```bash
# Switch to CRM user
sudo su - crm

# Create application directory
sudo mkdir -p /opt/narissa-crm
sudo chown crm:crm /opt/narissa-crm

# Clone application
git clone <repository-url> /opt/narissa-crm
cd /opt/narissa-crm

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### Step 4: Configuration
```bash
# Create environment file
cat > /opt/narissa-crm/.env << EOF
# Database Configuration
DATABASE_URL=postgresql://crm_user:your_secure_password@localhost/narissa_crm

# Security Keys
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
JWT_SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Application Settings
ENVIRONMENT=production
DEBUG=False
APP_HOST=0.0.0.0
APP_PORT=8000

# Email Configuration (configure as needed)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@domain.com
SMTP_PASSWORD=your-app-password

# Monitoring (optional)
SENTRY_DSN=your-sentry-dsn-here
EOF

# Set secure permissions
chmod 600 /opt/narissa-crm/.env
```

#### Step 5: Database Initialization
```bash
# Initialize database schema
cd /opt/narissa-crm
source venv/bin/activate
python deployment/postgresql_setup.py

# Create initial admin user
python -c "
from deployment.auth_system import UserManager
user_mgr = UserManager()
admin = user_mgr.create_user('admin', 'admin@narissarealty.com', 'AdminPass123!', 'admin')
print(f'Admin user created: {{admin.username}}')
"
```

#### Step 6: Systemd Service Setup
```bash
# Create systemd service file
sudo tee /etc/systemd/system/narissa-crm.service << EOF
[Unit]
Description=Narissa Realty CRM
After=network.target postgresql.service redis.service

[Service]
Type=exec
User=crm
Group=crm
WorkingDirectory=/opt/narissa-crm
Environment=PATH=/opt/narissa-crm/venv/bin
EnvironmentFile=/opt/narissa-crm/.env
ExecStart=/opt/narissa-crm/venv/bin/gunicorn --config deployment/gunicorn_config.py deployment.production_app:app
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable narissa-crm
sudo systemctl start narissa-crm

# Check status
sudo systemctl status narissa-crm
```

#### Step 7: Nginx Configuration
```bash
# Create Nginx configuration
sudo tee /etc/nginx/sites-available/narissa-crm << EOF
server {{
    listen 80;
    server_name your-domain.com www.your-domain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://\$server_name\$request_uri;
}}

server {{
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;
    
    # SSL Configuration (will be set up by certbot)
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=63072000" always;
    
    # Main application
    location / {{
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }}
    
    # Static files
    location /static/ {{
        alias /opt/narissa-crm/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }}
    
    # Health check
    location /health {{
        proxy_pass http://127.0.0.1:8000/health;
        access_log off;
    }}
}}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/narissa-crm /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### Step 8: SSL Certificate Setup
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Test auto-renewal
sudo certbot renew --dry-run
```

#### Step 9: Monitoring Setup
```bash
# Start monitoring system
cd /opt/narissa-crm
source venv/bin/activate
python -c "
from deployment.monitoring_system import MonitoringSystem
monitoring = MonitoringSystem()
monitoring.start_monitoring()
print('Monitoring system started')
"

# Setup automated backups
python -c "
from deployment.backup_restore_system import BackupRestoreSystem
backup_system = BackupRestoreSystem()
backup_system.schedule_automated_backups()
backup_system.start_backup_scheduler()
print('Backup system started')
"
```

## Post-Deployment Verification

### System Health Checks
```bash
# Application health
curl https://your-domain.com/health

# Database connectivity
curl https://your-domain.com/api/monitoring/metrics

# SSL certificate
curl -I https://your-domain.com

# Service status
sudo systemctl status narissa-crm nginx postgresql redis-server
```

### Performance Testing
```bash
# Run performance optimization
cd /opt/narissa-crm
source venv/bin/activate
python deployment/performance_optimization.py

# Load testing
python -c "
from deployment.performance_optimization import LoadTester
tester = LoadTester('https://your-domain.com')
result = tester.run_load_test('/health', concurrent_users=10, duration_seconds=60)
print(f'Load test completed: {{result[\"success_rate\"]}}% success rate')
"
```

### Security Validation
```bash
# Run security tests
python deployment/test_auth_system.py https://your-domain.com
python deployment/test_rbac_system.py

# SSL security test
nmap --script ssl-enum-ciphers -p 443 your-domain.com
```

## Environment-Specific Configurations

### Development Environment
```bash
# Development-specific settings in .env
ENVIRONMENT=development
DEBUG=True
DATABASE_URL=sqlite:///real_estate_crm.db

# Start development server
python app.py
```

### Staging Environment
```bash
# Staging-specific settings
ENVIRONMENT=staging
DEBUG=False
DATABASE_URL=postgresql://staging_user:password@staging-db/narissa_crm_staging

# Use staging domain
sudo certbot --nginx -d staging.narissarealty.com
```

### Production Environment
```bash
# Production settings (as shown in main deployment)
ENVIRONMENT=production
DEBUG=False
# Full monitoring and backup enabled
```

## Scaling and High Availability

### Database Scaling
```bash
# Master-slave replication setup
# (Requires additional PostgreSQL configuration)

# Connection pooling
pip install pgbouncer
# Configure pgbouncer for connection pooling
```

### Application Scaling
```bash
# Multiple Gunicorn workers
# Edit gunicorn_config.py:
workers = 4
worker_class = "gevent"
worker_connections = 1000

# Load balancing with multiple instances
# Configure Nginx upstream block
```

### Backup and Disaster Recovery
```bash
# Automated offsite backups
# Configure cloud storage backup destination

# Database replication
# Setup streaming replication to standby server

# Application clustering
# Deploy to multiple servers with shared database
```

## Maintenance and Updates

### Regular Maintenance Tasks
```bash
# Weekly maintenance script
cat > /opt/narissa-crm/maintenance.sh << 'EOF'
#!/bin/bash
cd /opt/narissa-crm
source venv/bin/activate

# Update system packages
sudo apt update && sudo apt upgrade -y

# Database maintenance
python -c "
import sqlite3
# Run VACUUM and ANALYZE
"

# Clean old logs
find /var/log -name "*.log" -mtime +30 -delete

# Check disk space
df -h

# Restart services if needed
sudo systemctl restart narissa-crm nginx
EOF

chmod +x /opt/narissa-crm/maintenance.sh

# Schedule via cron
echo "0 2 * * 0 /opt/narissa-crm/maintenance.sh" | sudo crontab -
```

### Application Updates
```bash
# Update deployment procedure
cd /opt/narissa-crm

# Backup current version
cp -r /opt/narissa-crm /opt/narissa-crm.backup.$(date +%Y%m%d)

# Pull latest code
git pull origin main

# Update dependencies
source venv/bin/activate
pip install -r requirements.txt

# Run migrations if any
python deployment/migrate_database.py

# Restart application
sudo systemctl restart narissa-crm

# Verify deployment
curl https://your-domain.com/health
```

## Troubleshooting Deployment Issues

### Common Deployment Problems

#### Permission Issues
```bash
# Fix ownership
sudo chown -R crm:crm /opt/narissa-crm

# Fix service permissions
sudo chmod 644 /etc/systemd/system/narissa-crm.service
```

#### Database Connection Issues
```bash
# Test database connection
psql -h localhost -U crm_user -d narissa_crm -c "SELECT 1;"

# Check PostgreSQL status
sudo systemctl status postgresql
```

#### SSL Certificate Issues
```bash
# Re-run certbot
sudo certbot --nginx -d your-domain.com

# Check certificate expiry
openssl x509 -in /etc/letsencrypt/live/your-domain.com/fullchain.pem -noout -dates
```

### Rollback Procedures
```bash
# Emergency rollback
sudo systemctl stop narissa-crm

# Restore from backup
cp -r /opt/narissa-crm.backup.YYYYMMDD/* /opt/narissa-crm/

# Restore database
# (Use backup restore procedures)

# Restart services
sudo systemctl start narissa-crm nginx
```

## Support and Resources

### Documentation
- System Administrator Guide: `docs/production/system_admin.md`
- API Documentation: `docs/production/api_docs.md`
- Troubleshooting Guide: `docs/production/troubleshooting.md`

### Monitoring
- Health Check: `https://your-domain.com/health`
- Monitoring Dashboard: `https://your-domain.com/api/monitoring/dashboard`
- Error Tracking: Sentry dashboard (if configured)

### Contact Information
- **System Administrator**: admin@narissarealty.com
- **Technical Support**: support@narissarealty.com
- **Emergency Contact**: +1-555-CRM-HELP

---

*Deployment guide version 1.0 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
    
    def _generate_security_documentation(self) -> str:
        """Generate security documentation"""
        return f"""# Security Documentation - Narissa Realty CRM

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Security Overview

The Narissa Realty CRM implements comprehensive security measures to protect sensitive real estate and client data.

## Authentication and Authorization

### Authentication Methods
- **Primary**: JWT token-based authentication
- **Session Management**: Redis-backed sessions with timeout
- **Password Policy**: Strong password requirements enforced
- **Account Lockout**: Automatic lockout after failed attempts

### Password Requirements
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number
- At least one special character
- Cannot be common passwords

### Role-Based Access Control (RBAC)

#### User Roles
1. **Admin**
   - Full system access
   - User management
   - System configuration
   - All data access

2. **Manager**
   - Team management
   - Client and property management
   - Transaction oversight
   - Reporting access

3. **Agent**
   - Own client management
   - Property browsing
   - Transaction creation
   - Limited reporting

#### Permission Matrix
```
Permission                    | Admin | Manager | Agent
------------------------------|-------|---------|-------
Create Users                  |   ✓   |    ✗    |   ✗
Manage Teams                  |   ✓   |    ✓    |   ✗
View All Clients              |   ✓   |    ✓    |   ✗
Manage Own Clients            |   ✓   |    ✓    |   ✓
System Configuration          |   ✓   |    ✗    |   ✗
View System Logs              |   ✓   |    ✗    |   ✗
Generate Reports              |   ✓   |    ✓    |   ✓
```

## Data Protection

### Data Classification
- **Public**: Marketing materials, property listings
- **Internal**: User profiles, system logs
- **Confidential**: Client information, financial data
- **Restricted**: Authentication credentials, encryption keys

### Data Encryption

#### At Rest
- Database encryption using PostgreSQL TDE
- File system encryption (LUKS)
- Backup encryption with AES-256

#### In Transit
- TLS 1.3 for all web traffic
- Database connections encrypted
- API communications use HTTPS only

#### Application Level
- Password hashing with bcrypt
- Sensitive data fields encrypted
- JWT tokens signed and encrypted

### Data Retention
- **Client Data**: 7 years (compliance requirement)
- **Transaction Records**: 10 years
- **System Logs**: 90 days
- **Backup Data**: 30 days rolling retention

## Network Security

### Firewall Configuration
```bash
# UFW rules for production
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow from 10.0.0.0/8 to any port 5432  # Database access
sudo ufw enable
```

### SSL/TLS Configuration
```nginx
# Strong SSL configuration
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
ssl_prefer_server_ciphers off;
ssl_session_timeout 1d;
ssl_session_cache shared:MozTLS:10m;
ssl_session_tickets off;

# HSTS
add_header Strict-Transport-Security "max-age=63072000" always;
```

### Security Headers
```nginx
# Security headers
add_header X-Frame-Options DENY;
add_header X-Content-Type-Options nosniff;
add_header X-XSS-Protection "1; mode=block";
add_header Referrer-Policy "strict-origin-when-cross-origin";
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';";
```

## Application Security

### Input Validation
- All user inputs validated and sanitized
- SQL injection prevention via parameterized queries
- XSS prevention with output encoding
- CSRF protection with tokens

### Session Management
- Secure session cookies
- Session timeout after inactivity
- Session invalidation on logout
- Concurrent session limits

### API Security
- Rate limiting (1000 requests/hour per user)
- Request size limits
- Input validation for all endpoints
- Output filtering to prevent data leakage

## Infrastructure Security

### Server Hardening
```bash
# Disable unnecessary services
sudo systemctl disable avahi-daemon
sudo systemctl disable cups
sudo systemctl disable bluetooth

# Update system
sudo apt update && sudo apt upgrade -y

# Install security updates automatically
sudo apt install unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

### SSH Security
```bash
# SSH configuration (/etc/ssh/sshd_config)
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
Port 2222  # Non-standard port
MaxAuthTries 3
ClientAliveInterval 300
ClientAliveCountMax 2
```

### Database Security
```sql
-- PostgreSQL security configuration
ALTER SYSTEM SET ssl = on;
ALTER SYSTEM SET log_connections = on;
ALTER SYSTEM SET log_disconnections = on;
ALTER SYSTEM SET log_statement = 'mod';
ALTER SYSTEM SET shared_preload_libraries = 'pg_stat_statements';
SELECT pg_reload_conf();
```

## Monitoring and Incident Response

### Security Monitoring
- Failed login attempt tracking
- Privilege escalation monitoring
- Data access audit logs
- System integrity monitoring

### Automated Alerts
```python
# Alert configuration
SECURITY_ALERTS = {{
    'failed_logins_threshold': 10,  # per hour
    'privilege_escalation': True,
    'data_access_anomalies': True,
    'system_changes': True
}}
```

### Incident Response Procedures

#### Security Incident Classification
1. **Low**: Minor policy violation
2. **Medium**: Unauthorized access attempt
3. **High**: Data breach or system compromise
4. **Critical**: Active attack or major data loss

#### Response Steps
1. **Immediate**: Contain the threat
2. **Assessment**: Determine scope and impact
3. **Communication**: Notify stakeholders
4. **Recovery**: Restore normal operations
5. **Analysis**: Post-incident review

### Backup Security
- Encrypted backup storage
- Secure backup transmission
- Regular backup testing
- Offsite backup storage

## Compliance and Auditing

### Regulatory Compliance
- **PIPEDA** (Canada): Personal information protection
- **CCPA** (California): Consumer privacy rights
- **SOX**: Financial reporting requirements
- **Industry Standards**: Real estate licensing requirements

### Audit Logging
```python
# Audit event types
AUDIT_EVENTS = [
    'user_login',
    'user_logout',
    'permission_change',
    'data_access',
    'data_modification',
    'system_configuration',
    'backup_operations'
]
```

### Access Reviews
- Quarterly user access reviews
- Annual privilege assessments
- Role-based access audits
- Terminated user access removal

## Security Best Practices

### For Administrators
1. Use strong, unique passwords
2. Enable two-factor authentication
3. Regular security updates
4. Monitor system logs
5. Backup encryption keys securely

### For Users
1. Create strong passwords
2. Log out when finished
3. Don't share credentials
4. Report suspicious activity
5. Keep software updated

### For Developers
1. Follow secure coding practices
2. Regular security testing
3. Code reviews for security
4. Dependency vulnerability scanning
5. Security training

## Security Testing

### Automated Security Scanning
```bash
# Run security tests
python deployment/test_auth_system.py
python deployment/test_rbac_system.py

# SSL/TLS testing
nmap --script ssl-enum-ciphers -p 443 your-domain.com

# Vulnerability scanning
sudo apt install nmap nikto
nikto -h https://your-domain.com
```

### Penetration Testing
- Annual third-party penetration testing
- Internal security assessments
- Code security reviews
- Infrastructure testing

## Incident Response Contacts

### Internal Team
- **Security Officer**: security@narissarealty.com
- **System Administrator**: admin@narissarealty.com
- **Development Team**: dev@narissarealty.com

### External Resources
- **Cyber Security Firm**: [Contact details]
- **Legal Counsel**: [Contact details]
- **Insurance Provider**: [Contact details]

## Security Policies

### Acceptable Use Policy
- System usage guidelines
- Data handling requirements
- Prohibited activities
- Violation consequences

### Data Protection Policy
- Data classification standards
- Handling procedures
- Retention requirements
- Disposal methods

### Incident Response Policy
- Reporting procedures
- Response team roles
- Communication protocols
- Recovery procedures

## Security Configuration Checklist

### Initial Setup
- [ ] Strong passwords for all accounts
- [ ] SSH key authentication enabled
- [ ] Firewall configured and enabled
- [ ] SSL certificates installed
- [ ] Database access restricted
- [ ] Regular backups scheduled
- [ ] Monitoring systems active

### Ongoing Maintenance
- [ ] Security updates applied monthly
- [ ] Access reviews quarterly
- [ ] Backup tests quarterly
- [ ] Penetration testing annually
- [ ] Security training annually
- [ ] Policy reviews annually

### Emergency Procedures
- [ ] Incident response plan documented
- [ ] Emergency contacts updated
- [ ] Backup recovery tested
- [ ] Disaster recovery plan
- [ ] Communication procedures
- [ ] Legal compliance verified

---

**Security Officer**: security@narissarealty.com  
**Last Security Review**: {datetime.now().strftime('%Y-%m-%d')}  
**Next Review Due**: {(datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d')}
"""

def main():
    """Generate all production documentation"""
    generator = ProductionDocumentationGenerator()
    
    print("Production Documentation Generator")
    print("=" * 40)
    
    # Generate all documentation
    results = generator.generate_all_documentation()
    
    if results['success']:
        print(f"✅ Documentation generation completed successfully!")
        print(f"Generated {len(results['generated_docs'])} documentation files:")
        
        for doc in results['generated_docs']:
            print(f"  - {doc['section']}: {doc['file_path']} ({doc['size_kb']:.1f} KB)")
        
        print(f"\n📁 Documentation available in: {generator.docs_dir}")
        print(f"📖 Start with: {generator.docs_dir}/README.md")
    else:
        print(f"❌ Documentation generation failed:")
        for error in results['errors']:
            print(f"  - {error}")

if __name__ == "__main__":
    main()