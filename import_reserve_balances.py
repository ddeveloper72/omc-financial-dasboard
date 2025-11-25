"""
Import reserve balance data from audited accounts
This data would typically be extracted from the Balance Sheet section of audited accounts.

For now, we'll enter the data manually based on the balance sheet information
from the audited account PDFs.
"""
from app import app, db
from models import ReserveBalance, Document

# Reserve balance data to import
# You would extract this from the "Balance Sheet" or "Statement of Financial Position"
# sections of the audited accounts PDFs, looking for lines like:
# - "Reserves"
# - "Sinking Fund"
# - "Retained Earnings"
# - "Capital and Reserves"

RESERVE_DATA = [
    # Format: (year, opening, contributions, expenditures, closing, notes)
    # Extracted from Balance Sheet "Other reserves" line in audited accounts
    
    # 2019: Other reserves = €37,200 (prev year €21,600, so contribution = €15,600)
    (2019, 21600.00, 15600.00, 0.00, 37200.00, 'From 2019 audited accounts balance sheet'),
    
    # 2022: Other reserves = €84,000 (prev year €68,400, so net increase = €15,600)
    # Note: Statement of Changes shows "Other €62,400" which was a large one-time transfer in 2022
    (2022, 68400.00, 15600.00, 0.00, 84000.00, 'From 2022 audited accounts balance sheet'),
    
    # 2023: Other reserves = €84,000 (unchanged - no net contribution in 2023)
    # Statement of Changes shows no "Other" line for 2023, meaning no reserve movement
    # Income statement shows "Transfer from sinking fund (€15,600)" meaning they drew down reserves
    (2023, 84000.00, 0.00, 0.00, 84000.00, 'From 2023 audited accounts - reserves unchanged'),
    
    # 2024: Other reserves = €84,000 (unchanged from 2023)
    (2024, 84000.00, 0.00, 0.00, 84000.00, 'From 2024 abridged accounts balance sheet'),
]

with app.app_context():
    print('='*70)
    print('RESERVE BALANCE DATA IMPORT')
    print('='*70)
    print()
    
    if not RESERVE_DATA:
        print('⚠️  NO DATA TO IMPORT')
        print()
        print('To track reserves, you need to:')
        print()
        print('1. Open each audited account PDF:')
        
        docs = Document.query.filter_by(document_type='Audited Accounts').order_by(Document.document_year).all()
        for doc in docs:
            print(f'   - {doc.document_year}: {doc.filename}')
        
        print()
        print('2. Find the "Balance Sheet" or "Statement of Financial Position"')
        print('3. Look for lines containing:')
        print('   - "Reserves"')
        print('   - "Sinking Fund"')
        print('   - "Retained Earnings"')
        print('   - "Capital and Reserves"')
        print()
        print('4. Extract the closing balance for each year')
        print()
        print('5. Add the data to the RESERVE_DATA list in this script:')
        print('   RESERVE_DATA = [')
        print('       (2019, None, None, None, 50000.00, "From 2019 balance sheet"),')
        print('       (2022, 50000.00, 15600.00, 0.00, 65600.00, "From 2022 balance sheet"),')
        print('       (2023, 65600.00, 15600.00, 0.00, 81200.00, "From 2023 balance sheet"),')
        print('   ]')
        print()
        print('6. Run this script again to import the data')
        
    else:
        imported = 0
        
        for year, opening, contributions, expenditures, closing, notes in RESERVE_DATA:
            # Check if already exists
            existing = ReserveBalance.query.filter_by(year=year).first()
            
            if existing:
                print(f'⚠️  {year}: Already exists (EUR {existing.closing_balance:,.2f}) - skipping')
                continue
            
            # Find source document
            source_doc = Document.query.filter_by(
                document_year=year,
                document_type='Audited Accounts'
            ).first()
            
            # Create reserve balance record
            reserve = ReserveBalance(
                year=year,
                opening_balance=opening,
                contributions=contributions,
                expenditures=expenditures,
                closing_balance=closing,
                source_document_id=source_doc.id if source_doc else None,
                notes=notes
            )
            
            db.session.add(reserve)
            print(f'✓ {year}: EUR {closing:,.2f} - {notes}')
            imported += 1
        
        if imported > 0:
            db.session.commit()
            print()
            print(f'Imported {imported} reserve balance record(s)')
        else:
            print()
            print('No new records to import')
        
        # Show summary
        print()
        print('='*70)
        print('CURRENT RESERVE BALANCE DATA')
        print('='*70)
        
        reserves = ReserveBalance.query.order_by(ReserveBalance.year).all()
        
        if reserves:
            for r in reserves:
                print(f'\n{r.year}:')
                if r.opening_balance:
                    print(f'  Opening Balance:  EUR {r.opening_balance:>12,.2f}')
                if r.contributions:
                    print(f'  + Contributions:  EUR {r.contributions:>12,.2f}')
                if r.expenditures:
                    print(f'  - Expenditures:   EUR {r.expenditures:>12,.2f}')
                print(f'  = Closing Balance: EUR {r.closing_balance:>12,.2f}')
                if r.notes:
                    print(f'  Notes: {r.notes}')
        else:
            print('\nNo reserve balance data in database yet.')
