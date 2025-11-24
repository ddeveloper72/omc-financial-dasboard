"""
Test pdfplumber table extraction on budget PDFs
"""
import pdfplumber
import sys

def extract_tables_from_pdf(pdf_path):
    """Extract tables from PDF using pdfplumber"""
    print(f"Analyzing: {pdf_path}")
    print("="*80)
    
    with pdfplumber.open(pdf_path) as pdf:
        print(f"Total pages: {len(pdf.pages)}\n")
        
        all_charges = []
        
        for page_num, page in enumerate(pdf.pages, 1):
            print(f"\nPage {page_num}:")
            print("-"*80)
            
            # Extract tables
            tables = page.extract_tables()
            
            if tables:
                print(f"Found {len(tables)} table(s)")
                
                for table_num, table in enumerate(tables, 1):
                    print(f"\nTable {table_num}:")
                    print(f"Rows: {len(table)}, Columns: {len(table[0]) if table else 0}")
                    
                    # Show first few rows
                    for row_idx, row in enumerate(table[:10]):
                        print(f"  Row {row_idx}: {row}")
                    
                    if len(table) > 10:
                        print(f"  ... ({len(table) - 10} more rows)")
            else:
                print("No tables found on this page")
                
                # Try extracting text as fallback
                text = page.extract_text()
                if text:
                    lines = text.split('\n')[:10]
                    print(f"\nText preview (first 10 lines):")
                    for line in lines:
                        print(f"  {line}")
    
    return all_charges

if __name__ == '__main__':
    # Test on the 2025 Proposed Budget OCR file
    pdf_path = r'C:\Users\Duncan\OneDrive\Documents\Yewtree Square Stuff\OMC\AGM\2025\Proposed Budget 2025 OCR.pdf'
    
    print("Testing pdfplumber table extraction")
    print("="*80)
    print()
    
    extract_tables_from_pdf(pdf_path)
