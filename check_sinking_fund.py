"""Check if Sinking Fund appears in audited accounts"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import ServiceCharge, Document

engine = create_engine('sqlite:///instance/db.sqlite3')
Session = sessionmaker(bind=engine)
session = Session()

print('='*70)
print('SINKING FUND CONTRIBUTION - Document Type Analysis')
print('='*70)

charges = session.query(
    ServiceCharge.year,
    ServiceCharge.amount,
    Document.document_type
).join(Document).filter(
    ServiceCharge.charge_name == 'Sinking Fund Contribution'
).order_by(
    ServiceCharge.year,
    Document.document_type
).all()

if charges:
    print(f'\nFound {len(charges)} Sinking Fund Contribution charges:\n')
    for year, amount, doc_type in charges:
        print(f'  {year} ({doc_type:25s}): EUR {amount:>10,.2f}')
else:
    print('\nNo Sinking Fund Contribution charges found in database.')

# Check what document types we have
print('\n' + '='*70)
print('DOCUMENT TYPES IN DATABASE')
print('='*70)
doc_types = session.query(Document.document_type).distinct().all()
for dt in doc_types:
    print(f'  - {dt[0]}')

# Check all Category 9 (Reserve Fund) charges
print('\n' + '='*70)
print('ALL CHARGES IN CATEGORY 9 (Reserve Fund)')
print('='*70)
cat9_charges = session.query(
    ServiceCharge.charge_name,
    ServiceCharge.year,
    Document.document_type
).join(Document).filter(
    ServiceCharge.category_id == 9
).order_by(
    ServiceCharge.year,
    ServiceCharge.charge_name
).all()

if cat9_charges:
    for charge_name, year, doc_type in cat9_charges:
        print(f'  {year} - {charge_name:30s} ({doc_type})')
else:
    print('  No charges found in Category 9')

session.close()
