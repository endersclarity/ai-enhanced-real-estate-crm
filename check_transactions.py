import sqlite3

print('🔍 CHECKING FOR TRANSACTION RECORDS IN CRM DATABASE')
print('=' * 60)

try:
    conn = sqlite3.connect('real_estate_crm.db')
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute(" SELECT name FROM sqlite_master WHERE type=table\)
