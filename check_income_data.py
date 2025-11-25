"""
Check if audited accounts contain income data
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Document, ServiceCharge

engine = create_engine('sqlite:///instance/db.sqlite3')
Session = sessionmaker(bind=engine)
session = Session()

print("="*80)
print("INCOME DATA IN AUDITED ACCOUNTS")
print("="*80)

# Check for any charges with charge_type='income'
income_charges = session.query(ServiceCharge).filter_by(charge_type='income').all()

if income_charges:
    print(f"\nFound {len(income_charges)} income charges in database:")
    for charge in income_charges:
        doc = session.query(Document).get(charge.document_id)
        print(f"  {charge.year}: {charge.charge_name} = EUR {charge.amount:,.2f} ({doc.filename})")
else:
    print("\nNo income charges found with charge_type='income'")

# Check for charges that might be income based on name
print("\n" + "="*80)
print("CHECKING FOR INCOME IN CHARGE NAMES")
print("="*80)

income_keywords = ['service charge', 'income', 'revenue', 'charges due', 'receivable']

audited_docs = session.query(Document).filter_by(document_type='Audited Accounts').all()

for doc in audited_docs:
    print(f"\n{doc.filename}:")
    charges = session.query(ServiceCharge).filter_by(document_id=doc.id).all()
    
    # Look for income-related charges
    potential_income = [c for c in charges if any(kw in c.charge_name.lower() for kw in income_keywords)]
    
    if potential_income:
        print(f"  Found {len(potential_income)} potential income items:")
        for charge in potential_income:
            print(f"    {charge.year}: {charge.charge_name} = EUR {charge.amount:,.2f} [charge_type={charge.charge_type}]")
    else:
        print(f"  No income items found in this document")
        print(f"  Total charges: {len(charges)}")

print("\n" + "="*80)
print("INCOME TOTALS FROM PDF ANALYSIS")
print("="*80)

# From earlier analysis, we know the PDFs show:
print("\nFrom Income and Expenditure Account pages:")
print("  2019: Income = ? (need to check)")
print("  2022: Income = EUR 99,553 (Page 9 of YTS Audited Accounts 2022.pdf)")
print("  2023: Income = EUR 143,472 (Page 9 of Financial Statements 2023.pdf)")

print("\nNote: These were the 'Service Charges' income values we DELETED earlier")
print("because they were mixed with expense data.")

session.close()
