"""
Reprocess all documents with updated OCR preprocessing
"""
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Document, ServiceCharge, ProcessingLog
from utils.pdf_parser import PDFParser
from utils.budget_extractor import BudgetExtractor
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Connect to database
engine = create_engine('sqlite:///instance/db.sqlite3')
Session = sessionmaker(bind=engine)
session = Session()

# Initialize processors
parser = PDFParser()
extractor = BudgetExtractor()

try:
    # Get all Audited Accounts and Proposed Budget documents
    docs = session.query(Document).filter(
        Document.document_type.in_(['Audited Accounts', 'Proposed Budget'])
    ).all()
    
    print(f"Found {len(docs)} financial documents to reprocess")
    print("="*80)
    
    processed = 0
    skipped = 0
    errors = 0
    
    for doc in docs:
        print(f"\nProcessing: {doc.filename}")
        
        # Delete existing charges for this document
        deleted = session.query(ServiceCharge).filter_by(document_id=doc.id).delete()
        if deleted > 0:
            print(f"  Deleted {deleted} existing charges")
        
        # Extract text
        try:
            text = parser.extract_text(doc.filepath)
            if not text or len(text) < 100:
                print(f"  ⚠️  Insufficient text extracted ({len(text)} chars)")
                doc.status = 'error'
                doc.error_message = f"Insufficient text: {len(text)} characters"
                errors += 1
                continue
            
            print(f"  Extracted {len(text)} characters")
            
            # Extract charges
            charges = extractor.extract_charges(text, year=doc.document_year)
            
            if not charges:
                print(f"  ⚠️  No charges found")
                doc.status = 'completed'
                doc.error_message = "No charges found in document"
                skipped += 1
                continue
            
            # Deduplicate
            charges = extractor.deduplicate_charges(charges)
            print(f"  Found {len(charges)} charges after deduplication")
            
            # Save charges
            for charge_data in charges:
                charge = ServiceCharge(
                    document_id=doc.id,
                    charge_name=charge_data['charge_name'],
                    amount=charge_data['amount'],
                    currency=charge_data.get('currency', 'EUR'),
                    year=charge_data.get('year', doc.document_year),
                    charge_type=charge_data.get('charge_type', 'expense'),
                    confidence_score=charge_data.get('confidence_score', 0.5)
                )
                session.add(charge)
            
            doc.status = 'completed'
            doc.error_message = None
            processed += 1
            print(f"  ✓ Saved {len(charges)} charges")
            
        except Exception as e:
            print(f"  ✗ Error: {str(e)}")
            doc.status = 'error'
            doc.error_message = str(e)
            errors += 1
    
    # Commit all changes
    session.commit()
    
    print("\n" + "="*80)
    print("SUMMARY:")
    print(f"  Processed successfully: {processed}")
    print(f"  Skipped (no charges):   {skipped}")
    print(f"  Errors:                 {errors}")
    print(f"  Total:                  {len(docs)}")
    
except Exception as e:
    logger.error(f"Fatal error: {e}")
    session.rollback()
    raise
finally:
    session.close()
