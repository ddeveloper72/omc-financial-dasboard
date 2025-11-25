"""
Check what we have for the 2019 Accounts document
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Document, ServiceCharge

engine = create_engine('sqlite:///instance/db.sqlite3')
Session = sessionmaker(bind=engine)
session = Session()

# Find the 2019 accounts document
doc = session.query(Document).filter(
    Document.filename.like('%2019%'),
    Document.document_type == 'Audited Accounts'
).first()

if doc:
    print(f"Found document: {doc.filename}")
    print(f"Document ID: {doc.id}")
    print(f"Filepath: {doc.filepath}")
    print(f"Type: {doc.document_type}")
    print(f"Status: {doc.status}")
    print("="*80)
    
    # Get charges
    charges = session.query(ServiceCharge).filter_by(document_id=doc.id).all()
    print(f"\nExtracted {len(charges)} charges:")
    
    # Group by year
    by_year = {}
    for charge in charges:
        if charge.year not in by_year:
            by_year[charge.year] = []
        by_year[charge.year].append(charge)
    
    for year in sorted(by_year.keys()):
        print(f"\nYear {year}: {len(by_year[year])} charges")
        total = 0
        for charge in by_year[year]:
            print(f"  {charge.charge_name:<50} EUR {charge.amount:>10,.2f}")
            total += charge.amount
        print(f"  {'TOTAL':50s} EUR {total:>10,.2f}")
else:
    print("Document not found in database")

session.close()
