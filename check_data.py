"""
Check current database state
"""
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app import app, db
from models import ServiceCharge, Document

def check_data():
    """Check what data is in the database"""
    with app.app_context():
        # Count documents
        total_docs = Document.query.count()
        completed_docs = Document.query.filter_by(status='completed').count()
        print(f"Documents: {completed_docs}/{total_docs} completed")
        
        # Count documents by type
        print("\nDocuments by type:")
        for doc_type in ['Audited Accounts', 'Proposed Budget', 'AGM Minutes', 'Other']:
            count = Document.query.filter_by(document_type=doc_type).count()
            print(f"  {doc_type}: {count}")
        
        # Count charges
        total_charges = ServiceCharge.query.count()
        print(f"\nTotal charges: {total_charges}")
        
        if total_charges > 0:
            # Count by charge_type
            print("\nCharges by type:")
            expense_count = ServiceCharge.query.filter_by(charge_type='expense').count()
            income_count = ServiceCharge.query.filter_by(charge_type='income').count()
            balance_sheet_count = ServiceCharge.query.filter_by(charge_type='balance_sheet').count()
            print(f"  expense: {expense_count}")
            print(f"  income: {income_count}")
            print(f"  balance_sheet: {balance_sheet_count}")
            
            # Sample charges
            print("\nSample charges:")
            sample_charges = ServiceCharge.query.join(Document).limit(10).all()
            for charge in sample_charges:
                print(f"  [{charge.charge_type}] {charge.charge_name}: EUR {charge.amount} ({charge.document.document_type})")
        else:
            print("\n⚠️ NO CHARGES FOUND - Documents need to be processed!")
            print("\nDocuments pending processing:")
            pending = Document.query.filter_by(status='pending').all()
            for doc in pending:
                print(f"  - {doc.filename} ({doc.document_type})")

if __name__ == '__main__':
    check_data()
