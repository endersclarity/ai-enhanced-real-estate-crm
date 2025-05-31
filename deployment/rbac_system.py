#!/usr/bin/env python3
"""
Role-Based Access Control (RBAC) System for Narissa Realty CRM
Implements Admin, Manager, Agent roles with permission-based access control
"""

import os
import json
import sqlite3
import logging
from datetime import datetime
from functools import wraps
from flask import request, jsonify, g
from flask_login import current_user
from enum import Enum
from typing import List, Dict, Set, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Role(Enum):
    """System roles with hierarchy"""
    ADMIN = "admin"
    MANAGER = "manager"
    AGENT = "agent"
    
    @classmethod
    def get_hierarchy_level(cls, role):
        """Get numeric hierarchy level for role comparison"""
        hierarchy = {
            cls.ADMIN: 3,
            cls.MANAGER: 2,
            cls.AGENT: 1
        }
        return hierarchy.get(role, 0)
    
    @classmethod
    def has_higher_privilege(cls, role1, role2):
        """Check if role1 has higher privilege than role2"""
        return cls.get_hierarchy_level(role1) > cls.get_hierarchy_level(role2)

class Permission(Enum):
    """System permissions for fine-grained access control"""
    
    # User Management
    CREATE_USER = "create_user"
    READ_USER = "read_user"
    UPDATE_USER = "update_user"
    DELETE_USER = "delete_user"
    MANAGE_ROLES = "manage_roles"
    
    # Client Management
    CREATE_CLIENT = "create_client"
    READ_CLIENT = "read_client"
    UPDATE_CLIENT = "update_client"
    DELETE_CLIENT = "delete_client"
    READ_ALL_CLIENTS = "read_all_clients"
    
    # Property Management
    CREATE_PROPERTY = "create_property"
    READ_PROPERTY = "read_property"
    UPDATE_PROPERTY = "update_property"
    DELETE_PROPERTY = "delete_property"
    READ_ALL_PROPERTIES = "read_all_properties"
    
    # Transaction Management
    CREATE_TRANSACTION = "create_transaction"
    READ_TRANSACTION = "read_transaction"
    UPDATE_TRANSACTION = "update_transaction"
    DELETE_TRANSACTION = "delete_transaction"
    READ_ALL_TRANSACTIONS = "read_all_transactions"
    APPROVE_TRANSACTION = "approve_transaction"
    
    # Document Management
    CREATE_DOCUMENT = "create_document"
    READ_DOCUMENT = "read_document"
    UPDATE_DOCUMENT = "update_document"
    DELETE_DOCUMENT = "delete_document"
    
    # Reporting and Analytics
    VIEW_REPORTS = "view_reports"
    VIEW_ANALYTICS = "view_analytics"
    EXPORT_DATA = "export_data"
    
    # System Administration
    SYSTEM_CONFIG = "system_config"
    VIEW_LOGS = "view_logs"
    MANAGE_BACKUP = "manage_backup"
    
    # Team Management
    MANAGE_TEAM = "manage_team"
    ASSIGN_LEADS = "assign_leads"
    VIEW_TEAM_PERFORMANCE = "view_team_performance"

