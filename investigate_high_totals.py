"""
Investigate why certain years have abnormally high totals
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Document, ServiceCharge

engine = create_engine('sqlite:///instance/db.sqlite3')
Session = sessionmaker(bind=engine)
session = Session()

print("\n" + "="*80)
print("INVESTIGATING 2024 PROPOSED BUDGET (EUR 435,983)")
print("="*80)

docs_2024 = session.query(Document).join(ServiceCharge).filter(
    ServiceCharge.year == 2024,
    Document.document_type == 'Proposed Budget'
).distinct().all()

for doc in docs_2024:
    print(f"\nDocument ID {doc.id}: {doc.filename}")
    charges = session.query(ServiceCharge).filter(
        ServiceCharge.document_id == doc.id,
        ServiceCharge.year == 2024
    ).all()
    
    total = sum(c.amount for c in charges)
    print(f"  Total: EUR {total:,.2f}")
    print(f"  Charges: {len(charges)}")
    print(f"\n  Top 10 charges:")
    for charge in sorted(charges, key=lambda x: x.amount, reverse=True)[:10]:
        print(f"    {charge.charge_name}: EUR {charge.amount:,.2f} [{charge.category or 'uncategorized'}]")

print("\n" + "="*80)
print("INVESTIGATING 2022 AUDITED ACCOUNTS (EUR 251,342)")
print("="*80)

docs_2022 = session.query(Document).join(ServiceCharge).filter(
    ServiceCharge.year == 2022,
    Document.document_type == 'Audited Accounts'
).distinct().all()

for doc in docs_2022:
    print(f"\nDocument ID {doc.id}: {doc.filename}")
    charges = session.query(ServiceCharge).filter(
        ServiceCharge.document_id == doc.id,
        ServiceCharge.year == 2022
    ).all()
    
    total = sum(c.amount for c in charges)
    print(f"  Total: EUR {total:,.2f}")
    print(f"  Charges: {len(charges)}")
    print(f"\n  All charges:")
    for charge in sorted(charges, key=lambda x: x.amount, reverse=True):
        print(f"    {charge.charge_name}: EUR {charge.amount:,.2f} [{charge.category or 'uncategorized'}]")

print("\n" + "="*80)
print("INVESTIGATING 2023 AUDITED ACCOUNTS (EUR 260,583)")
print("="*80)

docs_2023 = session.query(Document).join(ServiceCharge).filter(
    ServiceCharge.year == 2023,
    Document.document_type == 'Audited Accounts'
).distinct().all()

for doc in docs_2023:
    print(f"\nDocument ID {doc.id}: {doc.filename}")
    charges = session.query(ServiceCharge).filter(
        ServiceCharge.document_id == doc.id,
        ServiceCharge.year == 2023
    ).all()
    
    total = sum(c.amount for c in charges)
    print(f"  Total: EUR {total:,.2f}")
    print(f"  Charges: {len(charges)}")
    print(f"\n  All charges:")
    for charge in sorted(charges, key=lambda x: x.amount, reverse=True):
        print(f"    {charge.charge_name}: EUR {charge.amount:,.2f} [{charge.category or 'uncategorized'}]")

session.close()
