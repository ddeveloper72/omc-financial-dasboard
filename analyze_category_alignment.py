"""
Analyze category alignment between budget documents and audited accounts
to identify mismatched charge names that should be standardized.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import ServiceCharge, Document

engine = create_engine('sqlite:///instance/db.sqlite3')
Session = sessionmaker(bind=engine)
session = Session()

print('=== BUDGET CHARGES (by Category) ===')
budget_charges = session.query(
    ServiceCharge.charge_name, 
    ServiceCharge.category_id
).join(Document).filter(
    Document.document_type.like('%Budget%')
).distinct().order_by(
    ServiceCharge.category_id, 
    ServiceCharge.charge_name
).all()

budget_by_category = {}
for charge, category in budget_charges:
    if category not in budget_by_category:
        budget_by_category[category] = []
    budget_by_category[category].append(charge)

for cat_id in sorted(budget_by_category.keys()):
    print(f'\nCategory {cat_id}:')
    for charge in budget_by_category[cat_id]:
        print(f'  - {charge}')

print('\n\n=== AUDITED ACCOUNT CHARGES (by Category) ===')
audit_charges = session.query(
    ServiceCharge.charge_name, 
    ServiceCharge.category_id
).join(Document).filter(
    Document.document_type == 'Audited Accounts'
).distinct().order_by(
    ServiceCharge.category_id,
    ServiceCharge.charge_name
).all()

audit_by_category = {}
for charge, category in audit_charges:
    if category not in audit_by_category:
        audit_by_category[category] = []
    audit_by_category[category].append(charge)

for cat_id in sorted([k for k in audit_by_category.keys() if k is not None]):
    print(f'\nCategory {cat_id}:')
    for charge in audit_by_category[cat_id]:
        print(f'  - {charge}')

print('\n\n=== POTENTIAL MISALIGNMENTS ===')
# Find charges that appear in budgets but not in audits (and vice versa)
budget_names = set([c[0] for c in budget_charges])
audit_names = set([c[0] for c in audit_charges])

print('\nIn BUDGETS but not in AUDITED ACCOUNTS:')
for name in sorted(budget_names - audit_names):
    cat_id = [c[1] for c in budget_charges if c[0] == name][0]
    print(f'  - {name} (Category {cat_id})')

print('\nIn AUDITED ACCOUNTS but not in BUDGETS:')
for name in sorted(audit_names - budget_names):
    cat_id = [c[1] for c in audit_charges if c[0] == name][0]
    print(f'  - {name} (Category {cat_id})')

session.close()
