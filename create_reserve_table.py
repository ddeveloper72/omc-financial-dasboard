"""
Create reserve_balances table
"""
from app import app, db

with app.app_context():
    print('Creating reserve_balances table...')
    
    # Import the model to ensure it's registered
    from models import ReserveBalance
    
    # Create the table
    db.create_all()
    
    print('✓ reserve_balances table created successfully')
    print('\nTable structure:')
    print('  - id (Primary Key)')
    print('  - year (Integer, Unique)')
    print('  - opening_balance (Float)')
    print('  - contributions (Float)')
    print('  - expenditures (Float)')
    print('  - closing_balance (Float, Required)')
    print('  - source_document_id (Foreign Key to documents)')
    print('  - notes (Text)')
    print('  - created_date (DateTime)')
    print('  - updated_date (DateTime)')
