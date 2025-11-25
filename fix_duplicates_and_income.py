"""
Fix the 2024 duplicate budget issue and remove income charges from audited accounts
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Document, ServiceCharge

engine = create_engine('sqlite:///instance/db.sqlite3')
Session = sessionmaker(bind=engine)
session = Session()

print("FIXING 2024 DUPLICATE BUDGETS")
print("="*80)

# Check which document to keep
doc12 = session.query(Document).get(12)
doc15 = session.query(Document).get(15)

print(f"\nDoc 12: {doc12.filename}")
print(f"  Charges: {session.query(ServiceCharge).filter_by(document_id=12, year=2024).count()}")
print(f"  Total: EUR {sum(c.amount for c in session.query(ServiceCharge).filter_by(document_id=12, year=2024).all()):,.2f}")

print(f"\nDoc 15: {doc15.filename}")
print(f"  Charges: {session.query(ServiceCharge).filter_by(document_id=15, year=2024).count()}")
print(f"  Total: EUR {sum(c.amount for c in session.query(ServiceCharge).filter_by(document_id=15, year=2024).all()):,.2f}")

print("\n** Doc 15 has detailed breakdown (34 charges) vs Doc 12 summary (2 charges)")
print("** RECOMMENDATION: Delete Doc 12 charges (keep detailed Doc 15)")

response = input("\nDelete Document 12 charges for 2024? (yes/no): ")

if response.lower() == 'yes':
    charges_to_delete = session.query(ServiceCharge).filter_by(document_id=12, year=2024).all()
    print(f"\nDeleting {len(charges_to_delete)} charges from Doc 12:")
    for charge in charges_to_delete:
        print(f"  - {charge.charge_name}: EUR {charge.amount:,.2f}")
        session.delete(charge)
    
    session.commit()
    print("\n✓ Deleted Doc 12 charges successfully")
    
    new_total = sum(c.amount for c in session.query(ServiceCharge).filter_by(year=2024).all())
    print(f"New 2024 total: EUR {new_total:,.2f}")
else:
    print("Skipped deletion")

print("\n" + "="*80)
print("FIXING AUDITED ACCOUNTS - REMOVING INCOME CHARGES")
print("="*80)

# Find income charges in audited accounts
income_keywords = ['service charges', 'service charge due', 'charges due']

for year in [2022, 2023]:
    print(f"\nYear {year}:")
    doc = session.query(Document).join(ServiceCharge).filter(
        ServiceCharge.year == year,
        Document.document_type == 'Audited Accounts'
    ).first()
    
    if doc:
        print(f"  Document: {doc.filename}")
        
        # Find income charges
        income_charges = []
        for charge in session.query(ServiceCharge).filter_by(document_id=doc.id, year=year).all():
            if any(keyword in charge.charge_name.lower() for keyword in income_keywords):
                income_charges.append(charge)
        
        if income_charges:
            print(f"\n  Found {len(income_charges)} income charges:")
            for charge in income_charges:
                print(f"    - {charge.charge_name}: EUR {charge.amount:,.2f}")
            
            response = input(f"\n  Delete these income charges from {year}? (yes/no): ")
            
            if response.lower() == 'yes':
                for charge in income_charges:
                    session.delete(charge)
                
                session.commit()
                print(f"  ✓ Deleted {len(income_charges)} income charges")
                
                new_total = sum(c.amount for c in session.query(ServiceCharge).filter_by(year=year, document_id=doc.id).all())
                print(f"  New total for {year}: EUR {new_total:,.2f}")
            else:
                print("  Skipped deletion")

session.close()
