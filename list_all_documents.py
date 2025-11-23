"""
List all documents and their classification status
"""
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app import app, db
from models import Document

def list_all_documents():
    """List all documents with their classification"""
    with app.app_context():
        docs = Document.query.order_by(Document.document_year, Document.filename).all()
        
        print("All Documents:")
        print("="*80)
        for doc in docs:
            status_icon = "✓" if doc.status == 'completed' else "⏳" if doc.status == 'pending' else "✗"
            print(f"{status_icon} {doc.filename}")
            print(f"   Year: {doc.document_year}, Type: {doc.document_type}, Status: {doc.status}")
            if doc.error_message:
                print(f"   Error: {doc.error_message}")
            print()

if __name__ == '__main__':
    list_all_documents()
