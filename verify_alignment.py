"""Verify the alignment worked - check electricity charges across all documents"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import ServiceCharge, Document

engine = create_engine('sqlite:///instance/db.sqlite3')
Session = sessionmaker(bind=engine)
session = Session()

print('Electricity charges trend across ALL document types:')
print('='*60)
charges = session.query(
    ServiceCharge.year, 
    ServiceCharge.amount, 
    Document.document_type
).join(Document).filter(
    ServiceCharge.charge_name == 'Electricity charges'
).order_by(
    ServiceCharge.year, 
    Document.document_type
).all()

for year, amount, doc_type in charges:
    print(f'{year} ({doc_type:25s}): EUR {amount:>10,.2f}')

print('\n\nManaging Agent Fees across ALL document types:')
print('='*60)
charges = session.query(
    ServiceCharge.year, 
    ServiceCharge.amount, 
    Document.document_type
).join(Document).filter(
    ServiceCharge.charge_name == 'Managing Agent Fees'
).order_by(
    ServiceCharge.year, 
    Document.document_type
).all()

for year, amount, doc_type in charges:
    print(f'{year} ({doc_type:25s}): EUR {amount:>10,.2f}')

session.close()
