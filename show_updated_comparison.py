from app import app, db
from models import ServiceCharge, ActualCost, ChargeCategory, Document
from sqlalchemy import func

with app.app_context():
    print("\n" + "="*80)
    print("2025 BUDGET vs ACTUAL - UPDATED CATEGORIES")
    print("="*80)
    
    categories = ChargeCategory.query.order_by(ChargeCategory.name).all()
    
    print(f"\n{'Category':<25} {'Budget':>12} {'Actual':>12} {'Variance':>12} {'%':>8}")
    print("-"*80)
    
    total_budget = 0
    total_actual = 0
    
    for cat in categories:
        budget = db.session.query(func.sum(ServiceCharge.amount)).join(Document).filter(
            ServiceCharge.year == 2025,
            ServiceCharge.category_id == cat.id,
            Document.document_type == 'Proposed Budget'
        ).scalar() or 0
        
        actual = db.session.query(func.sum(ActualCost.total_amount)).filter(
            ActualCost.year == 2025,
            ActualCost.category_id == cat.id
        ).scalar() or 0
        
        if budget > 0 or actual > 0:
            variance = actual - budget
            pct = (variance / budget * 100) if budget else 0
            
            total_budget += budget
            total_actual += actual
            
            print(f"{cat.name:<25} {budget:>12,.2f} {actual:>12,.2f} {variance:>12,.2f} {pct:>7.1f}%")
    
    print("-"*80)
    total_variance = total_actual - total_budget
    total_pct = (total_variance / total_budget * 100) if total_budget else 0
    print(f"{'TOTAL':<25} {total_budget:>12,.2f} {total_actual:>12,.2f} {total_variance:>12,.2f} {total_pct:>7.1f}%")
    print("="*80)
    
    # Show updated category breakdown
    print("\n" + "="*80)
    print("CATEGORY SUMMARY")
    print("="*80)
    
    print("\nKey Changes:")
    print("  • Created: Waste Management category")
    print("  • Moved: Domestic & Non-domestic Waste Collections → Waste Management")
    print("  • Moved: Vermin Control → Grounds")
    print("  • Moved: Controlled Parking → Security")
    print("  • Moved: THORNTONS invoices → Waste Management (11 invoices)")
    
    print("\nUpdated Totals:")
    print(f"  Other category: EUR 31,196 → EUR 7,446 (reduced by EUR 23,750)")
    print(f"  New Waste Management: EUR 22,000 budget")
    print(f"  Grounds: +EUR 1,000 (Vermin Control)")
    print(f"  Security: +EUR 750 (Controlled Parking)")
