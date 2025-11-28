"""
YTS Budget Analysis - Flask Application

This application extracts and analyzes service charge data from OMC AGM documents.
It uses rule-based text extraction (no AI/ML) to process PDF financial documents.

EU AI Act Compliance:
- Not classified as high-risk AI system (EU AI Act Article 6, Annex III)
- No machine learning or AI algorithms employed
- Rule-based deterministic processing only
- Processes financial data only (no personal information)

Data Protection:
- GDPR compliant (EU Regulation 2016/679)
- Local storage only, no external data transmission
- Data minimization and purpose limitation principles followed

For full compliance documentation, see COMPLIANCE.md

Technical References:
- Flask Framework: https://flask.palletsprojects.com/
- SQLAlchemy: https://docs.sqlalchemy.org/
- pypdf Library: https://pypdf.readthedocs.io/
"""

import os
import logging
from flask import Flask, render_template, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from models import db, Document, ServiceCharge, ChargeCategory, ProcessingLog, ActualCost
from utils.document_scanner import DocumentScanner
from utils.pdf_parser import PDFParser
from utils.budget_extractor import BudgetExtractor

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.getenv('DATABASE_PATH', 'db.sqlite3')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

# Document source path
DOCUMENT_SOURCE_PATH = os.getenv('DOCUMENT_SOURCE_PATH')


@app.route('/')
def index():
    """Home page with overview"""
    return render_template('index.html')


@app.route('/about')
def about():
    """About page with compliance documentation and references"""
    return render_template('about.html')


@app.route('/dashboard')
def dashboard():
    """Main dashboard with visualizations"""
    # Get summary statistics
    stats = {
        'total_documents': Document.query.count(),
        'total_charges': ServiceCharge.query.count(),
        'years_available': db.session.query(ServiceCharge.year).distinct().order_by(ServiceCharge.year).all(),
        'categories': ChargeCategory.query.filter_by(is_active=True).all(),
        'document_types': db.session.query(Document.document_type).distinct().filter(Document.document_type.isnot(None)).all()
    }
    
    return render_template('dashboard.html', stats=stats)


