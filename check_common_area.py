from utils.pdf_parser import PDFParser
import re

parser = PDFParser()
text = parser.extract_text(r'C:\Users\Duncan\OneDrive\Documents\Yewtree Square Stuff\OMC\AGM\2024\YTS Draft Budget 2024.pdf')

lines = text.split('\n')

for i, line in enumerate(lines):
    if 'Common Area' in line and 'Budget' in line:
        print(f'=== Found at line {i} ===')
        start = max(0, i-10)
        end = min(len(lines), i+10)
        for j in range(start, end):
            marker = '>>> ' if j == i else '    '
            print(f'{marker}{j}: {lines[j]}')
        break
