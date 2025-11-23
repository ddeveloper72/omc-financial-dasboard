from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Document(db.Model):
    """Track processed AGM documents"""
    __tablename__ = 'documents'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    filepath = db.Column(db.String(500), nullable=False, unique=True)
    file_modified_date = db.Column(db.DateTime)
    processed_date = db.Column(db.DateTime, default=datetime.utcnow)
    document_year = db.Column(db.Integer)
    document_type = db.Column(db.String(50))  # AGM, Budget, etc.
    status = db.Column(db.String(20), default='pending')  # pending, processed, error
    error_message = db.Column(db.Text)
    
    # Relationship
    service_charges = db.relationship('ServiceCharge', backref='document', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Document {self.filename} ({self.document_year})>'


class ChargeCategory(db.Model):
    """Normalize charge types across documents"""
    __tablename__ = 'charge_categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    service_charges = db.relationship('ServiceCharge', backref='category', lazy=True)
    
    def __repr__(self):
        return f'<ChargeCategory {self.name}>'


class ServiceCharge(db.Model):
    """Store extracted charge line items with year, category, amount"""
    __tablename__ = 'service_charges'
    
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('charge_categories.id'))
    
    # Extracted data
    year = db.Column(db.Integer, nullable=False)
    charge_name = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), default='EUR')
    charge_type = db.Column(db.String(20), default='expense')  # expense, income, balance_sheet
    
    # Metadata
    raw_text = db.Column(db.Text)  # Original text extracted from document
    confidence_score = db.Column(db.Float)  # Optional: extraction confidence
    is_new_charge = db.Column(db.Boolean, default=False)
    is_terminated = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text)
    
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Prevent duplicate charges from same document
    __table_args__ = (
        db.UniqueConstraint('document_id', 'charge_name', 'year', name='unique_charge_per_document'),
    )
    
    def __repr__(self):
        return f'<ServiceCharge {self.charge_name} ({self.year}): {self.currency}{self.amount}>'


class ProcessingLog(db.Model):
    """Track parsing success and failures"""
    __tablename__ = 'processing_log'
    
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20))  # success, warning, error
    message = db.Column(db.Text)
    details = db.Column(db.Text)  # JSON or additional details
    
    def __repr__(self):
        return f'<ProcessingLog {self.status} at {self.timestamp}>'
