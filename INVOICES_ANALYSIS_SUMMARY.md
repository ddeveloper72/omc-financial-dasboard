# INVOICES DIRECTORY ANALYSIS SUMMARY

## Date: 2025-11-28

## Overview
Successfully analyzed and imported invoice data from the Invoices directory:
`C:\Users\Duncan\OneDrive\Documents\Yewtree Square Stuff\OMC\Invoices`

---

## Files Analyzed

### 1. Bord Gáis Energy Ledgers (2 PDF files)
**Files:**
- 27282_Yew_Tree_Square_General_Ledger_Account_History_-_Electricity_internal___Apartments_04-57PM_27-05-2025.pdf
- 27283_Yew_Tree_Square_General_Ledger_Account_History_-_Electricity_internal___Apartments_04-59PM_27-05-2025.pdf

**Content:** General ledger account history for electricity supply to apartments (The Manor, The Lodge, The Hall, The Grange)

**Results:**
- ✓ Extracted: 32 invoices
- ✓ Total Amount: EUR 13,626.90
- ✓ Period: September 2024 - May 2025
- ✓ Category: Utilities
- ✓ All invoices imported (no duplicates found)

**Invoice Types:**
- Electricity supply to 4 apartment buildings
- Billing periods ranging from 2-3 months
- Average invoice: EUR 426 per bill

### 2. MAR 25 INVOICES.pdf
**Status:** Not processed (image-based PDF, requires OCR or alternative data source)
**Pages:** 17 pages
**Note:** Text extraction unsuccessful - file contains scanned images rather than searchable text

### 3. 2025 Invoices.xlsx
**Status:** File locked (permission denied - possibly open in Excel)
**Note:** Could not access during analysis session

---

## Database Impact

### Before Import
- Total Invoices: 151
- Total Amount: EUR 89,638.47

### After Import
- Total Invoices: 183 (+32)
- Total Amount: EUR 103,265.37 (+EUR 13,626.90)

### Category Breakdown (Updated)
| Category | Invoices | Total Spent | % of Total |
|----------|----------|-------------|------------|
| Cleaning | 28 | EUR 37,595.53 | 36.4% |
| **Utilities** | **65** | **EUR 23,757.72** | **23.0%** |
| Security | 53 | EUR 13,569.25 | 13.1% |
| Maintenance | 14 | EUR 11,496.93 | 11.1% |
| Grounds | 12 | EUR 9,026.66 | 8.7% |
| Lift/Elevator | 11 | EUR 7,819.28 | 7.6% |

**Note:** Utilities increased significantly with electricity invoices (+32 invoices, +EUR 13,626.90)

---

## 2025 Budget vs Actual Impact

### Utilities Category (Updated)
- **Budget:** EUR 19,700.00
- **Actual:** EUR 12,190.57 (was EUR 6,419.48 before import)
- **Variance:** EUR -7,509.43 (-38.1% under budget)

**Analysis:** 
- Still under budget despite adding EUR 5,771 in electricity costs
- Suggests not all utility invoices have been received yet for 2025
- Budget may include water, gas, and other utilities not yet invoiced

---

## Supplier Catalogue

### Total Active Suppliers: 18

### New Supplier Added
**Bord Gáis Energy**
- Description: Electricity and energy supplier for common areas and apartments
- Total Invoices: 32
- Total Spent: EUR 13,626.90
- Period: September 2024 - May 2025
- Category: Utilities
- Services: Electricity supply to 4 apartment buildings

### Existing Utility Suppliers
1. **Bord Gáis Energy** - EUR 13,626.90 (32 invoices) - *NEW*
2. **BORD GAIS** - EUR 8,186.69 (20 invoices) - Existing
3. **MAGNET** - EUR 1,944.13 (13 invoices) - Existing

**Note:** "BORD GAIS" and "Bord Gáis Energy" appear to be the same supplier with different naming conventions in source documents.

### Top 5 Suppliers by Spend (Updated)
1. **THORNTONS** - EUR 19,119.89 (18.5%) - Cleaning services
2. **DG** - EUR 17,158.96 (16.6%) - Cleaning services
3. **Bord Gáis Energy** - EUR 13,626.90 (13.2%) - Utilities *NEW*
4. **OMEGA** - EUR 9,225.00 (8.9%) - Security services
5. **EKO LANDSCAPE** - EUR 9,026.66 (8.7%) - Grounds maintenance

---

## Duplicate Prevention

✓ **No duplicates found** - All 32 electricity invoices were new records

**Duplicate Detection Method:**
- Supplier name + Invoice number + Transaction date matching
- Prevents re-importing invoices from overlapping documents

---

## Data Quality Notes

### Successful Elements
1. ✓ PDF text extraction working for ledger documents
2. ✓ Regex pattern matching for invoice lines
3. ✓ Date parsing (multiple date formats handled)
4. ✓ Cancelled invoice detection (skipped appropriately)
5. ✓ Automatic category mapping (Utilities)
6. ✓ VAT calculation (estimated at 13.5%)

### Challenges
1. **MAR 25 INVOICES.pdf** - Image-based PDF requires OCR or alternative source
2. **2025 Invoices.xlsx** - File access blocked (permission denied)
3. **Supplier naming** - "BORD GAIS" vs "Bord Gáis Energy" inconsistency

---

## Recommendations

### Immediate Actions
1. **Close Excel file** to allow access to "2025 Invoices.xlsx"
2. **Re-run analysis** after closing Excel to check for additional invoice data
3. **Clarify MAR 25 INVOICES.pdf** - Request alternative format or enable OCR processing

### Data Cleanup
1. **Standardize supplier names** - Merge "BORD GAIS" and "Bord Gáis Energy" records
2. **Review utility invoices** - Check if water, waste collection are missing
3. **Verify completeness** - 38.1% under budget suggests incomplete data

### Future Imports
1. **Establish naming standards** - Consistent supplier names across all sources
2. **Regular monitoring** - Process invoices directory monthly
3. **OCR capability** - Add for image-based PDF processing if needed

---

## Files Generated

1. **supplier_catalogue.txt** - Comprehensive supplier directory with spend analysis
2. **import_electricity_invoices.py** - Reusable script for electricity ledger imports
3. **create_supplier_catalogue.py** - Supplier analysis and reporting tool

---

## Conclusion

Successfully imported 32 electricity invoices totaling EUR 13,626.90 from Bord Gáis Energy. Database now contains 183 invoices across 18 suppliers. Supplier catalogue created with detailed business descriptions. Two files remain unprocessed (MAR 25 INVOICES.pdf and 2025 Invoices.xlsx) pending access/format resolution.

**Database Status:** ✓ Updated and verified
**Duplicates:** ✓ None found
**Data Quality:** ✓ High (automated parsing successful)
**Next Steps:** Close Excel file and investigate remaining PDF formats
