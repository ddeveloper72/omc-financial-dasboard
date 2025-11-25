"""
Add ReserveBalance model to track sinking fund/reserve balances over time
"""
from models import db
from datetime import datetime

# This will be added to models.py
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
