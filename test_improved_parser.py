"""
Enhanced PDF parser using pdfplumber for better text extraction
"""
import pdfplumber
import re
from typing import List, Dict, Tuple

class PDFPlumberParser:
    """Extract budget data from PDFs using pdfplumber"""
    
    def __init__(self):
        self.amount_patterns = [
            r'€\s*([0-9,]+\.?[0-9]*)',  # €23,000 or €1,500.00
            r'EUR?\s*([0-9,]+\.?[0-9]*)',  # EUR 23000
            r'([0-9,]+\.?[0-9]*)\s*€',  # 23,000€
        ]
    
    def extract_text(self, pdf_path: str) -> str:
        """Extract text from PDF using pdfplumber"""
        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() + "\n"
        return text
    
    def parse_line_with_amounts(self, line: str) -> Tuple[str, List[float]]:
        """
        Parse a line to extract charge name and amounts
        Returns: (charge_name, [amount1, amount2, ...])
        """
        amounts = []
        
        # Find all amounts in the line
        for pattern in self.amount_patterns:
            matches = re.findall(pattern, line)
            for match in matches:
                try:
                    # Remove commas and convert to float
                    amount = float(match.replace(',', ''))
                    amounts.append(amount)
                except ValueError:
                    continue
        
        # Extract charge name (text before the first amount)
        charge_name = line
        for pattern in self.amount_patterns:
            charge_name = re.split(pattern, charge_name)[0]
        
        # Clean up charge name
        charge_name = charge_name.strip()
        charge_name = re.sub(r'\s+', ' ', charge_name)  # Normalize whitespace
        
        return charge_name, amounts
    
    def extract_charges_from_text(self, text: str, year: int = None) -> List[Dict]:
        """
        Extract charges from text
        Returns list of dicts with charge_name and amount
        """
        charges = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Parse the line
            charge_name, amounts = self.parse_line_with_amounts(line)
            
            # Skip if no amounts or no charge name
            if not amounts or not charge_name or len(charge_name) < 3:
                continue
            
            # Take the first (typically largest/main) amount
            # In "Building Insurance €23,000", we want €23,000
            # In "Lift Engineering... €1,500 €1,500", both are same so either works
            amount = amounts[0]
            
            charges.append({
                'charge_name': charge_name,
                'amount': amount,
                'year': year,
                'raw_text': line
            })
        
        return charges

if __name__ == '__main__':
    parser = PDFPlumberParser()
    
    pdf_path = r'C:\Users\Duncan\OneDrive\Documents\Yewtree Square Stuff\OMC\AGM\2025\Proposed Budget 2025 OCR.pdf'
    
    print("Testing improved pdfplumber parser")
    print("="*80)
    
    # Extract text
    text = parser.extract_text(pdf_path)
    
    # Extract charges
    charges = parser.extract_charges_from_text(text, year=2025)
    
    print(f"\nExtracted {len(charges)} charges:\n")
    
    # Focus on Insurance section
    print("INSURANCE CHARGES:")
    print("-"*80)
    for charge in charges:
        if 'insurance' in charge['charge_name'].lower():
            print(f"{charge['charge_name']:50s} | EUR {charge['amount']:>10,.2f}")
            print(f"  Raw: {charge['raw_text']}")
            print()
    
    print("\n" + "="*80)
    print("ALL CHARGES:")
    print("="*80)
    for charge in charges[:20]:  # First 20
        print(f"{charge['charge_name']:50s} | EUR {charge['amount']:>10,.2f}")
