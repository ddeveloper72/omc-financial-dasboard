"""
Summary report of category alignment improvements
"""

print('='*70)
print('CATEGORY ALIGNMENT REPORT')
print('='*70)
print('\n✅ SUCCESSFULLY ALIGNED CHARGES:\n')

alignments = [
    ('Light and heat', 'Electricity charges', 'Category 5 (Utilities)', '3 charges'),
    ('Management fees', 'Managing Agent Fees', 'Category 1 (Management)', '3 charges'),
    ('Insurance', 'Building Insurance', 'Category 2 (Insurance)', '3 charges'),
    ('Accountancy', 'Audit & Accountancy', 'Category 10 (Other)', '3 charges'),
    ('Printing and stationery', 'Postage and Stationery', 'Category 10 (Other)', '2 charges'),
    ('Telephone', 'Phone line in lift', 'Category 5 (Utilities)', '2 charges'),
    ('Waste disposal', 'Domestic Waste Collections', 'Category 10 (Other)', '3 charges'),
    ('Garden Maintenance', 'Grounds Maintenance', 'Category 3 (Maintenance)', '3 charges'),
    ('Bad and doubtful debts', 'Debt Collection', 'Category 10 (Other)', '1 charge'),
    ('Sundry expenses', 'Miscellaneous Outlay', 'Category 10 (Other)', '2 charges'),
    ('Building Remedial Works', 'Building - General Repairs', 'Category 3 (Maintenance)', '1 charge'),
]

for old, new, cat, count in alignments:
    print(f'  {old:30s} → {new:30s}')
    print(f'    {cat} | {count}')
    print()

print('='*70)
print('SUMMARY STATISTICS')
print('='*70)
print(f'Total charges aligned: 26')
print(f'Charge names standardized: 11')
print(f'Categories updated: Multiple (1, 2, 3, 5, 10)')
print()

print('='*70)
print('KEY IMPROVEMENTS')
print('='*70)
print('✓ Electricity costs now comparable across budgets and audited accounts')
print('✓ Management fees aligned for year-over-year comparison')
print('✓ Insurance charges standardized')
print('✓ Waste collection costs now matchable')
print('✓ Maintenance categories (garden, building repairs) aligned')
print('✓ Administrative costs (accountancy, stationery, phone) standardized')
print()

print('='*70)
print('EXAMPLE: ELECTRICITY CHARGES TREND')
print('='*70)
print('2019 (Audited): EUR  4,687.00')
print('2022 (Audited): EUR  9,716.00 | 2022 (Budget): EUR  9,000.00')
print('2023 (Audited): EUR 17,519.00 | 2023 (Budget): EUR 14,500.00')
print('2024 (Budget):  EUR 18,000.00')
print('2025 (Budget):  EUR 18,000.00')
print()
print('✓ Clear upward trend now visible across all document types')
print('✓ Can compare actual vs budgeted amounts for years with both')
print()
