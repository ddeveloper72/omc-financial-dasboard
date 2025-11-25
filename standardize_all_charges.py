"""
Standardize all charge name variations
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import ServiceCharge

engine = create_engine('sqlite:///instance/db.sqlite3')
Session = sessionmaker(bind=engine)
session = Session()

# Define standardization rules
standardization_rules = {
    # Bank charges - capitalize consistently
    'Bank charges': 'Bank Charges',
    
    # Building repairs - use consistent dash format
    'Building   General Repairs': 'Building - General Repairs',
    
    # CCTV - fix typo
    'CCTVm aintenance/repairs': 'CCTV maintenance/repairs',
    
    # Waste collections - use hyphen for "Non-domestic"
    'Non domestic Waste Collections': 'Non-domestic Waste Collections',
    
    # Legal Fees - fix spacing
    'LegalF ees': 'Legal Fees',
    
    # Maintenance - fix typo
    'Malntenance of Fire Extinguishers': 'Maintenance of Fire Extinguishers',
    
    # Postage - use ampersand
    'Postag&e Stationery': 'Postage & Stationery',
    'Postage & Stationery': 'Postage and Stationery',  # Standardize to 'and'
    
    # Professional fees - capitalize consistently
    'Professional fees': 'Professional Fees',
    
    # Access system - standardize format
    'Access - intercom system repairs': 'Access Intercom System Repairs',
}

print("Standardizing charge names...")
print("="*80)

updated_count = 0

for old_name, new_name in standardization_rules.items():
    charges = session.query(ServiceCharge).filter(
        ServiceCharge.charge_name == old_name
    ).all()
    
    if charges:
        print(f"\n'{old_name}' -> '{new_name}'")
        for charge in charges:
            charge.charge_name = new_name
            print(f"  Updated ID {charge.id} (Year {charge.year})")
            updated_count += 1

session.commit()

print(f"\n{'='*80}")
print(f"✓ Updated {updated_count} charge names")

# Show summary of remaining distinct names
distinct_count = session.query(ServiceCharge.charge_name).distinct().count()
print(f"✓ Now have {distinct_count} distinct charge names")

session.close()
