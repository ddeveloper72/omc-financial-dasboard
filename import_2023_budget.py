"""
Import 2023 Proposed Budget from "Approved Budget 2023 YTS.pdf"
This file contains multiple columns - we want the "Draft 2023" column
"""
import pdfplumber
import re
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Document, ServiceCharge

def extract_2023_budget(pdf_path):
    """Extract 2023 draft budget charges from the multi-column PDF"""
    charges = []
    
    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    
    # Looking at your image, the structure is:
    # Charge Name | Total 2023 | Common | Apartments Only | Commercial Only | Costs 31/12/2022 | Draft 2022
    # We want to extract charge names and amounts from lines
    
    amount_pattern = r'€([0-9,]+)'
    lines = text.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line or len(line) < 5:
            continue
        
        # Skip headers
        if any(x in line for x in ['Total 2023', 'Common', 'Draft', 'Apartments', 'Commercial', 'Costs']):
            continue
        
        # Find all amounts in the line
        amounts = re.findall(amount_pattern, line)
        if not amounts:
            continue
        
        # Extract charge name (text before first amount)
        parts = re.split(amount_pattern, line)
        charge_name = parts[0].strip()
        charge_name = re.sub(r'\s+', ' ', charge_name)
        
        if len(charge_name) < 3:
            continue
        
        # Skip section totals
        if any(x in charge_name.lower() for x in ['total', 'capital contribution']):
            continue
        
        # The first amount is typically the "Total 2023" column
        try:
            amount = float(amounts[0].replace(',', ''))
        except (ValueError, IndexError):
            continue
        
        if amount < 10:
            continue
        
        charges.append({
            'charge_name': charge_name,
            'amount': amount,
            'year': 2023,
            'currency': 'EUR',
            'raw_text': line,
            'confidence_score': 0.85
        })
    
    return charges

# Main execution
engine = create_engine('sqlite:///instance/db.sqlite3')
Session = sessionmaker(bind=engine)
session = Session()

pdf_path = r"C:\Users\Duncan\OneDrive\Documents\Yewtree Square Stuff\OMC\AGM\2022\Approved Budget 2023 YTS.pdf"
filename = "Approved Budget 2023 YTS.pdf"

# Check if document already exists
existing_doc = session.query(Document).filter_by(filename=filename).first()

if existing_doc:
    print(f"Document already exists (ID: {existing_doc.id})")
    print(f"Deleting existing charges...")
    session.query(ServiceCharge).filter_by(document_id=existing_doc.id).delete()
    session.commit()
    doc = existing_doc
else:
    # Add new document
    doc = Document(
        filename=filename,
        filepath=pdf_path,
        document_type='Proposed Budget',
        status='pending'
    )
    session.add(doc)
    session.commit()
    print(f"Added new document (ID: {doc.id})")

print(f"\nExtracting 2023 Proposed Budget from: {filename}")
print("="*80)

# Extract charges
charges = extract_2023_budget(pdf_path)
print(f"\nFound {len(charges)} charges for year 2023\n")

# Add to database
for charge_data in charges:
    charge = ServiceCharge(
        document_id=doc.id,
        charge_name=charge_data['charge_name'],
        amount=charge_data['amount'],
        currency=charge_data['currency'],
        year=2023,
        raw_text=charge_data['raw_text'],
        confidence_score=charge_data['confidence_score']
    )
    session.add(charge)
    print(f"  + {charge_data['charge_name']:50s} | EUR {charge_data['amount']:>10,.2f}")

doc.status = 'processed'
session.commit()

print(f"\nSuccessfully added {len(charges)} charges for year 2023")
print("\nNow you can compare:")
print("  - 2022: Proposed Budget vs Audited Accounts")
print("  - 2023: Proposed Budget vs Audited Accounts")

session.close()
