"""
Show detailed document status with charge counts
"""
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app import app, db
from models import Document, ServiceCharge

def show_status():
    """Show processing status for all documents"""
    with app.app_context():
        all_docs = Document.query.order_by(Document.document_year, Document.document_type, Document.filename).all()
        
        print("DOCUMENT PROCESSING STATUS:")
        print("="*120)
        print(f"{'Year':<6} {'Type':<20} {'Status':<12} {'Charges':<8} {'Filename'}")
        print("-"*120)
        
        for doc in all_docs:
            charge_count = ServiceCharge.query.filter_by(document_id=doc.id).count()
            status_icon = "✅" if doc.status == 'completed' and charge_count > 0 else "⚠️" if doc.status == 'completed' else "❌" if doc.status == 'error' else "⏳"
            
            print(f"{doc.document_year or 'N/A':<6} {doc.document_type:<20} {status_icon} {doc.status:<10} {charge_count:<8} {doc.filename}")
            if doc.error_message:
                print(f"       Error: {doc.error_message}")
        
        print("\n" + "="*120)
        print("\nPROPOSED BUDGET DOCUMENTS DETAIL:")
        print("-"*120)
        budgets = Document.query.filter_by(document_type='Proposed Budget').order_by(Document.document_year).all()
        for doc in budgets:
            charge_count = ServiceCharge.query.filter_by(document_id=doc.id).count()
            print(f"\n{doc.document_year}: {doc.filename}")
            print(f"  Status: {doc.status}, Charges: {charge_count}")
            if doc.error_message:
                print(f"  Error: {doc.error_message}")
            if charge_count > 0:
                charges = ServiceCharge.query.filter_by(document_id=doc.id).limit(3).all()
                print(f"  Sample charges:")
                for c in charges:
                    print(f"    - {c.charge_name}: EUR {c.amount:,.2f}")

if __name__ == '__main__':
    show_status()
