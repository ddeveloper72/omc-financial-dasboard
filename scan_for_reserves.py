"""
Scan audited accounts PDFs for balance sheet / reserve information
"""
import pdfplumber
from models import Document
from app import app

def extract_reserve_info(pdf_path):
    """Extract text that might contain reserve/balance sheet information"""
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, 1):
            text = page.extract_text()
            if not text:
                continue
            
            # Look for balance sheet related keywords
            lower_text = text.lower()
            keywords = [
                'balance sheet',
                'statement of financial position',
                'reserves',
                'sinking fund',
                'retained earnings',
                'capital and reserves',
                'members\' funds'
            ]
            
            if any(keyword in lower_text for keyword in keywords):
                print(f'\n📄 Page {page_num}:')
                print('-' * 70)
                
                # Print relevant lines
                lines = text.split('\n')
                for i, line in enumerate(lines):
                    line_lower = line.lower()
                    if any(keyword in line_lower for keyword in keywords):
                        # Print context (3 lines before and after)
                        start = max(0, i - 3)
                        end = min(len(lines), i + 4)
                        print('\n'.join(lines[start:end]))
                        print()

with app.app_context():
    docs = Document.query.filter_by(document_type='Audited Accounts').order_by(Document.document_year).all()
    
    for doc in docs:
        year = doc.document_year if doc.document_year else 'Unknown'
        print('\n' + '='*70)
        print(f'ANALYZING: {year} - {doc.filename}')
        print('='*70)
        
        try:
            extract_reserve_info(doc.filepath)
        except Exception as e:
            print(f'❌ Error: {e}')
        
        print('\n' + '='*70)
        print(f'END OF {year}')
        print('='*70)
