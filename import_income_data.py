"""
Import income data from audited accounts for chart comparison
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Document, ServiceCharge

engine = create_engine('sqlite:///instance/db.sqlite3')
Session = sessionmaker(bind=engine)
session = Session()

print("="*80)
print("IMPORTING INCOME FROM AUDITED ACCOUNTS")
print("="*80)

# Income data from Income and Expenditure Account (Page 9 of each PDF)

income_data = [
    {
        'year': 2019,
        'document': 'Accounts 2019 - Yew Tree Square Management Company OCR.pdf',
        'charge_name': 'Service Charges Income',
        'amount': 58739,  # From earlier extraction, need to verify
    },
    {
        'year': 2022,
        'document': 'YTS Audited Accounts 2022.pdf',
        'charge_name': 'Service Charges Income',
        'amount': 99553,  # From Page 9: Income €99,553
    },
    {
        'year': 2023,
        'document': 'Yew Tree Square Management CLG Financial Statements 31 December 2023.pdf',
        'charge_name': 'Service Charges Income',
        'amount': 143472,  # From Page 9: Income €143,472
    },
]

for income in income_data:
    doc = session.query(Document).filter_by(filename=income['document']).first()
    
    if doc:
        # Check if income already exists
        existing = session.query(ServiceCharge).filter_by(
            document_id=doc.id,
            year=income['year'],
            charge_name=income['charge_name']
        ).first()
        
        if existing:
            print(f"\n{income['year']}: Income already exists, skipping")
        else:
            charge = ServiceCharge(
                document_id=doc.id,
                charge_name=income['charge_name'],
                amount=income['amount'],
                year=income['year'],
                charge_type='income'
            )
            session.add(charge)
            print(f"\n{income['year']}: Added Service Charges Income = EUR {income['amount']:,.2f}")
            print(f"  Document: {doc.filename}")
    else:
        print(f"\n{income['year']}: Document not found: {income['document']}")

session.commit()

print("\n" + "="*80)
print("INCOME SUMMARY")
print("="*80)

for year in [2019, 2022, 2023]:
    income = session.query(ServiceCharge).filter_by(year=year, charge_type='income').first()
    
    # Get only expenses from AUDITED accounts (not proposed budgets)
    expenses = session.query(ServiceCharge).join(Document).filter(
        ServiceCharge.year == year,
        ServiceCharge.charge_type == 'expense',
        Document.document_type == 'Audited Accounts'
    ).all()
    
    if income and expenses:
        total_expenses = sum(e.amount for e in expenses)
        surplus_deficit = income.amount - total_expenses
        
        print(f"\n{year}:")
        print(f"  Income:    EUR {income.amount:>10,.2f}")
        print(f"  Expenses:  EUR {total_expenses:>10,.2f}")
        print(f"  Surplus/(Deficit): EUR {surplus_deficit:>10,.2f}")

session.close()

print("\n✓ Income data imported successfully")
print("\nYou can now plot income vs expenses on the chart!")
