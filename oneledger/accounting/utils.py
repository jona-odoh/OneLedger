from .models import Transaction
from oneledger import db
from datetime import datetime, date # Ensure date is imported
from sqlalchemy import func

def calculate_profit_loss(user_id, start_date, end_date):
    """
    Calculates profit and loss for a given user and date range.
    """
    # Ensure end_date includes the entire day by setting time to 23:59:59.999999
    # This is important if end_date is a date object without time.
    if isinstance(end_date, date) and not isinstance(end_date, datetime):
        end_date_dt = datetime.combine(end_date, datetime.max.time())
    else:
        end_date_dt = end_date

    if isinstance(start_date, date) and not isinstance(start_date, datetime):
        start_date_dt = datetime.combine(start_date, datetime.min.time())
    else:
        start_date_dt = start_date

    income_transactions = Transaction.query.filter(
        Transaction.user_id == user_id,
        Transaction.transaction_type == 'income',
        Transaction.date >= start_date_dt,
        Transaction.date <= end_date_dt
    ).all()

    expense_transactions = Transaction.query.filter(
        Transaction.user_id == user_id,
        Transaction.transaction_type == 'expense',
        Transaction.date >= start_date_dt,
        Transaction.date <= end_date_dt
    ).all()

    total_income = db.session.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == user_id,
        Transaction.transaction_type == 'income',
        Transaction.date >= start_date_dt,
        Transaction.date <= end_date_dt
    ).scalar() or 0.0

    total_expenses = db.session.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == user_id,
        Transaction.transaction_type == 'expense',
        Transaction.date >= start_date_dt,
        Transaction.date <= end_date_dt
    ).scalar() or 0.0

    net_profit = total_income - total_expenses

    return {
        'total_income': total_income,
        'total_expenses': total_expenses,
        'net_profit': net_profit,
        'start_date': start_date, # Original start_date for display
        'end_date': end_date,     # Original end_date for display
        'income_transactions_list': income_transactions,
        'expense_transactions_list': expense_transactions
    }

def calculate_balance_sheet(user_id, as_of_date):
    """
    Calculates balance sheet data for a given user as of a specific date.
    Note: This is a simplified model. True double-entry bookkeeping would be required for an accurate Balance Sheet.
    Assumes 'asset' transactions increase assets, 'liability' transactions increase liabilities.
    Equity is primarily represented by retained earnings (simplified).
    """

    # Ensure as_of_date includes the entire day
    if isinstance(as_of_date, date) and not isinstance(as_of_date, datetime):
        as_of_date_dt = datetime.combine(as_of_date, datetime.max.time())
    else:
        as_of_date_dt = as_of_date

    # Calculate Assets
    asset_transactions = Transaction.query.filter(
        Transaction.user_id == user_id,
        Transaction.transaction_type == 'asset', # Assuming 'asset' type exists and is used
        Transaction.date <= as_of_date_dt
    ).all()
    total_assets = db.session.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == user_id,
        Transaction.transaction_type == 'asset',
        Transaction.date <= as_of_date_dt
    ).scalar() or 0.0

    # Calculate Liabilities
    liability_transactions = Transaction.query.filter(
        Transaction.user_id == user_id,
        Transaction.transaction_type == 'liability', # Assuming 'liability' type exists
        Transaction.date <= as_of_date_dt
    ).all()
    total_liabilities = db.session.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == user_id,
        Transaction.transaction_type == 'liability',
        Transaction.date <= as_of_date_dt
    ).scalar() or 0.0

    # Calculate Retained Earnings (simplified as Total Income - Total Expenses up to as_of_date)
    total_income_to_date = db.session.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == user_id,
        Transaction.transaction_type == 'income',
        Transaction.date <= as_of_date_dt
    ).scalar() or 0.0

    total_expenses_to_date = db.session.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == user_id,
        Transaction.transaction_type == 'expense',
        Transaction.date <= as_of_date_dt
    ).scalar() or 0.0

    retained_earnings = total_income_to_date - total_expenses_to_date

    # Simplified Total Equity
    total_equity = retained_earnings
    # In a more complex model, equity would include owner contributions, distributions, etc.

    return {
        'as_of_date': as_of_date, # Original as_of_date for display
        'total_assets': total_assets,
        'asset_transactions_list': asset_transactions,
        'total_liabilities': total_liabilities,
        'liability_transactions_list': liability_transactions,
        'total_equity': total_equity,
        'retained_earnings': retained_earnings,
        'debug_total_income_to_date': total_income_to_date, # for verification
        'debug_total_expenses_to_date': total_expenses_to_date # for verification
    }