class RolePermissionMapping:
    """Defines default permissions for each role"""
    
    ROLE_PERMISSIONS = {
        Role.ADMIN: [
            # Full system access
            Permission.CREATE_USER, Permission.READ_USER, Permission.UPDATE_USER, Permission.DELETE_USER,
            Permission.MANAGE_ROLES,
            Permission.CREATE_CLIENT, Permission.READ_CLIENT, Permission.UPDATE_CLIENT, Permission.DELETE_CLIENT,
            Permission.READ_ALL_CLIENTS,
            Permission.CREATE_PROPERTY, Permission.READ_PROPERTY, Permission.UPDATE_PROPERTY, Permission.DELETE_PROPERTY,
            Permission.READ_ALL_PROPERTIES,
            Permission.CREATE_TRANSACTION, Permission.READ_TRANSACTION, Permission.UPDATE_TRANSACTION, 
            Permission.DELETE_TRANSACTION, Permission.READ_ALL_TRANSACTIONS, Permission.APPROVE_TRANSACTION,
            Permission.CREATE_DOCUMENT, Permission.READ_DOCUMENT, Permission.UPDATE_DOCUMENT, Permission.DELETE_DOCUMENT,
            Permission.VIEW_REPORTS, Permission.VIEW_ANALYTICS, Permission.EXPORT_DATA,
            Permission.SYSTEM_CONFIG, Permission.VIEW_LOGS, Permission.MANAGE_BACKUP,
            Permission.MANAGE_TEAM, Permission.ASSIGN_LEADS, Permission.VIEW_TEAM_PERFORMANCE
        ],
        
        Role.MANAGER: [
            # Team and business management
            Permission.READ_USER, Permission.UPDATE_USER,  # Limited user management
            Permission.CREATE_CLIENT, Permission.READ_CLIENT, Permission.UPDATE_CLIENT, Permission.DELETE_CLIENT,
            Permission.READ_ALL_CLIENTS,
            Permission.CREATE_PROPERTY, Permission.READ_PROPERTY, Permission.UPDATE_PROPERTY, Permission.DELETE_PROPERTY,
            Permission.READ_ALL_PROPERTIES,
            Permission.CREATE_TRANSACTION, Permission.READ_TRANSACTION, Permission.UPDATE_TRANSACTION,
            Permission.READ_ALL_TRANSACTIONS, Permission.APPROVE_TRANSACTION,
            Permission.CREATE_DOCUMENT, Permission.READ_DOCUMENT, Permission.UPDATE_DOCUMENT, Permission.DELETE_DOCUMENT,
            Permission.VIEW_REPORTS, Permission.VIEW_ANALYTICS, Permission.EXPORT_DATA,
            Permission.MANAGE_TEAM, Permission.ASSIGN_LEADS, Permission.VIEW_TEAM_PERFORMANCE
        ],
        
        Role.AGENT: [
            # Basic agent operations
            Permission.READ_USER,  # Can read own profile
            Permission.CREATE_CLIENT, Permission.READ_CLIENT, Permission.UPDATE_CLIENT,  # Own clients only
            Permission.CREATE_PROPERTY, Permission.READ_PROPERTY, Permission.UPDATE_PROPERTY,  # Own properties
            Permission.CREATE_TRANSACTION, Permission.READ_TRANSACTION, Permission.UPDATE_TRANSACTION,  # Own transactions
            Permission.CREATE_DOCUMENT, Permission.READ_DOCUMENT, Permission.UPDATE_DOCUMENT,
            Permission.VIEW_REPORTS  # Limited reports
        ]
    }
    
    @classmethod
    def get_permissions_for_role(cls, role: Role) -> List[Permission]:
        """Get list of permissions for a specific role"""
        return cls.ROLE_PERMISSIONS.get(role, [])
    
    @classmethod
    def has_permission(cls, role: Role, permission: Permission) -> bool:
        """Check if role has specific permission"""
        return permission in cls.get_permissions_for_role(role)

