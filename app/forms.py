# Enhanced Real Estate CRM Forms (Boilerplate Integration)
# Professional form processing with Flask-WTF patterns

from flask_wtf import FlaskForm
from wtforms import (
    StringField, TextAreaField, SelectField, IntegerField, 
    FloatField, DateTimeField, BooleanField, PasswordField,
    RadioField, SelectMultipleField, HiddenField, SubmitField
)
from wtforms.validators import (
    DataRequired, Email, Length, Optional, NumberRange,
    ValidationError, EqualTo, Regexp
)
from wtforms.widgets import TextArea
# Import enums directly to avoid circular imports
from enum import Enum

# Define enum choices directly
CLIENT_TYPE_CHOICES = [
    ('buyer', 'Buyer'),
    ('seller', 'Seller'),
    ('both', 'Both'),
    ('investor', 'Investor')
]

PROPERTY_STATUS_CHOICES = [
    ('active', 'Active'),
    ('pending', 'Pending'),
    ('sold', 'Sold'),
    ('withdrawn', 'Withdrawn'),
    ('expired', 'Expired')
]

INTERACTION_TYPE_CHOICES = [
    ('call', 'Phone Call'),
    ('email', 'Email'),
    ('text', 'Text Message'),
    ('meeting', 'Meeting'),
    ('showing', 'Property Showing'),
    ('viewing', 'Property Viewing'),
    ('offer', 'Offer Discussion'),
    ('follow_up', 'Follow Up')
]
import re

# ============================================================================
# Authentication Forms (From Flask Boilerplate)
# ============================================================================

class LoginForm(FlaskForm):
    """User login form"""
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    """User registration form for new agents"""
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=4, max=20),
        Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0, 'Usernames must start with a letter and contain only letters, numbers, dots or underscores')
    ])
    email = StringField('Email', validators=[DataRequired(), Email()])
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=50)])
    phone = StringField('Phone', validators=[Optional(), Length(max=20)])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long')
    ])
    password_confirm = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])

class ForgotPasswordForm(FlaskForm):
    """Password reset request form"""
    email = StringField('Email', validators=[DataRequired(), Email()])

class ResetPasswordForm(FlaskForm):
    """Password reset form"""
    password = PasswordField('New Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long')
    ])
    password_confirm = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])

# ============================================================================
# Lead Capture Forms (Your Sister's Primary Need)
# ============================================================================

class LeadCaptureForm(FlaskForm):
    """Main lead capture form for website integration"""
    # Basic Information
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=50)])
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number', validators=[DataRequired(), Length(max=20)])
    secondary_phone = StringField('Secondary Phone', validators=[Optional(), Length(max=20)])
    
    # Real Estate Intent
    client_type = SelectField('I am a...', choices=[
        ('buyer', 'Looking to Buy'),
        ('seller', 'Looking to Sell'),
        ('both', 'Both Buying and Selling'),
        ('investor', 'Real Estate Investor')
    ], default='buyer')
    
    # Budget Information (for buyers)
    budget_min = IntegerField('Minimum Budget ($)', validators=[Optional()])
    budget_max = IntegerField('Maximum Budget ($)', validators=[Optional()])
    
    # Location Preferences
    preferred_areas = TextAreaField('Preferred Areas/Neighborhoods', validators=[Optional()])
    
    # Property Requirements
    bedrooms = SelectField('Bedrooms', choices=[
        ('', 'Any'),
        ('1', '1+'), ('2', '2+'), ('3', '3+'), ('4', '4+'), ('5', '5+')
    ], validators=[Optional()])
    
    bathrooms = SelectField('Bathrooms', choices=[
        ('', 'Any'),
        ('1', '1+'), ('2', '2+'), ('3', '3+'), ('4', '4+')
    ], validators=[Optional()])
    
    property_type = SelectField('Property Type', choices=[
        ('', 'Any'),
        ('house', 'Single Family Home'),
        ('condo', 'Condominium'),
        ('townhouse', 'Townhouse'),
        ('multi_family', 'Multi-Family'),
        ('commercial', 'Commercial')
    ], validators=[Optional()])
    
    # Timeline
    timeline = SelectField('Timeline', choices=[
        ('immediate', 'Ready Now'),
        ('30days', 'Within 30 Days'),
        ('3months', 'Within 3 Months'),
        ('6months', 'Within 6 Months'),
        ('exploring', 'Just Exploring')
    ], default='3months')
    
    # Lead Source Tracking
    lead_source = HiddenField('Lead Source')  # Populated by JavaScript/UTM params
    
    # Additional Information
    additional_notes = TextAreaField('Additional Comments or Questions', 
                                   validators=[Optional(), Length(max=1000)])
    
    # Marketing Consent
    marketing_consent = BooleanField('I agree to receive marketing communications via email/text')
    
    def validate_budget_min(self, budget_min):
        if budget_min.data and budget_min.data < 0:
            raise ValidationError('Budget must be a positive number')
    
    def validate_budget_max(self, budget_max):
        if budget_max.data and self.budget_min.data:
            if budget_max.data < self.budget_min.data:
                raise ValidationError('Maximum budget must be greater than minimum budget')