@app.route('/api/scan-documents', methods=['POST'])
def scan_documents():
    """Scan directory for new documents"""
    try:
        if not DOCUMENT_SOURCE_PATH:
            return jsonify({'error': 'Document source path not configured'}), 400
        
        scanner = DocumentScanner(DOCUMENT_SOURCE_PATH)
        documents = scanner.scan_directory()
        
        return jsonify({
            'success': True,
            'documents_found': len(documents),
            'documents': documents
        })
        
    except Exception as e:
        logger.error(f"Error scanning documents: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/process-document/<int:document_id>', methods=['POST'])
def process_document(document_id):
    """Process a single document and extract charges"""
    try:
        document = Document.query.get_or_404(document_id)
        
        # Extract text from PDF
        parser = PDFParser()
        text = parser.extract_text(document.filepath)
        
        if not text:
            document.status = 'error'
            document.error_message = 'Failed to extract text from PDF'
            db.session.commit()
            return jsonify({'error': 'Failed to extract text'}), 400
        
        # Extract charges
        extractor = BudgetExtractor()
        charges = extractor.extract_charges(text, document.document_year)
        
        # Save charges to database
        for charge_data in charges:
            charge = ServiceCharge(
                document_id=document.id,
                year=charge_data['year'] or document.document_year,
                charge_name=charge_data['charge_name'],
                amount=charge_data['amount'],
                currency=charge_data['currency'],
                raw_text=charge_data['raw_text'],
                confidence_score=charge_data['confidence_score']
            )
            db.session.add(charge)
        
        document.status = 'processed'
        db.session.commit()
        
        # Log success
        log_entry = ProcessingLog(
            document_id=document.id,
            status='success',
            message=f'Extracted {len(charges)} charges'
        )
        db.session.add(log_entry)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'charges_extracted': len(charges)
        })
        
    except Exception as e:
        logger.error(f"Error processing document {document_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/charges')
def get_charges():
    """Get all service charges with optional filtering"""
    # Support multiple years
    years = request.args.getlist('year')
    if years:
        years = [int(y) for y in years]
    
    category_id = request.args.get('category_id', type=int)
    charge_name = request.args.get('charge_name')
    
    # Support multiple document types
    document_types = request.args.getlist('document_type')
    
    query = ServiceCharge.query.join(Document)
    
    if years:
        query = query.filter(ServiceCharge.year.in_(years))
    if category_id:
        query = query.filter(ServiceCharge.category_id == category_id)
    if charge_name:
        query = query.filter(ServiceCharge.charge_name == charge_name)
    if document_types:
        query = query.filter(Document.document_type.in_(document_types))
    
    charges = query.all()
    
    return jsonify([{
        'id': c.id,
        'year': c.year,
        'charge_name': c.charge_name,
        'amount': c.amount,
        'currency': c.currency,
        'category': c.category.name if c.category else None,
        'document_type': c.document.document_type
    } for c in charges])


@app.route('/api/trends')
def get_trends():
    """Get year-over-year trend data with separate lines for actuals, budgets, and income"""
    from sqlalchemy import func
    
    charge_type = request.args.get('charge_type', 'expense')  # Default to expenses only
    category_id = request.args.get('category_id', type=int)
    charge_name = request.args.get('charge_name')
    
    # Get audited accounts (actuals)
    actuals_query = db.session.query(
        ServiceCharge.year,
        func.sum(ServiceCharge.amount).label('total_amount')
    ).join(Document).filter(
        Document.document_type == 'Audited Accounts',
        ServiceCharge.charge_type == charge_type
    )
    
    if category_id:
        actuals_query = actuals_query.filter(ServiceCharge.category_id == category_id)
    if charge_name:
        actuals_query = actuals_query.filter(ServiceCharge.charge_name == charge_name)
    
    actuals_query = actuals_query.group_by(ServiceCharge.year).order_by(ServiceCharge.year)
    actuals = actuals_query.all()
    
    # Get proposed budgets
    budgets_query = db.session.query(
        ServiceCharge.year,
        func.sum(ServiceCharge.amount).label('total_amount')
    ).join(Document).filter(
        Document.document_type == 'Proposed Budget',
        ServiceCharge.charge_type == charge_type
    )
    
    if category_id:
        budgets_query = budgets_query.filter(ServiceCharge.category_id == category_id)
    if charge_name:
        budgets_query = budgets_query.filter(ServiceCharge.charge_name == charge_name)
    
    budgets_query = budgets_query.group_by(ServiceCharge.year).order_by(ServiceCharge.year)
    budgets = budgets_query.all()
    
    # Get income data (from audited accounts only) - but ONLY when not filtering by category/charge
    # Income is total revenue, so it doesn't make sense to show it when filtering specific expenses
    income = []
    if not category_id and not charge_name:
        income_query = db.session.query(
            ServiceCharge.year,
            func.sum(ServiceCharge.amount).label('total_amount')
        ).join(Document).filter(
            Document.document_type == 'Audited Accounts',
            ServiceCharge.charge_type == 'income'
        ).group_by(ServiceCharge.year).order_by(ServiceCharge.year)
        
        income = income_query.all()
    
    # Combine all years
    all_years = sorted(set([t.year for t in actuals] + [t.year for t in budgets] + [t.year for t in income]))
    
    # Build response with separate datasets
    actuals_dict = {t.year: float(t.total_amount) for t in actuals}
    budgets_dict = {t.year: float(t.total_amount) for t in budgets}
    income_dict = {t.year: float(t.total_amount) for t in income}
    
    return jsonify({
        'years': all_years,
        'actuals': [actuals_dict.get(year, None) for year in all_years],
        'budgets': [budgets_dict.get(year, None) for year in all_years],
        'income': [income_dict.get(year, None) for year in all_years]
    })


@app.route('/api/charge-names')
def get_charge_names():
    """Get distinct charge names for a specific category"""
    from sqlalchemy import func, distinct
    
    category_id = request.args.get('category_id', type=int)
    
    if not category_id:
        return jsonify({'error': 'category_id required'}), 400
    
    # Get distinct charge names for this category, ordered alphabetically
    charge_names = db.session.query(
        distinct(ServiceCharge.charge_name)
    ).filter(
        ServiceCharge.category_id == category_id
    ).order_by(ServiceCharge.charge_name).all()
    
    return jsonify({
        'charge_names': [name[0] for name in charge_names]
    })


@app.route('/api/categories')
def get_categories():
    """Get all charge categories"""
    categories = ChargeCategory.query.filter_by(is_active=True).all()
    
    return jsonify([{
        'id': c.id,
        'name': c.name,
        'description': c.description
    } for c in categories])


@app.route('/api/glossary')
def get_glossary():
    """Get all glossary definitions"""
    from models import ChargeGlossary
    
    glossary = ChargeGlossary.query.filter_by(is_active=True).all()
    
    return jsonify({entry.charge_name: {
        'definition': entry.definition,
        'examples': entry.examples
    } for entry in glossary})


@app.route('/api/reserves')
def get_reserves():
    """Get reserve balance data over time"""
    from models import ReserveBalance
    
    reserves = ReserveBalance.query.order_by(ReserveBalance.year).all()
    
    return jsonify({
        'years': [r.year for r in reserves],
        'opening_balances': [r.opening_balance for r in reserves],
        'contributions': [r.contributions for r in reserves],
        'expenditures': [r.expenditures for r in reserves],
        'closing_balances': [r.closing_balance for r in reserves],
        'notes': [r.notes for r in reserves]
    })


@app.route('/comparison')
def comparison_dashboard():
    """Actuals vs Budget comparison dashboard"""
    from sqlalchemy import func
    
    # Get years that have both audited accounts and proposed budgets
    audited_years = db.session.query(ServiceCharge.year).join(Document).filter(
        Document.document_type == 'Audited Accounts'
    ).distinct().all()
    
    budget_years = db.session.query(ServiceCharge.year).join(Document).filter(
        Document.document_type == 'Proposed Budget'
    ).distinct().all()
    
    # Get years with actual costs (invoice data)
    invoice_years = db.session.query(ActualCost.year).distinct().all()
    
    stats = {
        'audited_count': Document.query.filter_by(document_type='Audited Accounts').count(),
        'budget_count': Document.query.filter_by(document_type='Proposed Budget').count(),
        'invoice_count': ActualCost.query.count(),
        'audited_years': sorted([y[0] for y in audited_years if y[0]]),
        'budget_years': sorted([y[0] for y in budget_years if y[0]]),
        'invoice_years': sorted([y[0] for y in invoice_years if y[0]]),
        'categories': ChargeCategory.query.filter_by(is_active=True).all()
    }
    
    return render_template('comparison.html', stats=stats)


@app.route('/api/comparison')
def get_comparison_data():
    """Get actuals vs budget comparison data"""
    from sqlalchemy import func
    
    year = request.args.get('year', type=int)
    category_id = request.args.get('category_id', type=int)
    mode = request.args.get('mode', 'audited')  # 'audited' or 'invoices'
    
    if not year:
        return jsonify({'error': 'Year parameter required'}), 400
    
    # Mode: invoices - compare Budget vs Invoice Actuals
    if mode == 'invoices':
        return get_invoice_comparison(year, category_id)
    
    # Get audited actuals
    actuals_query = db.session.query(
        ServiceCharge.charge_name,
        ChargeCategory.name.label('category_name'),
        func.sum(ServiceCharge.amount).label('actual_amount')
    ).join(Document).join(ChargeCategory, ServiceCharge.category_id == ChargeCategory.id, isouter=True).filter(
        ServiceCharge.year == year,
        Document.document_type == 'Audited Accounts'
    )
    
    if category_id:
        actuals_query = actuals_query.filter(ServiceCharge.category_id == category_id)
    
    actuals = actuals_query.group_by(ServiceCharge.charge_name, ChargeCategory.name).all()
    
    # Get proposed budgets
    budget_query = db.session.query(
        ServiceCharge.charge_name,
        ChargeCategory.name.label('category_name'),
        func.sum(ServiceCharge.amount).label('budget_amount')
    ).join(Document).join(ChargeCategory, ServiceCharge.category_id == ChargeCategory.id, isouter=True).filter(
        ServiceCharge.year == year,
        Document.document_type == 'Proposed Budget'
    )
    
    if category_id:
        budget_query = budget_query.filter(ServiceCharge.category_id == category_id)
    
    budgets = budget_query.group_by(ServiceCharge.charge_name, ChargeCategory.name).all()
    
    # Combine data
    comparison = {}
    
    for charge_name, category, actual_amount in actuals:
        key = charge_name.lower().strip()
        comparison[key] = {
            'charge_name': charge_name,
            'category': category or 'Other',
            'actual': float(actual_amount) if actual_amount else 0,
            'budget': 0
        }
    
    for charge_name, category, budget_amount in budgets:
        key = charge_name.lower().strip()
        if key in comparison:
            comparison[key]['budget'] = float(budget_amount) if budget_amount else 0
        else:
            comparison[key] = {
                'charge_name': charge_name,
                'category': category or 'Other',
                'actual': 0,
                'budget': float(budget_amount) if budget_amount else 0
            }
    
    # Calculate variances
    results = []
    for data in comparison.values():
        variance = data['actual'] - data['budget']
        variance_pct = ((variance / data['budget']) * 100) if data['budget'] > 0 else 0
        
        results.append({
            'charge_name': data['charge_name'],
            'category': data['category'],
            'actual': data['actual'],
            'budget': data['budget'],
            'variance': variance,
            'variance_pct': variance_pct
        })
    
    # Sort by absolute variance (biggest differences first)
    results.sort(key=lambda x: abs(x['variance']), reverse=True)
    
    return jsonify(results)


def get_invoice_comparison(year, category_id=None):
    """Compare proposed budget vs actual invoice costs by category"""
    from sqlalchemy import func
    
    # Get proposed budget data (sum by category)
    budget_query = db.session.query(
        ChargeCategory.id,
        ChargeCategory.name,
        func.sum(ServiceCharge.amount).label('budget_amount')
    ).join(ServiceCharge).join(Document).filter(
        ServiceCharge.year == year,
        Document.document_type == 'Proposed Budget'
    )
    
    if category_id:
        budget_query = budget_query.filter(ChargeCategory.id == category_id)
    
    budgets = budget_query.group_by(ChargeCategory.id, ChargeCategory.name).all()
    
    # Get actual costs data (sum by category)
    actuals_query = db.session.query(
        ChargeCategory.id,
        ChargeCategory.name,
        func.sum(ActualCost.total_amount).label('actual_amount')
    ).join(ActualCost).filter(
        ActualCost.year == year
    )
    
    if category_id:
        actuals_query = actuals_query.filter(ChargeCategory.id == category_id)
    
    actuals = actuals_query.group_by(ChargeCategory.id, ChargeCategory.name).all()
    
    # Combine data by category
    comparison = {}
    
    for cat_id, cat_name, budget_amount in budgets:
        comparison[cat_id] = {
            'charge_name': cat_name,
            'category': cat_name,
            'budget': float(budget_amount) if budget_amount else 0,
            'actual': 0
        }
    
    for cat_id, cat_name, actual_amount in actuals:
        if cat_id in comparison:
            comparison[cat_id]['actual'] = float(actual_amount) if actual_amount else 0
        else:
            comparison[cat_id] = {
                'charge_name': cat_name,
                'category': cat_name,
                'budget': 0,
                'actual': float(actual_amount) if actual_amount else 0
            }
    
    # Calculate variances
    results = []
    for data in comparison.values():
        variance = data['actual'] - data['budget']
        variance_pct = ((variance / data['budget']) * 100) if data['budget'] > 0 else 0
        
        results.append({
            'charge_name': data['charge_name'],
            'category': data['category'],
            'actual': data['actual'],
            'budget': data['budget'],
            'variance': variance,
            'variance_pct': variance_pct
        })
    
    # Sort by absolute variance
    results.sort(key=lambda x: abs(x['variance']), reverse=True)
    
    return jsonify(results)


@app.route('/api/category-charges')
def get_category_charges():
    """Get list of charges within a specific category for a given year"""
    from sqlalchemy import func
    
    year = request.args.get('year', type=int)
    category_name = request.args.get('category')
    mode = request.args.get('mode', 'invoices')
    
    if not year or not category_name:
        return jsonify({'error': 'Year and category parameters required'}), 400
    
    # Get the category
    category = ChargeCategory.query.filter_by(name=category_name).first()
    if not category:
        return jsonify({'error': 'Category not found'}), 404
    
    # Get charges for this category from budget
    budget_charges = db.session.query(
        ServiceCharge.charge_name,
        ServiceCharge.amount
    ).join(Document).filter(
        ServiceCharge.year == year,
        ServiceCharge.category_id == category.id,
        Document.document_type == 'Proposed Budget'
    ).all()
    
    charges = [
        {
            'name': charge_name,
            'amount': float(amount) if amount else 0
        }
        for charge_name, amount in budget_charges
    ]
    
    # Sort by amount descending
    charges.sort(key=lambda x: x['amount'], reverse=True)
    
    return jsonify(charges)


@app.route('/api/gap-analysis')
def gap_analysis():
    """Compare budgets between two years"""
    year1 = request.args.get('year1', type=int)
    year2 = request.args.get('year2', type=int)
    
    if not year1 or not year2:
        return jsonify({'error': 'Both year1 and year2 are required'}), 400
    
    if year1 == year2:
        return jsonify({'error': 'Please select two different years'}), 400
    
    # Get all charges for both years
    year1_charges = ServiceCharge.query.filter_by(year=year1).all()
    year2_charges = ServiceCharge.query.filter_by(year=year2).all()
    
    # Create dictionaries for easy lookup
    year1_dict = {}
    for charge in year1_charges:
        key = charge.charge_name.strip().lower()
        if key in year1_dict:
            year1_dict[key]['amount'] += charge.amount
        else:
            year1_dict[key] = {
                'name': charge.charge_name,
                'amount': charge.amount,
                'category': charge.category.name if charge.category else 'Other'
            }
    
    year2_dict = {}
    for charge in year2_charges:
        key = charge.charge_name.strip().lower()
        if key in year2_dict:
            year2_dict[key]['amount'] += charge.amount
        else:
            year2_dict[key] = {
                'name': charge.charge_name,
                'amount': charge.amount,
                'category': charge.category.name if charge.category else 'Other'
            }
    
    # Get all unique charge names
    all_charges = set(year1_dict.keys()) | set(year2_dict.keys())
    
    details = []
    total_year1 = 0
    total_year2 = 0
    increases_count = 0
    decreases_count = 0
    increases_total = 0
    decreases_total = 0
    
    for charge_key in all_charges:
        year1_data = year1_dict.get(charge_key, {'name': '', 'amount': 0, 'category': 'Other'})
        year2_data = year2_dict.get(charge_key, {'name': '', 'amount': 0, 'category': 'Other'})
        
        charge_name = year2_data.get('name') or year1_data.get('name')
        year1_amount = year1_data['amount']
        year2_amount = year2_data['amount']
        category = year2_data.get('category') or year1_data.get('category')
        
        change = year2_amount - year1_amount
        
        total_year1 += year1_amount
        total_year2 += year2_amount
        
        if change > 0:
            increases_count += 1
            increases_total += change
        elif change < 0:
            decreases_count += 1
            decreases_total += change
        
        details.append({
            'charge_name': charge_name,
            'category': category,
            'year1_amount': round(year1_amount, 2),
            'year2_amount': round(year2_amount, 2),
            'change': round(change, 2)
        })
    
    # Sort by absolute change (biggest changes first)
    details.sort(key=lambda x: abs(x['change']), reverse=True)
    
    total_change = total_year2 - total_year1
    total_change_percent = ((total_change / total_year1) * 100) if total_year1 > 0 else 0
    
    return jsonify({
        'year1': year1,
        'year2': year2,
        'summary': {
            'total_year1': round(total_year1, 2),
            'total_year2': round(total_year2, 2),
            'total_change': round(total_change, 2),
            'total_change_percent': round(total_change_percent, 2),
            'increases_count': increases_count,
            'decreases_count': decreases_count,
            'increases_total': round(increases_total, 2),
            'decreases_total': round(decreases_total, 2)
        },
        'details': details
    })


@app.route('/api/budget-vs-actual')
def budget_vs_actual():
    """
    Compare budgeted amounts vs actual costs for a given year.
    
    Returns budget, actual, and variance by category.
    Variance = Actual - Budget (positive means over budget)
    """
    year = request.args.get('year', type=int)
    
    if not year:
        return jsonify({'error': 'year parameter is required'}), 400
    
    from sqlalchemy import func
    
    # Get budget data (sum by category)
    budget_query = db.session.query(
        ChargeCategory.id,
        ChargeCategory.name,
        func.sum(ServiceCharge.amount).label('budget_amount')
    ).join(ServiceCharge).filter(
        ServiceCharge.year == year
    ).group_by(ChargeCategory.id).all()
    
    # Get actual cost data (sum by category)
    actual_query = db.session.query(
        ChargeCategory.id,
        ChargeCategory.name,
        func.sum(ActualCost.total_amount).label('actual_amount')
    ).join(ActualCost).filter(
        ActualCost.year == year
    ).group_by(ChargeCategory.id).all()
    
    # Create dictionaries for easy lookup
    budget_dict = {cat_id: {'name': name, 'amount': amount or 0} 
                   for cat_id, name, amount in budget_query}
    actual_dict = {cat_id: {'name': name, 'amount': amount or 0} 
                   for cat_id, name, amount in actual_query}
    
    # Get all categories that have either budget or actual data
    all_categories = set(budget_dict.keys()) | set(actual_dict.keys())
    
    details = []
    total_budget = 0
    total_actual = 0
    
    for cat_id in all_categories:
        budget_data = budget_dict.get(cat_id, {'name': '', 'amount': 0})
        actual_data = actual_dict.get(cat_id, {'name': '', 'amount': 0})
        
        category_name = budget_data.get('name') or actual_data.get('name')
        budget_amount = budget_data['amount']
        actual_amount = actual_data['amount']
        
        variance = actual_amount - budget_amount
        variance_percent = ((variance / budget_amount) * 100) if budget_amount > 0 else 0
        
        total_budget += budget_amount
        total_actual += actual_amount
        
        details.append({
            'category': category_name,
            'budget': round(budget_amount, 2),
            'actual': round(actual_amount, 2),
            'variance': round(variance, 2),
            'variance_percent': round(variance_percent, 2),
            'status': 'over' if variance > 0 else 'under' if variance < 0 else 'on'
        })
    
    # Sort by variance (biggest overruns first)
    details.sort(key=lambda x: x['variance'], reverse=True)
    
    total_variance = total_actual - total_budget
    total_variance_percent = ((total_variance / total_budget) * 100) if total_budget > 0 else 0
    
    return jsonify({
        'year': year,
        'summary': {
            'total_budget': round(total_budget, 2),
            'total_actual': round(total_actual, 2),
            'total_variance': round(total_variance, 2),
            'total_variance_percent': round(total_variance_percent, 2),
            'over_budget_count': len([d for d in details if d['status'] == 'over']),
            'under_budget_count': len([d for d in details if d['status'] == 'under'])
        },
        'details': details
    })


def init_db():
    """Initialize database tables"""
    with app.app_context():
        db.create_all()
        logger.info("Database tables created")
        
        # Create default categories if none exist
        if ChargeCategory.query.count() == 0:
            default_categories = [
                'Management', 'Insurance', 'Maintenance', 'Cleaning',
                'Utilities', 'Lift/Elevator', 'Grounds', 'Security',
                'Reserve Fund', 'Other'
            ]
            
            for cat_name in default_categories:
                category = ChargeCategory(name=cat_name)
                db.session.add(category)
            
            db.session.commit()
            logger.info(f"Created {len(default_categories)} default categories")


if __name__ == '__main__':
    init_db()
    app.run(debug=os.getenv('FLASK_DEBUG', 'False').lower() == 'true')
