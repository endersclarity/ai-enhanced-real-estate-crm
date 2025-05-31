#!/usr/bin/env python3
"""
User Authentication System for Narissa Realty CRM
Implements Flask-Login, bcrypt password hashing, Redis sessions, and password reset
"""

import os
import redis
import bcrypt
import secrets
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, request, session, jsonify, render_template_string
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
import logging
import json
import sqlite3
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AuthConfig:
    """Authentication system configuration"""
    
    # Redis configuration for session management
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
    REDIS_DB = int(os.getenv('REDIS_DB', 0))
    REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', None)
    
    # Session configuration
    SECRET_KEY = os.getenv('SECRET_KEY', secrets.token_hex(32))
    SESSION_TIMEOUT = int(os.getenv('SESSION_TIMEOUT', 3600))  # 1 hour
    REMEMBER_COOKIE_DURATION = timedelta(days=30)
    
    # Password requirements
    MIN_PASSWORD_LENGTH = 8
    REQUIRE_UPPERCASE = True
    REQUIRE_LOWERCASE = True
    REQUIRE_DIGITS = True
    REQUIRE_SPECIAL_CHARS = True
    
    # Email configuration for password reset
    SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
    SMTP_EMAIL = os.getenv('SMTP_EMAIL', 'admin@narissarealty.com')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
    
    # Security settings
    MAX_LOGIN_ATTEMPTS = 5
    LOCKOUT_DURATION = 900  # 15 minutes
    PASSWORD_RESET_TIMEOUT = 3600  # 1 hour

