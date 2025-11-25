"""
Analyze 2022 and 2023 audited accounts PDFs to find detailed expense schedules
"""
import pdfplumber
import os

pdf_dir = r"C:\Users\Duncan\OneDrive\Documents\Yewtree Square Stuff\OMC\AGM"

# 2022 Audited Accounts
pdf_2022 = None
pdf_2023 = None

for root, dirs, files in os.walk(pdf_dir):
    for file in files:
        if "2022" in file and "audit" in file.lower():
            pdf_2022 = os.path.join(root, file)
        if "2023" in file and ("statement" in file.lower() or "audit" in file.lower()):
            if "budget" not in file.lower():  # Exclude budget files
                pdf_2023 = os.path.join(root, file)

print("="*80)
print("2022 AUDITED ACCOUNTS ANALYSIS")
print("="*80)

if pdf_2022:
    print(f"\nFile: {pdf_2022}")
    with pdfplumber.open(pdf_2022) as pdf:
        print(f"Total pages: {len(pdf.pages)}")
        
        # Search for schedule pages
        for i, page in enumerate(pdf.pages, 1):
            text = page.extract_text() or ""
            
            # Look for schedule keywords
            if any(keyword in text.lower() for keyword in ['schedule', 'administrative', 'other costs', 'operating']):
                print(f"\n--- Page {i} ---")
                print(text[:500])  # First 500 chars
else:
    print("\n2022 PDF not found")

print("\n" + "="*80)
print("2023 AUDITED ACCOUNTS ANALYSIS")
print("="*80)

if pdf_2023:
    print(f"\nFile: {pdf_2023}")
    with pdfplumber.open(pdf_2023) as pdf:
        print(f"Total pages: {len(pdf.pages)}")
        
        # Search for schedule pages
        for i, page in enumerate(pdf.pages, 1):
            text = page.extract_text() or ""
            
            # Look for schedule keywords
            if any(keyword in text.lower() for keyword in ['schedule', 'administrative', 'other costs', 'operating']):
                print(f"\n--- Page {i} ---")
                print(text[:500])  # First 500 chars
else:
    print("\n2023 PDF not found")
