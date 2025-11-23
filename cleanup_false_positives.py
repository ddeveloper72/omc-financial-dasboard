"""
Clean up false positive charges before reprocessing
"""
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app import app, db
from models import ServiceCharge, Document

def cleanup_false_positives():
    """Remove charges that are clearly false positives"""
    with app.app_context():
        deleted_count = 0
        
        # First: Delete ALL charges from non-financial documents (AGM Minutes, Other, etc.)
        # Only keep charges from Audited Accounts and Proposed Budget
        non_financial_docs = Document.query.filter(
            Document.document_type.notin_(['Audited Accounts', 'Proposed Budget'])
        ).all()
        
        for doc in non_financial_docs:
            doc_charges = ServiceCharge.query.filter_by(document_id=doc.id).all()
            for charge in doc_charges:
                print(f"Deleting {doc.document_type} charge: {charge.charge_name[:50]}... (EUR {charge.amount}) from {doc.filename}")
                db.session.delete(charge)
                deleted_count += 1
        
        # Second: Patterns that indicate false positives in other documents
        false_positive_patterns = [
            'Section ',
            'Chapter ',
            'Part ',
            ' policies',
            ' convention',
            'accordance with',
            'the company must',
            'is availing',
            'were levied',
            'Income represents',
            'Accounting policies',
            'Accounting periods',
            'Adoption of',
            'Appoint',
            'A copy of',
            'Approval of',
            'Remuneration',
        ]
        
        # Find and delete remaining false positives
        all_charges = ServiceCharge.query.all()
        
        for charge in all_charges:
            charge_name = charge.charge_name
            
            # Check if this looks like a false positive
            for pattern in false_positive_patterns:
                if pattern in charge_name:
                    print(f"Deleting false positive: {charge_name} (EUR {charge.amount})")
                    db.session.delete(charge)
                    deleted_count += 1
                    break
            
            # Also check for very long charge names (likely narrative text)
            if len(charge_name) > 100:
                print(f"Deleting overly long charge: {charge_name[:80]}... (EUR {charge.amount})")
                db.session.delete(charge)
                deleted_count += 1
        
        db.session.commit()
        print(f"\nDeleted {deleted_count} false positive charges")
        
        # Show remaining charge count
        remaining = ServiceCharge.query.count()
        print(f"Remaining charges: {remaining}")

if __name__ == '__main__':
    cleanup_false_positives()
