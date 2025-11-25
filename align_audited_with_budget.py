"""
Align audited account charge names with budget charge names for better comparison.
Key mappings identified:
- Light and heat -> Electricity charges (Category 5 for utilities)
- Management fees -> Managing Agent Fees
- Insurance -> Building Insurance
- Accountancy -> Audit & Accountancy
- Printing and stationery -> Postage and Stationery
- Telephone -> Phone line in lift (Category 5 for utilities)
- Waste disposal -> Domestic Waste Collections
- Garden Maintenance -> Grounds Maintenance
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import ServiceCharge, Document

# Mapping of audited account names to budget names
ALIGNMENT_RULES = {
    'Light and heat': {
        'new_name': 'Electricity charges',
        'new_category': 5  # Utilities category
    },
    'Management fees': {
        'new_name': 'Managing Agent Fees',
        'new_category': 1  # Management category
    },
    'Insurance': {
        'new_name': 'Building Insurance',
        'new_category': 2  # Insurance category
    },
    'Accountancy': {
        'new_name': 'Audit & Accountancy',
        'new_category': 10  # Other category
    },
    'Printing and stationery': {
        'new_name': 'Postage and Stationery',
        'new_category': 10  # Other category
    },
    'Telephone': {
        'new_name': 'Phone line in lift',
        'new_category': 5  # Utilities category
    },
    'Waste disposal': {
        'new_name': 'Domestic Waste Collections',
        'new_category': 10  # Other category
    },
    'Garden Maintenance': {
        'new_name': 'Grounds Maintenance',
        'new_category': 3  # Maintenance category
    },
    'Bad and doubtful debts': {
        'new_name': 'Debt Collection',
        'new_category': 10  # Other category
    },
    'Sundry expenses': {
        'new_name': 'Miscellaneous Outlay',
        'new_category': 10  # Other category
    },
    'Building Remedial Works': {
        'new_name': 'Building - General Repairs',
        'new_category': 3  # Maintenance category
    }
}

engine = create_engine('sqlite:///instance/db.sqlite3')
Session = sessionmaker(bind=engine)
session = Session()

print('Aligning audited account charge names with budget charge names...\n')

total_updated = 0
for old_name, updates in ALIGNMENT_RULES.items():
    new_name = updates['new_name']
    new_category = updates['new_category']
    
    # Find charges in audited accounts with the old name
    charges = session.query(ServiceCharge).join(Document).filter(
        ServiceCharge.charge_name == old_name,
        Document.document_type == 'Audited Accounts'
    ).all()
    
    if charges:
        print(f"'{old_name}' -> '{new_name}' (Category {new_category})")
        print(f"  Found {len(charges)} charge(s) to update:")
        
        for charge in charges:
            print(f"    ID {charge.id}: {charge.year} - EUR {charge.amount:,.2f}")
            charge.charge_name = new_name
            charge.category_id = new_category
            total_updated += 1
        
        print()

print(f'\nTotal charges updated: {total_updated}')
print('Committing changes...')
session.commit()
session.close()
print('Done! Audited account charges are now aligned with budget charges.')
