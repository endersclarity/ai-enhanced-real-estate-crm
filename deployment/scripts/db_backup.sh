#!/bin/bash
# Automated PostgreSQL backup script for Narissa Realty CRM
# Runs daily at 2:00 AM with 30-day retention

BACKUP_DIR="/var/backups/postgresql"
DB_NAME="narissa_realty_crm"
DB_HOST="db-narissa-realty-crm-prod.db.ondigitalocean.com"
DB_PORT="25060"
DB_USER="crm_backup"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/crm_backup_$TIMESTAMP.sql.gz"

# Create backup directory
mkdir -p $BACKUP_DIR

# Create database backup
pg_dump -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME | gzip > $BACKUP_FILE

# Verify backup
if [ $? -eq 0 ]; then
    echo "✅ Backup successful: $BACKUP_FILE"
    
    # Upload to S3 (if configured)
    # aws s3 cp $BACKUP_FILE s3://narissa-crm-backups/database/
    
    # Remove backups older than 30 days
    find $BACKUP_DIR -name "crm_backup_*.sql.gz" -mtime +30 -delete
    
    echo "🗑️ Cleaned up old backups (30+ days)"
else
    echo "❌ Backup failed"
    exit 1
fi
