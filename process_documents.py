"""Process documents to extract budget information"""
import os
from dotenv import load_dotenv
from app import app
from models import db, Document, ServiceCharge, ChargeCategory, ProcessingLog
from utils.pdf_parser import PDFParser
from utils.budget_extractor import BudgetExtractor

load_dotenv()

with app.app_context():
    # Get pending documents
    pending_docs = Document.query.filter_by(status='pending').order_by(Document.document_year).all()
    
    print(f"Found {len(pending_docs)} documents to process")
    print()
    
    parser = PDFParser()
    extractor = BudgetExtractor()
    
    processed = 0
    errors = 0
    
    for doc in pending_docs:
        print(f"Processing: {doc.filename} (Year: {doc.document_year}, Type: {doc.document_type})")
        
        # Only process Audited Accounts and Proposed Budget documents
        if doc.document_type not in ['Audited Accounts', 'Proposed Budget']:
            doc.status = 'completed'
            doc.error_message = None
            print(f"  SKIPPED: Only processing Audited Accounts and Proposed Budget documents")
            print(f"  Document type '{doc.document_type}' does not contain budget line items")
            db.session.commit()
            continue
        
        try:
            # Extract text from PDF
            text = parser.extract_text(doc.filepath)
            
            if not text or len(text.strip()) < 50:
                doc.status = 'error'
                doc.error_message = 'Failed to extract text from PDF or text too short'
                
                # Log error
                log_entry = ProcessingLog(
                    document_id=doc.id,
                    status='error',
                    message=doc.error_message
                )
                db.session.add(log_entry)
                
                print(f"  ERROR: Could not extract text")
                errors += 1
                continue
            
            print(f"  Extracted {len(text)} characters of text")
            
            # Extract charges
            charges = extractor.extract_charges(text, doc.document_year)
            
            print(f"  Found {len(charges)} potential charges")
            
            if charges:
                # Deduplicate charges within this document before saving
                deduplicated_charges = extractor.deduplicate_charges(charges)
                
                print(f"  After deduplication: {len(deduplicated_charges)} unique charges")
                
                # Save charges to database
                charges_added = 0
                for charge_data in deduplicated_charges:
                    # Check if a similar charge already exists for this document and year
                    normalized_name = extractor._normalize_charge_name(charge_data['charge_name'])
                    
                    # Get all charges from this document with the same year
                    existing_charges = ServiceCharge.query.filter_by(
                        document_id=doc.id,
                        year=charge_data['year']
                    ).all()
                    
                    # Check if any have similar normalized names
                    similar_charge = None
                    for existing in existing_charges:
                        if extractor._normalize_charge_name(existing.charge_name) == normalized_name:
                            similar_charge = existing
                            break
                    
                    if similar_charge:
                        # Update if new one has higher confidence
                        if charge_data.get('confidence_score', 0) > similar_charge.confidence_score:
                            print(f"    - UPDATE (higher confidence): {charge_data['charge_name']}")
                            similar_charge.charge_name = charge_data['charge_name']
                            similar_charge.amount = charge_data['amount']
                            similar_charge.confidence_score = charge_data.get('confidence_score', 0.5)
                            similar_charge.charge_type = charge_data.get('charge_type', 'expense')
                        else:
                            print(f"    - SKIP (similar exists): {charge_data['charge_name']}")
                        continue
                    
                    # Detect category from charge name
                    detected_category = extractor._detect_category(charge_data['charge_name'])
                    
                    # Find or create category
                    category = ChargeCategory.query.filter_by(name=detected_category).first()
                    
                    charge = ServiceCharge(
                        document_id=doc.id,
                        charge_name=charge_data['charge_name'],
                        category_id=category.id if category else None,
                        year=charge_data['year'],
                        amount=charge_data['amount'],
                        charge_type=charge_data.get('charge_type', 'expense'),
                        confidence_score=charge_data.get('confidence_score', 0.5)
                    )
                    
                    db.session.add(charge)
                    charges_added += 1
                    charge_type_label = charge_data.get('charge_type', 'expense').upper()
                    print(f"    - [{charge_type_label}] {charge_data['charge_name']}: EUR {charge_data['amount']:.2f}")
                
                doc.status = 'processed'
                
                # Log success
                log_entry = ProcessingLog(
                    document_id=doc.id,
                    status='success',
                    message=f'Extracted {len(charges)} charges',
                    details=str(len(charges))
                )
                db.session.add(log_entry)
                
                processed += 1
            else:
                doc.status = 'processed'
                doc.error_message = 'No charges found in document'
                
                # Log no charges
                log_entry = ProcessingLog(
                    document_id=doc.id,
                    status='warning',
                    message='No charges found'
                )
                db.session.add(log_entry)
                
                print(f"  WARNING: No charges found")
            
            # Commit after each document
            db.session.commit()
            print()
            
        except Exception as e:
            print(f"  ERROR: {str(e)}")
            
            doc.status = 'error'
            doc.error_message = str(e)
            
            log_entry = ProcessingLog(
                document_id=doc.id,
                status='error',
                message=str(e)
            )
            db.session.add(log_entry)
            db.session.commit()
            
            errors += 1
            print()
    
    print(f"Processing complete!")
    print(f"  Processed successfully: {processed}")
    print(f"  Errors: {errors}")
    print(f"  Total charges in database: {ServiceCharge.query.count()}")
