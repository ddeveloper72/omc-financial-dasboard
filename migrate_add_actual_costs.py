"""
Database Migration - Add ActualCost Table

This script adds the actual_costs table to the database schema.

Usage:
    python migrate_add_actual_costs.py
"""

from app import app, db
from models import ActualCost

def main():
    """Create actual_costs table"""
    with app.app_context():
        print("Creating actual_costs table...")
        
        # Create all tables (only creates missing tables, doesn't affect existing ones)
        db.create_all()
        
        print("Migration complete!")
        print("actual_costs table created successfully.")

if __name__ == '__main__':
    main()
