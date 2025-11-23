"""
Remove documents from database if files no longer exist
"""
from pathlib import Path
import sys
import os

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app import app, db
from models import Document, ServiceCharge

def cleanup_missing_files():
    """Remove documents whose files no longer exist"""
    with app.app_context():
        all_docs = Document.query.all()
        
        removed_count = 0
        
        for doc in all_docs:
            if not os.path.exists(doc.filepath):
                print(f"Removing missing file: {doc.filename}")
                
                # Delete associated charges first
                ServiceCharge.query.filter_by(document_id=doc.id).delete()
                
                # Delete document
                db.session.delete(doc)
                removed_count += 1
        
        db.session.commit()
        print(f"\nRemoved {removed_count} documents with missing files")
        print(f"Remaining documents: {Document.query.count()}")

if __name__ == '__main__':
    cleanup_missing_files()
