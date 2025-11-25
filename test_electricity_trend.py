"""
Test electricity charges trend data
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import ServiceCharge, ChargeCategory, Document

engine = create_engine('sqlite:///instance/db.sqlite3')
Session = sessionmaker(bind=engine)
session = Session()

# Find Utilities category
utilities = session.query(ChargeCategory).filter_by(name='Utilities').first()

if utilities:
    print(f"Utilities Category ID: {utilities.id}")
    print("="*80)
    
    # Get all distinct charge names in Utilities
    charges = session.query(ServiceCharge.charge_name).filter_by(
        category_id=utilities.id
    ).distinct().order_by(ServiceCharge.charge_name).all()
    
    print(f"\nDistinct charges in Utilities category ({len(charges)}):")
    for charge in charges:
        print(f"  - {charge[0]}")
    
    # Get electricity charges trend
    print("\n" + "="*80)
    print("ELECTRICITY CHARGES TREND")
    print("="*80)
    
    electricity_charges = session.query(
        ServiceCharge.year,
        ServiceCharge.charge_name,
        ServiceCharge.amount,
        Document.document_type
    ).join(Document).filter(
        ServiceCharge.category_id == utilities.id,
        ServiceCharge.charge_name.like('%Electricity%')
    ).order_by(ServiceCharge.year, Document.document_type).all()
    
    print("\nYear | Type            | Charge Name          | Amount")
    print("-"*80)
    for charge in electricity_charges:
        doc_type = charge.document_type[:15].ljust(15)
        print(f"{charge.year} | {doc_type} | {charge.charge_name:20} | EUR {charge.amount:>10,.2f}")
    
    # Summary by year
    print("\n" + "="*80)
    print("SUMMARY BY YEAR")
    print("="*80)
    
    from sqlalchemy import func
    
    for year in [2022, 2023, 2024, 2025]:
        # Proposed
        proposed = session.query(func.sum(ServiceCharge.amount)).join(Document).filter(
            ServiceCharge.year == year,
            ServiceCharge.category_id == utilities.id,
            ServiceCharge.charge_name.like('%Electricity%'),
            Document.document_type == 'Proposed Budget'
        ).scalar()
        
        # Audited
        audited = session.query(func.sum(ServiceCharge.amount)).join(Document).filter(
            ServiceCharge.year == year,
            ServiceCharge.category_id == utilities.id,
            ServiceCharge.charge_name.like('%Electricity%'),
            Document.document_type == 'Audited Accounts'
        ).scalar()
        
        print(f"\n{year}:")
        print(f"  Proposed: EUR {proposed:>10,.2f}" if proposed else "  Proposed: None")
        print(f"  Audited:  EUR {audited:>10,.2f}" if audited else "  Audited:  None")

session.close()
