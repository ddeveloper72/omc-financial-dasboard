"""
Database Models - YTS Budget Analysis

This module defines the SQLAlchemy database models for storing
financial document data and processing logs.

Data Protection:
- No personal data stored (financial information only)
- Local SQLite database (no cloud transmission)
- Audit trail maintained via processing_log table

Technical Reference:
- SQLAlchemy: https://docs.sqlalchemy.org/
- SQLite: https://www.sqlite.org/docs.html

EU AI Act & GDPR Compliance:
- Data minimization principle followed
- Purpose limitation respected (financial analysis only)
- Transparency through audit logging
- See COMPLIANCE.md for full documentation
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Document(db.Model):
    """
    Track processed AGM documents.
    
    Stores metadata about source documents for audit trail
    and to prevent duplicate processing.
    """
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


class ReserveBalance(db.Model):
    """Track sinking fund/reserve balance over time"""
    __tablename__ = 'reserve_balances'
    
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, nullable=False, unique=True)
    opening_balance = db.Column(db.Float)  # Balance at start of year
    contributions = db.Column(db.Float)  # Money added to reserve during year
    expenditures = db.Column(db.Float)  # Money spent from reserve during year
    closing_balance = db.Column(db.Float, nullable=False)  # Balance at end of year
    source_document_id = db.Column(db.Integer, db.ForeignKey('documents.id'))
    notes = db.Column(db.Text)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    updated_date = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    source_document = db.relationship('Document', backref='reserve_balances', lazy=True)
    
    def __repr__(self):
        return f'<ReserveBalance {self.year}: EUR {self.closing_balance:,.2f}>'


class ChargeGlossary(db.Model):
    """Glossary of charge name definitions and explanations"""
    __tablename__ = 'charge_glossary'
    
    id = db.Column(db.Integer, primary_key=True)
    charge_name = db.Column(db.String(200), nullable=False, unique=True, index=True)
    definition = db.Column(db.Text, nullable=False)
    examples = db.Column(db.Text)  # Examples of what this charge typically covers
    is_active = db.Column(db.Boolean, default=True)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    updated_date = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<ChargeGlossary {self.charge_name}>'
