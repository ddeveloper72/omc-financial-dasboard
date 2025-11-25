"""
Analyze the 2019 PDF structure
"""
import pdfplumber

pdf_path = r"C:\Users\Duncan\OneDrive\Documents\Yewtree Square Stuff\OMC\AGM\2019\Accounts 2019 - Yew Tree Square Management Company OCR.pdf"

with pdfplumber.open(pdf_path) as pdf:
    print(f"Total pages: {len(pdf.pages)}\n")
    
    for page_num, page in enumerate(pdf.pages, 1):
        print(f"{'='*80}")
        print(f"PAGE {page_num}")
        print(f"{'='*80}")
        
        text = page.extract_text()
        if text:
            # Look for the administrative expenses schedule
            if 'administrative' in text.lower() or 'expense' in text.lower():
                print(text)
                print()
        else:
            print("No text extracted from this page\n")
