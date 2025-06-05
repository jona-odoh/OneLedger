# Payroll utility functions
from datetime import date, timedelta # Add timedelta

def calculate_period_gross_salary(annual_salary, pay_period_start_date, pay_period_end_date):
    """
    Calculates the gross salary for a specific pay period based on an annual salary.
    Args:
        annual_salary (float): The employee's annual salary.
        pay_period_start_date (date): The start date of the pay period.
        pay_period_end_date (date): The end date of the pay period.
    Returns:
        float: The calculated gross salary for the period.
    """
    if not all([annual_salary, pay_period_start_date, pay_period_end_date]):
        return 0.0 # Or raise an error

    # Calculate the number of days in the pay period
    num_days_in_period = (pay_period_end_date - pay_period_start_date).days + 1

    # Calculate the number of days in the year of the pay period for slightly more accuracy
    # This handles leap years for the daily rate calculation.
    # We use the year of the start_date as a reference.
    year = pay_period_start_date.year
    days_in_year = 366 if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0) else 365

    # A more common approach for fixed salaries is monthly/bi-weekly division rather than daily.
    # For example, if it's a monthly pay period: annual_salary / 12
    # If bi-weekly: annual_salary / 26
    # The daily rate method is more suited for irregular periods or hourly calculations.
    # Given "PayPeriod" can be arbitrary, daily rate is a flexible start.
    # However, for salaried employees, this can lead to slightly different pay each month.
    # Let's stick to the daily rate for now as per the initial thought process for flexibility.

    daily_rate = annual_salary / days_in_year # Using the specific year's day count

    period_gross_salary = daily_rate * num_days_in_period

    return round(period_gross_salary, 2)

# Placeholder for other payroll utilities if needed
# e.g., tax calculation, net pay calculation (though parts are in routes)
