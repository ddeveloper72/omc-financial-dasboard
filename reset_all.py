"""
Delete all charges and reset for clean reprocessing
"""
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app import app, db
from models import ServiceCharge, Document

def reset_all():
    """Delete all charges and reset documents to pending"""
    with app.app_context():
        # Delete all charges
        charge_count = ServiceCharge.query.count()
        ServiceCharge.query.delete()
        print(f"Deleted {charge_count} charges")
        
        # Reset all documents to pending (except AGM Minutes and Other)
        docs = Document.query.filter(
            Document.document_type.in_(['Audited Accounts', 'Proposed Budget'])
        ).all()
        
        for doc in docs:
            doc.status = 'pending'
            doc.error_message = None
        
        db.session.commit()
        print(f"Reset {len(docs)} documents to pending")
        print("\nReady for clean reprocessing!")

if __name__ == '__main__':
    reset_all()
