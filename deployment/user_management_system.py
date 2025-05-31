#!/usr/bin/env python3
"""
Multi-User Management and Permissions System for Narissa Realty CRM
Implements user creation/management interface, role assignment, team management
"""

import os
import json
import sqlite3
import logging
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, render_template_string
from flask_login import login_required, current_user
from deployment.auth_system import UserManager, User
from deployment.rbac_system import RBACManager, Role, Permission, requires_permission, requires_role
from typing import List, Dict, Optional
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TeamManager:
    """Manages team structures and assignments"""
    
    def __init__(self, db_path="real_estate_crm.db"):
        self.db_path = db_path
        self.init_team_tables()
    
    def init_team_tables(self):
        """Initialize team management tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Teams table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS teams (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    description TEXT,
                    manager_id INTEGER,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (manager_id) REFERENCES users (id)
                )
            ''')
            
            # Team memberships table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS team_members (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    team_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    role_in_team TEXT DEFAULT 'member',
                    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1,
                    FOREIGN KEY (team_id) REFERENCES teams (id),
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    UNIQUE(team_id, user_id)
                )
            ''')
            
            # Lead assignments table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS lead_assignments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    lead_id INTEGER NOT NULL,
                    assigned_to INTEGER NOT NULL,
                    assigned_by INTEGER NOT NULL,
                    assignment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'active',
                    notes TEXT,
                    FOREIGN KEY (assigned_to) REFERENCES users (id),
                    FOREIGN KEY (assigned_by) REFERENCES users (id)
                )
            ''')
            
            # User profiles table for additional information
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_profiles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER UNIQUE NOT NULL,
                    first_name TEXT,
                    last_name TEXT,
                    phone TEXT,
                    address TEXT,
                    bio TEXT,
                    avatar_url TEXT,
                    timezone TEXT DEFAULT 'UTC',
                    preferences TEXT,  -- JSON string
                    emergency_contact TEXT,
                    hire_date DATE,
                    department TEXT,
                    commission_rate DECIMAL(5,4),
                    license_number TEXT,
                    license_expiry DATE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            conn.commit()
            logger.info("Team management tables initialized")

class UserManagementSystem:
    """Comprehensive user management system"""
    
    def __init__(self, db_path="real_estate_crm.db"):
        self.db_path = db_path
        self.user_manager = UserManager(db_path)
        self.rbac_manager = RBACManager(db_path)
        self.team_manager = TeamManager(db_path)
    
    def create_user_with_profile(self, user_data: Dict, created_by: int) -> Dict:
        """Create user with complete profile information"""
        try:
            # Validate required fields
            required_fields = ['username', 'email', 'password', 'first_name', 'last_name']
            for field in required_fields:
                if not user_data.get(field):
                    raise ValueError(f"Field '{field}' is required")
            
            # Validate email format
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', user_data['email']):
                raise ValueError("Invalid email format")
            
            # Create user account
            user = self.user_manager.create_user(
                username=user_data['username'],
                email=user_data['email'],
                password=user_data['password'],
                role=user_data.get('role', 'agent')
            )
            
            # Create user profile
            profile_data = {
                'user_id': user.id,
                'first_name': user_data['first_name'],
                'last_name': user_data['last_name'],
                'phone': user_data.get('phone', ''),
                'address': user_data.get('address', ''),
                'bio': user_data.get('bio', ''),
                'department': user_data.get('department', 'Sales'),
                'commission_rate': user_data.get('commission_rate', 0.03),
                'license_number': user_data.get('license_number', ''),
                'license_expiry': user_data.get('license_expiry'),
                'hire_date': user_data.get('hire_date', datetime.now().date()),
                'timezone': user_data.get('timezone', 'UTC'),
                'preferences': json.dumps(user_data.get('preferences', {}))
            }
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                columns = ', '.join(profile_data.keys())
                placeholders = ', '.join(['?' for _ in profile_data])
                
                cursor.execute(f'''
                    INSERT INTO user_profiles ({columns})
                    VALUES ({placeholders})
                ''', list(profile_data.values()))
                
                conn.commit()
            
            # Log user creation
            logger.info(f"User created with profile: {user_data['username']} by user {created_by}")
            
            return {
                'success': True,
                'user': user.to_dict(),
                'profile': profile_data,
                'message': 'User created successfully'
            }
            
        except Exception as e:
            logger.error(f"User creation failed: {e}")
            raise e
    
    def get_user_with_profile(self, user_id: int) -> Optional[Dict]:
        """Get user with complete profile information"""
        user = self.user_manager.get_user_by_id(user_id)
        if not user:
            return None
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get user profile
            profile = cursor.execute('''
                SELECT first_name, last_name, phone, address, bio, avatar_url,
                       timezone, preferences, emergency_contact, hire_date,
                       department, commission_rate, license_number, license_expiry
                FROM user_profiles WHERE user_id = ?
            ''', (user_id,)).fetchone()
            
            # Get user permissions
            permissions = self.rbac_manager.get_user_permissions(user_id)
            
            # Get team memberships
            teams = cursor.execute('''
                SELECT t.id, t.name, tm.role_in_team, tm.joined_at
                FROM teams t
                JOIN team_members tm ON t.id = tm.team_id
                WHERE tm.user_id = ? AND tm.is_active = 1
            ''', (user_id,)).fetchall()
            
            user_data = user.to_dict()
            
            if profile:
                user_data.update({
                    'first_name': profile[0],
                    'last_name': profile[1],
                    'phone': profile[2],
                    'address': profile[3],
                    'bio': profile[4],
                    'avatar_url': profile[5],
                    'timezone': profile[6],
                    'preferences': json.loads(profile[7]) if profile[7] else {},
                    'emergency_contact': profile[8],
                    'hire_date': profile[9],
                    'department': profile[10],
                    'commission_rate': profile[11],
                    'license_number': profile[12],
                    'license_expiry': profile[13]
                })
            
            user_data.update({
                'permissions': permissions,
                'teams': [{'id': t[0], 'name': t[1], 'role': t[2], 'joined_at': t[3]} for t in teams]
            })
            
            return user_data
    
    def update_user_profile(self, user_id: int, profile_data: Dict, updated_by: int) -> Dict:
        """Update user profile information"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Build dynamic update query
                update_fields = []
                values = []
                
                allowed_fields = [
                    'first_name', 'last_name', 'phone', 'address', 'bio',
                    'avatar_url', 'timezone', 'emergency_contact', 'hire_date',
                    'department', 'commission_rate', 'license_number', 'license_expiry'
                ]
                
                for field in allowed_fields:
                    if field in profile_data:
                        update_fields.append(f"{field} = ?")
                        if field == 'preferences':
                            values.append(json.dumps(profile_data[field]))
                        else:
                            values.append(profile_data[field])
                
                if update_fields:
                    update_fields.append("updated_at = CURRENT_TIMESTAMP")
                    values.append(user_id)
                    
                    query = f'''
                        UPDATE user_profiles 
                        SET {', '.join(update_fields)}
                        WHERE user_id = ?
                    '''
                    
                    cursor.execute(query, values)
                    conn.commit()
                
                logger.info(f"User profile updated: {user_id} by user {updated_by}")
                
                return {
                    'success': True,
                    'message': 'Profile updated successfully'
                }
                
        except Exception as e:
            logger.error(f"Profile update failed: {e}")
            raise e
    
    def list_users(self, page: int = 1, limit: int = 50, filters: Dict = None) -> Dict:
        """List users with pagination and filtering"""
        offset = (page - 1) * limit
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Build query with filters
            where_conditions = ["u.is_active = 1"]
            params = []
            
            if filters:
                if filters.get('role'):
                    where_conditions.append("u.role = ?")
                    params.append(filters['role'])
                
                if filters.get('department'):
                    where_conditions.append("up.department = ?")
                    params.append(filters['department'])
                
                if filters.get('search'):
                    search_term = f"%{filters['search']}%"
                    where_conditions.append('''
                        (u.username LIKE ? OR u.email LIKE ? OR 
                         up.first_name LIKE ? OR up.last_name LIKE ?)
                    ''')
                    params.extend([search_term] * 4)
            
            where_clause = " AND ".join(where_conditions)
            
            # Count total users
            count_query = f'''
                SELECT COUNT(*) FROM users u
                LEFT JOIN user_profiles up ON u.id = up.user_id
                WHERE {where_clause}
            '''
            
            total_count = cursor.execute(count_query, params).fetchone()[0]
            
            # Get users with pagination
            query = f'''
                SELECT u.id, u.username, u.email, u.role, u.is_active, u.last_login,
                       up.first_name, up.last_name, up.department, up.phone
                FROM users u
                LEFT JOIN user_profiles up ON u.id = up.user_id
                WHERE {where_clause}
                ORDER BY u.created_at DESC
                LIMIT ? OFFSET ?
            '''
            
            params.extend([limit, offset])
            users = cursor.fetchall()
            
            user_list = []
            for user in users:
                user_list.append({
                    'id': user[0],
                    'username': user[1],
                    'email': user[2],
                    'role': user[3],
                    'is_active': user[4],
                    'last_login': user[5],
                    'first_name': user[6],
                    'last_name': user[7],
                    'department': user[8],
                    'phone': user[9]
                })
            
            return {
                'users': user_list,
                'pagination': {
                    'page': page,
                    'limit': limit,
                    'total': total_count,
                    'pages': (total_count + limit - 1) // limit
                }
            }
    
    def deactivate_user(self, user_id: int, deactivated_by: int, reason: str = None) -> Dict:
        """Deactivate user account"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    UPDATE users 
                    SET is_active = 0, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (user_id,))
                
                # Deactivate team memberships
                cursor.execute('''
                    UPDATE team_members 
                    SET is_active = 0
                    WHERE user_id = ?
                ''', (user_id,))
                
                conn.commit()
                
                logger.info(f"User deactivated: {user_id} by user {deactivated_by}. Reason: {reason}")
                
                return {
                    'success': True,
                    'message': 'User deactivated successfully'
                }
                
        except Exception as e:
            logger.error(f"User deactivation failed: {e}")
            raise e
    
    def assign_role(self, user_id: int, new_role: str, assigned_by: int) -> Dict:
        """Assign new role to user"""
        try:
            # Validate role
            if new_role not in [role.value for role in Role]:
                raise ValueError(f"Invalid role: {new_role}")
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    UPDATE users 
                    SET role = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (new_role, user_id))
                
                conn.commit()
                
                logger.info(f"Role assigned: {new_role} to user {user_id} by user {assigned_by}")
                
                return {
                    'success': True,
                    'message': f'Role {new_role} assigned successfully'
                }
                
        except Exception as e:
            logger.error(f"Role assignment failed: {e}")
            raise e
    
    def create_team(self, team_data: Dict, created_by: int) -> Dict:
        """Create new team"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO teams (name, description, manager_id)
                    VALUES (?, ?, ?)
                ''', (team_data['name'], team_data.get('description', ''), team_data.get('manager_id')))
                
                team_id = cursor.lastrowid
                
                # Add manager as team member if specified
                if team_data.get('manager_id'):
                    cursor.execute('''
                        INSERT INTO team_members (team_id, user_id, role_in_team)
                        VALUES (?, ?, 'manager')
                    ''', (team_id, team_data['manager_id']))
                
                conn.commit()
                
                logger.info(f"Team created: {team_data['name']} by user {created_by}")
                
                return {
                    'success': True,
                    'team_id': team_id,
                    'message': 'Team created successfully'
                }
                
        except Exception as e:
            logger.error(f"Team creation failed: {e}")
            raise e
    
    def add_team_member(self, team_id: int, user_id: int, role_in_team: str, added_by: int) -> Dict:
        """Add user to team"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO team_members (team_id, user_id, role_in_team)
                    VALUES (?, ?, ?)
                ''', (team_id, user_id, role_in_team))
                
                conn.commit()
                
                logger.info(f"User {user_id} added to team {team_id} as {role_in_team} by user {added_by}")
                
                return {
                    'success': True,
                    'message': 'User added to team successfully'
                }
                
        except Exception as e:
            logger.error(f"Team member addition failed: {e}")
            raise e
    
    def assign_lead(self, lead_id: int, assigned_to: int, assigned_by: int, notes: str = None) -> Dict:
        """Assign lead to agent"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO lead_assignments (lead_id, assigned_to, assigned_by, notes)
                    VALUES (?, ?, ?, ?)
                ''', (lead_id, assigned_to, assigned_by, notes))
                
                conn.commit()
                
                logger.info(f"Lead {lead_id} assigned to user {assigned_to} by user {assigned_by}")
                
                return {
                    'success': True,
                    'message': 'Lead assigned successfully'
                }
                
        except Exception as e:
            logger.error(f"Lead assignment failed: {e}")
            raise e
    
    def get_team_performance(self, team_id: int, start_date: datetime, end_date: datetime) -> Dict:
        """Get team performance metrics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get team members
            members = cursor.execute('''
                SELECT u.id, u.username, up.first_name, up.last_name, tm.role_in_team
                FROM team_members tm
                JOIN users u ON tm.user_id = u.id
                LEFT JOIN user_profiles up ON u.id = up.user_id
                WHERE tm.team_id = ? AND tm.is_active = 1
            ''', (team_id,)).fetchall()
            
            # Calculate performance metrics for each member
            member_performance = []
            for member in members:
                user_id = member[0]
                
                # Get lead assignments count
                lead_count = cursor.execute('''
                    SELECT COUNT(*) FROM lead_assignments
                    WHERE assigned_to = ? AND assignment_date BETWEEN ? AND ?
                ''', (user_id, start_date, end_date)).fetchone()[0]
                
                member_performance.append({
                    'user_id': user_id,
                    'username': member[1],
                    'first_name': member[2],
                    'last_name': member[3],
                    'role_in_team': member[4],
                    'leads_assigned': lead_count
                })
            
            return {
                'team_id': team_id,
                'period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat()
                },
                'members': member_performance
            }

