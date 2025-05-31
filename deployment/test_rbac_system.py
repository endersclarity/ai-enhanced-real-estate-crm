#!/usr/bin/env python3
"""
Test script for Role-Based Access Control (RBAC) System
Validates role hierarchy, permission management, and access control
"""

import unittest
import tempfile
import os
import json
import logging
from datetime import datetime, timedelta
from deployment.rbac_system import RBACManager, Role, Permission, RolePermissionMapping

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RBACSystemTester:
    """Comprehensive testing for RBAC system"""
    
    def __init__(self):
        # Create temporary database for testing
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db_path = self.temp_db.name
        
        self.rbac = RBACManager(self.db_path)
        self.test_results = {}
        
        # Setup test data
        self.setup_test_users()
    
    def __del__(self):
        """Cleanup temporary database"""
        try:
            os.unlink(self.db_path)
        except:
            pass
    
    def setup_test_users(self):
        """Setup test users with different roles"""
        import sqlite3
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT DEFAULT 'agent',
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Insert test users
            test_users = [
                (1, 'admin_user', 'admin@test.com', 'hash', 'admin'),
                (2, 'manager_user', 'manager@test.com', 'hash', 'manager'),
                (3, 'agent_user', 'agent@test.com', 'hash', 'agent'),
                (4, 'agent2_user', 'agent2@test.com', 'hash', 'agent')
            ]
            
            for user_data in test_users:
                cursor.execute('''
                    INSERT OR REPLACE INTO users (id, username, email, password_hash, role)
                    VALUES (?, ?, ?, ?, ?)
                ''', user_data)
            
            # Create test resources
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS clients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    agent_id INTEGER,
                    FOREIGN KEY (agent_id) REFERENCES users (id)
                )
            ''')
            
            cursor.execute('''
                INSERT OR REPLACE INTO clients (id, name, agent_id) VALUES
                (1, 'Client 1', 3),
                (2, 'Client 2', 3),
                (3, 'Client 3', 4)
            ''')
            
            conn.commit()
    
    def test_role_hierarchy(self):
        """Test role hierarchy and privilege levels"""
        try:
            # Test hierarchy levels
            admin_level = Role.get_hierarchy_level(Role.ADMIN)
            manager_level = Role.get_hierarchy_level(Role.MANAGER)
            agent_level = Role.get_hierarchy_level(Role.AGENT)
            
            if admin_level > manager_level > agent_level:
                logger.info("Role hierarchy levels correct")
                
                # Test privilege comparison
                if (Role.has_higher_privilege(Role.ADMIN, Role.MANAGER) and
                    Role.has_higher_privilege(Role.MANAGER, Role.AGENT) and
                    not Role.has_higher_privilege(Role.AGENT, Role.ADMIN)):
                    
                    self.test_results["role_hierarchy"] = {
                        "status": "pass",
                        "admin_level": admin_level,
                        "manager_level": manager_level,
                        "agent_level": agent_level,
                        "message": "Role hierarchy working correctly"
                    }
                    logger.info("Role hierarchy test passed")
                    return True
            
            logger.error("Role hierarchy test failed")
            return False
            
        except Exception as e:
            self.test_results["role_hierarchy"] = {
                "status": "error",
                "error": str(e),
                "message": "Role hierarchy test failed"
            }
            logger.error(f"Role hierarchy test failed: {e}")
            return False
    
    def test_default_role_permissions(self):
        """Test default role permission assignments"""
        try:
            test_cases = [
                (Role.ADMIN, Permission.SYSTEM_CONFIG, True),
                (Role.ADMIN, Permission.MANAGE_ROLES, True),
                (Role.MANAGER, Permission.MANAGE_TEAM, True),
                (Role.MANAGER, Permission.SYSTEM_CONFIG, False),
                (Role.AGENT, Permission.CREATE_CLIENT, True),
                (Role.AGENT, Permission.MANAGE_TEAM, False),
                (Role.AGENT, Permission.READ_ALL_CLIENTS, False)
            ]
            
            passed_tests = 0
            total_tests = len(test_cases)
            
            for role, permission, expected in test_cases:
                actual = RolePermissionMapping.has_permission(role, permission)
                if actual == expected:
                    passed_tests += 1
                    logger.info(f"✅ {role.value} - {permission.value}: {actual} (expected {expected})")
                else:
                    logger.error(f"❌ {role.value} - {permission.value}: {actual} (expected {expected})")
            
            success_rate = (passed_tests / total_tests) * 100
            
            if success_rate >= 90:
                self.test_results["default_permissions"] = {
                    "status": "pass",
                    "success_rate": success_rate,
                    "passed_tests": passed_tests,
                    "total_tests": total_tests,
                    "message": "Default role permissions correct"
                }
                logger.info(f"Default permissions test passed: {success_rate:.1f}%")
                return True
            else:
                self.test_results["default_permissions"] = {
                    "status": "fail",
                    "success_rate": success_rate,
                    "message": "Default role permissions incorrect"
                }
                logger.error(f"Default permissions test failed: {success_rate:.1f}%")
                return False
                
        except Exception as e:
            self.test_results["default_permissions"] = {
                "status": "error",
                "error": str(e),
                "message": "Default permissions test failed"
            }
            logger.error(f"Default permissions test failed: {e}")
            return False
    
    def test_user_permission_checking(self):
        """Test user permission checking functionality"""
        try:
            test_cases = [
                (1, Permission.SYSTEM_CONFIG, True),     # Admin should have system config
                (1, Permission.CREATE_CLIENT, True),     # Admin should have client creation
                (2, Permission.MANAGE_TEAM, True),       # Manager should have team management
                (2, Permission.SYSTEM_CONFIG, False),    # Manager should not have system config
                (3, Permission.CREATE_CLIENT, True),     # Agent should have client creation
                (3, Permission.MANAGE_TEAM, False),      # Agent should not have team management
                (3, Permission.READ_ALL_CLIENTS, False), # Agent should not read all clients
            ]
            
            passed_tests = 0
            total_tests = len(test_cases)
            
            for user_id, permission, expected in test_cases:
                actual = self.rbac.user_has_permission(user_id, permission)
                if actual == expected:
                    passed_tests += 1
                    logger.info(f"✅ User {user_id} - {permission.value}: {actual} (expected {expected})")
                else:
                    logger.error(f"❌ User {user_id} - {permission.value}: {actual} (expected {expected})")
            
            success_rate = (passed_tests / total_tests) * 100
            
            if success_rate >= 90:
                self.test_results["user_permission_checking"] = {
                    "status": "pass",
                    "success_rate": success_rate,
                    "message": "User permission checking working correctly"
                }
                logger.info(f"User permission checking test passed: {success_rate:.1f}%")
                return True
            else:
                self.test_results["user_permission_checking"] = {
                    "status": "fail",
                    "success_rate": success_rate,
                    "message": "User permission checking failed"
                }
                logger.error(f"User permission checking test failed: {success_rate:.1f}%")
                return False
                
        except Exception as e:
            self.test_results["user_permission_checking"] = {
                "status": "error",
                "error": str(e),
                "message": "User permission checking test failed"
            }
            logger.error(f"User permission checking test failed: {e}")
            return False
    
    def test_resource_ownership(self):
        """Test resource ownership checking"""
        try:
            # Set up resource ownership
            self.rbac.set_resource_owner(3, 'client', 1)  # Agent 3 owns client 1
            self.rbac.set_resource_owner(3, 'client', 2)  # Agent 3 owns client 2
            self.rbac.set_resource_owner(4, 'client', 3)  # Agent 4 owns client 3
            
            test_cases = [
                (1, Permission.READ_CLIENT, 1, 'client', True),   # Admin can read any client
                (2, Permission.READ_CLIENT, 1, 'client', True),   # Manager can read any client
                (3, Permission.READ_CLIENT, 1, 'client', True),   # Agent 3 can read own client 1
                (3, Permission.READ_CLIENT, 3, 'client', False),  # Agent 3 cannot read agent 4's client
                (4, Permission.READ_CLIENT, 3, 'client', True),   # Agent 4 can read own client 3
                (4, Permission.READ_CLIENT, 1, 'client', False),  # Agent 4 cannot read agent 3's client
            ]
            
            passed_tests = 0
            total_tests = len(test_cases)
            
            for user_id, permission, resource_id, resource_type, expected in test_cases:
                actual = self.rbac.user_has_permission(user_id, permission, resource_id, resource_type)
                if actual == expected:
                    passed_tests += 1
                    logger.info(f"✅ User {user_id} - {permission.value} on {resource_type} {resource_id}: {actual}")
                else:
                    logger.error(f"❌ User {user_id} - {permission.value} on {resource_type} {resource_id}: {actual} (expected {expected})")
            
            success_rate = (passed_tests / total_tests) * 100
            
            if success_rate >= 80:
                self.test_results["resource_ownership"] = {
                    "status": "pass",
                    "success_rate": success_rate,
                    "message": "Resource ownership checking working"
                }
                logger.info(f"Resource ownership test passed: {success_rate:.1f}%")
                return True
            else:
                self.test_results["resource_ownership"] = {
                    "status": "fail",
                    "success_rate": success_rate,
                    "message": "Resource ownership checking failed"
                }
                logger.error(f"Resource ownership test failed: {success_rate:.1f}%")
                return False
                
        except Exception as e:
            self.test_results["resource_ownership"] = {
                "status": "error",
                "error": str(e),
                "message": "Resource ownership test failed"
            }
            logger.error(f"Resource ownership test failed: {e}")
            return False
    
    def test_permission_overrides(self):
        """Test user-specific permission overrides"""
        try:
            # Grant special permission to agent
            self.rbac.grant_permission_to_user(
                user_id=3,
                permission=Permission.MANAGE_TEAM,
                granted_by=1,
                reason="Special project assignment"
            )
            
            # Check if agent now has the permission
            has_permission = self.rbac.user_has_permission(3, Permission.MANAGE_TEAM)
            
            if has_permission:
                logger.info("Permission override grant working")
                
                # Revoke the permission
                self.rbac.revoke_permission_from_user(
                    user_id=3,
                    permission=Permission.MANAGE_TEAM,
                    granted_by=1,
                    reason="Project completed"
                )
                
                # Check if permission is revoked
                has_permission_after_revoke = self.rbac.user_has_permission(3, Permission.MANAGE_TEAM)
                
                if not has_permission_after_revoke:
                    self.test_results["permission_overrides"] = {
                        "status": "pass",
                        "message": "Permission overrides working correctly"
                    }
                    logger.info("Permission override test passed")
                    return True
                else:
                    logger.error("Permission revoke failed")
                    return False
            else:
                logger.error("Permission grant failed")
                return False
                
        except Exception as e:
            self.test_results["permission_overrides"] = {
                "status": "error",
                "error": str(e),
                "message": "Permission overrides test failed"
            }
            logger.error(f"Permission overrides test failed: {e}")
            return False
    
    def test_temporary_permissions(self):
        """Test temporary permission grants with expiration"""
        try:
            # Grant temporary permission (expires in 1 second)
            expires_at = datetime.now() + timedelta(seconds=1)
            
            self.rbac.grant_permission_to_user(
                user_id=3,
                permission=Permission.VIEW_ANALYTICS,
                granted_by=1,
                reason="Temporary analytics access",
                expires_at=expires_at
            )
            
            # Check if permission is granted
            has_permission = self.rbac.user_has_permission(3, Permission.VIEW_ANALYTICS)
            
            if has_permission:
                logger.info("Temporary permission granted successfully")
                
                # Wait for expiration
                import time
                time.sleep(2)
                
                # Check if permission is expired
                has_permission_after_expiry = self.rbac.user_has_permission(3, Permission.VIEW_ANALYTICS)
                
                if not has_permission_after_expiry:
                    self.test_results["temporary_permissions"] = {
                        "status": "pass",
                        "message": "Temporary permissions working correctly"
                    }
                    logger.info("Temporary permission test passed")
                    return True
                else:
                    logger.error("Temporary permission did not expire")
                    return False
            else:
                logger.error("Temporary permission grant failed")
                return False
                
        except Exception as e:
            self.test_results["temporary_permissions"] = {
                "status": "error",
                "error": str(e),
                "message": "Temporary permissions test failed"
            }
            logger.error(f"Temporary permissions test failed: {e}")
            return False
    
    def test_get_user_permissions(self):
        """Test getting all user permissions"""
        try:
            # Test for different user roles
            admin_permissions = self.rbac.get_user_permissions(1)
            manager_permissions = self.rbac.get_user_permissions(2)
            agent_permissions = self.rbac.get_user_permissions(3)
            
            # Admin should have the most permissions
            # Manager should have moderate permissions
            # Agent should have the least permissions
            
            if (len(admin_permissions) > len(manager_permissions) > len(agent_permissions) and
                len(admin_permissions) > 10 and  # Admin should have many permissions
                len(agent_permissions) > 0):     # Agent should have some permissions
                
                self.test_results["get_user_permissions"] = {
                    "status": "pass",
                    "admin_permissions_count": len(admin_permissions),
                    "manager_permissions_count": len(manager_permissions),
                    "agent_permissions_count": len(agent_permissions),
                    "message": "Get user permissions working correctly"
                }
                logger.info("Get user permissions test passed")
                return True
            else:
                self.test_results["get_user_permissions"] = {
                    "status": "fail",
                    "message": "Permission count hierarchy incorrect"
                }
                logger.error("Get user permissions test failed")
                return False
                
        except Exception as e:
            self.test_results["get_user_permissions"] = {
                "status": "error",
                "error": str(e),
                "message": "Get user permissions test failed"
            }
            logger.error(f"Get user permissions test failed: {e}")
            return False
    
    def test_access_logging(self):
        """Test access logging functionality"""
        try:
            # Perform some permission checks to generate logs
            self.rbac.user_has_permission(1, Permission.SYSTEM_CONFIG)
            self.rbac.user_has_permission(2, Permission.MANAGE_TEAM)
            self.rbac.user_has_permission(3, Permission.CREATE_CLIENT)
            
            # Check if logs were created
            import sqlite3
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                log_count = cursor.execute('SELECT COUNT(*) FROM access_log').fetchone()[0]
                
                if log_count >= 3:  # At least 3 log entries
                    # Check log structure
                    sample_log = cursor.execute('''
                        SELECT user_id, resource_type, action, permission_checked, access_granted
                        FROM access_log LIMIT 1
                    ''').fetchone()
                    
                    if sample_log and len(sample_log) == 5:
                        self.test_results["access_logging"] = {
                            "status": "pass",
                            "log_count": log_count,
                            "message": "Access logging working correctly"
                        }
                        logger.info("Access logging test passed")
                        return True
            
            logger.error("Access logging test failed")
            return False
            
        except Exception as e:
            self.test_results["access_logging"] = {
                "status": "error",
                "error": str(e),
                "message": "Access logging test failed"
            }
            logger.error(f"Access logging test failed: {e}")
            return False
    
    def run_all_tests(self):
        """Run all RBAC system tests"""
        logger.info("Starting comprehensive RBAC system tests")
        
        tests = [
            ("Role Hierarchy", self.test_role_hierarchy),
            ("Default Role Permissions", self.test_default_role_permissions),
            ("User Permission Checking", self.test_user_permission_checking),
            ("Resource Ownership", self.test_resource_ownership),
            ("Permission Overrides", self.test_permission_overrides),
            ("Temporary Permissions", self.test_temporary_permissions),
            ("Get User Permissions", self.test_get_user_permissions),
            ("Access Logging", self.test_access_logging)
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test_name, test_function in tests:
            logger.info(f"Running test: {test_name}")
            try:
                if test_function():
                    passed_tests += 1
                    logger.info(f"✅ {test_name} - PASSED")
                else:
                    logger.error(f"❌ {test_name} - FAILED")
            except Exception as e:
                logger.error(f"💥 {test_name} - ERROR: {e}")
        
        # Generate summary
        success_rate = (passed_tests / total_tests) * 100
        
        summary = {
            "test_date": datetime.now().isoformat(),
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "success_rate": success_rate,
            "overall_status": "pass" if success_rate >= 80 else "fail",
            "detailed_results": self.test_results
        }
        
        # Save results
        with open("deployment/rbac_system_test_results.json", "w") as f:
            json.dump(summary, f, indent=2)
        
        logger.info(f"Test Summary: {passed_tests}/{total_tests} tests passed ({success_rate:.1f}%)")
        
        return summary

def main():
    """Main execution function"""
    tester = RBACSystemTester()
    results = tester.run_all_tests()
    
    if results["overall_status"] == "pass":
        print(f"✅ RBAC system tests PASSED")
        return 0
    else:
        print(f"❌ RBAC system tests FAILED")
        return 1

if __name__ == "__main__":
    exit(main())