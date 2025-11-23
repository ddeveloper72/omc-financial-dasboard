import os
import logging
from flask import Flask, render_template, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from models import db, Document, ServiceCharge, ChargeCategory, ProcessingLog
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
    year = request.args.get('year', type=int)
    category_id = request.args.get('category_id', type=int)
    document_type = request.args.get('document_type')
    
    query = ServiceCharge.query.join(Document)
    
    if year:
        query = query.filter(ServiceCharge.year == year)
    if category_id:
        query = query.filter(ServiceCharge.category_id == category_id)
    if document_type:
        query = query.filter(Document.document_type == document_type)
    
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
    """Get year-over-year trend data with separate lines for actuals and budgets"""
    from sqlalchemy import func
    
    charge_type = request.args.get('charge_type', 'expense')  # Default to expenses only
    
    # Get audited accounts (actuals)
    actuals_query = db.session.query(
        ServiceCharge.year,
        func.sum(ServiceCharge.amount).label('total_amount')
    ).join(Document).filter(
        Document.document_type == 'Audited Accounts',
        ServiceCharge.charge_type == charge_type
    ).group_by(ServiceCharge.year).order_by(ServiceCharge.year)
    
    actuals = actuals_query.all()
    
    # Get proposed budgets
    budgets_query = db.session.query(
        ServiceCharge.year,
        func.sum(ServiceCharge.amount).label('total_amount')
    ).join(Document).filter(
        Document.document_type == 'Proposed Budget',
        ServiceCharge.charge_type == charge_type
    ).group_by(ServiceCharge.year).order_by(ServiceCharge.year)
    
    budgets = budgets_query.all()
    
    # Combine all years
    all_years = sorted(set([t.year for t in actuals] + [t.year for t in budgets]))
    
    # Build response with separate datasets
    actuals_dict = {t.year: float(t.total_amount) for t in actuals}
    budgets_dict = {t.year: float(t.total_amount) for t in budgets}
    
    return jsonify({
        'years': all_years,
        'actuals': [actuals_dict.get(year, None) for year in all_years],
        'budgets': [budgets_dict.get(year, None) for year in all_years]
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
    
    stats = {
        'audited_count': Document.query.filter_by(document_type='Audited Accounts').count(),
        'budget_count': Document.query.filter_by(document_type='Proposed Budget').count(),
        'audited_years': sorted([y[0] for y in audited_years if y[0]]),
        'budget_years': sorted([y[0] for y in budget_years if y[0]]),
        'categories': ChargeCategory.query.filter_by(is_active=True).all()
    }
    
    return render_template('comparison.html', stats=stats)


@app.route('/api/comparison')
def get_comparison_data():
    """Get actuals vs budget comparison data"""
    from sqlalchemy import func
    
    year = request.args.get('year', type=int)
    category_id = request.args.get('category_id', type=int)
    
    if not year:
        return jsonify({'error': 'Year parameter required'}), 400
    
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
