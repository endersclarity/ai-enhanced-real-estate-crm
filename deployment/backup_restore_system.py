#!/usr/bin/env python3
"""
Data Backup and Restore System for Narissa Realty CRM
Implements automated database backups, application data backup, and disaster recovery
"""

import os
import json
import sqlite3
import shutil
import gzip
import logging
import schedule
import time
from datetime import datetime, timedelta
from pathlib import Path
import subprocess
import threading
from typing import Dict, List, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BackupRestoreSystem:
    """Complete backup and restore system"""
    
    def __init__(self, db_path="real_estate_crm.db", backup_dir="backups"):
        self.db_path = db_path
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
        
        # Backup configuration
        self.config = {
            'retention_days': 30,
            'max_backup_size_mb': 1000,
            'compression_enabled': True,
            'backup_schedule': {
                'full_backup': 'daily',
                'incremental_backup': 'hourly'
            }
        }
        
        self.init_backup_tracking()
    
    def init_backup_tracking(self):
        """Initialize backup tracking database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS backup_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    backup_type TEXT NOT NULL,
                    backup_path TEXT NOT NULL,
                    file_size INTEGER,
                    checksum TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    verified BOOLEAN DEFAULT 0,
                    status TEXT DEFAULT 'completed'
                )
            ''')
            
            conn.commit()
    
    def create_full_backup(self) -> Dict:
        """Create complete database backup"""
        backup_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"full_backup_{backup_timestamp}.db"
        
        if self.config['compression_enabled']:
            backup_filename += ".gz"
        
        backup_path = self.backup_dir / backup_filename
        
        try:
            # Create database backup
            logger.info(f"Creating full backup: {backup_filename}")
            
            if self.config['compression_enabled']:
                with open(self.db_path, 'rb') as src, gzip.open(backup_path, 'wb') as dst:
                    shutil.copyfileobj(src, dst)
            else:
                shutil.copy2(self.db_path, backup_path)
            
            # Calculate file size and checksum
            file_size = backup_path.stat().st_size
            checksum = self._calculate_checksum(backup_path)
            
            # Record backup in history
            self._record_backup(
                backup_type='full',
                backup_path=str(backup_path),
                file_size=file_size,
                checksum=checksum
            )
            
            # Verify backup
            verification_result = self.verify_backup(str(backup_path))
            
            result = {
                'success': True,
                'backup_path': str(backup_path),
                'file_size_mb': file_size / (1024 * 1024),
                'checksum': checksum,
                'verified': verification_result['valid'],
                'timestamp': backup_timestamp
            }
            
            logger.info(f"Full backup completed: {backup_filename} ({file_size / (1024 * 1024):.2f} MB)")
            return result
            
        except Exception as e:
            logger.error(f"Full backup failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_incremental_backup(self, since_timestamp: datetime = None) -> Dict:
        """Create incremental backup with changes since last backup"""
        if since_timestamp is None:
            # Get last backup timestamp
            since_timestamp = self._get_last_backup_timestamp()
        
        backup_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"incremental_backup_{backup_timestamp}.json"
        
        if self.config['compression_enabled']:
            backup_filename += ".gz"
        
        backup_path = self.backup_dir / backup_filename
        
        try:
            logger.info(f"Creating incremental backup since {since_timestamp}")
            
            # Extract changes since timestamp
            changes = self._extract_changes_since(since_timestamp)
            
            # Save changes to backup file
            if self.config['compression_enabled']:
                with gzip.open(backup_path, 'wt') as f:
                    json.dump(changes, f, indent=2, default=str)
            else:
                with open(backup_path, 'w') as f:
                    json.dump(changes, f, indent=2, default=str)
            
            file_size = backup_path.stat().st_size
            checksum = self._calculate_checksum(backup_path)
            
            # Record backup
            self._record_backup(
                backup_type='incremental',
                backup_path=str(backup_path),
                file_size=file_size,
                checksum=checksum
            )
            
            result = {
                'success': True,
                'backup_path': str(backup_path),
                'file_size_mb': file_size / (1024 * 1024),
                'checksum': checksum,
                'changes_count': sum(len(table_changes) for table_changes in changes.values()),
                'timestamp': backup_timestamp
            }
            
            logger.info(f"Incremental backup completed: {backup_filename}")
            return result
            
        except Exception as e:
            logger.error(f"Incremental backup failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def restore_from_backup(self, backup_path: str, restore_type: str = 'full') -> Dict:
        """Restore database from backup"""
        logger.info(f"Starting {restore_type} restore from {backup_path}")
        
        backup_file = Path(backup_path)
        if not backup_file.exists():
            return {
                'success': False,
                'error': f"Backup file not found: {backup_path}"
            }
        
        try:
            # Verify backup before restore
            verification = self.verify_backup(backup_path)
            if not verification['valid']:
                return {
                    'success': False,
                    'error': f"Backup verification failed: {verification['error']}"
                }
            
            # Create backup of current database
            current_backup = self._backup_current_database()
            
            if restore_type == 'full':
                result = self._restore_full_backup(backup_path)
            else:
                result = self._restore_incremental_backup(backup_path)
            
            if result['success']:
                logger.info(f"Restore completed successfully from {backup_path}")
            else:
                # Restore original database if restore failed
                self._restore_from_temp_backup(current_backup)
                logger.error(f"Restore failed, original database restored")
            
            # Clean up temporary backup
            if current_backup and Path(current_backup).exists():
                os.remove(current_backup)
            
            return result
            
        except Exception as e:
            logger.error(f"Restore operation failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def verify_backup(self, backup_path: str) -> Dict:
        """Verify backup integrity"""
        backup_file = Path(backup_path)
        
        if not backup_file.exists():
            return {
                'valid': False,
                'error': 'Backup file does not exist'
            }
        
        try:
            # Calculate current checksum
            current_checksum = self._calculate_checksum(backup_file)
            
            # Get stored checksum from backup history
            stored_checksum = self._get_stored_checksum(backup_path)
            
            if stored_checksum and current_checksum != stored_checksum:
                return {
                    'valid': False,
                    'error': 'Checksum mismatch - backup may be corrupted'
                }
            
            # Additional validation based on backup type
            if backup_path.endswith('.db') or backup_path.endswith('.db.gz'):
                validation = self._validate_database_backup(backup_path)
            else:
                validation = self._validate_incremental_backup(backup_path)
            
            if validation['valid']:
                # Update verification status
                self._update_backup_verification(backup_path, True)
            
            return validation
            
        except Exception as e:
            return {
                'valid': False,
                'error': str(e)
            }
    
    def cleanup_old_backups(self) -> Dict:
        """Clean up old backups based on retention policy"""
        cutoff_date = datetime.now() - timedelta(days=self.config['retention_days'])
        
        removed_backups = []
        total_space_freed = 0
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get old backups
                old_backups = cursor.execute('''
                    SELECT id, backup_path, file_size FROM backup_history
                    WHERE created_at < ?
                ''', (cutoff_date,)).fetchall()
                
                for backup_id, backup_path, file_size in old_backups:
                    backup_file = Path(backup_path)
                    
                    if backup_file.exists():
                        backup_file.unlink()
                        removed_backups.append(backup_path)
                        total_space_freed += file_size or 0
                    
                    # Remove from history
                    cursor.execute('DELETE FROM backup_history WHERE id = ?', (backup_id,))
                
                conn.commit()
            
            logger.info(f"Cleaned up {len(removed_backups)} old backups, freed {total_space_freed / (1024 * 1024):.2f} MB")
            
            return {
                'success': True,
                'removed_count': len(removed_backups),
                'space_freed_mb': total_space_freed / (1024 * 1024)
            }
            
        except Exception as e:
            logger.error(f"Backup cleanup failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def schedule_automated_backups(self):
        """Schedule automated backup jobs"""
        # Schedule full backup daily at 2 AM
        schedule.every().day.at("02:00").do(self.create_full_backup)
        
        # Schedule incremental backup every 4 hours
        schedule.every(4).hours.do(self.create_incremental_backup)
        
        # Schedule cleanup weekly
        schedule.every().week.do(self.cleanup_old_backups)
        
        logger.info("Automated backup schedule configured")
    
    def start_backup_scheduler(self):
        """Start background backup scheduler"""
        def run_scheduler():
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
        logger.info("Backup scheduler started")
    
    def get_backup_status(self) -> Dict:
        """Get current backup system status"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get backup statistics
            total_backups = cursor.execute('SELECT COUNT(*) FROM backup_history').fetchone()[0]
            
            recent_backups = cursor.execute('''
                SELECT backup_type, backup_path, created_at, verified, file_size
                FROM backup_history
                ORDER BY created_at DESC
                LIMIT 10
            ''').fetchall()
            
            last_full_backup = cursor.execute('''
                SELECT created_at FROM backup_history
                WHERE backup_type = 'full'
                ORDER BY created_at DESC
                LIMIT 1
            ''').fetchone()
            
            # Calculate total backup size
            total_size = cursor.execute('SELECT SUM(file_size) FROM backup_history').fetchone()[0] or 0
            
        return {
            'total_backups': total_backups,
            'total_size_mb': total_size / (1024 * 1024),
            'last_full_backup': last_full_backup[0] if last_full_backup else None,
            'recent_backups': [
                {
                    'type': backup[0],
                    'path': backup[1],
                    'created_at': backup[2],
                    'verified': bool(backup[3]),
                    'size_mb': (backup[4] or 0) / (1024 * 1024)
                }
                for backup in recent_backups
            ],
            'backup_directory': str(self.backup_dir),
            'config': self.config
        }
    
    # Helper methods
    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate MD5 checksum of file"""
        import hashlib
        
        md5_hash = hashlib.md5()
        
        if str(file_path).endswith('.gz'):
            with gzip.open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    md5_hash.update(chunk)
        else:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    md5_hash.update(chunk)
        
        return md5_hash.hexdigest()
    
    def _record_backup(self, backup_type: str, backup_path: str, file_size: int, checksum: str):
        """Record backup in history"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO backup_history (backup_type, backup_path, file_size, checksum)
                VALUES (?, ?, ?, ?)
            ''', (backup_type, backup_path, file_size, checksum))
            conn.commit()
    
    def _get_last_backup_timestamp(self) -> datetime:
        """Get timestamp of last backup"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            result = cursor.execute('''
                SELECT created_at FROM backup_history
                ORDER BY created_at DESC
                LIMIT 1
            ''').fetchone()
            
            if result:
                return datetime.fromisoformat(result[0])
            else:
                return datetime.now() - timedelta(hours=24)  # Default to 24 hours ago
    
    def _extract_changes_since(self, since_timestamp: datetime) -> Dict:
        """Extract database changes since timestamp"""
        changes = {}
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get list of tables with timestamp columns
            tables_with_timestamps = [
                ('users', 'created_at'),
                ('clients', 'created_at'),
                ('properties', 'created_at'),
                ('transactions', 'created_at'),
                ('request_metrics', 'timestamp'),
                ('system_metrics', 'timestamp')
            ]
            
            for table, timestamp_col in tables_with_timestamps:
                try:
                    # Check if table exists
                    cursor.execute('''
                        SELECT name FROM sqlite_master
                        WHERE type='table' AND name=?
                    ''', (table,))
                    
                    if cursor.fetchone():
                        # Get changes since timestamp
                        cursor.execute(f'''
                            SELECT * FROM {table}
                            WHERE {timestamp_col} > ?
                        ''', (since_timestamp,))
                        
                        rows = cursor.fetchall()
                        if rows:
                            # Get column names
                            cursor.execute(f'PRAGMA table_info({table})')
                            columns = [col[1] for col in cursor.fetchall()]
                            
                            changes[table] = [
                                dict(zip(columns, row)) for row in rows
                            ]
                
                except Exception as e:
                    logger.warning(f"Could not extract changes from {table}: {e}")
        
        return changes
    
    def _backup_current_database(self) -> str:
        """Create temporary backup of current database"""
        temp_backup_path = f"{self.db_path}.temp_backup_{int(time.time())}"
        shutil.copy2(self.db_path, temp_backup_path)
        return temp_backup_path
    
    def _restore_full_backup(self, backup_path: str) -> Dict:
        """Restore from full backup"""
        try:
            if backup_path.endswith('.gz'):
                with gzip.open(backup_path, 'rb') as src, open(self.db_path, 'wb') as dst:
                    shutil.copyfileobj(src, dst)
            else:
                shutil.copy2(backup_path, self.db_path)
            
            return {'success': True}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _restore_incremental_backup(self, backup_path: str) -> Dict:
        """Restore from incremental backup"""
        try:
            # Load incremental changes
            if backup_path.endswith('.gz'):
                with gzip.open(backup_path, 'rt') as f:
                    changes = json.load(f)
            else:
                with open(backup_path, 'r') as f:
                    changes = json.load(f)
            
            # Apply changes to database
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                for table, rows in changes.items():
                    if rows:
                        # Simple approach: insert/replace rows
                        columns = list(rows[0].keys())
                        placeholders = ', '.join(['?' for _ in columns])
                        
                        for row in rows:
                            values = [row[col] for col in columns]
                            cursor.execute(f'''
                                INSERT OR REPLACE INTO {table} ({', '.join(columns)})
                                VALUES ({placeholders})
                            ''', values)
                
                conn.commit()
            
            return {'success': True}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _validate_database_backup(self, backup_path: str) -> Dict:
        """Validate database backup file"""
        try:
            # Create temporary file for validation
            temp_db_path = f"temp_validation_{int(time.time())}.db"
            
            if backup_path.endswith('.gz'):
                with gzip.open(backup_path, 'rb') as src, open(temp_db_path, 'wb') as dst:
                    shutil.copyfileobj(src, dst)
            else:
                shutil.copy2(backup_path, temp_db_path)
            
            # Try to open and query the database
            with sqlite3.connect(temp_db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) FROM users')
                cursor.fetchone()
            
            # Clean up
            os.remove(temp_db_path)
            
            return {'valid': True}
            
        except Exception as e:
            # Clean up
            if os.path.exists(temp_db_path):
                os.remove(temp_db_path)
            
            return {'valid': False, 'error': str(e)}
    
    def _validate_incremental_backup(self, backup_path: str) -> Dict:
        """Validate incremental backup file"""
        try:
            if backup_path.endswith('.gz'):
                with gzip.open(backup_path, 'rt') as f:
                    changes = json.load(f)
            else:
                with open(backup_path, 'r') as f:
                    changes = json.load(f)
            
            # Validate JSON structure
            if isinstance(changes, dict):
                return {'valid': True}
            else:
                return {'valid': False, 'error': 'Invalid backup format'}
            
        except Exception as e:
            return {'valid': False, 'error': str(e)}

def main():
    """Test the backup and restore system"""
    backup_system = BackupRestoreSystem()
    
    print("Data Backup and Restore System Test")
    print("=" * 40)
    
    # Test full backup
    print("1. Creating full backup...")
    full_backup_result = backup_system.create_full_backup()
    print(f"Result: {full_backup_result}")
    
    # Test incremental backup
    print("\n2. Creating incremental backup...")
    inc_backup_result = backup_system.create_incremental_backup()
    print(f"Result: {inc_backup_result}")
    
    # Test backup verification
    if full_backup_result['success']:
        print("\n3. Verifying backup...")
        verification = backup_system.verify_backup(full_backup_result['backup_path'])
        print(f"Verification: {verification}")
    
    # Get backup status
    print("\n4. Getting backup status...")
    status = backup_system.get_backup_status()
    print(f"Total backups: {status['total_backups']}")
    print(f"Total size: {status['total_size_mb']:.2f} MB")
    
    print("\nBackup and restore system test completed!")

if __name__ == "__main__":
    main()