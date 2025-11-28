"""Drop and recreate actual_costs table"""
from app import app, db
from sqlalchemy import text

with app.app_context():
    with db.engine.connect() as conn:
        conn.execute(text('DROP TABLE IF EXISTS actual_costs'))
        conn.commit()
    print("Dropped actual_costs table")
    
    db.create_all()
    print("Recreated actual_costs table")
