"""
Fix 2019 income amount
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import ServiceCharge, Document

engine = create_engine('sqlite:///instance/db.sqlite3')
Session = sessionmaker(bind=engine)
session = Session()

# Find 2019 income charge
doc_2019 = session.query(Document).filter_by(filename="Accounts 2019 - Yew Tree Square Management Company OCR.pdf").first()

if doc_2019:
    income_2019 = session.query(ServiceCharge).filter_by(
        document_id=doc_2019.id,
        year=2019,
        charge_type='income'
    ).first()
    
    if income_2019:
        print(f"Current 2019 income: EUR {income_2019.amount:,.2f}")
        print(f"Correct 2019 income: EUR 94,633.00")
        
        income_2019.amount = 94633
        session.commit()
        
        print("\n✓ Updated 2019 income to EUR 94,633.00")
        
        # Recalculate surplus/deficit
        expenses = session.query(ServiceCharge).filter_by(
            document_id=doc_2019.id,
            year=2019,
            charge_type='expense'
        ).all()
        
        total_expenses = sum(e.amount for e in expenses)
        surplus_deficit = 94633 - total_expenses
        
        print(f"\n2019 Summary:")
        print(f"  Income:    EUR {94633:>10,.2f}")
        print(f"  Expenses:  EUR {total_expenses:>10,.2f}")
        print(f"  Surplus/(Deficit): EUR {surplus_deficit:>10,.2f}")

session.close()