class User(UserMixin):
    """User model for Flask-Login"""
    
    def __init__(self, user_id, username, email, password_hash, role='agent', 
                 is_active=True, last_login=None, failed_login_attempts=0, 
                 locked_until=None, created_at=None):
        self.id = user_id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.role = role
        self.is_active = is_active
        self.last_login = last_login
        self.failed_login_attempts = failed_login_attempts
        self.locked_until = locked_until
        self.created_at = created_at or datetime.now()
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def is_account_locked(self):
        """Check if account is locked due to failed login attempts"""
        if self.locked_until:
            locked_until = datetime.fromisoformat(self.locked_until)
            return datetime.now() < locked_until
        return False
    
    def can_login(self):
        """Check if user can login (active and not locked)"""
        return self.is_active and not self.is_account_locked()
    
    def to_dict(self):
        """Convert user to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'is_active': self.is_active,
            'last_login': self.last_login,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at
        }

class UserManager:
    """Manages user operations and database interactions"""
    
    def __init__(self, db_path="real_estate_crm.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize user tables in database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT DEFAULT 'agent',
                    is_active BOOLEAN DEFAULT 1,
                    last_login TIMESTAMP,
                    failed_login_attempts INTEGER DEFAULT 0,
                    locked_until TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Password reset tokens table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS password_reset_tokens (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    token TEXT UNIQUE NOT NULL,
                    expires_at TIMESTAMP NOT NULL,
                    used BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # User sessions table (backup to Redis)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    session_id TEXT UNIQUE NOT NULL,
                    ip_address TEXT,
                    user_agent TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            conn.commit()
            logger.info("User database tables initialized")
    
    def create_user(self, username, email, password, role='agent'):
        """Create a new user with hashed password"""
        # Validate password strength
        if not self.validate_password_strength(password):
            raise ValueError("Password does not meet strength requirements")
        
        # Hash password
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    INSERT INTO users (username, email, password_hash, role)
                    VALUES (?, ?, ?, ?)
                ''', (username, email, password_hash, role))
                
                user_id = cursor.lastrowid
                conn.commit()
                
                logger.info(f"User created: {username} (ID: {user_id})")
                return self.get_user_by_id(user_id)
                
            except sqlite3.IntegrityError as e:
                if 'username' in str(e):
                    raise ValueError("Username already exists")
                elif 'email' in str(e):
                    raise ValueError("Email already exists")
                else:
                    raise ValueError("User creation failed")
    
    def get_user_by_id(self, user_id):
        """Get user by ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, username, email, password_hash, role, is_active, 
                       last_login, failed_login_attempts, locked_until, created_at
                FROM users WHERE id = ?
            ''', (user_id,))
            
            row = cursor.fetchone()
            if row:
                return User(*row)
            return None
    
    def get_user_by_username(self, username):
        """Get user by username"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, username, email, password_hash, role, is_active, 
                       last_login, failed_login_attempts, locked_until, created_at
                FROM users WHERE username = ?
            ''', (username,))
            
            row = cursor.fetchone()
            if row:
                return User(*row)
            return None
    
    def get_user_by_email(self, email):
        """Get user by email"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, username, email, password_hash, role, is_active, 
                       last_login, failed_login_attempts, locked_until, created_at
                FROM users WHERE email = ?
            ''', (email,))
            
            row = cursor.fetchone()
            if row:
                return User(*row)
            return None
    
    def authenticate_user(self, username_or_email, password):
        """Authenticate user with username/email and password"""
        # Try to get user by username first, then email
        user = self.get_user_by_username(username_or_email)
        if not user:
            user = self.get_user_by_email(username_or_email)
        
        if not user:
            logger.warning(f"Authentication failed: User not found - {username_or_email}")
            return None
        
        # Check if account is locked
        if user.is_account_locked():
            logger.warning(f"Authentication failed: Account locked - {username_or_email}")
            return None
        
        # Check password
        if user.check_password(password):
            # Successful login - reset failed attempts and update last login
            self.reset_failed_login_attempts(user.id)
            self.update_last_login(user.id)
            logger.info(f"Authentication successful: {username_or_email}")
            return user
        else:
            # Failed login - increment failed attempts
            self.increment_failed_login_attempts(user.id)
            logger.warning(f"Authentication failed: Invalid password - {username_or_email}")
            return None
    
    def increment_failed_login_attempts(self, user_id):
        """Increment failed login attempts and lock account if necessary"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get current failed attempts
            cursor.execute('SELECT failed_login_attempts FROM users WHERE id = ?', (user_id,))
            result = cursor.fetchone()
            
            if result:
                failed_attempts = result[0] + 1
                
                # Lock account if max attempts reached
                locked_until = None
                if failed_attempts >= AuthConfig.MAX_LOGIN_ATTEMPTS:
                    locked_until = (datetime.now() + timedelta(seconds=AuthConfig.LOCKOUT_DURATION)).isoformat()
                
                cursor.execute('''
                    UPDATE users 
                    SET failed_login_attempts = ?, locked_until = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (failed_attempts, locked_until, user_id))
                
                conn.commit()
                
                if locked_until:
                    logger.warning(f"Account locked due to failed attempts: User ID {user_id}")
    
    def reset_failed_login_attempts(self, user_id):
        """Reset failed login attempts for user"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE users 
                SET failed_login_attempts = 0, locked_until = NULL, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (user_id,))
            conn.commit()
    
    def update_last_login(self, user_id):
        """Update last login timestamp"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE users 
                SET last_login = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (user_id,))
            conn.commit()
    
    def validate_password_strength(self, password):
        """Validate password meets strength requirements"""
        if len(password) < AuthConfig.MIN_PASSWORD_LENGTH:
            return False
        
        if AuthConfig.REQUIRE_UPPERCASE and not any(c.isupper() for c in password):
            return False
        
        if AuthConfig.REQUIRE_LOWERCASE and not any(c.islower() for c in password):
            return False
        
        if AuthConfig.REQUIRE_DIGITS and not any(c.isdigit() for c in password):
            return False
        
        if AuthConfig.REQUIRE_SPECIAL_CHARS and not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            return False
        
        return True
    
    def change_password(self, user_id, old_password, new_password):
        """Change user password after validating old password"""
        user = self.get_user_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        if not user.check_password(old_password):
            raise ValueError("Current password is incorrect")
        
        if not self.validate_password_strength(new_password):
            raise ValueError("New password does not meet strength requirements")
        
        # Hash new password
        new_password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE users 
                SET password_hash = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (new_password_hash, user_id))
            conn.commit()
        
        logger.info(f"Password changed for user ID: {user_id}")
    
    def create_password_reset_token(self, email):
        """Create password reset token for user"""
        user = self.get_user_by_email(email)
        if not user:
            # Don't reveal if email exists
            logger.warning(f"Password reset requested for non-existent email: {email}")
            return None
        
        # Generate secure token
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(seconds=AuthConfig.PASSWORD_RESET_TIMEOUT)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO password_reset_tokens (user_id, token, expires_at)
                VALUES (?, ?, ?)
            ''', (user.id, token, expires_at))
            conn.commit()
        
        logger.info(f"Password reset token created for user: {email}")
        return token
    
    def reset_password_with_token(self, token, new_password):
        """Reset password using valid token"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Find valid token
            cursor.execute('''
                SELECT user_id FROM password_reset_tokens 
                WHERE token = ? AND expires_at > ? AND used = 0
            ''', (token, datetime.now()))
            
            result = cursor.fetchone()
            if not result:
                raise ValueError("Invalid or expired reset token")
            
            user_id = result[0]
            
            # Validate new password
            if not self.validate_password_strength(new_password):
                raise ValueError("Password does not meet strength requirements")
            
            # Hash new password
            new_password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            # Update password
            cursor.execute('''
                UPDATE users 
                SET password_hash = ?, failed_login_attempts = 0, locked_until = NULL, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (new_password_hash, user_id))
            
            # Mark token as used
            cursor.execute('''
                UPDATE password_reset_tokens 
                SET used = 1 
                WHERE token = ?
            ''', (token,))
            
            conn.commit()
        
        logger.info(f"Password reset completed for user ID: {user_id}")

class SessionManager:
    """Manages user sessions with Redis"""
    
    def __init__(self):
        self.redis_client = redis.Redis(
            host=AuthConfig.REDIS_HOST,
            port=AuthConfig.REDIS_PORT,
            db=AuthConfig.REDIS_DB,
            password=AuthConfig.REDIS_PASSWORD,
            decode_responses=True
        )
    
    def create_session(self, user_id, session_data=None):
        """Create user session in Redis"""
        session_id = secrets.token_urlsafe(32)
        session_key = f"session:{session_id}"
        
        data = {
            'user_id': user_id,
            'created_at': datetime.now().isoformat(),
            'last_activity': datetime.now().isoformat(),
            **(session_data or {})
        }
        
        # Store in Redis with expiration
        self.redis_client.hmset(session_key, data)
        self.redis_client.expire(session_key, AuthConfig.SESSION_TIMEOUT)
        
        logger.info(f"Session created: {session_id} for user {user_id}")
        return session_id
    
    def get_session(self, session_id):
        """Get session data from Redis"""
        session_key = f"session:{session_id}"
        data = self.redis_client.hgetall(session_key)
        
        if data:
            # Update last activity
            self.redis_client.hset(session_key, 'last_activity', datetime.now().isoformat())
            self.redis_client.expire(session_key, AuthConfig.SESSION_TIMEOUT)
        
        return data
    
    def destroy_session(self, session_id):
        """Destroy session in Redis"""
        session_key = f"session:{session_id}"
        self.redis_client.delete(session_key)
        logger.info(f"Session destroyed: {session_id}")
    
    def cleanup_expired_sessions(self):
        """Clean up expired sessions (Redis handles this automatically)"""
        # Redis TTL handles expiration, but we can log cleanup
        logger.info("Session cleanup completed (handled by Redis TTL)")

class AuthenticationApp:
    """Main authentication application"""
    
    def __init__(self, app=None):
        self.app = app
        self.user_manager = UserManager()
        self.session_manager = SessionManager()
        self.login_manager = LoginManager()
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize authentication with Flask app"""
        # Configure app
        app.config['SECRET_KEY'] = AuthConfig.SECRET_KEY
        app.config['REMEMBER_COOKIE_DURATION'] = AuthConfig.REMEMBER_COOKIE_DURATION
        
        # Initialize login manager
        self.login_manager.init_app(app)
        self.login_manager.login_view = 'auth.login'
        self.login_manager.login_message = 'Please log in to access this page.'
        self.login_manager.login_message_category = 'info'
        
        @self.login_manager.user_loader
        def load_user(user_id):
            return self.user_manager.get_user_by_id(int(user_id))
        
        # Register routes
        self.register_routes(app)
    
    def register_routes(self, app):
        """Register authentication routes"""
        
        @app.route('/auth/login', methods=['GET', 'POST'])
        def login():
            if request.method == 'POST':
                data = request.get_json() or request.form
                username = data.get('username', '').strip()
                password = data.get('password', '')
                remember = data.get('remember', False)
                
                if not username or not password:
                    return jsonify({'error': 'Username and password required'}), 400
                
                user = self.user_manager.authenticate_user(username, password)
                if user and user.can_login():
                    login_user(user, remember=remember)
                    
                    # Create session
                    session_id = self.session_manager.create_session(
                        user.id, 
                        {
                            'ip_address': request.remote_addr,
                            'user_agent': request.user_agent.string
                        }
                    )
                    
                    session['session_id'] = session_id
                    
                    return jsonify({
                        'success': True,
                        'user': user.to_dict(),
                        'message': 'Login successful'
                    })
                else:
                    return jsonify({'error': 'Invalid credentials or account locked'}), 401
            
            # GET request - return login form
            return render_template_string("""
                <form method="post" action="/auth/login">
                    <input type="text" name="username" placeholder="Username" required>
                    <input type="password" name="password" placeholder="Password" required>
                    <input type="checkbox" name="remember"> Remember me
                    <button type="submit">Login</button>
                </form>
            """)
        
        @app.route('/auth/logout', methods=['POST'])
        @login_required
        def logout():
            # Destroy session
            session_id = session.get('session_id')
            if session_id:
                self.session_manager.destroy_session(session_id)
            
            logout_user()
            session.clear()
            
            return jsonify({'success': True, 'message': 'Logged out successfully'})
        
        @app.route('/auth/register', methods=['POST'])
        def register():
            data = request.get_json() or request.form
            username = data.get('username', '').strip()
            email = data.get('email', '').strip()
            password = data.get('password', '')
            role = data.get('role', 'agent')
            
            try:
                user = self.user_manager.create_user(username, email, password, role)
                return jsonify({
                    'success': True,
                    'user': user.to_dict(),
                    'message': 'User created successfully'
                })
            except ValueError as e:
                return jsonify({'error': str(e)}), 400
        
        @app.route('/auth/change-password', methods=['POST'])
        @login_required
        def change_password():
            data = request.get_json() or request.form
            old_password = data.get('old_password', '')
            new_password = data.get('new_password', '')
            
            try:
                self.user_manager.change_password(current_user.id, old_password, new_password)
                return jsonify({'success': True, 'message': 'Password changed successfully'})
            except ValueError as e:
                return jsonify({'error': str(e)}), 400
        
        @app.route('/auth/reset-password-request', methods=['POST'])
        def reset_password_request():
            data = request.get_json() or request.form
            email = data.get('email', '').strip()
            
            token = self.user_manager.create_password_reset_token(email)
            
            # Always return success to prevent email enumeration
            return jsonify({
                'success': True,
                'message': 'If the email exists, a reset link has been sent'
            })
        
        @app.route('/auth/reset-password', methods=['POST'])
        def reset_password():
            data = request.get_json() or request.form
            token = data.get('token', '')
            new_password = data.get('new_password', '')
            
            try:
                self.user_manager.reset_password_with_token(token, new_password)
                return jsonify({'success': True, 'message': 'Password reset successfully'})
            except ValueError as e:
                return jsonify({'error': str(e)}), 400
        
        @app.route('/auth/profile')
        @login_required
        def profile():
            return jsonify({
                'user': current_user.to_dict(),
                'session_id': session.get('session_id')
            })

def create_default_admin():
    """Create default admin user if none exists"""
    user_manager = UserManager()
    
    # Check if any admin exists
    with sqlite3.connect(user_manager.db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'admin'")
        admin_count = cursor.fetchone()[0]
    
    if admin_count == 0:
        try:
            admin_user = user_manager.create_user(
                username='admin',
                email='admin@narissarealty.com',
                password='Admin123!',  # Should be changed immediately
                role='admin'
            )
            logger.info("Default admin user created: admin / Admin123!")
            return admin_user
        except Exception as e:
            logger.error(f"Failed to create default admin: {e}")
    
    return None

def main():
    """Test the authentication system"""
    from flask import Flask
    
    app = Flask(__name__)
    auth = AuthenticationApp(app)
    
    # Create default admin
    create_default_admin()
    
    # Test routes
    @app.route('/')
    def index():
        return jsonify({'message': 'CRM Authentication System', 'status': 'running'})
    
    @app.route('/protected')
    @login_required
    def protected():
        return jsonify({'message': 'This is a protected route', 'user': current_user.username})
    
    print("Authentication system test server starting...")
    print("Visit http://localhost:5000/auth/login to test login")
    print("Default admin: admin / Admin123!")
    
    app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == "__main__":
    main()