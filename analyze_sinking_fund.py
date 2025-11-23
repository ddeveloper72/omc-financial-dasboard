"""
Show sinking fund charges by document
"""
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app import app, db
from models import ServiceCharge, Document

def analyze_sinking_fund():
    """Show sinking fund charges grouped by document"""
    with app.app_context():
        sinking_charges = ServiceCharge.query.join(Document).filter(
            ServiceCharge.charge_name.ilike('%sinking%')
        ).order_by(Document.document_year, Document.filename, ServiceCharge.id).all()
        
        print("SINKING FUND CHARGES BY DOCUMENT:")
        print("="*80)
        
        current_doc = None
        for charge in sinking_charges:
            if current_doc != charge.document.filename:
                current_doc = charge.document.filename
                print(f"\n{charge.document.filename}")
                print(f"  Type: {charge.document.document_type}")
                print(f"  Year: {charge.document.document_year}")
                print(f"  Path: {charge.document.filepath}")
                print(f"  Charges:")
            
            print(f"    [{charge.id}] Year:{charge.year} {charge.charge_name}: EUR {charge.amount:,.2f} (confidence: {charge.confidence_score:.2f})")
        
        # Also show all charges with amount 2023
        print("\n" + "="*80)
        print("ALL CHARGES WITH AMOUNT EUR 2,023:")
        print("="*80)
        charges_2023 = ServiceCharge.query.join(Document).filter(
            ServiceCharge.amount == 2023.0
        ).all()
        
        for charge in charges_2023:
            print(f"\n{charge.charge_name}")
            print(f"  From: {charge.document.filename} ({charge.document.document_type}, Year: {charge.document.document_year})")
            print(f"  Charge Year: {charge.year}, Amount: EUR {charge.amount:,.2f}")

if __name__ == '__main__':
    analyze_sinking_fund()
