from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, Response
from flask_login import login_required, current_user
from oneledger import db
from oneledger.payroll.forms import EmployeeForm, PayPeriodForm, PayrollRunForm, PayslipEditForm, PayslipItemLineForm
from oneledger.payroll.models import Employee, PayPeriod, Payslip, PayrollAddition, PayrollDeduction
from .utils import calculate_period_gross_salary # Import the new utility
from sqlalchemy.exc import IntegrityError
from datetime import date, timedelta
import csv
import io

payroll_bp = Blueprint('payroll', __name__, url_prefix='/payroll')

# Employee CRUD (already implemented in previous subtask, ensure it's complete)
# ... (routes from previous subtask for employee CRUD) ...

# Pay Period CRUD
@payroll_bp.route('/pay-periods')
@login_required
def list_pay_periods():
    page = request.args.get('page', 1, type=int)
    pay_periods = PayPeriod.query.filter_by(user_id=current_user.id)\
                                 .order_by(PayPeriod.start_date.desc())\
                                 .paginate(page=page, per_page=10)
    return render_template('payroll/pay_period_list.html', pay_periods=pay_periods, title="Pay Periods")

@payroll_bp.route('/pay-period/new', methods=['GET', 'POST'])
@login_required
def add_pay_period():
    form = PayPeriodForm()
    if form.validate_on_submit():
        try:
            pay_period = PayPeriod(name=form.name.data,
                                   start_date=form.start_date.data,
                                   end_date=form.end_date.data,
                                   pay_date=form.pay_date.data,
                                   user_id=current_user.id)
            db.session.add(pay_period)
            db.session.commit()
            flash('Pay period created successfully!', 'success')
            return redirect(url_for('payroll.list_pay_periods'))
        except IntegrityError:
            db.session.rollback()
            flash('A pay period with this name already exists. Please use a unique name.', 'danger')
    return render_template('payroll/pay_period_form.html', title='Add New Pay Period', form=form, legend='New Pay Period')

