"""
Match 2022-2023 charge categories with best matches from 2024-2026
"""
from app import app, db
from models import ServiceCharge, ChargeCategory

def main():
    with app.app_context():
        print("\n=== 2022-2023 Charges (Current State) ===")
        charges_2022_2023 = db.session.query(
            ServiceCharge.charge_name, 
            ServiceCharge.year, 
            ChargeCategory.name
        ).outerjoin(ChargeCategory).filter(
            ServiceCharge.year.in_([2022, 2023])
        ).order_by(
            ServiceCharge.year, 
            ServiceCharge.charge_name
        ).all()
        
        for charge, year, cat in charges_2022_2023:
            print(f"{year} | {charge:50s} | Category: {cat}")
        
        print("\n=== 2024-2026 Unique Charges ===")
        charges_2024_2026 = db.session.query(
            ServiceCharge.charge_name, 
            ChargeCategory.name
        ).outerjoin(ChargeCategory).filter(
            ServiceCharge.year.in_([2024, 2025, 2026])
        ).group_by(
            ServiceCharge.charge_name,
            ChargeCategory.name
        ).order_by(ServiceCharge.charge_name).all()
        
        for charge, cat in charges_2024_2026:
            print(f"{charge:50s} | Category: {cat}")
        
        # Based on the screenshot, let's match these specific charges:
        matches = {
            "Roof Repairs": "Maintenance",
            "Access Intercom System Repairs": "Maintenance", 
            "CCTV/Intercom maintenance": "Maintenance",
            "Gate Maintenance": "Maintenance",
            "Re-instatement valuation": "Insurance",
            "Professional Fees": "Other"
        }
        
        print("\n=== Proposed Matches ===")
        for charge_name, target_category in matches.items():
            # Find charges in 2022-2023 matching this pattern
            charges = db.session.query(ServiceCharge).filter(
                ServiceCharge.charge_name.like(f"%{charge_name}%"),
                ServiceCharge.year.in_([2022, 2023])
            ).all()
            
            if charges:
                # Get the category ID
                category = db.session.query(ChargeCategory).filter(
                    ChargeCategory.name == target_category
                ).first()
                
                if category:
                    print(f"\n{charge_name} -> {target_category} (ID: {category.id})")
                    for charge in charges:
                        print(f"  Year {charge.year}: {charge.charge_name}")
                        print(f"    Current: {charge.category.name if charge.category else 'None'}")
                        print(f"    Will update to: {target_category}")

if __name__ == "__main__":
    main()
