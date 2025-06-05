from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from oneledger import db
from oneledger.accounting.forms import TransactionForm, ReportPeriodForm, BalanceSheetDateForm
from oneledger.accounting.models import Transaction
from .utils import calculate_profit_loss, calculate_balance_sheet, calculate_cash_flow # Import new util
from datetime import datetime, date

accounting_bp = Blueprint('accounting', __name__, url_prefix='/accounting')

@accounting_bp.route('/')
@accounting_bp.route('/transactions')
@login_required
def list_transactions():
    page = request.args.get('page', 1, type=int)
    per_page = 10 # Show 10 transactions per page
    user_transactions = Transaction.query.filter_by(author=current_user)\
                                     .order_by(Transaction.date.desc())\
                                     .paginate(page=page, per_page=per_page)
    return render_template('accounting/transactions.html', transactions=user_transactions, title="Transactions")

@accounting_bp.route('/transaction/new', methods=['GET', 'POST'])
@login_required
def add_transaction():
    form = TransactionForm()
    if form.validate_on_submit():
        transaction = Transaction(date=form.date.data,
                                  description=form.description.data,
                                  category=form.category.data,
                                  amount=form.amount.data,
                                  transaction_type=form.transaction_type.data,
                                  author=current_user)
        db.session.add(transaction)
        db.session.commit()
        flash('Your transaction has been added!', 'success')
        return redirect(url_for('accounting.list_transactions'))
    return render_template('accounting/transaction_form.html', title='Add New Transaction', form=form, legend='New Transaction')

@accounting_bp.route('/transaction/<int:transaction_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_transaction(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)
    if transaction.author != current_user:
        abort(403)  # Forbidden access

    form = TransactionForm()
    if form.validate_on_submit():
        transaction.date = form.date.data
        transaction.description = form.description.data
        transaction.category = form.category.data
        transaction.amount = form.amount.data
        transaction.transaction_type = form.transaction_type.data
        db.session.commit()
        flash('Your transaction has been updated!', 'success')
        return redirect(url_for('accounting.list_transactions'))
    elif request.method == 'GET':
        form.date.data = transaction.date
        form.description.data = transaction.description
        form.category.data = transaction.category
        form.amount.data = transaction.amount
        form.transaction_type.data = transaction.transaction_type

    return render_template('accounting/transaction_form.html', title='Edit Transaction', form=form, legend=f'Edit Transaction ID: {transaction.id}')

@accounting_bp.route('/transaction/<int:transaction_id>/delete', methods=['POST'])
@login_required
def delete_transaction(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)
    if transaction.author != current_user:
        abort(403)
    db.session.delete(transaction)
    db.session.commit()
    flash('Your transaction has been deleted!', 'success')
    return redirect(url_for('accounting.list_transactions'))

@accounting_bp.route('/reports/profit-loss', methods=['GET', 'POST'])
@login_required
def profit_loss_statement():
    form = ReportPeriodForm()
    data = None

    # Default dates for initial GET request or if form not submitted yet
    # Set start_date to the first day of the current month
    default_start_date = date.today().replace(day=1)
    # Set end_date to the current day
    default_end_date = date.today()

    if form.validate_on_submit():
        start_date = form.start_date.data
        end_date = form.end_date.data
        if end_date < start_date:
            flash('End date cannot be earlier than start date.', 'danger')
        else:
            data = calculate_profit_loss(current_user.id, start_date, end_date)
    else:
        # For GET request, or if form validation fails, set form defaults for display
        # but don't calculate data yet, or calculate for a default period.
        # Let's calculate for the default period on initial GET.
        form.start_date.data = default_start_date
        form.end_date.data = default_end_date
        # Optionally, you could auto-trigger calculation on GET:
        # data = calculate_profit_loss(current_user.id, default_start_date, default_end_date)


    return render_template('accounting/reports/profit_loss.html',
                           title='Profit & Loss Statement',
                           form=form,
                           data=data)

@accounting_bp.route('/reports/balance-sheet', methods=['GET', 'POST'])
@login_required
def balance_sheet_report():
    form = BalanceSheetDateForm()
    data = None

    # Default date for initial GET request
    default_as_of_date = date.today()

    if form.validate_on_submit():
        as_of_date = form.as_of_date.data
        data = calculate_balance_sheet(current_user.id, as_of_date)
    else:
        # For GET request, set form default for display
        form.as_of_date.data = default_as_of_date
        # Optionally, calculate for default date on GET, or require form submission
        # data = calculate_balance_sheet(current_user.id, default_as_of_date)


    return render_template('accounting/reports/balance_sheet.html',
                           title='Balance Sheet',
                           form=form,
                           data=data)

@accounting_bp.route('/reports/cash-flow', methods=['GET', 'POST'])
@login_required
def cash_flow_statement():
    form = ReportPeriodForm() # Reusing ReportPeriodForm
    data = None

    default_start_date = date.today().replace(day=1)
    default_end_date = date.today()

    if form.validate_on_submit():
        start_date = form.start_date.data
        end_date = form.end_date.data
        if end_date < start_date:
            flash('End date cannot be earlier than start date.', 'danger')
        else:
            data = calculate_cash_flow(current_user.id, start_date, end_date)
    else:
        form.start_date.data = default_start_date
        form.end_date.data = default_end_date
        # Optionally, calculate for default period on GET
        # data = calculate_cash_flow(current_user.id, default_start_date, default_end_date)

    return render_template('accounting/reports/cash_flow.html',
                           title='Cash Flow Statement',
                           form=form,
                           data=data)
