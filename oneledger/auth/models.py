from oneledger import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(60), nullable=False) # Store hashed passwords
    transactions = db.relationship('Transaction', backref='author', lazy=True)
    employees = db.relationship('Employee', backref='employer', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

    # # The following properties and methods are for password hashing and checking
    # # You would typically use bcrypt for this.
    # @property
    # def password(self):
    #     raise AttributeError('password is not a readable attribute')

    # @password.setter
    # def password(self, password):
    #     from oneledger import bcrypt # Import bcrypt here to avoid circular import if it's in __init__
    #     self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    # def verify_password(self, password):
    #     from oneledger import bcrypt # Import bcrypt here
    #     return bcrypt.check_password_hash(self.password_hash, password)
