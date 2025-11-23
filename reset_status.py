"""Reset document status to pending for reprocessing"""
from app import app
from models import db, Document

with app.app_context():
    # Reset all documents to pending
    count = Document.query.update({'status': 'pending', 'error_message': None})
    db.session.commit()
    
    print(f"Reset {count} documents to pending status")
    print(f"Pending documents: {Document.query.filter_by(status='pending').count()}")
