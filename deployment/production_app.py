#!/usr/bin/env python3
"""
Production Flask Application for AI-Enhanced Real Estate CRM
Optimized for production deployment with PostgreSQL and security
"""

import os
import json
from flask import Flask, request, render_template, jsonify, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
import logging
from logging.handlers import RotatingFileHandler
import uuid
from datetime import datetime
import redis
from flask_session import Session
import gunicorn

# Production Configuration Class
class ProductionConfig:
    """Production configuration with security and performance optimizations"""
    
    # Database Configuration
    DATABASE_URL = os.environ.get('DATABASE_URL') or \
        'postgresql://crm_app:CRM_App_2025_Secure!@db-narissa-realty-crm-prod.db.ondigitalocean.com:25060/narissa_realty_crm?sslmode=require'
    
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 20,
        'pool_timeout': 30,
        'pool_recycle': 3600,
        'max_overflow': 10,
        'pool_pre_ping': True,
        'echo': False  # Set to True for debugging
    }
    
    # Security Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'CRM_Prod_Secret_2025_Ultra_Secure_Key!'
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600
    
    # Session Configuration
    SESSION_TYPE = 'redis'
    SESSION_REDIS = redis.from_url(os.environ.get('REDIS_URL') or 'redis://localhost:6379')
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    SESSION_KEY_PREFIX = 'crm:'
    
    # Application Configuration
    DEBUG = False
    TESTING = False
    ENV = 'production'
    FLASK_ENV = 'production'
    
    # File Upload Configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = '/var/www/narissa-realty-crm/uploads'
    
    # Email Configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # Logging Configuration
    LOG_LEVEL = 'INFO'
    LOG_FILE = '/var/log/narissa-realty-crm/app.log'
    LOG_MAX_BYTES = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT = 5

