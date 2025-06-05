from oneledger import db
# from oneledger.auth.models import User # Not strictly needed for ForeignKey if using string 'user.id'
from datetime import date

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), nullable=True)  # For contact, not login
    phone_number = db.Column(db.String(20), nullable=True)
    date_of_birth = db.Column(db.Date, nullable=True)
    date_hired = db.Column(db.Date, nullable=False, default=date.today)
    job_title = db.Column(db.String(100), nullable=True)
    # Using Float for salary. For higher precision, especially with financial data,
    # SQLAlchemy's Numeric type is often preferred, mapped to DECIMAL or NUMERIC in SQL.
    salary = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50), nullable=True) # e.g., "Bank Transfer", "Check"
    bank_account_details = db.Column(db.String(200), nullable=True) # Consider encryption for sensitive data
    is_active = db.Column(db.Boolean, default=True, nullable=False) # To mark if employee is current

    # Foreign Key to link Employee to the User (business owner/admin)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Relationship to Payslip - one employee can have many payslips
    payslips = db.relationship('Payslip', backref='employee_record', lazy='dynamic')


    def __repr__(self):
        return f"Employee('{self.first_name}', '{self.last_name}', '{self.job_title}')"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class PayPeriod(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False) # e.g., "Monthly - Jan 2024", "Weekly - Week 1 Jan 2024"
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    pay_date = db.Column(db.Date, nullable=False) # When payment is due/made

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) # Who defined this pay period

    # Relationships
    payslips = db.relationship('Payslip', backref='pay_period_info', lazy='dynamic')

    # Unique constraint for name per user
    __table_args__ = (db.UniqueConstraint('name', 'user_id', name='uq_payperiod_name_user'),)


    def __repr__(self):
        return f"PayPeriod('{self.name}', '{self.start_date.strftime('%Y-%m-%d')}' to '{self.end_date.strftime('%Y-%m-%d')}')"


class Payslip(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    pay_period_id = db.Column(db.Integer, db.ForeignKey('pay_period.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) # The user running payroll (owner of the payslip)

    gross_salary = db.Column(db.Float, nullable=False) # Base salary for the period
    total_additions = db.Column(db.Float, default=0.0)
    total_deductions = db.Column(db.Float, default=0.0)
    taxable_income = db.Column(db.Float, default=0.0) # Gross + taxable additions - pre-tax deductions
    income_tax = db.Column(db.Float, default=0.0) # Calculated tax amount
    net_pay = db.Column(db.Float, default=0.0) # Gross + additions - deductions - tax

    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp()) # Use db.func for server-side default
    status = db.Column(db.String(20), default="draft") # e.g., "draft", "processed", "paid"

    # Relationships
    # Direct reference to the employee this payslip belongs to (already handled by employee_id FK)
    # employee = db.relationship('Employee', backref='payslips_ref') # This is what was suggested, but backref on Employee.payslips is better

    additions = db.relationship('PayrollAddition', backref='payslip', lazy='dynamic', cascade='all, delete-orphan')
    deductions = db.relationship('PayrollDeduction', backref='payslip', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f"Payslip(ID: {self.id}, EmployeeID: {self.employee_id}, PeriodID: {self.pay_period_id}, NetPay: {self.net_pay})"


class PayrollAddition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    is_taxable = db.Column(db.Boolean, default=True)

    payslip_id = db.Column(db.Integer, db.ForeignKey('payslip.id'), nullable=False)

    def __repr__(self):
        return f"PayrollAddition('{self.description}', Amount: {self.amount}, PayslipID: {self.payslip_id})"


class PayrollDeduction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    is_pre_tax = db.Column(db.Boolean, default=False) # If deduction happens before tax calculation

    payslip_id = db.Column(db.Integer, db.ForeignKey('payslip.id'), nullable=False)

    def __repr__(self):
        return f"PayrollDeduction('{self.description}', Amount: {self.amount}, PayslipID: {self.payslip_id})"
