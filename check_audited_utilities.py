"""
Check utility-related charges in audited accounts
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import ServiceCharge, Document

engine = create_engine('sqlite:///instance/db.sqlite3')
Session = sessionmaker(bind=engine)
session = Session()

print("Utility-related charges in Audited Accounts:")
print("="*80)

charges = session.query(
    ServiceCharge.year,
    ServiceCharge.charge_name,
    ServiceCharge.amount
).join(Document).filter(
    Document.document_type == 'Audited Accounts',
    ServiceCharge.charge_name.like('%light%') | 
    ServiceCharge.charge_name.like('%heat%') |
    ServiceCharge.charge_name.like('%electric%')
).order_by(ServiceCharge.year, ServiceCharge.charge_name).all()

for charge in charges:
    print(f"{charge.year}: {charge.charge_name:30} EUR {charge.amount:>10,.2f}")

session.close()