def create_app(config_class=ProductionConfig):
    """Application factory pattern for production deployment"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db = SQLAlchemy()
    migrate = Migrate()
    
    # Initialize Flask-Session for Redis-based session management
    sess = Session()
    
    db.init_app(app)
    migrate.init_app(app, db)
    sess.init_app(app)
    
    # Configure logging
    setup_logging(app)
    
    # Register blueprints and routes
    register_routes(app, db)
    register_error_handlers(app)
    register_security_headers(app)
    
    # Health check endpoint for load balancer
    @app.route('/health')
    def health_check():
        """Health check endpoint for load balancer monitoring"""
        try:
            # Test database connection
            db.engine.execute('SELECT 1')
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'version': '1.0.0',
                'database': 'connected'
            }), 200
        except Exception as e:
            app.logger.error(f"Health check failed: {e}")
            return jsonify({
                'status': 'unhealthy',
                'timestamp': datetime.utcnow().isoformat(),
                'error': str(e)
            }), 503
    
    return app

def setup_logging(app):
    """Configure production logging with rotation"""
    if not app.debug:
        # Ensure log directory exists
        log_dir = os.path.dirname(app.config['LOG_FILE'])
        os.makedirs(log_dir, exist_ok=True)
        
        # Configure rotating file handler
        file_handler = RotatingFileHandler(
            app.config['LOG_FILE'],
            maxBytes=app.config['LOG_MAX_BYTES'],
            backupCount=app.config['LOG_BACKUP_COUNT']
        )
        
        # Set logging format
        formatter = logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s '
            '[in %(pathname)s:%(lineno)d]'
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(getattr(logging, app.config['LOG_LEVEL']))
        
        # Add handler to app logger
        app.logger.addHandler(file_handler)
        app.logger.setLevel(getattr(logging, app.config['LOG_LEVEL']))
        
        app.logger.info('AI-Enhanced Real Estate CRM startup')

def register_routes(app, db):
    """Register all application routes"""
    
    @app.route('/')
    def index():
        """Main dashboard"""
        return render_template('index.html')
    
    @app.route('/clients')
    def clients():
        """Client management interface"""
        return render_template('clients_list.html')
    
    @app.route('/properties')
    def properties():
        """Property management interface"""
        return render_template('properties_list.html')
    
    @app.route('/transactions')
    def transactions():
        """Transaction management interface"""
        return render_template('transactions_list.html')
    
    @app.route('/chatbot')
    def chatbot():
        """AI-enhanced chatbot interface"""
        return render_template('chatbot-crm.html')
    
    @app.route('/api/clients', methods=['GET', 'POST'])
    def api_clients():
        """REST API for client operations"""
        if request.method == 'GET':
            # Simulate client data (would query database in production)
            clients = [
                {
                    'id': str(uuid.uuid4()),
                    'first_name': 'John',
                    'last_name': 'Smith',
                    'email': 'john.smith@example.com',
                    'phone': '(555) 123-4567',
                    'client_type': 'buyer',
                    'status': 'active'
                }
            ]
            return jsonify(clients)
        
        elif request.method == 'POST':
            # Create new client
            client_data = request.get_json()
            
            # Validate required fields
            required_fields = ['first_name', 'last_name', 'email']
            for field in required_fields:
                if not client_data.get(field):
                    return jsonify({'error': f'Missing required field: {field}'}), 400
            
            # Simulate client creation (would save to database in production)
            new_client = {
                'id': str(uuid.uuid4()),
                'created_at': datetime.utcnow().isoformat(),
                **client_data
            }
            
            app.logger.info(f"Client created: {new_client['id']}")
            return jsonify(new_client), 201
    
    @app.route('/api/properties', methods=['GET', 'POST'])
    def api_properties():
        """REST API for property operations"""
        if request.method == 'GET':
            # Simulate property data
            properties = [
                {
                    'id': str(uuid.uuid4()),
                    'address': '123 Main St, Anytown, CA 90210',
                    'listing_price': 750000,
                    'bedrooms': 3,
                    'bathrooms': 2.5,
                    'square_feet': 2100,
                    'status': 'active'
                }
            ]
            return jsonify(properties)
        
        elif request.method == 'POST':
            # Create new property listing
            property_data = request.get_json()
            
            # Validate required fields
            required_fields = ['address_line1', 'city', 'state', 'zip_code']
            for field in required_fields:
                if not property_data.get(field):
                    return jsonify({'error': f'Missing required field: {field}'}), 400
            
            # Simulate property creation
            new_property = {
                'id': str(uuid.uuid4()),
                'created_at': datetime.utcnow().isoformat(),
                **property_data
            }
            
            app.logger.info(f"Property created: {new_property['id']}")
            return jsonify(new_property), 201
    
    @app.route('/api/email-process', methods=['POST'])
    def api_email_process():
        """AI email processing endpoint from Phase 2"""
        try:
            data = request.get_json()
            email_content = data.get('email_content', '')
            
            if not email_content:
                return jsonify({'error': 'No email content provided'}), 400
            
            # Simulate AI processing (would use actual AI in production)
            extracted_data = {
                'entities': {
                    'names': ['John Smith', 'Jane Doe'],
                    'addresses': ['123 Main St, Anytown, CA 90210'],
                    'prices': ['$750,000'],
                    'dates': ['2025-06-15'],
                    'phone_numbers': ['(555) 123-4567'],
                    'email_addresses': ['john.smith@example.com']
                },
                'confidence': 0.95,
                'processing_time': 0.8,
                'email_type': 'inquiry'
            }
            
            app.logger.info(f"Email processed with {extracted_data['confidence']} confidence")
            return jsonify(extracted_data)
            
        except Exception as e:
            app.logger.error(f"Email processing error: {e}")
            return jsonify({'error': 'Email processing failed'}), 500

def register_error_handlers(app):
    """Register custom error handlers"""
    
    @app.errorhandler(404)
    def not_found_error(error):
        app.logger.warning(f"404 error: {request.url}")
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f"500 error: {error}")
        return render_template('500.html'), 500
    
    @app.errorhandler(403)
    def forbidden_error(error):
        app.logger.warning(f"403 error: {request.url}")
        return render_template('403.html'), 403

def register_security_headers(app):
    """Add security headers to all responses"""
    
    @app.after_request
    def add_security_headers(response):
        # Security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';"
        
        return response

# WSGI entry point for production servers
app = create_app()

if __name__ == '__main__':
    # Development server (not used in production)
    app.run(host='0.0.0.0', port=5000, debug=False)