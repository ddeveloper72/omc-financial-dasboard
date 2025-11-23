"""
Test OCR preprocessing logic directly
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from utils.budget_extractor import BudgetExtractor

# Sample OCR text from Proposed Budget 2025 OCR
sample_text = """Insurance
Building Insurance
Lift Engineering Inspection insurance
Directors and officers liability insurance Re-instatement valuation
Electricity charges
Repairs and malntenance
Building - General Repairs
Access issue repairs
CCTV maintenance/repairs
Electrical Repairs
Bulb replacement
Building Remedial Works
Gate
Gate Maintenance and Repairs
Gate Access System
Lift Costs
Lift Maintenance
Phone line in lift
Fire Alarm
Fire Alarm maintenance and repairs
Malntenance of Fire Extinguishers
External Maintenance
Grounds Maintenance
Vermin Control
Controlled Parking
Salting
Cleaning
Cleaning
Bin store cleaning
Window cleaning
Refuse
Domestic Waste Collections
Non-domestic Waste Collections
General Costs
Bank Charges
Postage & Stationery
MyBlockman ~ Annual charge
Miscellaneous Outlay
Professional Fees
Legal Fees
Audit & Accountancy Debt Collection
Managing Agent Fees
Capital Contributions
Sinking Fund Contribution Tota! 2025
€23,000
€1,500 €400
€0
€18,000
€28,000 €500
€1,200 €750
€1,300
€1,000 €500
€7,000
€1,700
€4,000 €800
€9,520
€1,000 €750
€250
€18,000
€2,000
€2,400
€21,000
€1,000
€150
€1,000 €384
€150
€1,150
€1,496
€3,500
€13,923
€167,323
€15,600 €182,923"""

print("Original text (first 500 chars):")
print("="*80)
print(sample_text[:500])
print("="*80)
print()

extractor = BudgetExtractor()
preprocessed = extractor._preprocess_ocr_text(sample_text)

print("Preprocessed text:")
print("="*80)
print(preprocessed)
print("="*80)
print()

charges = extractor.extract_charges(preprocessed, year=2025)
print(f"\nExtracted {len(charges)} charges:")
for charge in charges[:10]:  # Show first 10
    print(f"  - {charge['charge_name']}: {charge['amount']:.2f} (confidence: {charge['confidence_score']:.2f})")
