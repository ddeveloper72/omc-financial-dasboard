"""
Analyze 2024 Draft Budget to understand the charge structure
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Document, ServiceCharge

engine = create_engine('sqlite:///instance/db.sqlite3')
Session = sessionmaker(bind=engine)
session = Session()

doc = session.query(Document).get(15)  # YTS Draft Budget 2024.pdf

print("="*80)
print("2024 DRAFT BUDGET - All Charges")
print("="*80)
print(f"\nDocument: {doc.filename}")

charges = session.query(ServiceCharge).filter_by(document_id=15, year=2024).order_by(ServiceCharge.amount.desc()).all()

total = sum(c.amount for c in charges)
print(f"Total: EUR {total:,.2f}")
print(f"Number of charges: {len(charges)}")

print("\nAll charges (sorted by amount):")
for i, charge in enumerate(charges, 1):
    print(f"{i:2}. {charge.charge_name:50} EUR {charge.amount:>10,.2f}  [{charge.category or 'uncategorized'}]")

# Check if "Common Area Budget" might be a summary
print("\n" + "="*80)
print("ANALYSIS: Is 'Common Area Budget' a double-count?")
print("="*80)

common_area = next((c for c in charges if 'common area' in c.charge_name.lower()), None)
if common_area:
    print(f"\n'Common Area Budget' = EUR {common_area.amount:,.2f}")
    
    # Sum all other non-capital charges
    other_charges_sum = sum(c.amount for c in charges if c != common_area and 'sinking' not in c.charge_name.lower() and 'gate' not in c.charge_name.lower())
    
    print(f"\nSum of all other charges (excluding Gate and Sinking Fund) = EUR {other_charges_sum:,.2f}")
    print(f"\nIf we exclude 'Common Area Budget', total = EUR {total - common_area.amount:,.2f}")

session.close()
