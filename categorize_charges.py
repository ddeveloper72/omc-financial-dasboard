"""
Automatically categorize service charges based on their names
"""
from app import app, db
from models import ServiceCharge, ChargeCategory

def categorize_charges():
    """Assign categories to charges based on keywords in their names"""
    
    # Define keyword mappings for each category
    # Order matters - more specific keywords should come first
    category_keywords = {
        'Management': ['management fee', 'management charges', 'managing agent', 'agent fee', 'agent charges', 'myblockman', 'my blockman'],
        'Insurance': ['insurance', 'liability', 'reinstatement', 're-instatement'],
        'Maintenance': [
            'maintenance', 'repair', 'servicing', 'inspection', 'external maintenance',
            'malntenance',  # OCR typo
            'building   general repairs', 'building repair'
        ],
        'Cleaning': ['cleaning', 'cleaner', 'bulb replacement', 'bulb'],
        'Utilities': ['electricity', 'water', 'utilities', 'phone line', 'broadband', 'electrical'],
        'Lift/Elevator': ['lift', 'elevator'],
        'Grounds': ['garden', 'landscaping', 'grounds', 'grass', 'planting', 'salting'],
        'Security': [
            'security', 'fire alarm', 'fire extinguisher', 'gate', 'access system', 'cctv',
            'access issue', 'alarm'
        ],
        'Reserve Fund': ['sinking fund', 'reserve fund', 'reserve account', 'capital contribution'],
        'Other': [
            # Professional/Legal/Financial - could be a separate category
            'professional fee', 'legal fee', 'audit', 'accountancy', 'accounting', 'debt collection',
            # Waste management - could be Utilities or separate category
            'waste', 'refuse', 'domestic waste', 'non domestic waste',
            # Miscellaneous
            'vermin', 'pest control', 'parking', 'postage', 'stationery', 'printing',
            'common area budget', 'service charge', 'miscellaneous'
        ]
    }
    
    with app.app_context():
        # Get all categories
        categories = {cat.name: cat for cat in ChargeCategory.query.all()}
        
        # Get all charges without categories
        uncategorized = ServiceCharge.query.filter(ServiceCharge.category_id == None).all()
        
        print(f"Found {len(uncategorized)} uncategorized charges\n")
        
        categorized_count = 0
        category_counts = {name: 0 for name in categories.keys()}
        
        for charge in uncategorized:
            charge_name_lower = charge.charge_name.lower()
            assigned = False
            
            # Try to match against each category's keywords
            for category_name, keywords in category_keywords.items():
                if category_name == 'Other':
                    continue
                    
                for keyword in keywords:
                    if keyword in charge_name_lower:
                        charge.category_id = categories[category_name].id
                        category_counts[category_name] += 1
                        categorized_count += 1
                        print(f"  {charge.charge_name:50s} -> {category_name}")
                        assigned = True
                        break
                
                if assigned:
                    break
            
            # If no category matched, assign to "Other"
            if not assigned:
                charge.category_id = categories['Other'].id
                category_counts['Other'] += 1
                categorized_count += 1
                print(f"  {charge.charge_name:50s} -> Other")
        
        # Commit all changes
        db.session.commit()
        
        print(f"\n{'='*80}")
        print(f"Successfully categorized {categorized_count} charges:\n")
        for category_name, count in sorted(category_counts.items()):
            if count > 0:
                print(f"  {category_name:20s}: {count:3d} charges")
        
        # Show total per category
        print(f"\n{'='*80}")
        print("Total charges per category (including previously categorized):\n")
        for category_name, category in sorted(categories.items()):
            total = ServiceCharge.query.filter(ServiceCharge.category_id == category.id).count()
            print(f"  {category_name:20s}: {total:3d} charges")

if __name__ == '__main__':
    categorize_charges()