class QuickContactForm(FlaskForm):
    """Simplified contact form for property pages"""
    name = StringField('Full Name', validators=[DataRequired(), Length(max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone', validators=[DataRequired(), Length(max=20)])
    message = TextAreaField('Message', validators=[Optional(), Length(max=500)])
    property_id = HiddenField('Property ID')

# ============================================================================
# Client Management Forms
# ============================================================================

class ClientForm(FlaskForm):
    """Comprehensive client creation/editing form"""
    # Basic Information
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Primary Phone', validators=[DataRequired(), Length(max=20)])
    secondary_phone = StringField('Secondary Phone', validators=[Optional(), Length(max=20)])
    
    # Real Estate Profile
    client_type = SelectField('Client Type', choices=CLIENT_TYPE_CHOICES)
    
    # Financial Information
    budget_min = IntegerField('Minimum Budget', validators=[Optional()])
    budget_max = IntegerField('Maximum Budget', validators=[Optional()])
    qualification_status = SelectField('Qualification Status', choices=[
        ('unqualified', 'Not Qualified'),
        ('pre_approved', 'Pre-Approved'),
        ('cash_buyer', 'Cash Buyer'),
        ('financing_pending', 'Financing Pending'),
        ('qualified', 'Fully Qualified')
    ], default='unqualified')
    
    # Preferences
    preferred_areas = TextAreaField('Preferred Areas', validators=[Optional()])
    property_requirements = TextAreaField('Property Requirements', 
                                        render_kw={'rows': 4},
                                        validators=[Optional()])
    timeline = SelectField('Timeline', choices=[
        ('immediate', 'Immediate'),
        ('30days', '30 Days'),
        ('3months', '3 Months'),
        ('6months', '6 Months'),
        ('1year', '1 Year'),
        ('flexible', 'Flexible')
    ])
    
    # Lead Management
    lead_source = StringField('Lead Source', validators=[Optional(), Length(max=100)])
    lead_quality = SelectField('Lead Quality', choices=[
        ('hot', 'Hot'),
        ('warm', 'Warm'),
        ('cold', 'Cold')
    ], default='warm')
    
    # Notes
    notes = TextAreaField('Notes', render_kw={'rows': 6}, validators=[Optional()])

class ClientSearchForm(FlaskForm):
    """Client search and filtering form"""
    search_term = StringField('Search', validators=[Optional()])
    client_type = SelectField('Client Type', choices=[
        ('', 'All Types')] + CLIENT_TYPE_CHOICES)
    lead_quality = SelectField('Lead Quality', choices=[
        ('', 'All Qualities'),
        ('hot', 'Hot'),
        ('warm', 'Warm'),
        ('cold', 'Cold')
    ])
    agent_id = SelectField('Agent', choices=[], coerce=int, validators=[Optional()])

# ============================================================================
# Property Management Forms
# ============================================================================

class PropertyForm(FlaskForm):
    """Property listing creation/editing form"""
    # MLS Information
    mls_number = StringField('MLS Number', validators=[Optional(), Length(max=50)])
    listing_id = StringField('Listing ID', validators=[Optional(), Length(max=100)])
    
    # Location
    address = StringField('Street Address', validators=[DataRequired(), Length(max=200)])
    city = StringField('City', validators=[DataRequired(), Length(max=100)])
    state = StringField('State', validators=[Optional(), Length(max=10)], default='CA')
    zip_code = StringField('ZIP Code', validators=[DataRequired(), Length(max=10)])
    county = StringField('County', validators=[Optional(), Length(max=100)])
    
    # Property Details
    property_type = SelectField('Property Type', choices=[
        ('house', 'Single Family Home'),
        ('condo', 'Condominium'),
        ('townhouse', 'Townhouse'),
        ('multi_family', 'Multi-Family'),
        ('commercial', 'Commercial'),
        ('land', 'Land/Lot'),
        ('other', 'Other')
    ])
    
    price = FloatField('List Price', validators=[DataRequired(), NumberRange(min=0)])
    bedrooms = IntegerField('Bedrooms', validators=[Optional(), NumberRange(min=0, max=20)])
    bathrooms = FloatField('Bathrooms', validators=[Optional(), NumberRange(min=0, max=20)])
    square_feet = IntegerField('Square Feet', validators=[Optional(), NumberRange(min=0)])
    lot_size = FloatField('Lot Size (acres)', validators=[Optional(), NumberRange(min=0)])
    year_built = IntegerField('Year Built', validators=[Optional(), NumberRange(min=1800, max=2030)])
    
    # Listing Information
    status = SelectField('Status', choices=PROPERTY_STATUS_CHOICES, default='active')
    
    listing_date = DateTimeField('Listing Date', validators=[Optional()])
    listing_office = StringField('Listing Office', validators=[Optional(), Length(max=200)])
    
    # Description and Features
    description = TextAreaField('Property Description', 
                               render_kw={'rows': 6},
                               validators=[Optional()])
    features = TextAreaField('Key Features (one per line)',
                           render_kw={'rows': 4},
                           validators=[Optional()])
    virtual_tour_url = StringField('Virtual Tour URL', validators=[Optional(), Length(max=500)])
    
    def validate_zip_code(self, zip_code):
        # Basic US ZIP code validation
        if zip_code.data and not re.match(r'^\d{5}(-\d{4})?$', zip_code.data):
            raise ValidationError('Please enter a valid ZIP code (e.g., 12345 or 12345-6789)')

class PropertySearchForm(FlaskForm):
    """Property search and filtering form"""
    search_term = StringField('Search', validators=[Optional()])
    min_price = IntegerField('Min Price', validators=[Optional(), NumberRange(min=0)])
    max_price = IntegerField('Max Price', validators=[Optional(), NumberRange(min=0)])
    bedrooms = SelectField('Min Bedrooms', choices=[
        ('', 'Any'),
        ('1', '1+'), ('2', '2+'), ('3', '3+'), ('4', '4+'), ('5', '5+')
    ])
    bathrooms = SelectField('Min Bathrooms', choices=[
        ('', 'Any'),
        ('1', '1+'), ('2', '2+'), ('3', '3+'), ('4', '4+')
    ])
    property_type = SelectField('Property Type', choices=[
        ('', 'All Types'),
        ('house', 'House'),
        ('condo', 'Condo'),
        ('townhouse', 'Townhouse'),
        ('multi_family', 'Multi-Family'),
        ('commercial', 'Commercial')
    ])
    status = SelectField('Status', choices=[
        ('', 'All Statuses')] + PROPERTY_STATUS_CHOICES)
    city = StringField('City', validators=[Optional()])
    zip_code = StringField('ZIP Code', validators=[Optional()])

# ============================================================================
# Interaction and Task Management Forms
# ============================================================================

class InteractionForm(FlaskForm):
    """Client interaction logging form"""
    client_id = SelectField('Client', choices=[], coerce=int, validators=[DataRequired()])
    interaction_type = SelectField('Type', choices=INTERACTION_TYPE_CHOICES)
    
    subject = StringField('Subject', validators=[Optional(), Length(max=200)])
    notes = TextAreaField('Notes', render_kw={'rows': 4}, validators=[Optional()])
    outcome = SelectField('Outcome', choices=[
        ('positive', 'Positive'),
        ('neutral', 'Neutral'),
        ('negative', 'Negative'),
        ('no_answer', 'No Answer/Response')
    ], validators=[Optional()])
    
    duration_minutes = IntegerField('Duration (minutes)', validators=[Optional()])
    property_id = SelectField('Related Property', choices=[], coerce=int, validators=[Optional()])
    
    # Follow-up
    follow_up_required = BooleanField('Follow-up Required')
    follow_up_date = DateTimeField('Follow-up Date', validators=[Optional()])
    follow_up_notes = TextAreaField('Follow-up Notes', validators=[Optional()])

class TaskForm(FlaskForm):
    """Task creation and management form"""
    title = StringField('Task Title', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Description', render_kw={'rows': 4}, validators=[Optional()])
    priority = SelectField('Priority', choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High')
    ], default='medium')
    
    due_date = DateTimeField('Due Date', validators=[Optional()])
    reminder_date = DateTimeField('Reminder Date', validators=[Optional()])
    
    # Optional associations
    client_id = SelectField('Related Client', choices=[], coerce=int, validators=[Optional()])
    property_id = SelectField('Related Property', choices=[], coerce=int, validators=[Optional()])

# ============================================================================
# Property Matching and Interest Forms
# ============================================================================

class PropertyInterestForm(FlaskForm):
    """Track client interest in properties"""
    client_id = SelectField('Client', choices=[], coerce=int, validators=[DataRequired()])
    property_id = SelectField('Property', choices=[], coerce=int, validators=[DataRequired()])
    interest_level = SelectField('Interest Level', choices=[
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low')
    ], default='medium')
    
    notes = TextAreaField('Notes', validators=[Optional()])
    showing_requested = BooleanField('Showing Requested')
    showing_date = DateTimeField('Showing Date', validators=[Optional()])

# ============================================================================
# Form Helper Functions
# ============================================================================

def validate_phone_number(form, field):
    """Custom phone number validator"""
    if field.data:
        # Remove common phone number formatting
        phone = re.sub(r'[^\d]', '', field.data)
        if len(phone) != 10:
            raise ValidationError('Please enter a valid 10-digit phone number')
