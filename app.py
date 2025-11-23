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
        'categories': ChargeCategory.query.filter_by(is_active=True).all()
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
    
    query = ServiceCharge.query
    
    if year:
        query = query.filter_by(year=year)
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    charges = query.all()
    
    return jsonify([{
        'id': c.id,
        'year': c.year,
        'charge_name': c.charge_name,
        'amount': c.amount,
        'currency': c.currency,
        'category': c.category.name if c.category else None
    } for c in charges])


@app.route('/api/trends')
def get_trends():
    """Get year-over-year trend data"""
    # Group charges by year and calculate totals
    from sqlalchemy import func
    
    trends = db.session.query(
        ServiceCharge.year,
        func.sum(ServiceCharge.amount).label('total_amount'),
        func.count(ServiceCharge.id).label('charge_count')
    ).group_by(ServiceCharge.year).order_by(ServiceCharge.year).all()
    
    return jsonify([{
        'year': t.year,
        'total_amount': float(t.total_amount),
        'charge_count': t.charge_count
    } for t in trends])


@app.route('/api/categories')
def get_categories():
    """Get all charge categories"""
    categories = ChargeCategory.query.filter_by(is_active=True).all()
    
    return jsonify([{
        'id': c.id,
        'name': c.name,
        'description': c.description
    } for c in categories])


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
