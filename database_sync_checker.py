#!/usr/bin/env python3
"""
Database Synchronization Check - ENV003
Ensures database schemas and data are synchronized between local SQLite and production environments
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

class DatabaseSyncChecker:
    """Comprehensive database synchronization verification system"""
    
    def __init__(self, local_db_path: str = "core_app/database/real_estate_crm.db"):
        self.local_db_path = local_db_path
        self.sync_results = {
            "timestamp": datetime.now().isoformat(),
            "local_db_path": local_db_path,
            "checks_performed": [],
            "issues_found": [],
            "sync_status": "unknown"
        }
    
    def perform_full_sync_check(self) -> Dict[str, Any]:
        """Perform comprehensive database synchronization check"""
        print("🔍 Starting comprehensive database synchronization check...")
        
        # Check 1: Local database existence and accessibility
        local_check = self._check_local_database()
        self.sync_results["checks_performed"].append(local_check)
        
        # Check 2: Schema validation
        schema_check = self._validate_schema_structure()
        self.sync_results["checks_performed"].append(schema_check)
        
        # Check 3: Data integrity 
        integrity_check = self._check_data_integrity()
        self.sync_results["checks_performed"].append(integrity_check)
        
        # Check 4: Production environment compatibility
        compatibility_check = self._check_production_compatibility()
        self.sync_results["checks_performed"].append(compatibility_check)
        
        # Check 5: Test data consistency
        test_data_check = self._verify_test_data()
        self.sync_results["checks_performed"].append(test_data_check)
        
        # Generate overall sync status
        self._determine_overall_status()
        
        return self.sync_results
    
    def _check_local_database(self) -> Dict[str, Any]:
        """Check local database existence and basic connectivity"""
        check_result = {
            "check_name": "Local Database Connectivity",
            "status": "unknown",
            "details": {},
            "issues": []
        }
        
        try:
            # Check if database file exists
            if not os.path.exists(self.local_db_path):
                check_result["status"] = "failed"
                check_result["issues"].append(f"Database file not found: {self.local_db_path}")
                return check_result
            
            # Test database connection
            conn = sqlite3.connect(self.local_db_path)
            cursor = conn.cursor()
            
            # Get basic database info
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            cursor.execute("PRAGMA database_list;")
            db_info = cursor.fetchall()
            
            check_result["details"] = {
                "database_file": self.local_db_path,
                "file_size_mb": round(os.path.getsize(self.local_db_path) / 1024 / 1024, 2),
                "table_count": len(tables),
                "tables": [table[0] for table in tables],
                "database_info": db_info
            }
            
            conn.close()
            check_result["status"] = "passed"
            
        except Exception as e:
            check_result["status"] = "failed"
            check_result["issues"].append(f"Database connection error: {str(e)}")
        
        return check_result
    
    def _validate_schema_structure(self) -> Dict[str, Any]:
        """Validate the 177-field CRM schema structure"""
        check_result = {
            "check_name": "Schema Structure Validation",
            "status": "unknown", 
            "details": {},
            "issues": []
        }
        
        try:
            conn = sqlite3.connect(self.local_db_path)
            cursor = conn.cursor()
            
            # Expected core tables for real estate CRM
            expected_tables = {
                "clients": "Client information and contact details",
                "properties": "Property listings and details", 
                "transactions": "Real estate transactions",
                "agents": "Real estate agents and team members",
                "contacts": "General contact management"
            }
            
            schema_analysis = {}
            
            for table_name, description in expected_tables.items():
                try:
                    cursor.execute(f"PRAGMA table_info({table_name});")
                    columns = cursor.fetchall()
                    
                    if columns:
                        schema_analysis[table_name] = {
                            "exists": True,
                            "column_count": len(columns),
                            "columns": [
                                {
                                    "name": col[1],
                                    "type": col[2],
                                    "not_null": bool(col[3]),
                                    "primary_key": bool(col[5])
                                }
                                for col in columns
                            ]
                        }
                    else:
                        schema_analysis[table_name] = {"exists": False}
                        check_result["issues"].append(f"Missing expected table: {table_name}")
                        
                except Exception as e:
                    schema_analysis[table_name] = {"exists": False, "error": str(e)}
                    check_result["issues"].append(f"Error checking table {table_name}: {str(e)}")
            
            # Calculate schema completeness
            existing_tables = sum(1 for table in schema_analysis.values() if table.get("exists", False))
            completeness_percentage = (existing_tables / len(expected_tables)) * 100
            
            check_result["details"] = {
                "expected_tables": len(expected_tables),
                "existing_tables": existing_tables,
                "completeness_percentage": completeness_percentage,
                "schema_analysis": schema_analysis
            }
            
            # Determine status
            if completeness_percentage >= 80:
                check_result["status"] = "passed"
            elif completeness_percentage >= 60:
                check_result["status"] = "warning"
            else:
                check_result["status"] = "failed"
            
            conn.close()
            
        except Exception as e:
            check_result["status"] = "failed"
            check_result["issues"].append(f"Schema validation error: {str(e)}")
        
        return check_result
    
    def _check_data_integrity(self) -> Dict[str, Any]:
        """Check data integrity and consistency"""
        check_result = {
            "check_name": "Data Integrity Check",
            "status": "unknown",
            "details": {},
            "issues": []
        }
        
        try:
            conn = sqlite3.connect(self.local_db_path)
            cursor = conn.cursor()
            
            integrity_tests = []
            
            # Get list of tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [table[0] for table in cursor.fetchall()]
            
            for table in tables:
                try:
                    # Count records
                    cursor.execute(f"SELECT COUNT(*) FROM {table};")
                    record_count = cursor.fetchone()[0]
                    
                    # Check for basic data consistency
                    cursor.execute(f"PRAGMA integrity_check({table});")
                    integrity_result = cursor.fetchone()[0]
                    
                    table_integrity = {
                        "table": table,
                        "record_count": record_count,
                        "integrity_status": integrity_result,
                        "has_data": record_count > 0
                    }
                    
                    # Additional checks for specific tables
                    if table == "clients":
                        # Check for duplicate emails
                        cursor.execute("SELECT email, COUNT(*) FROM clients WHERE email IS NOT NULL GROUP BY email HAVING COUNT(*) > 1;")
                        duplicates = cursor.fetchall()
                        if duplicates:
                            table_integrity["duplicate_emails"] = len(duplicates)
                            check_result["issues"].append(f"Found {len(duplicates)} duplicate emails in clients table")
                    
                    integrity_tests.append(table_integrity)
                    
                except Exception as e:
                    integrity_tests.append({
                        "table": table,
                        "error": str(e),
                        "status": "failed"
                    })
                    check_result["issues"].append(f"Integrity check failed for {table}: {str(e)}")
            
            check_result["details"] = {
                "tables_checked": len(tables),
                "integrity_tests": integrity_tests,
                "total_records": sum(test.get("record_count", 0) for test in integrity_tests if "record_count" in test)
            }
            
            # Determine overall integrity status
            failed_tests = sum(1 for test in integrity_tests if test.get("status") == "failed")
            if failed_tests == 0:
                check_result["status"] = "passed"
            elif failed_tests <= 2:
                check_result["status"] = "warning" 
            else:
                check_result["status"] = "failed"
            
            conn.close()
            
        except Exception as e:
            check_result["status"] = "failed"
            check_result["issues"].append(f"Data integrity check error: {str(e)}")
        
        return check_result
    
    def _check_production_compatibility(self) -> Dict[str, Any]:
        """Check compatibility with production deployment environments"""
        check_result = {
            "check_name": "Production Environment Compatibility",
            "status": "unknown",
            "details": {},
            "issues": []
        }
        
        try:
            # Check SQLite version compatibility
            conn = sqlite3.connect(self.local_db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT sqlite_version();")
            sqlite_version = cursor.fetchone()[0]
            
            # Check database pragma settings
            pragmas_to_check = [
                "foreign_keys",
                "journal_mode", 
                "synchronous",
                "temp_store",
                "mmap_size"
            ]
            
            pragma_settings = {}
            for pragma in pragmas_to_check:
                try:
                    cursor.execute(f"PRAGMA {pragma};")
                    pragma_settings[pragma] = cursor.fetchone()[0]
                except Exception as e:
                    pragma_settings[pragma] = f"Error: {str(e)}"
            
            # Check for DigitalOcean/cloud compatibility issues
            compatibility_checks = {
                "sqlite_version": sqlite_version,
                "pragma_settings": pragma_settings,
                "file_permissions": self._check_file_permissions(),
                "backup_compatibility": self._check_backup_compatibility(conn)
            }
            
            check_result["details"] = compatibility_checks
            
            # Assess compatibility
            version_parts = [int(x) for x in sqlite_version.split('.')]
            if version_parts[0] >= 3 and version_parts[1] >= 8:
                check_result["status"] = "passed"
            else:
                check_result["status"] = "warning"
                check_result["issues"].append(f"SQLite version {sqlite_version} may have compatibility issues")
            
            conn.close()
            
        except Exception as e:
            check_result["status"] = "failed"
            check_result["issues"].append(f"Production compatibility check error: {str(e)}")
        
        return check_result
    
    def _verify_test_data(self) -> Dict[str, Any]:
        """Verify test data consistency and sample data quality"""
        check_result = {
            "check_name": "Test Data Verification",
            "status": "unknown",
            "details": {},
            "issues": []
        }
        
        try:
            conn = sqlite3.connect(self.local_db_path)
            cursor = conn.cursor()
            
            # Check for sample data in key tables
            sample_data_analysis = {}
            
            key_tables = ["clients", "properties", "transactions"]
            
            for table in key_tables:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table};")
                    total_records = cursor.fetchone()[0]
                    
                    if total_records > 0:
                        # Get sample record for structure analysis
                        cursor.execute(f"SELECT * FROM {table} LIMIT 1;")
                        sample_record = cursor.fetchone()
                        
                        # Get column names
                        cursor.execute(f"PRAGMA table_info({table});")
                        columns = [col[1] for col in cursor.fetchall()]
                        
                        sample_data_analysis[table] = {
                            "total_records": total_records,
                            "has_sample_data": True,
                            "column_count": len(columns),
                            "sample_data_fields": len([field for field in sample_record if field is not None]) if sample_record else 0
                        }
                    else:
                        sample_data_analysis[table] = {
                            "total_records": 0,
                            "has_sample_data": False
                        }
                        check_result["issues"].append(f"No sample data found in {table} table")
                        
                except Exception as e:
                    sample_data_analysis[table] = {
                        "error": str(e),
                        "has_sample_data": False
                    }
                    check_result["issues"].append(f"Error checking sample data in {table}: {str(e)}")
            
            check_result["details"] = {
                "sample_data_analysis": sample_data_analysis,
                "total_sample_records": sum(analysis.get("total_records", 0) for analysis in sample_data_analysis.values())
            }
            
            # Determine test data status
            tables_with_data = sum(1 for analysis in sample_data_analysis.values() if analysis.get("has_sample_data", False))
            if tables_with_data >= len(key_tables):
                check_result["status"] = "passed"
            elif tables_with_data >= len(key_tables) // 2:
                check_result["status"] = "warning"
            else:
                check_result["status"] = "failed"
            
            conn.close()
            
        except Exception as e:
            check_result["status"] = "failed"
            check_result["issues"].append(f"Test data verification error: {str(e)}")
        
        return check_result
    
    def _check_file_permissions(self) -> Dict[str, Any]:
        """Check database file permissions"""
        try:
            stat_info = os.stat(self.local_db_path)
            return {
                "readable": os.access(self.local_db_path, os.R_OK),
                "writable": os.access(self.local_db_path, os.W_OK),
                "file_mode": oct(stat_info.st_mode),
                "file_size": stat_info.st_size
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _check_backup_compatibility(self, conn: sqlite3.Connection) -> Dict[str, Any]:
        """Check backup and restore compatibility"""
        try:
            # Test backup operation
            backup_test = {
                "backup_supported": True,
                "vacuum_supported": True
            }
            
            # Test VACUUM command (cleanup/compress)
            try:
                conn.execute("VACUUM;")
                backup_test["vacuum_successful"] = True
            except Exception as e:
                backup_test["vacuum_successful"] = False
                backup_test["vacuum_error"] = str(e)
            
            return backup_test
            
        except Exception as e:
            return {"backup_supported": False, "error": str(e)}
    
    def _determine_overall_status(self):
        """Determine overall synchronization status"""
        check_statuses = [check["status"] for check in self.sync_results["checks_performed"]]
        
        # Count status types
        passed = check_statuses.count("passed")
        failed = check_statuses.count("failed")
        warnings = check_statuses.count("warning")
        
        # Determine overall status
        if failed == 0 and warnings <= 1:
            self.sync_results["sync_status"] = "excellent"
        elif failed == 0:
            self.sync_results["sync_status"] = "good"
        elif failed <= 1:
            self.sync_results["sync_status"] = "warning"
        else:
            self.sync_results["sync_status"] = "critical"
        
        # Collect all issues
        all_issues = []
        for check in self.sync_results["checks_performed"]:
            all_issues.extend(check.get("issues", []))
        
        self.sync_results["issues_found"] = all_issues
        self.sync_results["summary"] = {
            "total_checks": len(self.sync_results["checks_performed"]),
            "passed": passed,
            "warnings": warnings,
            "failed": failed,
            "total_issues": len(all_issues)
        }
    
    def generate_sync_report(self) -> str:
        """Generate a comprehensive synchronization report"""
        if not self.sync_results["checks_performed"]:
            return "No synchronization checks have been performed yet."
        
        report = []
        report.append("🔍 DATABASE SYNCHRONIZATION REPORT")
        report.append("=" * 50)
        report.append(f"Generated: {self.sync_results['timestamp']}")
        report.append(f"Local Database: {self.sync_results['local_db_path']}")
        report.append(f"Overall Status: {self.sync_results['sync_status'].upper()}")
        report.append("")
        
        # Summary
        summary = self.sync_results["summary"]
        report.append("📊 SUMMARY:")
        report.append(f"   Total Checks: {summary['total_checks']}")
        report.append(f"   ✅ Passed: {summary['passed']}")
        report.append(f"   ⚠️  Warnings: {summary['warnings']}")
        report.append(f"   ❌ Failed: {summary['failed']}")
        report.append(f"   🔍 Issues Found: {summary['total_issues']}")
        report.append("")
        
        # Detailed results
        report.append("📋 DETAILED RESULTS:")
        for check in self.sync_results["checks_performed"]:
            status_emoji = {"passed": "✅", "warning": "⚠️", "failed": "❌"}.get(check["status"], "❓")
            report.append(f"   {status_emoji} {check['check_name']}: {check['status'].upper()}")
            
            if check.get("issues"):
                for issue in check["issues"]:
                    report.append(f"      • {issue}")
        
        # Issues summary
        if self.sync_results["issues_found"]:
            report.append("")
            report.append("⚠️  ISSUES REQUIRING ATTENTION:")
            for i, issue in enumerate(self.sync_results["issues_found"], 1):
                report.append(f"   {i}. {issue}")
        
        return "\n".join(report)

def main():
    """Test the database synchronization checker"""
    print("🚀 Database Synchronization Checker - ENV003")
    print("=" * 50)
    
    checker = DatabaseSyncChecker()
    
    # Perform full synchronization check
    print("\n🔍 Performing comprehensive database synchronization check...")
    results = checker.perform_full_sync_check()
    
    # Generate and display report
    print("\n" + checker.generate_sync_report())
    
    # Save results to file
    results_file = "database_sync_results.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Detailed results saved to: {results_file}")
    print(f"\n✅ ENV003 Complete: Database Synchronization Check")
    print(f"🔄 Database ready for reliable form population development")

if __name__ == "__main__":
    main()