def calculate_cash_flow(user_id, start_date, end_date):
    """
    Calculates cash flow statement data for a given user and date range.
    Simplified version based on current transaction model.
    """
    if isinstance(end_date, date) and not isinstance(end_date, datetime):
        end_date_dt = datetime.combine(end_date, datetime.max.time())
    else:
        end_date_dt = end_date

    if isinstance(start_date, date) and not isinstance(start_date, datetime):
        start_date_dt = datetime.combine(start_date, datetime.min.time())
    else:
        start_date_dt = start_date

    # --- Operating Activities ---
    # Start with Net Income for the period
    period_income_transactions = Transaction.query.filter(
        Transaction.user_id == user_id,
        Transaction.transaction_type == 'income',
        Transaction.date >= start_date_dt,
        Transaction.date <= end_date_dt
    ).all()
    period_total_income = sum(t.amount for t in period_income_transactions)

    period_expense_transactions = Transaction.query.filter(
        Transaction.user_id == user_id,
        Transaction.transaction_type == 'expense',
        Transaction.date >= start_date_dt,
        Transaction.date <= end_date_dt
    ).all()
    period_total_expenses = sum(t.amount for t in period_expense_transactions)

    net_income = period_total_income - period_total_expenses
    # For this simplified model, cash from operations is effectively net income,
    # as we assume all income/expenses are cash transactions and no non-cash adjustments.
    cash_from_operating = net_income

    # --- Investing Activities ---
    # Purchase of asset = cash outflow (-ve). Sale of asset = cash inflow (+ve).
    # If 'asset' transaction amount is positive (asset value increase), it's an outflow.
    investing_transactions_period = Transaction.query.filter(
        Transaction.user_id == user_id,
        Transaction.transaction_type == 'asset',
        Transaction.date >= start_date_dt,
        Transaction.date <= end_date_dt
    ).all()
    # Assuming positive amount for asset type means purchase (outflow)
    # and negative amount means sale (inflow).
    cash_from_investing = sum(-t.amount for t in investing_transactions_period)


    # --- Financing Activities ---
    # Taking a loan = cash inflow (+ve). Repaying loan principal = cash outflow (-ve).
    # If 'liability' transaction amount is positive (liability value increase), it's an inflow.
    financing_transactions_period = Transaction.query.filter(
        Transaction.user_id == user_id,
        Transaction.transaction_type == 'liability',
        Transaction.date >= start_date_dt,
        Transaction.date <= end_date_dt
    ).all()
    cash_from_financing = sum(t.amount for t in financing_transactions_period)

    net_cash_flow = cash_from_operating + cash_from_investing + cash_from_financing

    # Cash at beginning/end of period is complex without a dedicated cash account or opening balances.
    # For now, we'll focus on the flows during the period.

    return {
        'start_date': start_date,
        'end_date': end_date,
        'net_income_for_period': net_income, # For operating activities starting point
        'cash_from_operating': cash_from_operating,
        'operating_income_transactions': period_income_transactions,
        'operating_expense_transactions': period_expense_transactions,
        'cash_from_investing': cash_from_investing,
        'investing_transactions_list': investing_transactions_period,
        'cash_from_financing': cash_from_financing,
        'financing_transactions_list': financing_transactions_period,
        'net_cash_flow': net_cash_flow
    }
