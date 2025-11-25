"""
Re-analyze 2023 balance sheet data more carefully
"""
import pdfplumber

pdf_path = r"C:\Users\Duncan\OneDrive\Documents\Yewtree Square Stuff\OMC\AGM\2025\Yew Tree Square Management CLG Financial Statements 31 December 2023.pdf"

print('='*70)
print('2023 BALANCE SHEET ANALYSIS')
print('='*70)

with pdfplumber.open(pdf_path) as pdf:
    # Balance sheet is typically on page with "BALANCE SHEET" in title
    for page_num, page in enumerate(pdf.pages, 1):
        text = page.extract_text()
        if 'BALANCE SHEET' in text:
            print(f'\nPage {page_num} - BALANCE SHEET:')
            print('='*70)
            lines = text.split('\n')
            
            # Find and print relevant sections
            in_reserves_section = False
            for i, line in enumerate(lines):
                if 'Reserves' in line or 'reserves' in line.lower():
                    in_reserves_section = True
                    # Print context around reserves
                    start = max(0, i - 2)
                    end = min(len(lines), i + 8)
                    print('\n'.join(lines[start:end]))
                    break

print('\n' + '='*70)
print('STATEMENT OF CHANGES IN EQUITY')
print('='*70)

with pdfplumber.open(pdf_path) as pdf:
    for page_num, page in enumerate(pdf.pages, 1):
        text = page.extract_text()
        if 'STATEMENT OF CHANGES IN EQUITY' in text:
            print(f'\nPage {page_num}:')
            print('='*70)
            print(text)
            break

print('\n' + '='*70)
print('INCOME AND EXPENDITURE - Look for sinking fund transfer')
print('='*70)

with pdfplumber.open(pdf_path) as pdf:
    for page_num, page in enumerate(pdf.pages, 1):
        text = page.extract_text()
        if 'sinking fund' in text.lower() or 'transfer' in text.lower():
            print(f'\nPage {page_num}:')
            lines = text.split('\n')
            for i, line in enumerate(lines):
                if 'sinking' in line.lower() or 'transfer' in line.lower():
                    start = max(0, i - 3)
                    end = min(len(lines), i + 4)
                    print('\n'.join(lines[start:end]))
                    print()
