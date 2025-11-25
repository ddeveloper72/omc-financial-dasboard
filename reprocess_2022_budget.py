"""
Reprocess Draft Budget 2022 to extract as year 2022 data
Currently shows as 2021, but should be 2022
"""
import pdfplumber
import re
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Document, ServiceCharge

def extract_charges(pdf_path, year):
    """Extract charges using pdfplumber"""
    charges = []
    amount_pattern = r'[\u20ac€�]\s*([0-9,]+\.?[0-9]*)'
    
    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    
    lines = text.split('\n')
    
    exclusions = [
        'total', 'common only', 'commercial only', 'draft budget', 
        'proposed budget', 'audited', 'unaudited'
    ]
    
    for line in lines:
        line = line.strip()
        if not line or len(line) < 5:
            continue
        
        amounts = re.findall(amount_pattern, line)
        if not amounts:
            continue
        
        parts = re.split(amount_pattern, line)
        charge_name = parts[0].strip()
        charge_name = re.sub(r'\s+', ' ', charge_name)
        
        if len(charge_name) < 3:
            continue
        
        charge_lower = charge_name.lower()
        if any(excl in charge_lower for excl in exclusions):
            continue
        
        try:
            amount = float(amounts[0].replace(',', ''))
        except ValueError:
            continue
        
        if amount < 10:
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

# Get Document ID 21
doc = session.query(Document).filter_by(id=21).first()

print(f"Reprocessing: {doc.filename}")
print(f"Current year in DB: Shows as 2021 data")
print(f"Target year: 2022")
print("="*80)

# Delete existing charges
existing = session.query(ServiceCharge).filter_by(document_id=21).all()
print(f"\nDeleting {len(existing)} existing charges...")
for charge in existing:
    session.delete(charge)
session.commit()

# Extract with year = 2022
print(f"\nExtracting charges for year 2022...")
charges = extract_charges(doc.filepath, 2022)
print(f"Found {len(charges)} charges\n")

# Add to database
for charge_data in charges:
    charge = ServiceCharge(
        document_id=21,
        charge_name=charge_data['charge_name'],
        amount=charge_data['amount'],
        currency=charge_data['currency'],
        year=2022,  # Force year to 2022
        raw_text=charge_data['raw_text'],
        confidence_score=charge_data['confidence_score']
    )
    session.add(charge)
    print(f"  + {charge_data['charge_name']:50s} | EUR {charge_data['amount']:>10,.2f}")

session.commit()
print(f"\nSuccessfully added {len(charges)} charges for year 2022")

session.close()
