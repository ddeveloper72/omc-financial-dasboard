"""
Migrate database schema to add new columns
"""
import sqlite3
from pathlib import Path

# Database path
DB_PATH = Path(__file__).parent / 'instance' / 'db.sqlite3'

def migrate_database():
    """Add new columns to existing tables"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("Starting database migration...")
    
    # Check if charge_type column exists
    cursor.execute("PRAGMA table_info(service_charges)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'charge_type' not in columns:
        print("Adding charge_type column to service_charges table...")
        cursor.execute("""
            ALTER TABLE service_charges 
            ADD COLUMN charge_type VARCHAR(20) DEFAULT 'expense'
        """)
        print("  - charge_type column added successfully")
    else:
        print("  - charge_type column already exists")
    
    # Check if document_type column exists in documents table
    cursor.execute("PRAGMA table_info(documents)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'document_type' not in columns:
        print("Adding document_type column to documents table...")
        cursor.execute("""
            ALTER TABLE documents 
            ADD COLUMN document_type VARCHAR(50) DEFAULT 'Other'
        """)
        print("  - document_type column added successfully")
    else:
        print("  - document_type column already exists")
    
    conn.commit()
    conn.close()
    
    print("\nDatabase migration completed successfully!")
    print("\nNext steps:")
    print("1. Run: python classify_documents.py")
    print("2. Run: python reset_status.py")
    print("3. Run: python process_documents.py")

if __name__ == '__main__':
    migrate_database()
