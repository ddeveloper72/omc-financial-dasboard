"""
Check year-by-year totals
"""
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from models import Document, ServiceCharge

engine = create_engine('sqlite:///instance/db.sqlite3')
Session = sessionmaker(bind=engine)
session = Session()

print("Year-by-Year Breakdown:")
print("="*80)

for year in [2019, 2021, 2022, 2023, 2024, 2025]:
    print(f"\nYear {year}:")
    print("-"*80)
    
    # Proposed Budget
    proposed = session.query(
        func.sum(ServiceCharge.amount)
    ).join(Document).filter(
        ServiceCharge.year == year,
        Document.document_type == 'Proposed Budget'
    ).scalar()
    
    # Audited Accounts
    audited = session.query(
        func.sum(ServiceCharge.amount)
    ).join(Document).filter(
        ServiceCharge.year == year,
        Document.document_type == 'Audited Accounts'
    ).scalar()
    
    print(f"  Proposed Budget: EUR {proposed:>12,.2f}" if proposed else "  Proposed Budget: None")
    print(f"  Audited Accounts: EUR {audited:>12,.2f}" if audited else "  Audited Accounts: None")
    
    # Show charge counts
    if proposed:
        count = session.query(ServiceCharge).join(Document).filter(
            ServiceCharge.year == year,
            Document.document_type == 'Proposed Budget'
        ).count()
        print(f"  Proposed charges: {count}")
    
    if audited:
        count = session.query(ServiceCharge).join(Document).filter(
            ServiceCharge.year == year,
            Document.document_type == 'Audited Accounts'
        ).count()
        print(f"  Audited charges: {count}")

session.close()
