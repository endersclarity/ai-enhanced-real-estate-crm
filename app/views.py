"""
Enhanced Real Estate CRM Views
Flask Blueprint routes for authentication and CRM functionality
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from werkzeug.security import check_password_hash
from .models import User, Client, Property
from .forms import LoginForm, ClientForm, PropertyForm

# Create blueprints
main_bp = Blueprint('main', __name__)
auth_bp = Blueprint('auth', __name__)
crm_bp = Blueprint('crm', __name__)

@main_bp.route('/')
def index():
    """Main landing page - redirect to dashboard if logged in"""
    if 'user_id' in session:
        return redirect(url_for('crm.dashboard'))
    return redirect(url_for('auth.login'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User authentication"""
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            session['user_id'] = user.id
            session['username'] = user.username
            flash('Login successful!', 'success')
            return redirect(url_for('crm.dashboard'))
        flash('Invalid username or password', 'error')
    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
def logout():
    """User logout"""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

@crm_bp.route('/dashboard')
def dashboard():
    """Main CRM dashboard"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    # Get recent activity for dashboard
    recent_clients = Client.query.order_by(Client.created_at.desc()).limit(5).all()
    recent_properties = Property.query.order_by(Property.created_at.desc()).limit(5).all()
    
    stats = {
        'total_clients': Client.query.count(),
        'total_properties': Property.query.count(),
        'active_listings': Property.query.filter_by(status='active').count()
    }
    
    return render_template('dashboard/main.html', 
                         recent_clients=recent_clients,
                         recent_properties=recent_properties,
                         stats=stats)

@crm_bp.route('/clients')
def clients():
    """Client management page"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    clients = Client.query.all()
    return render_template('crm/clients.html', clients=clients)

@crm_bp.route('/properties')
def properties():
    """Property management page"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    properties = Property.query.all()
    return render_template('crm/properties.html', properties=properties)