def register_user_management_routes(app: Flask, user_mgmt: UserManagementSystem):
    """Register user management routes with Flask app"""
    
    @app.route('/api/users', methods=['POST'])
    @login_required
    @requires_permission(Permission.CREATE_USER)
    def create_user():
        """Create new user"""
        try:
            user_data = request.get_json()
            result = user_mgmt.create_user_with_profile(user_data, current_user.id)
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    
    @app.route('/api/users', methods=['GET'])
    @login_required
    @requires_permission(Permission.READ_USER)
    def list_users():
        """List users with pagination and filtering"""
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 50))
        
        filters = {}
        if request.args.get('role'):
            filters['role'] = request.args.get('role')
        if request.args.get('department'):
            filters['department'] = request.args.get('department')
        if request.args.get('search'):
            filters['search'] = request.args.get('search')
        
        result = user_mgmt.list_users(page, limit, filters)
        return jsonify(result)
    
    @app.route('/api/users/<int:user_id>', methods=['GET'])
    @login_required
    @requires_permission(Permission.READ_USER)
    def get_user(user_id):
        """Get user details"""
        user_data = user_mgmt.get_user_with_profile(user_id)
        if user_data:
            return jsonify(user_data)
        else:
            return jsonify({'error': 'User not found'}), 404
    
    @app.route('/api/users/<int:user_id>', methods=['PUT'])
    @login_required
    @requires_permission(Permission.UPDATE_USER)
    def update_user(user_id):
        """Update user profile"""
        try:
            profile_data = request.get_json()
            result = user_mgmt.update_user_profile(user_id, profile_data, current_user.id)
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    
    @app.route('/api/users/<int:user_id>/deactivate', methods=['POST'])
    @login_required
    @requires_permission(Permission.DELETE_USER)
    def deactivate_user(user_id):
        """Deactivate user account"""
        try:
            data = request.get_json() or {}
            reason = data.get('reason', '')
            result = user_mgmt.deactivate_user(user_id, current_user.id, reason)
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    
    @app.route('/api/users/<int:user_id>/role', methods=['PUT'])
    @login_required
    @requires_permission(Permission.MANAGE_ROLES)
    def assign_role(user_id):
        """Assign role to user"""
        try:
            data = request.get_json()
            new_role = data.get('role')
            result = user_mgmt.assign_role(user_id, new_role, current_user.id)
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    
    @app.route('/api/teams', methods=['POST'])
    @login_required
    @requires_permission(Permission.MANAGE_TEAM)
    def create_team():
        """Create new team"""
        try:
            team_data = request.get_json()
            result = user_mgmt.create_team(team_data, current_user.id)
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    
    @app.route('/api/teams/<int:team_id>/members', methods=['POST'])
    @login_required
    @requires_permission(Permission.MANAGE_TEAM)
    def add_team_member(team_id):
        """Add member to team"""
        try:
            data = request.get_json()
            user_id = data.get('user_id')
            role_in_team = data.get('role_in_team', 'member')
            result = user_mgmt.add_team_member(team_id, user_id, role_in_team, current_user.id)
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    
    @app.route('/api/leads/<int:lead_id>/assign', methods=['POST'])
    @login_required
    @requires_permission(Permission.ASSIGN_LEADS)
    def assign_lead(lead_id):
        """Assign lead to agent"""
        try:
            data = request.get_json()
            assigned_to = data.get('assigned_to')
            notes = data.get('notes', '')
            result = user_mgmt.assign_lead(lead_id, assigned_to, current_user.id, notes)
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    
    @app.route('/api/teams/<int:team_id>/performance')
    @login_required
    @requires_permission(Permission.VIEW_TEAM_PERFORMANCE)
    def get_team_performance(team_id):
        """Get team performance metrics"""
        start_date = datetime.fromisoformat(request.args.get('start_date', (datetime.now() - timedelta(days=30)).isoformat()))
        end_date = datetime.fromisoformat(request.args.get('end_date', datetime.now().isoformat()))
        
        result = user_mgmt.get_team_performance(team_id, start_date, end_date)
        return jsonify(result)
    
    @app.route('/api/users/management-interface')
    @login_required
    @requires_permission(Permission.READ_USER)
    def user_management_interface():
        """User management web interface"""
        interface_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>User Management - Narissa Realty CRM</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .container { max-width: 1200px; margin: 0 auto; }
                .header { background: #f4f4f4; padding: 20px; border-radius: 5px; margin-bottom: 20px; }
                .section { margin-bottom: 30px; }
                .user-card { border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 5px; }
                .btn { padding: 8px 16px; margin: 5px; background: #007cba; color: white; border: none; border-radius: 3px; cursor: pointer; }
                .btn-danger { background: #dc3545; }
                .btn-success { background: #28a745; }
                .form-group { margin: 10px 0; }
                .form-group label { display: block; margin-bottom: 5px; }
                .form-group input, .form-group select, .form-group textarea { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 3px; }
                .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
                @media (max-width: 768px) { .grid { grid-template-columns: 1fr; } }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>User Management</h1>
                    <p>Manage users, roles, and team assignments</p>
                </div>
                
                <div class="grid">
                    <div class="section">
                        <h2>Create New User</h2>
                        <form id="createUserForm">
                            <div class="form-group">
                                <label>Username:</label>
                                <input type="text" name="username" required>
                            </div>
                            <div class="form-group">
                                <label>Email:</label>
                                <input type="email" name="email" required>
                            </div>
                            <div class="form-group">
                                <label>Password:</label>
                                <input type="password" name="password" required>
                            </div>
                            <div class="form-group">
                                <label>First Name:</label>
                                <input type="text" name="first_name" required>
                            </div>
                            <div class="form-group">
                                <label>Last Name:</label>
                                <input type="text" name="last_name" required>
                            </div>
                            <div class="form-group">
                                <label>Role:</label>
                                <select name="role">
                                    <option value="agent">Agent</option>
                                    <option value="manager">Manager</option>
                                    <option value="admin">Admin</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label>Department:</label>
                                <input type="text" name="department" value="Sales">
                            </div>
                            <div class="form-group">
                                <label>Phone:</label>
                                <input type="tel" name="phone">
                            </div>
                            <button type="submit" class="btn btn-success">Create User</button>
                        </form>
                    </div>
                    
                    <div class="section">
                        <h2>Create Team</h2>
                        <form id="createTeamForm">
                            <div class="form-group">
                                <label>Team Name:</label>
                                <input type="text" name="name" required>
                            </div>
                            <div class="form-group">
                                <label>Description:</label>
                                <textarea name="description" rows="3"></textarea>
                            </div>
                            <div class="form-group">
                                <label>Manager:</label>
                                <select name="manager_id" id="managerSelect">
                                    <option value="">Select Manager</option>
                                </select>
                            </div>
                            <button type="submit" class="btn btn-success">Create Team</button>
                        </form>
                    </div>
                </div>
                
                <div class="section">
                    <h2>User List</h2>
                    <div class="form-group">
                        <input type="text" id="searchUsers" placeholder="Search users...">
                        <select id="filterRole">
                            <option value="">All Roles</option>
                            <option value="admin">Admin</option>
                            <option value="manager">Manager</option>
                            <option value="agent">Agent</option>
                        </select>
                        <button onclick="loadUsers()" class="btn">Search</button>
                    </div>
                    <div id="userList"></div>
                </div>
            </div>
            
            <script>
                // Load users on page load
                document.addEventListener('DOMContentLoaded', function() {
                    loadUsers();
                    loadManagers();
                });
                
                // Create user form submission
                document.getElementById('createUserForm').addEventListener('submit', function(e) {
                    e.preventDefault();
                    const formData = new FormData(e.target);
                    const userData = Object.fromEntries(formData);
                    
                    fetch('/api/users', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify(userData)
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            alert('User created successfully!');
                            e.target.reset();
                            loadUsers();
                        } else {
                            alert('Error: ' + data.error);
                        }
                    });
                });
                
                // Create team form submission
                document.getElementById('createTeamForm').addEventListener('submit', function(e) {
                    e.preventDefault();
                    const formData = new FormData(e.target);
                    const teamData = Object.fromEntries(formData);
                    
                    fetch('/api/teams', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify(teamData)
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            alert('Team created successfully!');
                            e.target.reset();
                        } else {
                            alert('Error: ' + data.error);
                        }
                    });
                });
                
                // Load users function
                function loadUsers() {
                    const search = document.getElementById('searchUsers').value;
                    const role = document.getElementById('filterRole').value;
                    
                    let params = new URLSearchParams();
                    if (search) params.append('search', search);
                    if (role) params.append('role', role);
                    
                    fetch('/api/users?' + params.toString())
                    .then(response => response.json())
                    .then(data => {
                        const userList = document.getElementById('userList');
                        userList.innerHTML = '';
                        
                        data.users.forEach(user => {
                            const userCard = document.createElement('div');
                            userCard.className = 'user-card';
                            userCard.innerHTML = `
                                <h3>${user.first_name} ${user.last_name} (${user.username})</h3>
                                <p><strong>Email:</strong> ${user.email}</p>
                                <p><strong>Role:</strong> ${user.role}</p>
                                <p><strong>Department:</strong> ${user.department || 'N/A'}</p>
                                <p><strong>Last Login:</strong> ${user.last_login || 'Never'}</p>
                                <button onclick="editUser(${user.id})" class="btn">Edit</button>
                                <button onclick="deactivateUser(${user.id})" class="btn btn-danger">Deactivate</button>
                            `;
                            userList.appendChild(userCard);
                        });
                    });
                }
                
                // Load managers for team creation
                function loadManagers() {
                    fetch('/api/users?role=manager')
                    .then(response => response.json())
                    .then(data => {
                        const select = document.getElementById('managerSelect');
                        data.users.forEach(user => {
                            const option = document.createElement('option');
                            option.value = user.id;
                            option.textContent = `${user.first_name} ${user.last_name}`;
                            select.appendChild(option);
                        });
                    });
                }
                
                // Edit user function
                function editUser(userId) {
                    // Implementation for editing user
                    alert('Edit user functionality would be implemented here');
                }
                
                // Deactivate user function
                function deactivateUser(userId) {
                    if (confirm('Are you sure you want to deactivate this user?')) {
                        fetch(`/api/users/${userId}/deactivate`, {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({reason: 'Deactivated via management interface'})
                        })
                        .then(response => response.json())
                        .then(data => {
                            if (data.success) {
                                alert('User deactivated successfully!');
                                loadUsers();
                            } else {
                                alert('Error: ' + data.error);
                            }
                        });
                    }
                }
            </script>
        </body>
        </html>
        """
        return interface_html

def main():
    """Test the user management system"""
    from flask import Flask
    
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'test-secret-key'
    
    # Initialize user management system
    user_mgmt = UserManagementSystem()
    
    # Register routes
    register_user_management_routes(app, user_mgmt)
    
    print("User Management System test server starting...")
    print("Visit http://localhost:5001/api/users/management-interface")
    
    app.run(debug=True, host='0.0.0.0', port=5001)

if __name__ == "__main__":
    main()