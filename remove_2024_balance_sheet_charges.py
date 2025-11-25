"""
Remove the incorrect balance sheet charges from 2024 abridged accounts
These are not expenses, just balance sheet items
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Document, ServiceCharge

engine = create_engine('sqlite:///instance/db.sqlite3')
Session = sessionmaker(bind=engine)
session = Session()

print("Removing incorrect 2024 balance sheet charges...")
print("=" * 80)

# Show what we're deleting
charges_to_delete = session.query(ServiceCharge).filter(
    ServiceCharge.document_id == 25,
    ServiceCharge.year == 2024
).all()

print(f"\nCharges to delete from Document ID 25 (2024 Abridged):")
for charge in charges_to_delete:
    print(f"  - {charge.charge_name:<50} EUR {charge.amount:>10,.2f}")

# Delete them
deleted_count = len(charges_to_delete)
for charge in charges_to_delete:
    session.delete(charge)

session.commit()

print(f"\nDeleted {deleted_count} charges")
print("\nThese were balance sheet items (Debtors/Creditors), not actual expenses.")
print("We need the full 2024 audited accounts with expense breakdown for comparison.")

session.close()