class RBACManager:
    """Role-Based Access Control Manager"""
    
    def __init__(self, db_path="real_estate_crm.db"):
        self.db_path = db_path
        self.init_rbac_tables()
        self.setup_default_permissions()
    
    def init_rbac_tables(self):
        """Initialize RBAC database tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Role definitions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS roles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    description TEXT,
                    hierarchy_level INTEGER DEFAULT 1,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Permission definitions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS permissions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    description TEXT,
                    category TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Role-Permission mapping table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS role_permissions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role_id INTEGER NOT NULL,
                    permission_id INTEGER NOT NULL,
                    granted_by INTEGER,
                    granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (role_id) REFERENCES roles (id),
                    FOREIGN KEY (permission_id) REFERENCES permissions (id),
                    FOREIGN KEY (granted_by) REFERENCES users (id),
                    UNIQUE(role_id, permission_id)
                )
            ''')
            
            # User-specific permission overrides table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_permission_overrides (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    permission_id INTEGER NOT NULL,
                    granted BOOLEAN NOT NULL,
                    granted_by INTEGER NOT NULL,
                    reason TEXT,
                    expires_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    FOREIGN KEY (permission_id) REFERENCES permissions (id),
                    FOREIGN KEY (granted_by) REFERENCES users (id),
                    UNIQUE(user_id, permission_id)
                )
            ''')
            
            # Resource ownership tracking table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS resource_ownership (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    resource_type TEXT NOT NULL,
                    resource_id INTEGER NOT NULL,
                    ownership_type TEXT DEFAULT 'owner',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    UNIQUE(user_id, resource_type, resource_id)
                )
            ''')
            
            # Access log table for auditing
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS access_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    resource_type TEXT NOT NULL,
                    resource_id INTEGER,
                    action TEXT NOT NULL,
                    permission_checked TEXT NOT NULL,
                    access_granted BOOLEAN NOT NULL,
                    ip_address TEXT,
                    user_agent TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            conn.commit()
            logger.info("RBAC database tables initialized")
    
    def setup_default_permissions(self):
        """Setup default roles and permissions"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Insert default roles
            default_roles = [
                ('admin', 'System Administrator', 3),
                ('manager', 'Team Manager', 2),
                ('agent', 'Real Estate Agent', 1)
            ]
            
            for role_name, description, level in default_roles:
                cursor.execute('''
                    INSERT OR IGNORE INTO roles (name, description, hierarchy_level)
                    VALUES (?, ?, ?)
                ''', (role_name, description, level))
            
            # Insert default permissions
            for permission in Permission:
                category = self._get_permission_category(permission)
                cursor.execute('''
                    INSERT OR IGNORE INTO permissions (name, description, category)
                    VALUES (?, ?, ?)
                ''', (permission.value, permission.value.replace('_', ' ').title(), category))
            
            # Setup role-permission mappings
            for role, permissions in RolePermissionMapping.ROLE_PERMISSIONS.items():
                role_id = cursor.execute('SELECT id FROM roles WHERE name = ?', (role.value,)).fetchone()
                if role_id:
                    role_id = role_id[0]
                    
                    for permission in permissions:
                        perm_id = cursor.execute('SELECT id FROM permissions WHERE name = ?', (permission.value,)).fetchone()
                        if perm_id:
                            perm_id = perm_id[0]
                            cursor.execute('''
                                INSERT OR IGNORE INTO role_permissions (role_id, permission_id)
                                VALUES (?, ?)
                            ''', (role_id, perm_id))
            
            conn.commit()
            logger.info("Default roles and permissions setup completed")
    
    def _get_permission_category(self, permission: Permission) -> str:
        """Get category for a permission"""
        categories = {
            'user': ['CREATE_USER', 'READ_USER', 'UPDATE_USER', 'DELETE_USER', 'MANAGE_ROLES'],
            'client': ['CREATE_CLIENT', 'READ_CLIENT', 'UPDATE_CLIENT', 'DELETE_CLIENT', 'READ_ALL_CLIENTS'],
            'property': ['CREATE_PROPERTY', 'READ_PROPERTY', 'UPDATE_PROPERTY', 'DELETE_PROPERTY', 'READ_ALL_PROPERTIES'],
            'transaction': ['CREATE_TRANSACTION', 'READ_TRANSACTION', 'UPDATE_TRANSACTION', 'DELETE_TRANSACTION', 'READ_ALL_TRANSACTIONS', 'APPROVE_TRANSACTION'],
            'document': ['CREATE_DOCUMENT', 'READ_DOCUMENT', 'UPDATE_DOCUMENT', 'DELETE_DOCUMENT'],
            'reporting': ['VIEW_REPORTS', 'VIEW_ANALYTICS', 'EXPORT_DATA'],
            'system': ['SYSTEM_CONFIG', 'VIEW_LOGS', 'MANAGE_BACKUP'],
            'team': ['MANAGE_TEAM', 'ASSIGN_LEADS', 'VIEW_TEAM_PERFORMANCE']
        }
        
        for category, perms in categories.items():
            if permission.name in perms:
                return category
        return 'general'
    
    def user_has_permission(self, user_id: int, permission: Permission, resource_id: Optional[int] = None, resource_type: Optional[str] = None) -> bool:
        """Check if user has specific permission"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get user's role
            user_role = cursor.execute('SELECT role FROM users WHERE id = ?', (user_id,)).fetchone()
            if not user_role:
                return False
            
            user_role = Role(user_role[0])
            
            # Check for user-specific permission override first
            override = cursor.execute('''
                SELECT granted FROM user_permission_overrides upo
                JOIN permissions p ON upo.permission_id = p.id
                WHERE upo.user_id = ? AND p.name = ?
                AND (upo.expires_at IS NULL OR upo.expires_at > CURRENT_TIMESTAMP)
            ''', (user_id, permission.value)).fetchone()
            
            if override is not None:
                granted = bool(override[0])
                self._log_access(user_id, resource_type or 'system', resource_id, 'permission_check', permission.value, granted)
                return granted
            
            # Check role-based permission
            has_role_permission = cursor.execute('''
                SELECT COUNT(*) FROM role_permissions rp
                JOIN roles r ON rp.role_id = r.id
                JOIN permissions p ON rp.permission_id = p.id
                WHERE r.name = ? AND p.name = ?
            ''', (user_role.value, permission.value)).fetchone()[0] > 0
            
            # For resource-specific permissions, check ownership
            if resource_id and resource_type and has_role_permission:
                # Check if user owns the resource or has broader access
                if self._requires_ownership_check(permission):
                    owns_resource = self._user_owns_resource(user_id, resource_type, resource_id)
                    has_broad_access = self._user_has_broad_access(user_role, permission)
                    has_role_permission = owns_resource or has_broad_access
            
            self._log_access(user_id, resource_type or 'system', resource_id, 'permission_check', permission.value, has_role_permission)
            return has_role_permission
    
    def _requires_ownership_check(self, permission: Permission) -> bool:
        """Check if permission requires ownership validation"""
        ownership_permissions = [
            Permission.READ_CLIENT, Permission.UPDATE_CLIENT, Permission.DELETE_CLIENT,
            Permission.READ_PROPERTY, Permission.UPDATE_PROPERTY, Permission.DELETE_PROPERTY,
            Permission.READ_TRANSACTION, Permission.UPDATE_TRANSACTION, Permission.DELETE_TRANSACTION,
            Permission.READ_DOCUMENT, Permission.UPDATE_DOCUMENT, Permission.DELETE_DOCUMENT
        ]
        return permission in ownership_permissions
    
    def _user_owns_resource(self, user_id: int, resource_type: str, resource_id: int) -> bool:
        """Check if user owns specific resource"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Check resource ownership table
            ownership = cursor.execute('''
                SELECT COUNT(*) FROM resource_ownership
                WHERE user_id = ? AND resource_type = ? AND resource_id = ?
            ''', (user_id, resource_type, resource_id)).fetchone()[0]
            
            if ownership > 0:
                return True
            
            # Check resource-specific ownership (e.g., clients.agent_id)
            ownership_fields = {
                'client': 'agent_id',
                'property': 'agent_id',
                'transaction': 'agent_id'
            }
            
            if resource_type in ownership_fields:
                field = ownership_fields[resource_type]
                table = f"{resource_type}s"  # Pluralize table name
                
                owner = cursor.execute(f'''
                    SELECT {field} FROM {table} WHERE id = ?
                ''', (resource_id,)).fetchone()
                
                if owner and owner[0] == user_id:
                    return True
            
            return False
    
    def _user_has_broad_access(self, role: Role, permission: Permission) -> bool:
        """Check if user role has broad access to resource type"""
        broad_access_permissions = [
            Permission.READ_ALL_CLIENTS, Permission.READ_ALL_PROPERTIES, Permission.READ_ALL_TRANSACTIONS
        ]
        
        corresponding_permission = None
        if permission == Permission.READ_CLIENT:
            corresponding_permission = Permission.READ_ALL_CLIENTS
        elif permission == Permission.READ_PROPERTY:
            corresponding_permission = Permission.READ_ALL_PROPERTIES
        elif permission == Permission.READ_TRANSACTION:
            corresponding_permission = Permission.READ_ALL_TRANSACTIONS
        
        return corresponding_permission and RolePermissionMapping.has_permission(role, corresponding_permission)
    
    def _log_access(self, user_id: int, resource_type: str, resource_id: Optional[int], action: str, permission: str, granted: bool):
        """Log access attempt for auditing"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO access_log (user_id, resource_type, resource_id, action, permission_checked, access_granted)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, resource_type, resource_id, action, permission, granted))
            conn.commit()
    
    def grant_permission_to_user(self, user_id: int, permission: Permission, granted_by: int, reason: str = None, expires_at: datetime = None):
        """Grant specific permission to user (override role permissions)"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            perm_id = cursor.execute('SELECT id FROM permissions WHERE name = ?', (permission.value,)).fetchone()
            if not perm_id:
                raise ValueError(f"Permission {permission.value} not found")
            
            cursor.execute('''
                INSERT OR REPLACE INTO user_permission_overrides
                (user_id, permission_id, granted, granted_by, reason, expires_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, perm_id[0], True, granted_by, reason, expires_at))
            
            conn.commit()
            logger.info(f"Permission {permission.value} granted to user {user_id} by {granted_by}")
    
    def revoke_permission_from_user(self, user_id: int, permission: Permission, granted_by: int, reason: str = None):
        """Revoke specific permission from user"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            perm_id = cursor.execute('SELECT id FROM permissions WHERE name = ?', (permission.value,)).fetchone()
            if not perm_id:
                raise ValueError(f"Permission {permission.value} not found")
            
            cursor.execute('''
                INSERT OR REPLACE INTO user_permission_overrides
                (user_id, permission_id, granted, granted_by, reason)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, perm_id[0], False, granted_by, reason))
            
            conn.commit()
            logger.info(f"Permission {permission.value} revoked from user {user_id} by {granted_by}")
    
    def set_resource_owner(self, user_id: int, resource_type: str, resource_id: int, ownership_type: str = 'owner'):
        """Set user as owner of specific resource"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO resource_ownership
                (user_id, resource_type, resource_id, ownership_type)
                VALUES (?, ?, ?, ?)
            ''', (user_id, resource_type, resource_id, ownership_type))
            conn.commit()
    
    def get_user_permissions(self, user_id: int) -> List[str]:
        """Get all effective permissions for user"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get user's role
            user_role = cursor.execute('SELECT role FROM users WHERE id = ?', (user_id,)).fetchone()
            if not user_role:
                return []
            
            # Get role permissions
            role_permissions = cursor.execute('''
                SELECT p.name FROM role_permissions rp
                JOIN roles r ON rp.role_id = r.id
                JOIN permissions p ON rp.permission_id = p.id
                WHERE r.name = ?
            ''', (user_role[0],)).fetchall()
            
            permissions = set(perm[0] for perm in role_permissions)
            
            # Apply user-specific overrides
            overrides = cursor.execute('''
                SELECT p.name, upo.granted FROM user_permission_overrides upo
                JOIN permissions p ON upo.permission_id = p.id
                WHERE upo.user_id = ?
                AND (upo.expires_at IS NULL OR upo.expires_at > CURRENT_TIMESTAMP)
            ''', (user_id,)).fetchall()
            
            for perm_name, granted in overrides:
                if granted:
                    permissions.add(perm_name)
                else:
                    permissions.discard(perm_name)
            
            return list(permissions)

