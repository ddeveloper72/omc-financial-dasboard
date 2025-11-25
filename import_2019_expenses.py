"""
Properly extract 2019 administrative expenses from the schedule on page 15
"""
import pdfplumber
import re
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Document, ServiceCharge

# Define the charges manually based on the Schedule of Administrative Expenses
# Page 15 shows clear line items for 2019
charges_2019 = [
    {'charge_name': 'Cleaning', 'amount': 4730},
    {'charge_name': 'Waste disposal', 'amount': 9478},
    {'charge_name': 'Light and heat', 'amount': 4687},
    {'charge_name': 'Repairs and maintenance', 'amount': 47839},
    {'charge_name': 'Insurance', 'amount': 10414},
    {'charge_name': 'Insurance claim', 'amount': 9911},
    {'charge_name': 'Garden Maintenance', 'amount': 6659},
    {'charge_name': 'Management fees', 'amount': 19803},
    {'charge_name': 'Accountancy', 'amount': 1215},
    {'charge_name': 'Bank charges', 'amount': 199},
    {'charge_name': 'Printing and stationery', 'amount': 630},
    {'charge_name': 'Telephone', 'amount': 1354},
    {'charge_name': 'Sundry expenses', 'amount': 456}
]

# Main execution
engine = create_engine('sqlite:///instance/db.sqlite3')
Session = sessionmaker(bind=engine)
session = Session()

# Get Document ID 19
doc = session.query(Document).filter_by(id=19).first()

print(f"Adding 2019 administrative expenses from: {doc.filename}")
print("Data extracted from Schedule of Administrative Expenses (Page 15)")
print("="*80)

# Delete existing charges
existing = session.query(ServiceCharge).filter_by(document_id=19).all()
print(f"\nDeleting {len(existing)} existing charges...")
for charge in existing:
    session.delete(charge)
session.commit()

# Add the correct charges
print(f"\nAdding {len(charges_2019)} charges for year 2019:\n")

total = 0
for charge_data in charges_2019:
    charge = ServiceCharge(
        document_id=19,
        charge_name=charge_data['charge_name'],
        amount=charge_data['amount'],
        currency='EUR',
        year=2019,
        raw_text=f"{charge_data['charge_name']} €{charge_data['amount']:,}",
        confidence_score=1.0  # Manual entry from clear document
    )
    session.add(charge)
    print(f"  + {charge_data['charge_name']:50s} | EUR {charge_data['amount']:>10,.2f}")
    total += charge_data['amount']

session.commit()

print(f"\n  {'TOTAL':52s} EUR {total:>10,.2f}")
print(f"  {'Expected total from document':52s} EUR 117,375.00")
print(f"\nSuccessfully added {len(charges_2019)} charges for year 2019")

session.close()
