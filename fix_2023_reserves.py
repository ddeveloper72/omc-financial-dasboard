"""
Update the 2023 reserve balance data with correct figures
"""
from app import app, db
from models import ReserveBalance

with app.app_context():
    print('='*70)
    print('CORRECTING 2023 RESERVE BALANCE DATA')
    print('='*70)
    
    reserve_2023 = ReserveBalance.query.filter_by(year=2023).first()
    
    if reserve_2023:
        print(f'\nCurrent 2023 data:')
        print(f'  Opening: EUR {reserve_2023.opening_balance:,.2f}')
        print(f'  Contributions: EUR {reserve_2023.contributions:,.2f}')
        print(f'  Expenditures: EUR {reserve_2023.expenditures:,.2f}')
        print(f'  Closing: EUR {reserve_2023.closing_balance:,.2f}')
        print(f'  Notes: {reserve_2023.notes}')
        
        print('\n' + '-'*70)
        print('CORRECTION:')
        print('-'*70)
        print('The Statement of Changes in Equity shows:')
        print('  - Balance at 31 Dec 2022: €84,000')
        print('  - Balance at 31 Dec 2023: €84,000')
        print('  - NO "Other" movement in 2023 (no reserve contribution)')
        print('')
        print('The "Transfer from sinking fund (€15,600)" in income statement')
        print('was an ACCOUNTING ENTRY, not an actual drawdown of reserves.')
        print('It offsets the budgeted contribution that was included in expenses.')
        print('')
        print('CORRECT 2023 figures:')
        print('  Opening: EUR 84,000.00')
        print('  Contributions: EUR 0.00 (no net contribution)')
        print('  Expenditures: EUR 0.00 (no drawdown)')
        print('  Closing: EUR 84,000.00 (unchanged)')
        
        # Update the record
        reserve_2023.contributions = 0.00
        reserve_2023.expenditures = 0.00
        reserve_2023.notes = 'From 2023 audited accounts - reserves unchanged'
        
        db.session.commit()
        
        print('\n✓ Updated 2023 reserve balance data')
    else:
        print('❌ No 2023 reserve balance record found')
    
    print('\n' + '='*70)
    print('UPDATED RESERVE BALANCE DATA')
    print('='*70)
    
    reserves = ReserveBalance.query.order_by(ReserveBalance.year).all()
    for r in reserves:
        print(f'\n{r.year}:')
        print(f'  Opening:       EUR {r.opening_balance:>12,.2f}')
        if r.contributions and r.contributions > 0:
            print(f'  + Contributions: EUR {r.contributions:>12,.2f}')
        if r.expenditures and r.expenditures > 0:
            print(f'  - Expenditures:  EUR {r.expenditures:>12,.2f}')
        print(f'  = Closing:       EUR {r.closing_balance:>12,.2f}')
        if r.notes:
            print(f'  Notes: {r.notes}')
