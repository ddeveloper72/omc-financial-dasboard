"""
Check what audited account documents we have and look for balance sheet data
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Document
import os

engine = create_engine('sqlite:///instance/db.sqlite3')
Session = sessionmaker(bind=engine)
session = Session()

print('='*70)
print('AUDITED ACCOUNT DOCUMENTS')
print('='*70)

docs = session.query(Document).filter(
    Document.document_type == 'Audited Accounts'
).order_by(Document.filename).all()

print(f'\nFound {len(docs)} audited account documents:\n')

for doc in docs:
    print(f'ID: {doc.id}')
    print(f'  Filename: {doc.filename}')
    print(f'  File: {doc.filepath}')
    print(f'  Year: {doc.document_year}')
    print(f'  Status: {doc.status}')
    print(f'  Exists: {os.path.exists(doc.filepath) if doc.filepath else "No path"}')
    print()

session.close()

print('='*70)
print('NEXT STEPS TO TRACK RESERVES:')
print('='*70)
print("""
To track the sinking fund/reserve balance over time, we need to:

1. Extract balance sheet data from audited accounts PDFs
2. Look for sections like:
   - "Balance Sheet"
   - "Statement of Financial Position"
   - "Reserves" or "Sinking Fund"
   - "Retained Earnings"
   
3. Create a new table to store reserve balances:
   - Year
   - Opening Balance
   - Contributions (budgeted amount)
   - Expenditures (major works from reserve)
   - Closing Balance

4. Add visualization to dashboard showing:
   - Reserve balance trend over years
   - Contributions vs expenditures
   - Projected future balance based on planned contributions
""")
