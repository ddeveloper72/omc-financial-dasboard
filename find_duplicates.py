"""
Show duplicate charges
"""
from pathlib import Path
import sys
from collections import defaultdict

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app import app, db
from models import ServiceCharge, Document

def find_duplicates():
    """Find charges with similar names in the same year"""
    with app.app_context():
        charges = ServiceCharge.query.join(Document).order_by(
            ServiceCharge.year, ServiceCharge.charge_name
        ).all()
        
        # Group by year and normalized name
        groups = defaultdict(list)
        for charge in charges:
            # Normalize name (lowercase, remove extra spaces)
            normalized = ' '.join(charge.charge_name.lower().split())
            key = (charge.year, normalized)
            groups[key].append(charge)
        
        print("Potential Duplicates:")
        print("="*80)
        
        for (year, name), charge_list in sorted(groups.items()):
            if len(charge_list) > 1:
                print(f"\n{year} - {name.title()}")
                print(f"  Found {len(charge_list)} instances:")
                for charge in charge_list:
                    doc_type = charge.document.document_type if charge.document else "Unknown"
                    print(f"    EUR {charge.amount:,.2f} from {doc_type}: '{charge.charge_name}'")
        
        # Also show sinking fund specific
        print("\n\n" + "="*80)
        print("SINKING FUND ANALYSIS:")
        print("="*80)
        sinking_charges = ServiceCharge.query.join(Document).filter(
            ServiceCharge.charge_name.ilike('%sinking%')
        ).order_by(ServiceCharge.year).all()
        
        for charge in sinking_charges:
            doc_type = charge.document.document_type if charge.document else "Unknown"
            print(f"{charge.year} [{doc_type}] {charge.charge_name}: EUR {charge.amount:,.2f}")

if __name__ == '__main__':
    find_duplicates()
