# Enhanced Real Estate CRM Models (Boilerplate Integration)
# Combining RealPython Flask patterns with your existing real estate domain

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import enum

# Import db from app factory
from . import db

# ============================================================================
# Authentication Models (From Flask Boilerplate)
# ============================================================================

class User(UserMixin, db.Model):
    """User authentication model for agents and admins"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20))
    
    # Role and permissions
    role = db.Column(db.String(20), default='agent')  # agent, admin, assistant
    is_active = db.Column(db.Boolean, default=True)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships (simplified for now - can be restored when schema is unified)
    # clients = db.relationship('Client', backref='agent', lazy=True)
    # properties = db.relationship('Property', backref='listing_agent', lazy=True)
    # interactions = db.relationship('Interaction', backref='agent', lazy=True)
    
    def set_password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.password_hash, password)
    
    @property
    def full_name(self):
        """Return full name"""
        return f"{self.first_name} {self.last_name}"
    
    def __repr__(self):
        return f'<User {self.username}>'

# ============================================================================
# Real Estate Core Models (Enhanced from your existing)
# ============================================================================

class ClientTypeEnum(enum.Enum):
    BUYER = "buyer"
    SELLER = "seller"
    BOTH = "both"
    INVESTOR = "investor"

class PropertyStatusEnum(enum.Enum):
    ACTIVE = "active"
    PENDING = "pending"
    SOLD = "sold"
    WITHDRAWN = "withdrawn"
    EXPIRED = "expired"

class InteractionTypeEnum(enum.Enum):
    CALL = "call"
    EMAIL = "email"
    TEXT = "text"
    MEETING = "meeting"
    SHOWING = "showing"
    VIEWING = "viewing"
    OFFER = "offer"
    FOLLOW_UP = "follow_up"

class Client(db.Model):
    """Enhanced client model matching existing database schema"""
    __tablename__ = 'clients'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Basic Information (matching existing schema)
    client_type = db.Column(db.String(20), nullable=False)  # buyer, seller, etc.
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), index=True)
    home_phone = db.Column(db.String(20))  # matches existing 'home_phone' column
    city = db.Column(db.String(100))  # matches existing 'city' column
    status = db.Column(db.String(20), default='active')  # matches existing 'status' column
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Properties for compatibility with Flask forms
    @property
    def phone(self):
        """Alias for home_phone to maintain compatibility"""
        return self.home_phone
    
    @phone.setter
    def phone(self, value):
        """Setter for phone property"""
        self.home_phone = value
    
    # Relationships (removed due to schema mismatch - can be added back later)
    # interactions = db.relationship('Interaction', backref='client', lazy=True, cascade='all, delete-orphan')
    # property_interests = db.relationship('PropertyInterest', backref='client', lazy=True)
    # transactions = db.relationship('Transaction', backref='client', lazy=True)
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def __repr__(self):
        return f'<Client {self.full_name}>'

class Property(db.Model):
    """Enhanced property model with MLS integration capabilities"""
    __tablename__ = 'properties'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # MLS Information
    mls_number = db.Column(db.String(50), unique=True, index=True)
    listing_id = db.Column(db.String(100))  # External listing ID
    
    # Location
    address = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(10), nullable=False, default='CA')
    zip_code = db.Column(db.String(10), nullable=False)
    county = db.Column(db.String(100))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    
    # Property Details
    property_type = db.Column(db.String(50))  # house, condo, townhouse, etc.
    price = db.Column(db.Float, nullable=False)
    bedrooms = db.Column(db.Integer)
    bathrooms = db.Column(db.Float)
    square_feet = db.Column(db.Integer)
    lot_size = db.Column(db.Float)
    year_built = db.Column(db.Integer)
    
    # Listing Information
    status = db.Column(db.Enum(PropertyStatusEnum), default=PropertyStatusEnum.ACTIVE)
    listing_date = db.Column(db.DateTime)
    days_on_market = db.Column(db.Integer)
    price_per_sqft = db.Column(db.Float)
    
    # Agent and Office
    listing_agent_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    listing_office = db.Column(db.String(200))
    
    # Additional Details
    description = db.Column(db.Text)
    features = db.Column(db.Text)  # JSON string of features
    photos = db.Column(db.Text)  # JSON array of photo URLs
    virtual_tour_url = db.Column(db.String(500))
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    updated_date = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    interests = db.relationship('PropertyInterest', backref='property', lazy=True)
    transactions = db.relationship('Transaction', backref='property', lazy=True)
    
    @property
    def full_address(self):
        return f"{self.address}, {self.city}, {self.state} {self.zip_code}"
    
    def __repr__(self):
        return f'<Property {self.address}>'

class Interaction(db.Model):
    """Client interaction tracking with follow-up management"""
    __tablename__ = 'interactions'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Core Information
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    agent_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    interaction_type = db.Column(db.Enum(InteractionTypeEnum), nullable=False)
    
    # Content
    subject = db.Column(db.String(200))
    notes = db.Column(db.Text)
    outcome = db.Column(db.String(100))  # positive, neutral, negative, no_answer
    
    # Timing
    interaction_date = db.Column(db.DateTime, default=datetime.utcnow)
    duration_minutes = db.Column(db.Integer)
    
    # Follow-up Management
    follow_up_required = db.Column(db.Boolean, default=False)
    follow_up_date = db.Column(db.DateTime)
    follow_up_notes = db.Column(db.Text)
    follow_up_completed = db.Column(db.Boolean, default=False)
    
    # Property Context (if applicable)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id'))
    
    def __repr__(self):
        return f'<Interaction {self.interaction_type.value} with {self.client.full_name}>'

class PropertyInterest(db.Model):
    """Track client interest in specific properties"""
    __tablename__ = 'property_interests'
    
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id'), nullable=False)
    
    interest_level = db.Column(db.String(20))  # high, medium, low
    notes = db.Column(db.Text)
    showing_requested = db.Column(db.Boolean, default=False)
    showing_date = db.Column(db.DateTime)
    feedback = db.Column(db.Text)
    
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Interest: {self.client.full_name} -> {self.property.address}>'

class Transaction(db.Model):
    """Real estate transaction tracking"""
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Core Information
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id'), nullable=False)
    agent_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Transaction Details
    transaction_type = db.Column(db.String(20))  # purchase, sale, lease
    offer_price = db.Column(db.Float)
    accepted_price = db.Column(db.Float)
    commission_rate = db.Column(db.Float)
    commission_amount = db.Column(db.Float)
    
    # Timeline
    offer_date = db.Column(db.DateTime)
    acceptance_date = db.Column(db.DateTime)
    inspection_date = db.Column(db.DateTime)
    closing_date = db.Column(db.DateTime)
    
    # Status
    status = db.Column(db.String(30))  # pending, accepted, in_escrow, closed, cancelled
    notes = db.Column(db.Text)
    
    # Documents (JSON array of document URLs/paths)
    documents = db.Column(db.Text)
    
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    updated_date = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Transaction {self.transaction_type}: {self.property.address}>'

# ============================================================================
# Lead Management Models
# ============================================================================

class LeadSource(db.Model):
    """Track and analyze lead sources for marketing ROI"""
    __tablename__ = 'lead_sources'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    cost_per_lead = db.Column(db.Float)
    conversion_rate = db.Column(db.Float)
    active = db.Column(db.Boolean, default=True)
    
    created_date = db.Column(db.DateTime, default=datetime.utcnow)

class Task(db.Model):
    """Task and follow-up management"""
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Assignment
    agent_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'))
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id'))
    
    # Task Details
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    priority = db.Column(db.String(20), default='medium')  # high, medium, low
    status = db.Column(db.String(20), default='pending')  # pending, in_progress, completed, cancelled
    
    # Timing
    due_date = db.Column(db.DateTime)
    reminder_date = db.Column(db.DateTime)
    completed_date = db.Column(db.DateTime)
    
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    updated_date = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    agent = db.relationship('User', backref='tasks')
    
    def __repr__(self):
        return f'<Task: {self.title}>'

# ============================================================================
# Utility Functions
# ============================================================================

def init_database(app):
    """Initialize database with app context"""
    with app.app_context():
        db.create_all()
        
        # Create default admin user if none exists
        if not User.query.filter_by(role='admin').first():
            admin = User(
                username='admin',
                email='admin@realestate.local',
                first_name='System',
                last_name='Administrator',
                role='admin'
            )
            admin.set_password('admin123')  # Change in production!
            db.session.add(admin)
            db.session.commit()
            print("✅ Default admin user created")