@payroll_bp.route('/pay-period/<int:period_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_pay_period(period_id):
    pay_period = PayPeriod.query.get_or_404(period_id)
    if pay_period.user_id != current_user.id:
        abort(403)
    form = PayPeriodForm(obj=pay_period)
    if form.validate_on_submit():
        try:
            pay_period.name = form.name.data
            pay_period.start_date = form.start_date.data
            pay_period.end_date = form.end_date.data
            pay_period.pay_date = form.pay_date.data
            db.session.commit()
            flash('Pay period updated successfully!', 'success')
            return redirect(url_for('payroll.list_pay_periods'))
        except IntegrityError:
            db.session.rollback()
            flash('A pay period with this name already exists. Please use a unique name.', 'danger')
    return render_template('payroll/pay_period_form.html', title='Edit Pay Period', form=form, legend=f'Edit {pay_period.name}')

@payroll_bp.route('/pay-period/<int:period_id>/delete', methods=['POST'])
@login_required
def delete_pay_period(period_id):
    pay_period = PayPeriod.query.get_or_404(period_id)
    if pay_period.user_id != current_user.id:
        abort(403)
    if pay_period.payslips.count() > 0:
        flash('Cannot delete pay period as it has associated payslips. Please delete them first.', 'danger')
        return redirect(url_for('payroll.list_pay_periods'))
    db.session.delete(pay_period)
    db.session.commit()
    flash('Pay period deleted successfully!', 'success')
    return redirect(url_for('payroll.list_pay_periods'))

# Payroll Run & Payslip Management
@payroll_bp.route('/run/new', methods=['GET', 'POST'])
@login_required
def initiate_payroll_run():
    form = PayrollRunForm()
    form.pay_period_id.choices = [(pp.id, pp.name) for pp in PayPeriod.query.filter_by(user_id=current_user.id).order_by(PayPeriod.name).all()]

    active_employees = Employee.query.filter_by(user_id=current_user.id, is_active=True).order_by(Employee.last_name).all()

    if request.method == 'POST': # Simplified: using request.form for checkboxes
        pay_period_id = form.pay_period_id.data
        selected_employee_ids = request.form.getlist('selected_employees') # Get list of checked employee IDs

        if not selected_employee_ids:
            flash('Please select at least one employee for the payroll run.', 'warning')
            return render_template('payroll/payroll_run_form.html', title='Initiate Payroll Run', form=form, employees=active_employees)

        pay_period = PayPeriod.query.get_or_404(pay_period_id)
        if pay_period.user_id != current_user.id:
            abort(403)

        payslips_created_count = 0
        for emp_id_str in selected_employee_ids:
            emp_id = int(emp_id_str)
            # Check if payslip already exists for this employee and period
            existing_payslip = Payslip.query.filter_by(employee_id=emp_id, pay_period_id=pay_period.id, user_id=current_user.id).first()
            if existing_payslip:
                flash(f'Payslip for employee ID {emp_id} in period {pay_period.name} already exists. Skipped.', 'info')
                continue

            employee = Employee.query.get(emp_id)
            if not employee or employee.user_id != current_user.id:
                flash(f'Invalid employee ID {emp_id} or employee does not belong to you. Skipped.', 'warning')
                continue

            # Simplified gross salary calculation (e.g., annual salary / 12 for monthly)
            # This needs to be more robust based on pay period frequency vs salary frequency.
            # Assuming salary is annual and pay period is monthly for this simplification.
            # TODO: Make this calculation flexible (e.g., based on pay period duration)
            days_in_period = (pay_period.end_date - pay_period.start_date).days + 1
            # A common assumption for monthly from annual: salary / 12
            # Or more general: (salary / 365.25) * days_in_period
            # For now, let's use a placeholder /12 if it's a typical month (~30 days)
            # This is a major simplification.
            gross_for_period = employee.salary / 12 # Placeholder - very simplified
            # Use the new utility function for gross salary calculation
            gross_for_period = calculate_period_gross_salary(employee.salary,
                                                             pay_period.start_date,
                                                             pay_period.end_date)

            payslip = Payslip(employee_id=employee.id,
                              pay_period_id=pay_period.id,
                              user_id=current_user.id,
                              gross_salary=gross_for_period, # Calculated gross
                              status='draft')
            db.session.add(payslip)
            # Initial calculation of totals (will be zero before additions/deductions)
            # This can also be done in edit_payslip or a dedicated Payslip method
            payslip.total_additions = 0.0
            payslip.total_deductions = 0.0
            payslip.taxable_income = gross_for_period # Initial taxable is gross, adjusted later
            # Simplified tax, adjust as needed
            payslip.income_tax = payslip.taxable_income * 0.10 if payslip.taxable_income > 0 else 0
            payslip.net_pay = payslip.taxable_income - payslip.income_tax

            db.session.add(payslip) # Add again to capture updates if any
            payslips_created_count += 1

        if payslips_created_count > 0:
            db.session.commit()
            flash(f'{payslips_created_count} payslip(s) generated for period {pay_period.name}. Please review and edit.', 'success')
            return redirect(url_for('payroll.list_payslips_for_period', pay_period_id=pay_period.id))
        else:
            flash('No new payslips were generated.', 'info')
            return redirect(url_for('payroll.initiate_payroll_run'))

    return render_template('payroll/payroll_run_form.html', title='Initiate Payroll Run', form=form, employees=active_employees)


@payroll_bp.route('/period/<int:pay_period_id>/payslips')
@login_required
def list_payslips_for_period(pay_period_id):
    pay_period = PayPeriod.query.get_or_404(pay_period_id)
    if pay_period.user_id != current_user.id:
        abort(403)

    page = request.args.get('page', 1, type=int)
    payslips = Payslip.query.filter_by(pay_period_id=pay_period.id, user_id=current_user.id)\
                            .join(Employee).order_by(Employee.last_name)\
                            .paginate(page=page, per_page=10)
    return render_template('payroll/payslip_list.html', payslips=payslips, pay_period=pay_period, title=f"Payslips for {pay_period.name}")


@payroll_bp.route('/payslip/<int:payslip_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_payslip(payslip_id):
    payslip = Payslip.query.get_or_404(payslip_id)
    if payslip.user_id != current_user.id:
        abort(403)

    form = PayslipEditForm(obj=payslip) # Populate form from payslip object on GET

    if form.validate_on_submit():
        payslip.gross_salary = form.gross_salary.data
        payslip.notes = form.notes.data

        # Clear existing items before adding new ones from form
        PayrollAddition.query.filter_by(payslip_id=payslip.id).delete()
        PayrollDeduction.query.filter_by(payslip_id=payslip.id).delete()

        total_additions = 0
        taxable_additions = 0
        for item_data in form.additions.data:
            if item_data['description'] and item_data['amount'] is not None: # Ensure basic data exists
                addition = PayrollAddition(description=item_data['description'],
                                           amount=item_data['amount'],
                                           is_taxable=item_data.get('is_taxable', True), # .get for safety if checkbox not sent
                                           payslip_id=payslip.id)
                db.session.add(addition)
                total_additions += addition.amount
                if addition.is_taxable:
                    taxable_additions += addition.amount

        total_deductions = 0
        pre_tax_deductions = 0
        for item_data in form.deductions.data:
            if item_data['description'] and item_data['amount'] is not None:
                deduction = PayrollDeduction(description=item_data['description'],
                                             amount=item_data['amount'],
                                             is_pre_tax=item_data.get('is_pre_tax', False),
                                             payslip_id=payslip.id)
                db.session.add(deduction)
                total_deductions += deduction.amount
                if deduction.is_pre_tax:
                    pre_tax_deductions += deduction.amount

        payslip.total_additions = total_additions
        payslip.total_deductions = total_deductions

        # Simplified Tax Calculation
        payslip.taxable_income = payslip.gross_salary + taxable_additions - pre_tax_deductions
        # Flat 10% tax for simplicity. TODO: Implement proper tax calculation.
        payslip.income_tax = payslip.taxable_income * 0.10 if payslip.taxable_income > 0 else 0

        post_tax_deductions = total_deductions - pre_tax_deductions
        payslip.net_pay = payslip.taxable_income - payslip.income_tax - post_tax_deductions

        # Status could be updated here, e.g., 'reviewed', 'pending_payment'
        # For now, keeping it simple or handled by a separate "process payroll" step

        db.session.commit()
        flash(f'Payslip for {payslip.employee_record.full_name} updated successfully!', 'success')
        return redirect(url_for('payroll.list_payslips_for_period', pay_period_id=payslip.pay_period_id))

    # For GET request, pre-populate FieldLists if they are empty
    # WTForms FieldList with FormField should auto-populate from 'obj=payslip' if backrefs are set up
    # and if payslip.additions/deductions are lists of objects.
    # If they are SQLAlchemy dynamic query objects, they might need to be converted to lists for form population.
    # Let's assume obj=payslip handles it, if not, manual population for GET is needed here.

    return render_template('payroll/payslip_edit.html', title=f'Edit Payslip: {payslip.employee_record.full_name}', form=form, payslip=payslip)


@payroll_bp.route('/payslip/<int:payslip_id>/delete', methods=['POST'])
@login_required
def delete_payslip(payslip_id):
    payslip = Payslip.query.get_or_404(payslip_id)
    if payslip.user_id != current_user.id:
        abort(403)

    pay_period_id = payslip.pay_period_id # Store for redirect
    # Cascading delete should handle additions/deductions
    db.session.delete(payslip)
    db.session.commit()
    flash(f'Payslip for {payslip.employee_record.full_name} deleted successfully!', 'success')
    return redirect(url_for('payroll.list_payslips_for_period', pay_period_id=pay_period_id))


@payroll_bp.route('/payslip/<int:payslip_id>/download_csv')
@login_required
def download_payslip_csv(payslip_id):
    payslip = Payslip.query.get_or_404(payslip_id)
    if payslip.user_id != current_user.id:
        abort(403)

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(['Payslip Detail', 'Information'])
    writer.writerow(['Employee Name', payslip.employee_record.full_name])
    writer.writerow(['Pay Period', f"{payslip.pay_period_info.name} ({payslip.pay_period_info.start_date.strftime('%Y-%m-%d')} to {payslip.pay_period_info.end_date.strftime('%Y-%m-%d')})"])
    writer.writerow(['Payment Date', payslip.pay_period_info.pay_date.strftime('%Y-%m-%d')])
    writer.writerow(['Status', payslip.status.capitalize()])
    writer.writerow([])
    writer.writerow(['Component', 'Amount'])
    writer.writerow(['Gross Salary', f"{payslip.gross_salary:.2f}"])

    for add in payslip.additions:
        writer.writerow([f"Addition: {add.description} {'(Taxable)' if add.is_taxable else '(Non-Taxable)'}", f"{add.amount:.2f}"])
    writer.writerow(['Total Additions', f"{payslip.total_additions:.2f}"])

    for ded in payslip.deductions:
        writer.writerow([f"Deduction: {ded.description} {'(Pre-tax)' if ded.is_pre_tax else '(Post-tax)'}", f"{ded.amount:.2f}"])
    writer.writerow(['Total Deductions', f"{payslip.total_deductions:.2f}"])

    writer.writerow(['Taxable Income', f"{payslip.taxable_income:.2f}"])
    writer.writerow(['Income Tax', f"{payslip.income_tax:.2f}"])
    writer.writerow(['Net Pay', f"{payslip.net_pay:.2f}"])

    if payslip.notes:
        writer.writerow([])
        writer.writerow(['Notes', payslip.notes])

    output.seek(0)
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename=payslip_{payslip.employee_record.last_name}_{payslip.id}.csv"}
    )

@payroll_bp.route('/period/<int:pay_period_id>/download_summary_csv')
@login_required
def download_payroll_summary_csv(pay_period_id):
    pay_period = PayPeriod.query.get_or_404(pay_period_id)
    if pay_period.user_id != current_user.id:
        abort(403)

    payslips = Payslip.query.filter_by(pay_period_id=pay_period.id, user_id=current_user.id).all()

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(['Employee ID', 'Employee Name', 'Gross Salary', 'Total Additions', 'Total Deductions', 'Income Tax', 'Net Pay', 'Status'])
    for payslip in payslips:
        writer.writerow([
            payslip.employee_id,
            payslip.employee_record.full_name,
            f"{payslip.gross_salary:.2f}",
            f"{payslip.total_additions:.2f}",
            f"{payslip.total_deductions:.2f}",
            f"{payslip.income_tax:.2f}",
            f"{payslip.net_pay:.2f}",
            payslip.status.capitalize()
        ])

    output.seek(0)
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename=payroll_summary_{pay_period.name.replace(' ','_')}.csv"}
    )

