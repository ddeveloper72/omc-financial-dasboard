from app import app, db
from models import ServiceCharge, Document
from utils.pdf_parser import PDFParser

app.app_context().push()

# Find the professional fees charge for 2023
charge = ServiceCharge.query.join(Document).filter(
    ServiceCharge.charge_name == 'Professional Fees',
    ServiceCharge.year == 2023,
    ServiceCharge.amount == 2034.00
).first()

if charge:
    print(f'Charge: {charge.charge_name}')
    print(f'Amount: €{charge.amount:.2f}')
    print(f'Document: {charge.document.document_type}')
    print(f'Filename: {charge.document.filename}')
    print(f'Filepath: {charge.document.filepath}')
    print(f'Category: {charge.category.name if charge.category else "None"}')
    print('\n' + '='*80)
    print('Extracting context from PDF...\n')
    
    # Extract text and find context around Professional Fees
    parser = PDFParser()
    text = parser.extract_text(charge.document.filepath)
    
    if text:
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if 'Professional Fees' in line and '2,034' in line:
                print(f'=== Found at line {i} ===')
                start = max(0, i-15)
                end = min(len(lines), i+15)
                for j in range(start, end):
                    marker = '>>> ' if j == i else '    '
                    print(f'{marker}{j}: {lines[j]}')
                print('\n')
else:
    print('Professional Fees charge not found for 2023 with amount €2,034.00')