# Decorators for route protection
def requires_permission(permission: Permission, resource_type: str = None):
    """Decorator to require specific permission for route access"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return jsonify({'error': 'Authentication required'}), 401
            
            rbac = RBACManager()
            resource_id = None
            
            # Try to extract resource ID from request
            if resource_type:
                resource_id = request.view_args.get('id') or request.json.get('id') if request.json else None
            
            if not rbac.user_has_permission(current_user.id, permission, resource_id, resource_type):
                return jsonify({'error': 'Insufficient permissions'}), 403
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def requires_role(required_role: Role):
    """Decorator to require specific role for route access"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return jsonify({'error': 'Authentication required'}), 401
            
            user_role = Role(current_user.role)
            
            if not Role.has_higher_privilege(user_role, required_role) and user_role != required_role:
                return jsonify({'error': 'Insufficient role privileges'}), 403
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def requires_ownership_or_permission(permission: Permission, resource_type: str):
    """Decorator to require resource ownership OR specific permission"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return jsonify({'error': 'Authentication required'}), 401
            
            rbac = RBACManager()
            resource_id = request.view_args.get('id')
            
            if not resource_id:
                return jsonify({'error': 'Resource ID required'}), 400
            
            # Check ownership or broad permission
            if rbac.user_has_permission(current_user.id, permission, resource_id, resource_type):
                return f(*args, **kwargs)
            else:
                return jsonify({'error': 'Access denied'}), 403
        
        return decorated_function
    return decorator

def main():
    """Test the RBAC system"""
    rbac = RBACManager()
    
    # Test permission checking
    print("Testing RBAC system...")
    
    # Create a test user (assuming user ID 1 exists with role 'agent')
    permissions = rbac.get_user_permissions(1)
    print(f"User 1 permissions: {permissions}")
    
    # Test specific permission
    has_perm = rbac.user_has_permission(1, Permission.CREATE_CLIENT)
    print(f"User 1 can create clients: {has_perm}")
    
    print("RBAC system test completed!")

if __name__ == "__main__":
    main()