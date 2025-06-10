#!/usr/bin/env python3
"""
Database Initialization Script for Flask CRM
Creates proper database schema for the enhanced Flask application
"""

import os
import sys
import shutil
from datetime import datetime

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from app import create_app, db
from app.models import User, Client, Property, Interaction, Task

def backup_existing_database():
    """Backup existing database if it exists"""
    db_path = 'real_estate_crm.db'
    if os.path.exists(db_path):
        backup_path = f'real_estate_crm_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
        shutil.copy(db_path, backup_path)
        print(f"✅ Database backed up to {backup_path}")
        return backup_path
    return None

def initialize_database():
    """Initialize database with proper Flask schema"""
    print("🏗️ Initializing Flask CRM Database...")
    
    # Create Flask app
    app = create_app()
    
    with app.app_context():
        # Drop all existing tables and recreate
        db.drop_all()
        print("🗑️ Dropped existing tables")
        
        # Create all tables from models
        db.create_all()
        print("✅ Created new database schema")
        
        # Verify admin user exists (should be created by app factory)
        admin_user = User.query.filter_by(username='admin').first()
        if admin_user:
            print(f"✅ Admin user verified: {admin_user.username}")
        else:
            print("⚠️ No admin user found, creating one...")
            admin_user = User(
                username='admin',
                email='admin@localhost',
                first_name='Admin',
                last_name='User',
                role='admin'
            )
            admin_user.set_password('admin123')
            db.session.add(admin_user)
            db.session.commit()
            print("✅ Admin user created")
        
        # Add sample data for testing
        create_sample_data(admin_user)
        
        print("🎉 Database initialization complete!")

def create_sample_data(admin_user):
    """Create sample data for testing"""
    print("📝 Creating sample data...")
    
    # Create sample client
    sample_client = Client(
        first_name='John',
        last_name='Doe',
        email='john.doe@example.com',
        phone='555-0123',
        client_type='buyer',
        budget_min=300000,
        budget_max=500000,
        agent_id=admin_user.id,
        lead_source='website',
        lead_quality='warm'
    )
    db.session.add(sample_client)
    
    # Create sample property
    sample_property = Property(
        address='123 Main St',
        city='Sacramento',
        state='CA',
        zip_code='95814',
        property_type='house',
        price=450000,
        bedrooms=3,
        bathrooms=2.0,
        square_feet=1500,
        status='active',
        listing_agent_id=admin_user.id
    )
    db.session.add(sample_property)
    
    # Create sample task
    sample_task = Task(
        title='Follow up with John Doe',
        description='Call client to discuss property showing',
        priority='high',
        status='pending',
        agent_id=admin_user.id
    )
    db.session.add(sample_task)
    
    db.session.commit()
    print("✅ Sample data created")

def verify_database():
    """Verify database structure and content"""
    print("🔍 Verifying database...")
    
    app = create_app()
    with app.app_context():
        # Check tables exist
        tables = db.engine.table_names()
        print(f"📊 Tables created: {', '.join(tables)}")
        
        # Check content
        user_count = User.query.count()
        client_count = Client.query.count()
        property_count = Property.query.count()
        task_count = Task.query.count()
        
        print(f"👥 Users: {user_count}")
        print(f"🏠 Clients: {client_count}")
        print(f"🏡 Properties: {property_count}")
        print(f"📋 Tasks: {task_count}")
        
        # Test the query that was failing
        try:
            active_properties = Property.query.filter_by(status='active').count()
            print(f"✅ Active properties query works: {active_properties} properties")
        except Exception as e:
            print(f"❌ Active properties query failed: {e}")

if __name__ == '__main__':
    print("🚀 Flask CRM Database Initialization")
    print("====================================")
    
    # Backup existing database
    backup_file = backup_existing_database()
    
    # Initialize new database
    initialize_database()
    
    # Verify everything works
    verify_database()
    
    print("\n🎯 Next Steps:")
    print("1. Start the Flask application")
    print("2. Navigate to http://localhost:5000")
    print("3. Login with admin/admin123")
    print("4. Test the dashboard and navigation")
    
    if backup_file:
        print(f"\n💾 Previous database backed up to: {backup_file}")
