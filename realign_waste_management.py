from app import app, db
from models import ServiceCharge, ChargeCategory, Document, ActualCost

# Category realignment mapping
CHARGE_REALIGNMENT = {
    # Waste Management - create new category
    'Domestic Waste Collections': 'Waste Management',
    'Non-domestic Waste Collections': 'Waste Management',
    
    # Vermin Control and Parking - should be in appropriate categories
    'Vermin Control': 'Grounds',  # Pest control relates to grounds maintenance
    'Controlled Parking': 'Security',  # Parking control is a security function
    
    # Professional/Admin fees stay in Other
    # 'Bank Charges', 'Postage and Stationery', 'Miscellaneous Outlay',
    # 'Legal Fees', 'Audit & Accountancy', 'Debt Collection'
}

with app.app_context():
    print("\n" + "="*80)
    print("CATEGORY REALIGNMENT - OTHER CATEGORY CLEANUP")
    print("="*80)
    
    # Step 1: Create Waste Management category if it doesn't exist
    print("\nStep 1: Checking/Creating Waste Management category")
    print("-"*80)
    
    waste_mgmt = ChargeCategory.query.filter_by(name='Waste Management').first()
    
    if not waste_mgmt:
        waste_mgmt = ChargeCategory(name='Waste Management')
        db.session.add(waste_mgmt)
        db.session.commit()
        print("✓ Created new category: Waste Management")
    else:
        print("✓ Waste Management category already exists")
    
    # Get all necessary categories
    grounds_cat = ChargeCategory.query.filter_by(name='Grounds').first()
    security_cat = ChargeCategory.query.filter_by(name='Security').first()
    other_cat = ChargeCategory.query.filter_by(name='Other').first()
    
    # Step 2: Find and realign charges
    print("\nStep 2: Realigning charges from Other category")
    print("-"*80)
    
    category_map = {
        'Waste Management': waste_mgmt,
        'Grounds': grounds_cat,
        'Security': security_cat
    }
    
    realigned_count = 0
    
    for charge_name, new_category_name in CHARGE_REALIGNMENT.items():
        # Find all charges with this name
        charges = ServiceCharge.query.filter(
            ServiceCharge.charge_name == charge_name
        ).all()
        
        new_category = category_map[new_category_name]
        
        for charge in charges:
            current_cat = ChargeCategory.query.get(charge.category_id) if charge.category_id else None
            current_cat_name = current_cat.name if current_cat else 'None'
            
            if charge.category_id != new_category.id:
                print(f"\n{charge.charge_name}")
                print(f"  Year: {charge.year}")
                print(f"  Amount: EUR {charge.amount:,.2f}")
                print(f"  Current: {current_cat_name} → New: {new_category_name}")
                
                charge.category_id = new_category.id
                realigned_count += 1
    
    if realigned_count > 0:
        db.session.commit()
        print("\n" + "="*80)
        print(f"✓ Successfully realigned {realigned_count} charge(s)")
        print("="*80)
    
    # Step 3: Show updated Other category
    print("\n" + "="*80)
    print("UPDATED 2025 BUDGET - OTHER CATEGORY")
    print("="*80)
    
    other_charges = ServiceCharge.query.join(Document).filter(
        ServiceCharge.year == 2025,
        ServiceCharge.category_id == other_cat.id,
        Document.document_type == 'Proposed Budget'
    ).all()
    
    print()
    for charge in other_charges:
        print(f"{charge.charge_name:50} EUR {charge.amount:10,.2f}")
    
    print("-"*80)
    print(f"{'TOTAL':50} EUR {sum(c.amount for c in other_charges):10,.2f}")
    
    # Step 4: Show new Waste Management category
    print("\n" + "="*80)
    print("NEW 2025 BUDGET - WASTE MANAGEMENT CATEGORY")
    print("="*80)
    
    waste_charges = ServiceCharge.query.join(Document).filter(
        ServiceCharge.year == 2025,
        ServiceCharge.category_id == waste_mgmt.id,
        Document.document_type == 'Proposed Budget'
    ).all()
    
    print()
    for charge in waste_charges:
        print(f"{charge.charge_name:50} EUR {charge.amount:10,.2f}")
    
    print("-"*80)
    print(f"{'TOTAL':50} EUR {sum(c.amount for c in waste_charges):10,.2f}")
    
    # Step 5: Update actuals for THORNTONS (waste supplier)
    print("\n" + "="*80)
    print("UPDATING ACTUAL COSTS - THORNTONS TO WASTE MANAGEMENT")
    print("="*80)
    
    # Find Thorntons invoices (cleaning category, but should be waste management)
    thorntons = ActualCost.query.filter(
        ActualCost.supplier == 'THORNTONS'
    ).all()
    
    if thorntons:
        print(f"\nFound {len(thorntons)} THORNTONS invoices")
        print("Moving from Cleaning to Waste Management category")
        
        for invoice in thorntons:
            invoice.category_id = waste_mgmt.id
        
        db.session.commit()
        print(f"✓ Updated {len(thorntons)} actual cost records")
    
    print("\n" + "="*80)
    print("CATEGORY REALIGNMENT COMPLETE")
    print("="*80)
