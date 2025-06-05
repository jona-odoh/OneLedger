from oneledger import db
from datetime import datetime
# Import User if direct reference is needed, though SQLAlchemy handles relationships via strings too.
# from oneledger.auth.models import User # Not strictly necessary for ForeignKey definition but good for clarity

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    description = db.Column(db.String(200), nullable=False) # Increased length for better descriptions
    category = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False) # Consider Numeric for precision if using a DB that supports it well (e.g., PostgreSQL)
    transaction_type = db.Column(db.String(20), nullable=False) # e.g., "income", "expense"
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Transaction('{self.date.strftime('%Y-%m-%d')}', '{self.description[:30]}...', '{self.transaction_type}', {self.amount})"
