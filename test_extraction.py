"""
Test extraction on a specific document to debug
"""
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app import app
from models import Document
from utils.pdf_parser import PDFParser
from utils.budget_extractor import BudgetExtractor

def test_extraction(filename_pattern):
    """Test extraction on a specific document"""
    with app.app_context():
        # Find document
        doc = Document.query.filter(Document.filename.like(f'%{filename_pattern}%')).first()
        
        if not doc:
            print(f"Document matching '{filename_pattern}' not found")
            return
        
        print(f"Testing: {doc.filename}")
        print(f"Type: {doc.document_type}, Year: {doc.document_year}")
        print(f"Path: {doc.filepath}")
        print("="*80)
        
        # Extract text
        parser = PDFParser()
        text = parser.extract_text(doc.filepath)
        
        if not text:
            print("ERROR: Could not extract text")
            return
        
        print(f"\nExtracted {len(text)} characters")
        print("\nFirst 2000 characters:")
        print("-"*80)
        print(text[:2000])
        print("-"*80)
        
        # Try extraction
        extractor = BudgetExtractor()
        charges = extractor.extract_charges(text, doc.document_year)
        
        print(f"\nExtracted {len(charges)} charges:")
        for i, charge in enumerate(charges[:10], 1):
            print(f"{i}. {charge['charge_name']}: EUR {charge['amount']:.2f} (confidence: {charge.get('confidence_score', 0.5):.2f})")

if __name__ == '__main__':
    import sys
    pattern = sys.argv[1] if len(sys.argv) > 1 else "2025 OCR"
    test_extraction(pattern)
