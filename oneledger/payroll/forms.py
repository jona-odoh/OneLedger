from flask_wtf import FlaskForm
from wtforms import StringField, DateField, FloatField, SelectField, BooleanField, SubmitField, TextAreaField, HiddenField
from wtforms import FieldList, FormField # For PayslipEditForm
from wtforms.validators import DataRequired, Length, Email, Optional, ValidationError
from datetime import date

class EmployeeForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=50)])
    email = StringField('Email', validators=[Optional(), Email(message="Invalid email address."), Length(max=120)])
    phone_number = StringField('Phone Number', validators=[Optional(), Length(max=20)])

    date_of_birth = DateField('Date of Birth', format='%Y-%m-%d', validators=[Optional()])
    date_hired = DateField('Date Hired', format='%Y-%m-%d',
                           validators=[DataRequired(message="Date hired is required.")],
                           default=date.today)

    job_title = StringField('Job Title', validators=[Optional(), Length(max=100)])
    # Assuming salary is annual. Add help text in template if it's monthly/hourly.
    salary = FloatField('Salary', validators=[DataRequired(message="Salary is required.")])

    payment_method = SelectField('Payment Method',
                                 choices=[
                                     ('', 'Select...'),
                                     ('bank_transfer', 'Bank Transfer'),
                                     ('check', 'Check'),
                                     ('other', 'Other')
                                 ],
                                 validators=[Optional()])
    # Using TextAreaField for potentially multi-line bank details.
    bank_account_details = TextAreaField('Bank Account Details (if applicable)',
                                         validators=[Optional(), Length(max=300)])

    is_active = BooleanField('Is Active Employee', default=True)

    submit = SubmitField('Save Employee')


class PayPeriodForm(FlaskForm):
    name = StringField('Pay Period Name',
                       validators=[DataRequired(), Length(max=100)],
                       description="e.g., Monthly - January 2024, Weekly Wk1 Jan")
    start_date = DateField('Start Date', format='%Y-%m-%d', validators=[DataRequired()])
    end_date = DateField('End Date', format='%Y-%m-%d', validators=[DataRequired()])
    pay_date = DateField('Payment Date', format='%Y-%m-%d', validators=[DataRequired()])
    submit = SubmitField('Save Pay Period')

    def validate_end_date(self, field):
        if self.start_date.data and field.data < self.start_date.data:
            raise ValidationError('End date cannot be earlier than start date.')

    def validate_pay_date(self, field):
        if self.end_date.data and field.data < self.end_date.data:
            raise ValidationError('Pay date cannot be earlier than the period end date.')


class PayrollRunForm(FlaskForm):
    pay_period_id = SelectField('Select Pay Period', coerce=int, validators=[DataRequired()])
    # employees field will be SelectMultipleField, choices populated in route
    # For now, just defining it. Actual choices and validation will be tricky without JS for selection.
    # This field might be better handled with checkboxes or a more interactive UI in a real app.
    # employees = SelectMultipleField('Select Employees', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Generate Payslips')


# For individual additions/deductions lines within PayslipEditForm
class PayslipItemLineForm(FlaskForm):
    # Using a prefix to avoid clashes if rendered directly, though typically used with FormField
    # id = HiddenField("Line ID") # Optional: if you need to track existing items during edit
    description = StringField('Description', validators=[DataRequired(), Length(max=100)])
    amount = FloatField('Amount', validators=[DataRequired()])
    # item_type = HiddenField('Item Type') # 'addition' or 'deduction' - set programmatically

    # For Additions
    is_taxable = BooleanField('Taxable', default=True)
    # For Deductions
    is_pre_tax = BooleanField('Pre-tax', default=False)


class PayslipEditForm(FlaskForm):
    gross_salary = FloatField('Gross Salary for Period', validators=[DataRequired()])
    notes = TextAreaField('Notes', validators=[Optional(), Length(max=500)])

    # FieldList for dynamic additions and deductions
    # Note: Rendering and managing these effectively in HTML/JS can be complex
    additions = FieldList(FormField(PayslipItemLineForm), min_entries=0, label='Additions')
    deductions = FieldList(FormField(PayslipItemLineForm), min_entries=0, label='Deductions')

    submit = SubmitField('Update Payslip & Recalculate')
