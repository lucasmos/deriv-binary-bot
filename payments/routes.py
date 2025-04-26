from flask import render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from . import payments_bp
from .services import payment_service
from .forms import DepositForm, WithdrawForm

@payments_bp.route('/deposit', methods=['GET', 'POST'])
@login_required
def deposit():
    form = DepositForm()
    if form.validate_on_submit():
        result = payment_service.process_deposit(
            user_id=current_user.id,
            amount=form.amount.data,
            currency=form.currency.data,
            provider=form.provider.data,
            method_id=form.method_id.data
        )
        if result['success']:
            flash('Deposit initiated successfully!', 'success')
            return redirect(url_for('payments.transaction_status', transaction_id=result['transaction_id']))
        else:
            flash(result['message'], 'danger')
    return render_template('payments/deposit.html', form=form)

@payments_bp.route('/withdraw', methods=['GET', 'POST'])
@login_required
def withdraw():
    form = WithdrawForm()
    if form.validate_on_submit():
        result = payment_service.process_withdrawal(
            user_id=current_user.id,
            amount=form.amount.data,
            currency=form.currency.data,
            provider=form.provider.data,
            account_details=form.account_details.data
        )
        if result['success']:
            flash('Withdrawal request submitted!', 'success')
            return redirect(url_for('payments.transaction_status', transaction_id=result['transaction_id']))
        else:
            flash(result['message'], 'danger')
    return render_template('payments/withdraw.html', form=form)

@payments_bp.route('/transaction/<transaction_id>')
@login_required
def transaction_status(transaction_id):
    transaction = payment_service.get_transaction(transaction_id)
    if not transaction or transaction.user_id != current_user.id:
        flash('Transaction not found', 'danger')
        return redirect(url_for('main.index'))
    return render_template('payments/transaction_status.html', transaction=transaction)

@payments_bp.route('/webhook/<provider>', methods=['POST'])
def payment_webhook(provider):
    return payment_service.handle_webhook(provider, request)