@payroll_bp.route('/period/<int:pay_period_id>/process', methods=['POST'])
@login_required
def process_pay_period(pay_period_id):
    pay_period = PayPeriod.query.get_or_404(pay_period_id)
    if pay_period.user_id != current_user.id:
        abort(403)

    draft_payslips = Payslip.query.filter_by(pay_period_id=pay_period.id, user_id=current_user.id, status='draft').all()

    if not draft_payslips:
        flash('No draft payslips found for this period to process.', 'info')
        return redirect(url_for('payroll.list_payslips_for_period', pay_period_id=pay_period_id))

    processed_count = 0
    for payslip in draft_payslips:
        # Potentially re-calculate final values here if needed, or assume edit_payslip saved final state
        payslip.status = 'Processed'
        # TODO: Consider if any accounting entries should be generated here (e.g., to a ledger)
        processed_count +=1

    db.session.commit()
    flash(f'{processed_count} payslip(s) marked as Processed for period {pay_period.name}.', 'success')
    return redirect(url_for('payroll.list_payslips_for_period', pay_period_id=pay_period_id))


# Consolidating Employee CRUD routes (from Subtask 7, ensuring they are part of this blueprint)
@payroll_bp.route('/employees') # Changed from /employees_crud to be the primary employee list
@login_required
def list_employees():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    employees = Employee.query.filter_by(user_id=current_user.id)\
                              .order_by(Employee.last_name, Employee.first_name)\
                              .paginate(page=page, per_page=per_page)
    return render_template('payroll/employee_list.html', employees=employees, title="Employee Management")

