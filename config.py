#!/usr/bin/env python3
"""
Production Configuration Management - Task #6
Environment-based configuration for Real Estate CRM
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration with environment variable loading"""
    
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    FLASK_ENV = os.environ.get('FLASK_ENV', 'development')
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Server Configuration
    HOST = os.environ.get('HOST', '0.0.0.0')
    PORT = int(os.environ.get('PORT', 5000))
    
    # Database Configuration
    USE_SUPABASE = os.environ.get('USE_SUPABASE', 'true').lower() == 'true'
    
    # Supabase Configuration
    SUPABASE_URL = os.environ.get('SUPABASE_URL')
    SUPABASE_ANON_KEY = os.environ.get('SUPABASE_ANON_KEY')
    SUPABASE_SERVICE_ROLE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')
    
    # AI Integration
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
    
    # Security
    CSRF_SECRET_KEY = os.environ.get('CSRF_SECRET_KEY', SECRET_KEY)
    
    # Feature Flags
    ENABLE_AI_CHATBOT = os.environ.get('ENABLE_AI_CHATBOT', 'true').lower() == 'true'
    ENABLE_EMAIL_PROCESSING = os.environ.get('ENABLE_EMAIL_PROCESSING', 'true').lower() == 'true'
    ENABLE_WORKFLOW_AUTOMATION = os.environ.get('ENABLE_WORKFLOW_AUTOMATION', 'true').lower() == 'true'
    
    # File Upload
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16MB
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads/')
    
    # Email Configuration (optional)
    SMTP_SERVER = os.environ.get('SMTP_SERVER')
    SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))
    SMTP_USERNAME = os.environ.get('SMTP_USERNAME')
    SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD')
    
    @classmethod
    def validate_required_config(cls):
        """Validate required environment variables are set"""
        required_vars = []
        
        if cls.USE_SUPABASE:
            required_vars.extend([
                ('SUPABASE_URL', cls.SUPABASE_URL),
                ('SUPABASE_ANON_KEY', cls.SUPABASE_ANON_KEY),
                ('SUPABASE_SERVICE_ROLE_KEY', cls.SUPABASE_SERVICE_ROLE_KEY)
            ])
        
        if cls.ENABLE_AI_CHATBOT:
            required_vars.append(('GEMINI_API_KEY', cls.GEMINI_API_KEY))
        
        missing_vars = [var_name for var_name, var_value in required_vars if not var_value]
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        return True
    
    @classmethod
    def get_database_config(cls):
        """Get database configuration dictionary"""
        if cls.USE_SUPABASE:
            return {
                'type': 'supabase',
                'url': cls.SUPABASE_URL,
                'anon_key': cls.SUPABASE_ANON_KEY,
                'service_role_key': cls.SUPABASE_SERVICE_ROLE_KEY
            }
        else:
            return {
                'type': 'sqlite',
                'path': 'real_estate_crm.db'
            }
    
    @classmethod
    def get_ai_config(cls):
        """Get AI integration configuration"""
        return {
            'enabled': cls.ENABLE_AI_CHATBOT,
            'gemini_api_key': cls.GEMINI_API_KEY,
            'email_processing': cls.ENABLE_EMAIL_PROCESSING,
            'workflow_automation': cls.ENABLE_WORKFLOW_AUTOMATION
        }

class DevelopmentConfig(Config):
    """Development-specific configuration"""
    DEBUG = True
    FLASK_ENV = 'development'

class ProductionConfig(Config):
    """Production-specific configuration"""
    DEBUG = False
    FLASK_ENV = 'production'
    
    @classmethod
    def validate_production_config(cls):
        """Additional validation for production environment"""
        cls.validate_required_config()
        
        # Production-specific validations
        if cls.SECRET_KEY == 'dev-secret-key-change-in-production':
            raise ValueError("Production SECRET_KEY must be changed from default")
        
        if cls.DEBUG:
            raise ValueError("DEBUG must be False in production")
        
        return True

class TestingConfig(Config):
    """Testing-specific configuration"""
    TESTING = True
    DEBUG = True
    USE_SUPABASE = False  # Use SQLite for testing

# Configuration factory
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config(config_name=None):
    """Get configuration class based on environment"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    return config.get(config_name, config['default'])

# Current configuration instance
current_config = get_config()