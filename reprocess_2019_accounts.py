"""
Reprocess 2019 Audited Accounts to extract all administrative expenses
Currently only has 3 charges, should have ~13 detailed line items
"""
import pdfplumber
import re
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Document, ServiceCharge

def extract_charges(pdf_path, year):
    """Extract charges for the specified year"""
    charges = []
    amount_pattern = r'[€\u20ac]\s*([0-9,]+)'
    
    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    
    lines = text.split('\n')
    
    # Exclusions for headers and totals
    exclusions = [
        'schedule of', 'administrative expenses', 'year ended',
        'total', 'yew tree square', '2019', '2018', '€'
    ]
    
    for line in lines:
        line = line.strip()
        if not line or len(line) < 5:
            continue
        
        # Find amounts
        amounts = re.findall(amount_pattern, line)
        if not amounts:
            continue
        
        # Extract charge name
        parts = re.split(amount_pattern, line)
        charge_name = parts[0].strip()
        charge_name = re.sub(r'\s+', ' ', charge_name)
        
        if len(charge_name) < 3:
            continue
        
        # Skip if matches exclusions
        charge_lower = charge_name.lower()
        if any(excl in charge_lower for excl in exclusions):
            continue
        
        # Convert first amount (should be 2019 column)
        try:
            amount = float(amounts[0].replace(',', ''))
        except ValueError:
            continue
        
        if amount < 100:  # Skip very small amounts (likely page numbers)
            continue
        
        charges.append({
            'charge_name': charge_name,
            'amount': amount,
            'year': year,
            'currency': 'EUR',
            'raw_text': line,
            'confidence_score': 0.90
        })
    
    return charges

# Main execution
engine = create_engine('sqlite:///instance/db.sqlite3')
Session = sessionmaker(bind=engine)
session = Session()

# Get Document ID 19
doc = session.query(Document).filter_by(id=19).first()

print(f"Reprocessing: {doc.filename}")
print(f"Document ID: {doc.id}")
print("="*80)

# Delete existing charges
existing = session.query(ServiceCharge).filter_by(document_id=19).all()
print(f"\nDeleting {len(existing)} existing charges...")
for charge in existing:
    session.delete(charge)
session.commit()

# Extract charges for 2019
print(f"\nExtracting 2019 administrative expenses...")
charges = extract_charges(doc.filepath, 2019)
print(f"Found {len(charges)} charges\n")

# Add to database
total = 0
for charge_data in charges:
    charge = ServiceCharge(
        document_id=19,
        charge_name=charge_data['charge_name'],
        amount=charge_data['amount'],
        currency=charge_data['currency'],
        year=2019,
        raw_text=charge_data['raw_text'],
        confidence_score=charge_data['confidence_score']
    )
    session.add(charge)
    print(f"  + {charge_data['charge_name']:50s} | EUR {charge_data['amount']:>10,.2f}")
    total += charge_data['amount']

session.commit()
print(f"\n  {'TOTAL':52s} EUR {total:>10,.2f}")
print(f"\nSuccessfully added {len(charges)} charges for year 2019")

session.close()
