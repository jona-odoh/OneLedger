from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FloatField, DateField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, Optional # Optional might be useful for some fields later
from datetime import date, timedelta
from wtforms import SubmitField # Ensure SubmitField is imported

class TransactionForm(FlaskForm):
    date = DateField('Date', format='%Y-%m-%d', validators=[DataRequired()], default=date.today)
    description = TextAreaField('Description', validators=[DataRequired(), Length(min=1, max=200)])
    category = StringField('Category', validators=[DataRequired(), Length(min=1, max=50)])
    amount = FloatField('Amount', validators=[DataRequired()])
    # Choices should be value, label pairs
    transaction_type = SelectField('Type',
                                   choices=[
                                       ('income', 'Income'),
                                       ('expense', 'Expense'),
                                       ('asset', 'Asset'),
                                       ('liability', 'Liability')
                                   ],
                                   validators=[DataRequired()])
    submit = SubmitField('Save Transaction')

class ReportPeriodForm(FlaskForm):
    start_date = DateField('Start Date', format='%Y-%m-%d',
                           validators=[DataRequired()],
                           default=lambda: date.today().replace(day=1))
    end_date = DateField('End Date', format='%Y-%m-%d',
                         validators=[DataRequired()],
                         default=date.today)
    submit = SubmitField('Generate Report')

class BalanceSheetDateForm(FlaskForm):
    as_of_date = DateField('As of Date', format='%Y-%m-%d',
                           validators=[DataRequired()],
                           default=date.today)
    submit = SubmitField('Generate Report')
