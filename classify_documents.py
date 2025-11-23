"""Classify existing documents by type"""
from app import app
from models import db, Document
from utils.document_scanner import DocumentScanner

with app.app_context():
    # Get all documents
    documents = Document.query.all()
    
    # Create scanner for classification
    scanner = DocumentScanner('')
    
    print(f"Classifying {len(documents)} documents...")
    print()
    
    updated = 0
    for doc in documents:
        # Classify based on filename
        doc_type = scanner._classify_document_type(doc.filename)
        
        if doc.document_type != doc_type:
            old_type = doc.document_type or 'None'
            doc.document_type = doc_type
            print(f"{doc.filename}")
            print(f"  {old_type} -> {doc_type}")
            updated += 1
    
    # Commit changes
    db.session.commit()
    
    print()
    print(f"Updated {updated} documents")
    print()
    print("Document Type Summary:")
    print("=" * 60)
    
    types = db.session.query(Document.document_type, db.func.count(Document.id)).group_by(Document.document_type).all()
    for doc_type, count in sorted(types):
        print(f"  {doc_type}: {count}")
    
    print()
    print("Audited Accounts by Year:")
    print("=" * 60)
    audited = Document.query.filter_by(document_type='Audited Accounts').order_by(Document.document_year).all()
    for doc in audited:
        print(f"  {doc.document_year}: {doc.filename}")
    
    print()
    print("Proposed Budgets by Year:")
    print("=" * 60)
    budgets = Document.query.filter_by(document_type='Proposed Budget').order_by(Document.document_year).all()
    for doc in budgets:
        print(f"  {doc.document_year}: {doc.filename}")
