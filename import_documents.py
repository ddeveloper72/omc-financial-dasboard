"""Import scanned documents into the database"""
import os
from dotenv import load_dotenv
from app import app
from models import db, Document
from utils.document_scanner import DocumentScanner

load_dotenv()

with app.app_context():
    # Get document path
    doc_path = os.getenv('DOCUMENT_SOURCE_PATH', r'C:\Users\Duncan\OneDrive\Documents\Yewtree Square Stuff\OMC\AGM')
    
    # Scan for documents
    scanner = DocumentScanner(doc_path)
    documents = scanner.scan_directory()
    
    print(f"Found {len(documents)} documents to import")
    print()
    
    imported = 0
    skipped = 0
    
    for doc in documents:
        # Check if document already exists
        existing = Document.query.filter_by(filepath=doc['filepath']).first()
        
        if existing:
            print(f"Skipping (already exists): {doc['filename']}")
            skipped += 1
            continue
        
        # Create new document record
        new_doc = Document(
            filename=doc['filename'],
            filepath=doc['filepath'],
            file_modified_date=doc['modified_date'],
            document_year=doc['year'],
            document_type=doc.get('document_type', 'Other'),
            status='pending'
        )
        
        db.session.add(new_doc)
        print(f"Importing: {doc['filename']} (Year: {doc['year']}, Type: {doc.get('document_type', 'Other')})")
        imported += 1
    
    # Commit all changes
    db.session.commit()
    
    print()
    print(f"Import complete!")
    print(f"  Imported: {imported}")
    print(f"  Skipped: {skipped}")
    print(f"  Total in database: {Document.query.count()}")
