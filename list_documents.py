"""List all analyzed documents"""
from app import app
from models import db, Document

with app.app_context():
    docs = Document.query.order_by(Document.document_year, Document.filename).all()
    
    print(f"Total Documents: {len(docs)}")
    print("=" * 100)
    print()
    
    for i, doc in enumerate(docs, 1):
        print(f"{i:2}. Year: {doc.document_year or 'N/A':4} | Status: {doc.status:10} | {doc.filename}")
        if doc.error_message:
            print(f"    Error: {doc.error_message}")
    
    print()
    print("=" * 100)
    print("\nStatus Summary:")
    print(f"  Processed: {Document.query.filter_by(status='processed').count()}")
    print(f"  Pending: {Document.query.filter_by(status='pending').count()}")
    print(f"  Errors: {Document.query.filter_by(status='error').count()}")