@payroll_bp.route('/employee/new', methods=['GET', 'POST']) # Changed from /employee/new_crud
@login_required
def add_employee():
    form = EmployeeForm()
    if form.validate_on_submit():
        employee = Employee(first_name=form.first_name.data,
                            last_name=form.last_name.data,
                            email=form.email.data,
                            phone_number=form.phone_number.data,
                            date_of_birth=form.date_of_birth.data,
                            date_hired=form.date_hired.data,
                            job_title=form.job_title.data,
                            salary=form.salary.data,
                            payment_method=form.payment_method.data,
                            bank_account_details=form.bank_account_details.data,
                            is_active=form.is_active.data,
                            employer=current_user)
        db.session.add(employee)
        db.session.commit()
        flash('Employee has been successfully added!', 'success')
        return redirect(url_for('payroll.list_employees'))
    return render_template('payroll/employee_form.html', title='Add New Employee', form=form, legend='New Employee Details')

@payroll_bp.route('/employee/<int:employee_id>/view') # Changed from /employee/<id>/view_crud
@login_required
def view_employee(employee_id):
    employee = Employee.query.get_or_404(employee_id)
    if employee.employer != current_user:
        abort(403)
    return render_template('payroll/employee_detail.html', employee=employee, title=f"{employee.full_name} Details")

@payroll_bp.route('/employee/<int:employee_id>/edit', methods=['GET', 'POST']) # Changed from /employee/<id>/edit_crud
@login_required
def edit_employee(employee_id):
    employee = Employee.query.get_or_404(employee_id)
    if employee.employer != current_user:
        abort(403)

    form = EmployeeForm(obj=employee)
    if form.validate_on_submit():
        form.populate_obj(employee)
        db.session.commit()
        flash('Employee details have been updated!', 'success')
        return redirect(url_for('payroll.view_employee', employee_id=employee.id))

    return render_template('payroll/employee_form.html', title='Edit Employee', form=form, legend=f'Edit {employee.full_name}')

@payroll_bp.route('/employee/<int:employee_id>/toggle_active', methods=['POST']) # Changed from /employee/<id>/toggle_active_crud
@login_required
def toggle_active_employee(employee_id):
    employee = Employee.query.get_or_404(employee_id)
    if employee.employer != current_user:
        abort(403)

    employee.is_active = not employee.is_active
    db.session.commit()
    status = "activated" if employee.is_active else "deactivated"
    flash(f'Employee {employee.full_name} has been {status}.', 'success')
    return redirect(url_for('payroll.list_employees'))
