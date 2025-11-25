"""
Check what's left in audited accounts after removing income
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Document, ServiceCharge

engine = create_engine('sqlite:///instance/db.sqlite3')
Session = sessionmaker(bind=engine)
session = Session()

for year in [2022, 2023]:
    print(f"\n{'='*80}")
    print(f"{year} AUDITED ACCOUNTS - Remaining Charges")
    print(f"{'='*80}")
    
    doc = session.query(Document).join(ServiceCharge).filter(
        ServiceCharge.year == year,
        Document.document_type == 'Audited Accounts'
    ).first()
    
    if doc:
        charges = session.query(ServiceCharge).filter_by(
            document_id=doc.id,
            year=year
        ).order_by(ServiceCharge.amount.desc()).all()
        
        total = sum(c.amount for c in charges)
        
        print(f"\nDocument: {doc.filename}")
        print(f"Total charges: {len(charges)}")
        print(f"Total amount: EUR {total:,.2f}")
        print(f"\nAll charges:")
        for charge in charges:
            print(f"  {charge.charge_name}: EUR {charge.amount:,.2f} [{charge.category or 'uncategorized'}]")

session.close()
