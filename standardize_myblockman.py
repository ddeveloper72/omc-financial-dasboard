"""
Standardize MyBlockman charge name variations
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import ServiceCharge

engine = create_engine('sqlite:///instance/db.sqlite3')
Session = sessionmaker(bind=engine)
session = Session()

# Find all MyBlockman variations
myblockman_charges = session.query(ServiceCharge).filter(
    ServiceCharge.charge_name.like('%blockman%')
).all()

print("Found MyBlockman variations:")
print("="*80)
for charge in myblockman_charges:
    print(f"ID {charge.id}: '{charge.charge_name}' -> Year {charge.year}, EUR {charge.amount:,.2f}")

# Standardize to "MyBlockman Annual Charge"
standard_name = "MyBlockman Annual Charge"

print(f"\n{'='*80}")
print(f"Standardizing all to: '{standard_name}'")
print("="*80)

for charge in myblockman_charges:
    if charge.charge_name != standard_name:
        old_name = charge.charge_name
        charge.charge_name = standard_name
        print(f"Updated ID {charge.id}: '{old_name}' -> '{standard_name}'")

session.commit()

print(f"\n✓ Updated {len(myblockman_charges)} MyBlockman charges")

# Verify
updated = session.query(ServiceCharge).filter(
    ServiceCharge.charge_name == standard_name
).count()

print(f"✓ Verified: {updated} charges now named '{standard_name}'")

session.close()
