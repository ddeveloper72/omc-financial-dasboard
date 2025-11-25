"""
Find common charge name variations that need standardization
"""
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from models import ServiceCharge
import difflib

engine = create_engine('sqlite:///instance/db.sqlite3')
Session = sessionmaker(bind=engine)
session = Session()

# Get all distinct charge names
all_charges = session.query(
    ServiceCharge.charge_name,
    func.count(ServiceCharge.id).label('count')
).group_by(ServiceCharge.charge_name).order_by(ServiceCharge.charge_name).all()

print(f"Total distinct charge names: {len(all_charges)}")
print("="*80)

# Find similar names using fuzzy matching
potential_duplicates = []

for i, charge1 in enumerate(all_charges):
    for charge2 in all_charges[i+1:]:
        # Calculate similarity ratio
        ratio = difflib.SequenceMatcher(None, charge1.charge_name.lower(), charge2.charge_name.lower()).ratio()
        
        # If very similar (>85%), likely a variation
        if ratio > 0.85:
            potential_duplicates.append({
                'name1': charge1.charge_name,
                'count1': charge1.count,
                'name2': charge2.charge_name,
                'count2': charge2.count,
                'similarity': ratio
            })

if potential_duplicates:
    print(f"\nFound {len(potential_duplicates)} potential duplicate charge names:")
    print("="*80)
    for dup in potential_duplicates:
        print(f"\nSimilarity: {dup['similarity']:.1%}")
        print(f"  '{dup['name1']}' ({dup['count1']} occurrences)")
        print(f"  '{dup['name2']}' ({dup['count2']} occurrences)")
else:
    print("\n✓ No obvious duplicate charge names found")

# Show charges with unusual characters
print("\n" + "="*80)
print("Charges with unusual characters (spaces, dashes, tildes, etc.):")
print("="*80)

unusual = []
for charge in all_charges:
    name = charge.charge_name
    if '  ' in name or ' -' in name or '- ' in name or '~' in name or name != name.strip():
        unusual.append((name, charge.count))

if unusual:
    for name, count in unusual:
        print(f"  '{name}' ({count} occurrences)")
else:
    print("  ✓ No charges with unusual characters")

session.close()
