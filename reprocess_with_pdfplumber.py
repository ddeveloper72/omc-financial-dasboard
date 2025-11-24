"""
Reprocess PDFs using pdfplumber for better extraction
"""
import sys
sys.path.insert(0, r'c:\Users\Duncan\Visual_Studio_Projects\yts-budget')

import pdfplumber
import re
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Document, ServiceCharge
from utils.budget_extractor import BudgetExtractor

def extract_with_pdfplumber(pdf_path, year):
    """Extract charges using pdfplumber with line-by-line parsing"""
    charges = []
    # Match Euro symbol (Unicode 8364) or similar
    amount_pattern = r'[\u20ac€�]\s*([0-9,]+\.?[0-9]*)'
    
    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    
    lines = text.split('\n')
    
    # Simple exclusion list (section headers and noise only)
    exclusions = [
        'total', 'common only', 'commercial only', 'draft budget', 
        'proposed budget', 'audited', 'unaudited', 'vew trees quare'
    ]
    
    debug_total = 0
    debug_amount_found = 0
    debug_excluded = 0
    debug_added = 0
    
    for line in lines:
        line = line.strip()
        debug_total += 1
        if not line or len(line) < 5:
            continue
        
        # Find amounts
        amounts = re.findall(amount_pattern, line)
        if not amounts:
            continue
        debug_amount_found += 1
        
        # Extract charge name (text before first amount)
        parts = re.split(amount_pattern, line)
        charge_name = parts[0].strip()
        
        # Clean up charge name
        charge_name = re.sub(r'\s+', ' ', charge_name)
        
        # Skip if no meaningful charge name
        if len(charge_name) < 3:
            continue
        
        # Simple exclusion check
        charge_lower = charge_name.lower()
        if any(excl in charge_lower for excl in exclusions):
            debug_excluded += 1
            continue
        
        # Convert amount
        try:
            amount = float(amounts[0].replace(',', ''))
        except ValueError:
            continue
        
        # Skip very small amounts (likely page numbers or noise)
        if amount < 10:
            continue
        
        debug_added += 1
        charges.append({
            'charge_name': charge_name,
            'amount': amount,
            'year': year,
            'currency': 'EUR',
            'raw_text': line,
            'confidence_score': 0.90  # Higher confidence for pdfplumber
        })
    
    print(f"Debug: Total lines={debug_total}, Found amounts={debug_amount_found}, Excluded={debug_excluded}, Added={debug_added}")
    
    return charges

def reprocess_document(doc_id):
    """Reprocess a single document with pdfplumber"""
    engine = create_engine('sqlite:///c:/Users/Duncan/Visual_Studio_Projects/yts-budget/instance/db.sqlite3')
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Get document
    doc = session.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        print(f"Document ID {doc_id} not found")
        return
    
    # Extract year from filename
    year_match = re.search(r'20\d{2}', doc.filename)
    year = int(year_match.group()) if year_match else 2025
    
    print(f"Reprocessing: {doc.filename}")
    print(f"Year: {year}")
    print(f"Type: {doc.document_type}")
    print("="*80)
    
    # Delete existing charges for this document
    existing = session.query(ServiceCharge).filter(ServiceCharge.document_id == doc_id).all()
    print(f"\nDeleting {len(existing)} existing charges...")
    for charge in existing:
        session.delete(charge)
    session.commit()
    
    # Extract new charges
    print(f"\nExtracting charges with pdfplumber...")
    charges = extract_with_pdfplumber(doc.filepath, year)
    print(f"Found {len(charges)} charges\n")
    
    # Add to database
    for charge_data in charges:
        charge = ServiceCharge(
            document_id=doc_id,
            charge_name=charge_data['charge_name'],
            amount=charge_data['amount'],
            currency=charge_data['currency'],
            year=charge_data['year'],
            raw_text=charge_data['raw_text'],
            confidence_score=charge_data['confidence_score']
        )
        session.add(charge)
        print(f"  + {charge_data['charge_name']:50s} | EUR {charge_data['amount']:>10,.2f}")
    
    session.commit()
    print(f"\nSuccessfully added {len(charges)} charges")
    
    session.close()

if __name__ == '__main__':
    # Reprocess the 2025 Proposed Budget OCR document
    # First, find its document ID
    engine = create_engine('sqlite:///c:/Users/Duncan/Visual_Studio_Projects/yts-budget/instance/db.sqlite3')
    Session = sessionmaker(bind=engine)
    session = Session()
    
    doc = session.query(Document).filter(
        Document.filename == 'Proposed Budget 2025 OCR.pdf'
    ).first()
    
    if doc:
        print(f"Found document: {doc.filename} (ID: {doc.id})")
        print()
        reprocess_document(doc.id)
    else:
        print("Document not found!")
    
    session.close()
